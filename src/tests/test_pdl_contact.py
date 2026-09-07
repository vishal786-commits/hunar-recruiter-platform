import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PDL_API_KEY")
if not API_KEY:
    raise RuntimeError("PDL_API_KEY is not set")

PERSON_ID = "je-l1-nTyLkkRZPSeEyjwQ_0000"

url = "https://api.peopledatalabs.com/v5/person/enrich"

headers = {
    "X-Api-Key": API_KEY,
    "Accept": "application/json",
}

params = {
    "pdl_id": PERSON_ID,
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30,
)

print("HTTP status:", response.status_code)
print(response.text)