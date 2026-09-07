import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


class HunarAPIError(Exception):
    """Raised when Hunar API returns an error response."""


class HunarClient:
    def __init__(self):
        self.base_url = os.getenv(
            "HUNAR_BASE_URL",
            "https://api.voice.hunar.ai/external/v1",
        ).rstrip("/")

        self.api_key = os.getenv("HUNAR_API_KEY")

        if not self.api_key:
            raise RuntimeError("HUNAR_API_KEY is not configured.")

        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def create_call(
        self,
        *,
        agent_id: str,
        callee_name: str,
        mobile_number: str,
        custom_data: dict[str, Any] | None = None,
        request_id: str | None = None,
        callback_config: dict[str, str] | None = None,
    ) -> dict[str, Any]:

        payload: dict[str, Any] = {
            "agent_id": agent_id,
            "callee_name": callee_name,
            "mobile_number": mobile_number,
            "custom_data": custom_data or {},
        }

        if request_id:
            payload["request_id"] = request_id

        if callback_config:
            payload["callback_config"] = callback_config

        url = f"{self.base_url}/calls/"

        try:
            response = httpx.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
        except httpx.HTTPError as exc:
            raise HunarAPIError(
                f"Unable to reach Hunar API: {exc}"
            ) from exc

        if response.status_code != 200:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"message": response.text}

            raise HunarAPIError(
                f"Hunar create call failed "
                f"(HTTP {response.status_code}): {error_data}"
            )

        return response.json()

    def get_call(
        self,
        call_id: str,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/calls/{call_id}/"

        try:
            response = httpx.get(
                url,
                headers=self.headers,
                timeout=30.0,
            )
        except httpx.HTTPError as exc:
            raise HunarAPIError(
                f"Unable to reach Hunar API: {exc}"
            ) from exc

        if response.status_code != 200:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"message": response.text}

            raise HunarAPIError(
                f"Hunar get call failed "
                f"(HTTP {response.status_code}): {error_data}"
            )

        return response.json()