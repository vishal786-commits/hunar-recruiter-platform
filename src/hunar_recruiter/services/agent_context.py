from __future__ import annotations

from typing import Any


def get_agent_requirements(
    agent: dict[str, Any],
) -> list[str]:
    """
    Return the custom variables required by a Hunar agent.
    """

    return agent.get("custom_variables", []) or []


def build_agent_custom_data(
    agent: dict[str, Any],
    *,
    job_description: dict[str, Any],
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the custom_data required by the selected Hunar agent.

    Job-level values come from job_description.
    Candidate-level values come from candidate.
    """

    candidate = candidate or {}

    job_title = job_description.get("title")

    location = job_description.get("location") or {}

    if isinstance(location, dict):
        city = location.get("city")
        country = location.get("country")

        if city and country:
            role_location = f"{city}, {country}"
        else:
            role_location = city or country
    else:
        role_location = (
            str(location)
            if location
            else None
        )

    # All values that an agent might request.
    context: dict[str, Any] = {
        # Job-level values
        "role_title": job_title,
        "job_title": job_title,
        "role": job_title,
        "role_location": role_location,
        "location": role_location,
        "company": job_description.get("company"),
        "key_requirements": job_description.get(
            "requirements",
            [],
        ),

        # Candidate-level values
        "candidate_name": candidate.get("name"),
    }

    required_variables = get_agent_requirements(agent)

    missing_variables: list[str] = []
    custom_data: dict[str, Any] = {}

    for variable in required_variables:
        value = context.get(variable)

        if value is None:
            missing_variables.append(variable)
        else:
            custom_data[variable] = value

    if missing_variables:
        raise ValueError(
            "Unable to build Hunar custom_data. "
            f"Missing required variables: {missing_variables}"
        )

    return custom_data