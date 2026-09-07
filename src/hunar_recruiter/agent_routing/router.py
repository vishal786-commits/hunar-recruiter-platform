import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from hunar_recruiter.agent_routing.registry import load_agents
from hunar_recruiter.schemas import JobDescription

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not configured.")

client = OpenAI(api_key=api_key)


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

Return ONLY valid JSON matching the requested schema.
"""


def build_routing_agents(agents: list[dict]) -> list[dict]:
    return [
        {
            "agent_id": agent["agent_id"],
            "agent_code": agent["agent_code"],
            "name": agent["name"],
            "purpose": agent["purpose"],
            "language": agent["language"],
            "custom_variables": agent["custom_variables"],
        }
        for agent in agents
        if agent["status"] == "ACTIVE"
    ]


def route_agent(job_description: JobDescription) -> dict:

    agents = load_agents()

    routing_agents = build_routing_agents(agents)

    prompt = {
        "job_description": job_description.model_dump(),
        "available_agents": routing_agents,
    }

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(prompt),
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

    result = json.loads(response.output_text)

    valid_agents = {
        agent["agent_id"]: agent
        for agent in agents
    }

    selected_id = result["selected_agent_id"]

    if selected_id not in valid_agents:
        raise ValueError(
            "LLM selected an agent that does not exist in the registry."
        )

    for agent_id in result["alternative_agent_ids"]:
        if agent_id not in valid_agents:
            raise ValueError(
                f"LLM returned invalid alternative agent: {agent_id}"
            )

    return result