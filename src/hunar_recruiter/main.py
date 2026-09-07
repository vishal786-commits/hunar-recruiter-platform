from fastapi import FastAPI, File, HTTPException, UploadFile

from pathlib import Path
from tempfile import NamedTemporaryFile

from .document_parser import extract_text
from .jd_parser import parse_jd
from .schemas import JobDescription
from .pipeline import process_job_description
from .services.candidate_search import CandidateSearchService

from contextlib import asynccontextmanager
from hunar_recruiter.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Hunar Recruiter Platform",
    version="0.1.1",
    lifespan=lifespan,
)

candidate_search_service = CandidateSearchService()

from hunar_recruiter.api.job_routes import router as job_router

app.include_router(job_router)

from hunar_recruiter.api.screening_routes import (
    router as screening_router,
)

app.include_router(screening_router)

@app.get("/health")
def health_check():
    return {"status": "double-ok-macha👍"}


# Endpoint that returns parsed JD JSON
@app.post("/jobs/parse", response_model=JobDescription)
async def parse_job_description(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    try:
        content = await file.read()

        text = extract_text(
            file.filename,
            content,
        )

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the JD.",
            )

        return parse_jd(text)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}

from fastapi import Depends
from sqlalchemy.orm import Session

from hunar_recruiter.db import get_db
from hunar_recruiter.services.job_persistence import persist_analysis

# Endpoint that runs the complete JD analysis pipeline
@app.post("/jobs/analyze")
async def analyze_job(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a JD and run the complete:
    JD -> agent routing -> candidate search pipeline.
    """

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    temp_path = None
    jd_text = extract_text(
        file.filename,
        contents,
    )

    if not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the JD.",
        )



    try:
        # Save uploaded file temporarily
        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # Existing pipeline:
        # JD -> structured JD -> agent routing
        result = process_job_description(temp_path)

        # Extract structured JD
        job_description = result["job_description"]

        # Make sure it is a JobDescription model
        if not isinstance(job_description, JobDescription):
            job_description = JobDescription.model_validate(
                job_description
            )

        # New:
        # structured JD -> PDL + demo candidates -> ranking
        candidates = candidate_search_service.search(
            job_description
        )
        job = persist_analysis(
            db,
            raw_jd=jd_text,
            job_description=job_description.model_dump(),
            agent_routing=result["agent_routing"],
            candidates=candidates,
        )
        return {
            "filename": file.filename,
            **result,
            "candidates": candidates,
            "job_id": job.id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"ERROR processing job: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

    finally:
        if temp_path:
            Path(temp_path).unlink(
                missing_ok=True
            )