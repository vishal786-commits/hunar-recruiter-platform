from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hunar_recruiter.db import get_db
from hunar_recruiter.models.database import (
    CandidateDB,
    JobDB,
    ScreeningDB,
)
from hunar_recruiter.services.screening import (
    start_screening,
    sync_screening,
)


router = APIRouter(
    prefix="/jobs",
    tags=["screenings"],
)


class StartScreeningsRequest(BaseModel):
    candidate_ids: list[str]


@router.post("/{job_id}/screenings/start")
def start_job_screenings(
    job_id: str,
    request: StartScreeningsRequest,
    db: Session = Depends(get_db),
):
    """
    Start Hunar screening calls for recruiter-approved candidates.
    """

    # ---------------------------------------------------------
    # 1. Load the job
    # ---------------------------------------------------------

    job = db.get(
        JobDB,
        job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # ---------------------------------------------------------
    # 2. Make sure the job has a selected Hunar agent
    # ---------------------------------------------------------

    if not job.selected_agent_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "This job does not have a selected Hunar agent."
            ),
        )

    # ---------------------------------------------------------
    # 3. Validate candidates were supplied
    # ---------------------------------------------------------

    if not request.candidate_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one candidate must be selected.",
        )

    # ---------------------------------------------------------
    # 4. Load only candidates belonging to this job
    # ---------------------------------------------------------

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
                    "Some candidates do not "
                    "belong to this job."
                ),
                "candidate_ids": list(
                    missing_ids
                ),
            },
        )

    # ---------------------------------------------------------
    # 5. Enforce human approval
    # ---------------------------------------------------------

    not_approved = [
        candidate.id
        for candidate in candidates
        if not candidate.approved
    ]

    if not_approved:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Candidates must be approved "
                    "before screening."
                ),
                "candidate_ids": not_approved,
            },
        )

    # ---------------------------------------------------------
    # 6. Validate all candidates have phone numbers
    # ---------------------------------------------------------

    missing_phone = [
        candidate.id
        for candidate in candidates
        if not candidate.phone
    ]

    if missing_phone:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Some approved candidates "
                    "do not have a phone number."
                ),
                "candidate_ids": missing_phone,
            },
        )

    # ---------------------------------------------------------
    # 7. Start calls
    # ---------------------------------------------------------

    job_description = (
        job.parsed_jd
        if isinstance(job.parsed_jd, dict)
        else {}
    )

    results = []

    for candidate in candidates:

        try:
            screening = start_screening(
                db,
                candidate=candidate,
                agent_id=job.selected_agent_id,
                agent_code=job.selected_agent_code,
                job_description=job_description,
            )

            results.append(
                {
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.name,
                    "screening_id": screening.id,
                    "hunar_call_id": screening.hunar_call_id,
                    "status": screening.status,
                }
            )

        except Exception as exc:

            results.append(
                {
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.name,
                    "screening_id": None,
                    "hunar_call_id": None,
                    "status": "FAILED",
                    "error": str(exc),
                }
            )

    return {
        "job_id": job_id,
        "agent_id": job.selected_agent_id,
        "agent_code": job.selected_agent_code,
        "results": results,
    }


@router.get("/screenings/{screening_id}")
def get_screening(
    screening_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the current application-side screening state.
    """

    screening = db.get(
        ScreeningDB,
        screening_id,
    )

    if not screening:
        raise HTTPException(
            status_code=404,
            detail="Screening not found.",
        )

    return {
        "screening_id": screening.id,
        "candidate_id": screening.candidate_id,
        "agent_id": screening.agent_id,
        "agent_code": screening.agent_code,
        "hunar_call_id": screening.hunar_call_id,
        "status": screening.status,
        "lifecycle_status": screening.lifecycle_status,
        "recording_url": screening.recording_url,
        "result": screening.result,
        "error_message": screening.error_message,
        "created_at": screening.created_at,
        "updated_at": screening.updated_at,
        "started_at": screening.started_at,
        "ended_at": screening.ended_at,
    }


@router.post("/screenings/{screening_id}/sync")
def sync_screening_status(
    screening_id: str,
    db: Session = Depends(get_db),
):
    """
    Fetch the current call state from Hunar and update our DB.
    """

    screening = db.get(
        ScreeningDB,
        screening_id,
    )

    if not screening:
        raise HTTPException(
            status_code=404,
            detail="Screening not found.",
        )

    try:
        screening = sync_screening(
            db,
            screening,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to sync Hunar call: {exc}",
        ) from exc

    return {
        "screening_id": screening.id,
        "hunar_call_id": screening.hunar_call_id,
        "status": screening.status,
        "lifecycle_status": screening.lifecycle_status,
        "recording_url": screening.recording_url,
        "result": screening.result,
        "updated_at": screening.updated_at,
    }