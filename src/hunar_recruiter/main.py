from fastapi import FastAPI, File, HTTPException, UploadFile

from pathlib import Path
from tempfile import NamedTemporaryFile

from .document_parser import extract_text
from .jd_parser import parse_jd
from .schemas import JobDescription
from .pipeline import process_job_description
from .services.candidate_search import CandidateSearchService


app = FastAPI(
    title="Hunar Recruiter Platform",
    version="0.1.1",
)

candidate_search_service = CandidateSearchService()


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


# Endpoint that runs the complete JD analysis pipeline
@app.post("/jobs/analyze")
async def analyze_job(
    file: UploadFile = File(...),
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

        return {
            "filename": file.filename,
            **result,
            "candidates": candidates,
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