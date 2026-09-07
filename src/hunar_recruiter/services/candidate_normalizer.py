from __future__ import annotations

from typing import Any

from hunar_recruiter.models.candidate import Candidate


def get_location(record: dict[str, Any]) -> str | None:
    """
    PDL can return location_name as a boolean when the actual
    value is not exposed. Build a location from the usable fields.
    """

    location_name = record.get("location_name")

    if isinstance(location_name, str):
        return location_name

    locality = record.get("location_locality")
    region = record.get("location_region")
    country = record.get("location_country")

    parts = [
        value
        for value in (locality, region, country)
        if isinstance(value, str) and value.strip()
    ]

    return ", ".join(parts) if parts else None


def normalize_pdl_candidate(
    record: dict[str, Any],
) -> Candidate:

    return Candidate(
        id=f"pdl_{record.get('id')}",
        name=record.get("full_name") or "Unknown",

        current_title=record.get("job_title"),
        company=record.get("job_company_name"),
        location=get_location(record),

        skills=record.get("skills") or [],

        linkedin_url=record.get("linkedin_url"),

        # PDL free access tells us whether a phone exists,
        # but doesn't expose the actual phone value.
        phone_number=None,
        phone_source="demo_placeholder",

        source="pdl",
        is_demo=False,
    )