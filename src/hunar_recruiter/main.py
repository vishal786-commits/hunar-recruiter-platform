from fastapi import FastAPI, File, HTTPException, UploadFile

from pathlib import Path
from tempfile import NamedTemporaryFile

from .document_parser import extract_text
from .jd_parser import parse_jd
from .schemas import JobDescription
from .pipeline import process_job_description

app = FastAPI(
    title="Hunar Recruiter Platform",
    version="0.1.1",
)


@app.get("/health")
def health_check():
    return {"status": "double-ok-macha👍"}

# end point that return parsed JD json
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

# end point that return a list of selected agents for the give JD
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


@app.post("/jobs/analyze")
async def analyze_job(file: UploadFile = File(...)):
    """
    Upload a JD and run the complete JD -> agent routing pipeline.
    """

    extension = Path(file.filename or "").suffix.lower()

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
        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        result = process_job_description(temp_path)

        return {
            "filename": file.filename,
            **result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"ERROR processing job: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)