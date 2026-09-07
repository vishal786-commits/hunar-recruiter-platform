from hunar_recruiter.agent_routing.router import route_agent


job_description = {
    "title": "Senior Backend Engineer",
    "location": "Bengaluru",
    "min_experience": 5,
    "skills": [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "AWS",
    ],
    "employment_type": "Full-time",
}


result = route_agent(job_description)

print("\nAgent Routing Result")
print("====================")

print(f"Agent ID:     {result['selected_agent_id']}")
print(f"Agent Code:   {result['selected_agent_code']}")
print(f"Confidence:   {result['confidence']}")
print(f"Reason:       {result['reason']}")

print("\nAlternatives:")
for agent_id in result["alternative_agent_ids"]:
    print(f"- {agent_id}")