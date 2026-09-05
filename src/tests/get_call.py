import os, json

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("HUNAR_API_KEY")

if not api_key:
    raise RuntimeError("HUNAR_API_KEY is not set")


BASE_URL = "https://api.voice.hunar.ai/external/v1"

CALL_ID = "c098f84d-8186-493d-9d06-f73b42f4b095"

headers = {
    "X-API-Key": api_key,
}


response = httpx.get(
    f"{BASE_URL}/calls/{CALL_ID}/",
    headers=headers,
    timeout=30,
)

print(f"Status: {response.status_code}")
print("====================Call Status JSON:================")
# print(response.text)
data = response.json()
print("====================Call Response JSON:================")
print(json.dumps(data, indent=4))