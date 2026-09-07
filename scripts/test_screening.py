from hunar_recruiter.db import SessionLocal, init_db
from hunar_recruiter.models.database import CandidateDB, JobDB


def main():
    init_db()

    db = SessionLocal()

    try:
        job = JobDB(
            raw_jd="Senior Backend Engineer - Python FastAPI",
            parsed_jd={
                "job_title": "Senior Backend Engineer",
                "skills": [
                    "Python",
                    "FastAPI",
                    "PostgreSQL",
                ],
                "location": "Bengaluru",
                "min_experience": 3,
            },
            selected_agent_id="YOUR_AGENT_ID",
            selected_agent_code="FD106",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        candidate = CandidateDB(
            job_id=job.id,
            name="Demo Candidate",
            email="demo@example.com",
            phone="+91XXXXXXXXXX",
            current_title="Backend Engineer",
            location="Bengaluru",
            years_experience=5,
            skills=[
                "Python",
                "FastAPI",
                "PostgreSQL",
            ],
            match_score=92.0,
            source="demo",
            raw_data={},
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        print("Job ID:", job.id)
        print("Candidate ID:", candidate.id)

    finally:
        db.close()


if __name__ == "__main__":
    main()