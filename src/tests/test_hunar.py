import os, json, httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUNAR_API_KEY")

if not api_key:
    raise RuntimeError("HUNAR_API_KEY is not set")


url = "https://api.voice.hunar.ai/external/v1/agents/"

headers = {
    "X-API-Key": api_key,
}

response = httpx.get(url, headers=headers, timeout=30)

# print(f"Status: {response.status_code}")
# # print(response.text)

# print(f"=== Request Status: {response.status_code} ===")

try:
    # Attempt to parse and pretty-print JSON payload
    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=4))
except json.JSONDecodeError:
    # Fallback to plain text if the response isn't JSON (e.g., HTML error pages)
    print("Response Text (Not JSON):")
    print(response.text)

# # Check if request was successful
# if response.status_code == 200:
#     data = response.json()
#     for agent in data['results']:
#         print(f"Agent: {agent['name']} (ID: {agent['id']})")
# else:
#     print(f"Error: {response.status_code} - {response.text}")