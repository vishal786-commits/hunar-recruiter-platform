from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class PDLClient:
    BASE_URL = "https://api.peopledatalabs.com/v5/person/search"

    def __init__(self) -> None:
        self.api_key = os.getenv("PDL_API_KEY")

        if not self.api_key:
            raise RuntimeError("PDL_API_KEY is not set")

    def search(
        self,
        sql: str,
        size: int = 7,
    ) -> list[dict[str, Any]]:
        if not 1 <= size <= 100:
            raise ValueError("PDL size must be between 1 and 100")

        response = requests.get(
            self.BASE_URL,
            headers={
                "X-Api-Key": self.api_key,
                "Accept": "application/json",
            },
            params={
                "sql": sql,
                "size": size,
                "pretty": True,
            },
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") != 200:
            raise RuntimeError(f"PDL search failed: {payload}")

        return payload.get("data", [])