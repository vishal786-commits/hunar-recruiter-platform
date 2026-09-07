from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from hunar_recruiter.agent_routing.registry import load_agents
from hunar_recruiter.schemas import JobDescription


load_dotenv()


# -------------------------------------------------------------------
# OpenAI client
# -------------------------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured."
    )

client = OpenAI(
    api_key=api_key
)


# -------------------------------------------------------------------
# Prompt
# -------------------------------------------------------------------

SYSTEM_PROMPT = """
You are an agent-routing system for an AI recruiting platform.

Your task is to select the most appropriate Hunar voice agent
for a given structured job description.

Consider:

1. The role/title being recruited for.
2. Required technical and functional skills.
3. Seniority and experience.
4. The agent's purpose.
5. The type of screening the agent performs.
6. Whether the agent can realistically evaluate this role.
7. Whether the agent's required inputs are compatible with the
   information available from the job description.

Prefer agents specifically designed for the role over generic
screening agents.

Do not invent agents.
Only select agents from the supplied available_agents list.

Return ONLY valid JSON matching the requested schema.
"""


# -------------------------------------------------------------------
# Registry normalization
# -------------------------------------------------------------------

def normalize_registry_agent(
    agent: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize an agent from data/agents.json into the representation
    used by the router.

    The registry may expose the Hunar ID as either:
        - agent_id
        - id

    Similarly, purpose/summary may vary depending on how the registry
    was generated.
    """

    agent_id = agent.get("agent_id") or agent.get("id")

    if not agent_id:
        raise ValueError(
            f"Registry agent is missing an ID: {agent}"
        )

    agent_code = agent.get("agent_code")

    if not agent_code:
        raise ValueError(
            f"Registry agent {agent_id} is missing agent_code."
        )

    purpose = (
        agent.get("purpose")
        or agent.get("summary")
        or ""
    )

    return {
        "agent_id": agent_id,
        "agent_code": agent_code,
        "name": agent.get("name", ""),
        "purpose": purpose,
        "language": agent.get("language", ""),
        "custom_variables": (
            agent.get("custom_variables") or []
        ),
        "status": agent.get(
            "status",
            "ACTIVE",
        ),
    }


def build_routing_agents(
    agents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build the compact agent catalogue supplied to the LLM.
    """

    routing_agents: list[dict[str, Any]] = []

    for raw_agent in agents:

        normalized = normalize_registry_agent(
            raw_agent
        )

        if normalized["status"] != "ACTIVE":
            continue

        routing_agents.append(
            {
                "agent_id": normalized["agent_id"],
                "agent_code": normalized["agent_code"],
                "name": normalized["name"],
                "purpose": normalized["purpose"],
                "language": normalized["language"],
                "custom_variables": normalized[
                    "custom_variables"
                ],
            }
        )

    return routing_agents


# -------------------------------------------------------------------
# Router
# -------------------------------------------------------------------

def route_agent(
    job_description: JobDescription,
) -> dict[str, Any]:
    """
    Select the best Hunar agent for the supplied JD.

    The LLM selects from the local agent registry.
    The result is then validated locally before being returned.
    """

    # ---------------------------------------------------------------
    # Load local registry
    # ---------------------------------------------------------------

    raw_agents = load_agents()

    if not raw_agents:
        raise ValueError(
            "Agent registry is empty."
        )

    routing_agents = build_routing_agents(
        raw_agents
    )

    if not routing_agents:
        raise ValueError(
            "No ACTIVE agents are available in the registry."
        )

    # ---------------------------------------------------------------
    # Build LLM input
    # ---------------------------------------------------------------

    prompt = {
        "job_description": (
            job_description.model_dump()
        ),
        "available_agents": routing_agents,
    }

    # ---------------------------------------------------------------
    # Ask the LLM to select one
    # ---------------------------------------------------------------

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(
                    prompt,
                    ensure_ascii=False,
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "agent_routing_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "selected_agent_id": {
                            "type": "string"
                        },
                        "selected_agent_code": {
                            "type": "string"
                        },
                        "confidence": {
                            "type": "number"
                        },
                        "reason": {
                            "type": "string"
                        },
                        "alternative_agent_ids": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                        },
                    },
                    "required": [
                        "selected_agent_id",
                        "selected_agent_code",
                        "confidence",
                        "reason",
                        "alternative_agent_ids",
                    ],
                    "additionalProperties": False,
                },
            }
        },
    )

    # ---------------------------------------------------------------
    # Parse LLM response
    # ---------------------------------------------------------------

    try:
        result = json.loads(
            response.output_text
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON for agent routing."
        ) from exc

    # ---------------------------------------------------------------
    # Build authoritative local lookup
    # ---------------------------------------------------------------

    valid_agents = {}

    for raw_agent in raw_agents:

        normalized = normalize_registry_agent(
            raw_agent
        )

        if normalized["status"] != "ACTIVE":
            continue

        valid_agents[
            normalized["agent_id"]
        ] = normalized

    # ---------------------------------------------------------------
    # Validate selected agent
    # ---------------------------------------------------------------

    selected_id = result.get(
        "selected_agent_id"
    )

    if not selected_id:
        raise ValueError(
            "LLM did not return selected_agent_id."
        )

    selected_agent = valid_agents.get(
        selected_id
    )

    if selected_agent is None:
        raise ValueError(
            "LLM selected an agent that does not exist "
            "in the registry."
        )

    # ---------------------------------------------------------------
    # Validate selected agent code
    # ---------------------------------------------------------------

    returned_code = result.get(
        "selected_agent_code"
    )

    if returned_code != selected_agent["agent_code"]:
        raise ValueError(
            "LLM selected agent ID and agent code do not match "
            "the registry. "
            f"ID={selected_id}, "
            f"LLM code={returned_code}, "
            f"registry code={selected_agent['agent_code']}"
        )

    # ---------------------------------------------------------------
    # Validate alternatives
    # ---------------------------------------------------------------

    alternatives = result.get(
        "alternative_agent_ids",
        [],
    )

    for agent_id in alternatives:

        if agent_id not in valid_agents:
            raise ValueError(
                "LLM returned invalid alternative agent: "
                f"{agent_id}"
            )

    # ---------------------------------------------------------------
    # Return routing decision
    # ---------------------------------------------------------------

    return result