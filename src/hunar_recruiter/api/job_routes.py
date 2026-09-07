from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hunar_recruiter.db import get_db
from hunar_recruiter.models.database import CandidateDB, JobDB


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


class ApproveCandidatesRequest(BaseModel):
    candidate_ids: list[str]


@router.post("/{job_id}/candidates/approve")
def approve_candidates(
    job_id: str,
    request: ApproveCandidatesRequest,
    db: Session = Depends(get_db),
):
    job = db.get(
        JobDB,
        job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    candidates = (
        db.query(CandidateDB)
        .filter(
            CandidateDB.job_id == job_id,
            CandidateDB.source_candidate_id.in_(
                request.candidate_ids
            ),
        )
        .all()
    )

    found_ids = {
        candidate.source_candidate_id
        for candidate in candidates
    }

    missing_ids = (
        set(request.candidate_ids)
        - found_ids
    )

    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Some candidates do not belong "
                    "to this job."
                ),
                "candidate_ids": list(
                    missing_ids
                ),
            },
        )

    for candidate in candidates:
        candidate.approved = True

    db.commit()

    return {
        "job_id": job_id,
        "approved_candidates": [
            candidate.source_candidate_id
            for candidate in candidates
        ],
        "count": len(candidates),
    }