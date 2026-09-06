from fastapi import FastAPI, File, HTTPException, UploadFile

from .document_parser import extract_text
from .jd_parser import parse_jd
from .schemas import JobDescription


app = FastAPI(
    title="Hunar Recruiter Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "double-ok-macha👍"}


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