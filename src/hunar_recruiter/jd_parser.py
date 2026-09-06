from openai import OpenAI

from .schemas import JobDescription
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

client = OpenAI()


SYSTEM_PROMPT = """
You are a job description information extraction system.

Your task is to extract structured information from a job description.

Follow these rules carefully:

1. Only extract information supported by the job description.
2. Do not invent missing information.
3. Use null when a scalar value is not present.
4. Use an empty list when no items are available.
5. Distinguish required skills from preferred/nice-to-have skills.
6. Normalize obvious variations of the same skill.
   For example:
   - "Postgres" -> "PostgreSQL"
   - "Python programming" -> "Python"
7. Extract the minimum and maximum years of experience when stated.
8. If only a minimum is given, leave max_years as null.
9. Identify the location and whether remote work is explicitly allowed.
10. Extract concise responsibilities and requirements rather than copying
    large sections of the job description.

For screening_requirements:

Determine which candidate information should be assessed during a
recruiter screening call based on the JD.

Technical skills should contain the most important technical skills
that should actually be evaluated during screening.

Availability, notice period, compensation expectation, and interest
should generally be true for recruiting workflows unless the JD clearly
makes them irrelevant.

location_flexibility should only be true when relocation, remote work,
hybrid flexibility, or location constraints are relevant to the role.
"""


def parse_jd(text: str) -> JobDescription:
    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        text_format=JobDescription,
    )

    parsed = response.output_parsed

    if parsed is None:
        raise ValueError("LLM did not return a valid job description.")

    return parsed