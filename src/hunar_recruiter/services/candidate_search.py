from __future__ import annotations

from hunar_recruiter.integrations.pdl import PDLClient
from hunar_recruiter.models.candidate import Candidate
from hunar_recruiter.services.candidate_matcher import calculate_match_score
from hunar_recruiter.services.candidate_normalizer import (
    normalize_pdl_candidate,
)
from hunar_recruiter.services.demo_candidates import load_demo_candidates


class CandidateSearchService:
    def __init__(self) -> None:
        self.pdl = PDLClient()

    def search(self, job, pdl_count: int = 7) -> list[Candidate]:
        """
        Retrieve candidates from PDL, add demo participants,
        score them against the JD, and return the top 10.
        """

        # Your actual JobDescription structure:
        # job.location.country
        location_country = None

        if job.location:
            location_country = job.location.country

        # Keep the first version deliberately simple.
        if location_country:
            country = location_country.strip().lower()

            sql = f"""
                SELECT * FROM person
                WHERE location_country = '{country}'
                AND job_title IS NOT NULL
            """
        else:
            sql = """
                SELECT * FROM person
                WHERE job_title IS NOT NULL
            """

        # 1. Real PDL candidates
        pdl_records = self.pdl.search(
            sql=sql,
            size=pdl_count,
        )

        candidates = [
            normalize_pdl_candidate(record)
            for record in pdl_records
        ]

        # 2. Our three real demo participants
        candidates.extend(load_demo_candidates())

        # 3. Match every candidate to the JD
        for candidate in candidates:
            candidate.match_score = calculate_match_score(
                candidate,
                job,
            )

        # 4. Highest score first
        candidates.sort(
            key=lambda candidate: candidate.match_score,
            reverse=True,
        )

        # 7 PDL + 3 demo = 10
        return candidates[:10]