import os, json

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("HUNAR_API_KEY")

if not api_key:
    raise RuntimeError("HUNAR_API_KEY is not set")


BASE_URL = "https://api.voice.hunar.ai/external/v1"

AGENT_ID = "af122bd9-1bc1-4277-b166-f0ae19d286b3"
# voice_name	:	Neha
# summary	:	This AI agent conducts brief courtesy calls to verify candidate identity and assess availability for new job opportunities, primarily serving recruiting firms in the human resources industry.

headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
}


call_data = {
    "agent_id": AGENT_ID,
    "callee_name": "Mahesh",
    "mobile_number": "+918951409278",
    "custom_data": {
    "company": "Revolut",
    "role_title": "Quality Control Analyst"
    },
    "request_id": "hunar-recruiter-test-004",
}


response = httpx.post(
    f"{BASE_URL}/calls/",
    headers=headers,
    json=call_data,
    timeout=30,
)

print(f"Status: {response.status_code}")
# print(response.text)
data = response.json()
print("====================Call Response JSON:================")
print(json.dumps(data, indent=4))