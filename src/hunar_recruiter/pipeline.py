from pathlib import Path

from hunar_recruiter.document_parser import extract_text
from hunar_recruiter.jd_parser import parse_jd
from hunar_recruiter.agent_routing.router import route_agent


def process_job_description(file_path: str | Path) -> dict:
    file_path = Path(file_path)

    content = file_path.read_bytes()

    text = extract_text(
        filename=file_path.name,
        content=content,
    )

    if not text.strip():
        raise ValueError("The uploaded document contains no readable text.")

    job_description = parse_jd(text)

    routing_result = route_agent(job_description)

    return {
        "job_description": job_description.model_dump(),
        "agent_routing": routing_result,
    }