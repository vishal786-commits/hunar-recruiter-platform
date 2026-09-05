import os, json

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("HUNAR_API_KEY")

if not api_key:
    raise RuntimeError("HUNAR_API_KEY is not set")


BASE_URL = "https://api.voice.hunar.ai/external/v1"

AGENT_ID = "e30430c2-90a9-49bd-bf55-ba9f9ff744f3"

headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
}


response = httpx.get(
    f"{BASE_URL}/agents/{AGENT_ID}/",
    headers=headers,
    timeout=30,
)

print(f"Status: {response.status_code}")
data = response.json()
print("====================Response JSON:================")
print(json.dumps(data, indent=4))