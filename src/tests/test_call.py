import os, json

import httpx
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("HUNAR_API_KEY")

if not api_key:
    raise RuntimeError("HUNAR_API_KEY is not set")


BASE_URL = "https://api.voice.hunar.ai/external/v1"

AGENT_ID = "140d7bbd-a8eb-4808-8b27-2cbf28470196"
# voice_name	:	Neha
# summary	:	This AI agent conducts brief courtesy calls to verify candidate identity and assess availability for new job opportunities, primarily serving recruiting firms in the human resources industry.

headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
}


call_data = {
    "agent_id": AGENT_ID,
    "callee_name": "Akshaya",
    "mobile_number": "+917022633193",
    "custom_data": {
    "company": "Microsoft",
    "role_title": "Chief Design Officer",
    "key_requirements": "figma, cursor, sqlite", 
    "job_title": "Senior Designer"
    },
    "request_id": "hunar-recruiter-test-006",
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