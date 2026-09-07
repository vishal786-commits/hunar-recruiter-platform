import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv()

HUNAR_API_KEY = os.getenv("HUNAR_API_KEY")
HUNAR_BASE_URL = os.getenv(
    "HUNAR_BASE_URL",
    "https://api.voice.hunar.ai/external/v1",
)

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "agents.json"


def normalize_agent(agent: dict) -> dict:
    """Convert Hunar's agent representation into our routing representation."""

    return {
        "agent_id": agent["id"],
        "agent_code": agent.get("agent_code"),
        "name": agent.get("name"),
        "purpose": agent.get("summary"),
        "status": agent.get("status"),
        "language": agent.get("language"),
        "voice_persona": agent.get("voice_persona"),
        "persona_name": agent.get("persona_name"),
        "custom_variables": agent.get("custom_variables", []),
        "required_variables": agent.get("required_variables", []),
        "result_variables": agent.get("result_variables", []),
        "result_schema": agent.get("result_schema", {}),
    }


def fetch_agents() -> list[dict]:
    """Fetch all active agents from Hunar, following pagination."""

    if not HUNAR_API_KEY:
        raise RuntimeError("HUNAR_API_KEY is not configured.")

    headers = {
        "X-API-Key": HUNAR_API_KEY,
        "Content-Type": "application/json",
    }

    agents = []

    with httpx.Client(
        headers=headers,
        timeout=30.0,
    ) as client:

        url = f"{HUNAR_BASE_URL}/agents/"

        while url:
            print(f"Fetching: {url}")

            response = client.get(url)
            response.raise_for_status()

            data = response.json()

            for agent in data.get("results", []):
                if agent.get("status") == "ACTIVE":
                    agents.append(normalize_agent(agent))

            url = data.get("next")

    return agents


def save_agents(agents: list[dict]) -> None:
    """Save normalized agents to the local registry."""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            agents,
            file,
            indent=2,
            ensure_ascii=False,
        )


def main():
    print("Syncing Hunar agents...")

    agents = fetch_agents()

    save_agents(agents)

    print(f"\nSaved {len(agents)} active agents.")
    print(f"Registry: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()