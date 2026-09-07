from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from hunar_recruiter.integrations.hunar import HunarClient
from hunar_recruiter.models import candidate
from hunar_recruiter.models.database import (
    CandidateDB,
    ScreeningDB,
)
from hunar_recruiter.services.agent_context import (
    build_agent_custom_data,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTS_PATH = PROJECT_ROOT / "data" / "agents.json"


def load_agent_from_registry(
    agent_id: str,
) -> dict[str, Any]:
    """
    Load a Hunar agent from data/agents.json.
    """

    if not AGENTS_PATH.exists():
        raise FileNotFoundError(
            f"Agent registry not found: {AGENTS_PATH}"
        )

    with AGENTS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        registry = json.load(file)

    if isinstance(registry, dict):
        agents = registry.get("results", [])
    else:
        agents = registry

    for agent in agents:
        registry_agent_id = agent.get(
            "agent_id",
            agent.get("id"),
        )

        if registry_agent_id == agent_id:
            return agent

    raise ValueError(
        f"Agent {agent_id} was not found in data/agents.json."
    )


def start_screening(
    db: Session,
    *,
    candidate: CandidateDB,
    agent_id: str,
    agent_code: str | None,
    job_description: dict[str, Any],
) -> ScreeningDB:
    """
    Create a local screening record and start the corresponding
    Hunar voice call.
    """

    # ---------------------------------------------------------
    # Load selected agent configuration
    # ---------------------------------------------------------

    agent = load_agent_from_registry(agent_id)

    # ---------------------------------------------------------
    # Build custom_data required by this specific agent
    # ---------------------------------------------------------

    custom_data = build_agent_custom_data(
        agent,
        job_description=job_description,
        candidate={
            "name": candidate.name,
        },
    )

    # ---------------------------------------------------------
    # Deterministic request ID
    # ---------------------------------------------------------

    request_id = f"scr-{candidate.id[:20]}"

    # ---------------------------------------------------------
    # Avoid accidentally creating the same screening twice
    # ---------------------------------------------------------

    existing = (
        db.query(ScreeningDB)
        .filter(
            ScreeningDB.request_id == request_id
        )
        .first()
    )

    if existing:
        return existing

    # ---------------------------------------------------------
    # Create local screening record first
    # ---------------------------------------------------------

    screening = ScreeningDB(
        candidate_id=candidate.id,
        agent_id=agent_id,
        agent_code=agent_code,
        request_id=request_id,
        status="PENDING",
    )

    db.add(screening)
    db.commit()
    db.refresh(screening)

    # ---------------------------------------------------------
    # Call Hunar
    # ---------------------------------------------------------

    hunar = HunarClient()

    try:
        print(
            f"DEBUG Hunar request_id: {request_id} "
            f"(length={len(request_id)})"
        )
        
        response = hunar.create_call(
            agent_id=agent_id,
            callee_name=candidate.name,
            mobile_number=candidate.phone,
            custom_data=custom_data,
            request_id=request_id,
        )

        call_id = response.get("id")

        if not call_id:
            raise ValueError(
                "Hunar API response did not contain a call ID."
            )

        # -----------------------------------------------------
        # Save Hunar response locally
        # -----------------------------------------------------

        screening.hunar_call_id = call_id

        screening.status = response.get(
            "status",
            "NOT_STARTED",
        )

        screening.lifecycle_status = response.get(
            "lifecycle_status"
        )

        screening.raw_hunar_response = response

        screening.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(screening)

        return screening

    except Exception as exc:
        screening.status = "FAILED"
        screening.error_message = str(exc)
        screening.updated_at = datetime.utcnow()

        db.commit()

        raise


def sync_screening(
    db: Session,
    screening: ScreeningDB,
) -> ScreeningDB:
    """
    Fetch the latest Hunar call state and synchronize
    it into our local database.
    """

    if not screening.hunar_call_id:
        raise ValueError(
            "Screening does not have a Hunar call ID."
        )

    hunar = HunarClient()

    response = hunar.get_call(
        screening.hunar_call_id
    )

    screening.status = response.get(
        "status",
        screening.status,
    )

    screening.lifecycle_status = response.get(
        "lifecycle_status"
    )

    screening.recording_url = response.get(
        "recording_url"
    )

    screening.result = response.get(
        "result"
    )

    screening.raw_hunar_response = response

    screening.started_at = _parse_datetime(
        response.get("started_at")
    )

    screening.ended_at = _parse_datetime(
        response.get("ended_at")
    )

    screening.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(screening)

    return screening


def _parse_datetime(
    value: str | None,
) -> datetime | None:

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError:
        return None