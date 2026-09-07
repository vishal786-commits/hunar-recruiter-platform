from __future__ import annotations

import json
from pathlib import Path

from hunar_recruiter.models.candidate import Candidate


DEMO_FILE = Path("data/demo_candidates.json")


def load_demo_candidates() -> list[Candidate]:
    if not DEMO_FILE.exists():
        raise FileNotFoundError(
            f"Demo candidate file not found: {DEMO_FILE}"
        )

    with DEMO_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        Candidate(
            id=record["id"],
            name=record["name"],
            phone_number=record["phone_number"],
            phone_source="demo_participant",
            source="demo",
            is_demo=True,
        )
        for record in records
    ]