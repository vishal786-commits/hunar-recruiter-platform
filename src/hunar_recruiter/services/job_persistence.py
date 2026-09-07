from typing import Any

from sqlalchemy.orm import Session

from hunar_recruiter.models.database import CandidateDB, JobDB


def persist_analysis(
    db: Session,
    *,
    raw_jd: str,
    job_description: dict[str, Any],
    agent_routing: dict[str, Any],
    candidates: list[Any],
) -> JobDB:
    """
    Persist one complete JD analysis.

    A candidate's external/source ID is NOT used as our database
    primary key because the same person can appear for multiple jobs.
    """

    job = JobDB(
        raw_jd=raw_jd,
        parsed_jd=job_description,
        selected_agent_id=agent_routing.get(
            "selected_agent_id"
        ),
        selected_agent_code=agent_routing.get(
            "selected_agent_code"
        ),
    )

    db.add(job)
    db.flush()

    candidate_rows = []

    for candidate in candidates:

        candidate_data = candidate.model_dump()

        candidate_row = CandidateDB(
            # Internal DB ID is auto-generated.
            job_id=job.id,

            # Preserve PDL/demo ID separately.
            source_candidate_id=candidate.id,

            name=candidate.name or "Unknown",

            email=getattr(
                candidate,
                "email",
                None,
            ),

            phone=getattr(
                candidate,
                "phone_number",
                None,
            ),

            current_title=getattr(
                candidate,
                "current_title",
                None,
            ),

            location=getattr(
                candidate,
                "location",
                None,
            ),

            years_experience=getattr(
                candidate,
                "years_experience",
                None,
            ),

            skills=getattr(
                candidate,
                "skills",
                [],
            ),

            match_score=getattr(
                candidate,
                "match_score",
                None,
            ),

            source=getattr(
                candidate,
                "source",
                None,
            ),

            raw_data=candidate_data,

            approved=False,
        )

        candidate_rows.append(candidate_row)

    db.add_all(candidate_rows)
    db.commit()
    db.refresh(job)

    return job