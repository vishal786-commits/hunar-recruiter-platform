from __future__ import annotations

import os

from dotenv import load_dotenv

from hunar_recruiter.integrations.pdl import PDLClient
from hunar_recruiter.models.candidate import Candidate
from hunar_recruiter.services.candidate_matcher import (
    calculate_match_score,
)
from hunar_recruiter.services.candidate_normalizer import (
    normalize_pdl_candidate,
)
from hunar_recruiter.services.demo_candidates import (
    load_demo_candidates,
)


load_dotenv()


class CandidateSearchService:
    def __init__(self) -> None:
        self.candidate_source = os.getenv(
            "CANDIDATE_SOURCE",
            "demo",
        ).lower()

        self.pdl = PDLClient()

    def search(
        self,
        job,
        pdl_count: int = 7,
    ) -> list[Candidate]:
        """
        Retrieve candidates, score them against the JD,
        and return the top candidates.

        Candidate source is controlled by:

            CANDIDATE_SOURCE=demo
            CANDIDATE_SOURCE=pdl
            CANDIDATE_SOURCE=hybrid

        demo:
            Use only local demo candidates.

        pdl:
            Use only PDL candidates.

        hybrid:
            Use PDL + demo candidates.
        """

        if self.candidate_source == "demo":
            candidates = self._load_demo_candidates()

        elif self.candidate_source == "pdl":
            candidates = self._load_pdl_candidates(
                job,
                pdl_count,
            )

        elif self.candidate_source == "hybrid":
            candidates = self._load_hybrid_candidates(
                job,
                pdl_count,
            )

        else:
            raise ValueError(
                "Unsupported CANDIDATE_SOURCE: "
                f"{self.candidate_source}. "
                "Expected one of: demo, pdl, hybrid."
            )

        # -----------------------------------------------------
        # Score every candidate against the JD
        # -----------------------------------------------------

        for candidate in candidates:
            candidate.match_score = (
                calculate_match_score(
                    candidate,
                    job,
                )
            )

        # -----------------------------------------------------
        # Highest score first
        # -----------------------------------------------------

        candidates.sort(
            key=lambda candidate: (
                candidate.match_score
                if candidate.match_score is not None
                else 0.0
            ),
            reverse=True,
        )

        # -----------------------------------------------------
        # Keep the top 10
        # -----------------------------------------------------

        return candidates[:10]

    def _load_demo_candidates(self) -> list[Candidate]:
        """
        Load only our local demo participants.
        """

        return load_demo_candidates()

    def _load_pdl_candidates(
        self,
        job,
        pdl_count: int,
    ) -> list[Candidate]:
        """
        Load candidates from PDL.
        """

        location_country = None

        if job.location:
            location_country = job.location.country

        if location_country:
            country = (
                location_country
                .strip()
                .lower()
            )

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

        pdl_records = self.pdl.search(
            sql=sql,
            size=pdl_count,
        )

        return [
            normalize_pdl_candidate(record)
            for record in pdl_records
        ]

    def _load_hybrid_candidates(
        self,
        job,
        pdl_count: int,
    ) -> list[Candidate]:
        """
        Load PDL candidates and add our local demo candidates.
        """

        candidates = self._load_pdl_candidates(
            job,
            pdl_count,
        )

        candidates.extend(
            self._load_demo_candidates()
        )

        return candidates