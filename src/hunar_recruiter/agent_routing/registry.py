import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTS_PATH = PROJECT_ROOT / "data" / "agents.json"


def load_agents() -> list[dict]:
    """Load the locally cached Hunar agent registry."""

    if not AGENTS_PATH.exists():
        raise FileNotFoundError(
            f"Agent registry not found at {AGENTS_PATH}. "
            "Run scripts/sync_agents.py first."
        )

    with AGENTS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)