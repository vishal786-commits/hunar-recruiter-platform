import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PDL_API_KEY")

if not API_KEY:
    raise RuntimeError("PDL_API_KEY is not set")

url = "https://api.peopledatalabs.com/v5/person/search"

headers = {
    "X-Api-Key": API_KEY,
    "Accept": "application/json",
}

params = {
    "sql": "SELECT * FROM person",
    "size": 1,
    "pretty": True,
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30,
)

print("HTTP status:", response.status_code)
print(response.text)