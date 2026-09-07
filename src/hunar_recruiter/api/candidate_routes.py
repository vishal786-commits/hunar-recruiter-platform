from fastapi import APIRouter, HTTPException

from hunar_recruiter.models.candidate_search import (
    CandidateSearchResponse,
)
from hunar_recruiter.services.candidate_search import (
    CandidateSearchService,
)

# from hunar_recruiter.models.job_description import JobDescription

router = APIRouter(
    prefix="/jobs",
    tags=["candidates"],
)

candidate_search_service = CandidateSearchService()


@router.post(
    "/candidates/search",
    response_model=CandidateSearchResponse,
)
def search_candidates(job):
    """
    Search and rank candidates for a structured JD.
    """

    try:
        candidates = candidate_search_service.search(job)

        return CandidateSearchResponse(
            candidates=candidates,
            total=len(candidates),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc