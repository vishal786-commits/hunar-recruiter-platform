from pydantic import BaseModel

from hunar_recruiter.models.candidate import Candidate


class CandidateSearchResponse(BaseModel):
    candidates: list[Candidate]
    total: int