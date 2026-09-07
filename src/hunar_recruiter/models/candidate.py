from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: str
    name: str

    current_title: str | None = None
    company: str | None = None
    location: str | None = None

    skills: list[str] = Field(default_factory=list)
    years_experience: float | None = None

    linkedin_url: str | None = None

    phone_number: str | None = None
    phone_source: Literal[
        "pdl",
        "demo_placeholder",
        "demo_participant",
    ] | None = None

    source: Literal["pdl", "demo"]
    is_demo: bool = False

    match_score: float = 0.0