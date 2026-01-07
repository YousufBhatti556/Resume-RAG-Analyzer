from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database.deps import get_db
from backend.database.models import AnalysisResult, JobDescription, Resume, User
from backend.rag.service import analyze_resume_with_job_description


router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/analyze")
async def analyze_resume(
    job_description: str = Form(..., description="Job description text"),
    file: UploadFile = File(..., description="Resume PDF file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upload a resume PDF and a job description, run the RAG pipeline,
    store the result in the database, and return the structured analysis.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    # 1. Persist file to disk
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = file.filename or "resume.pdf"
    file_path = uploads_dir / safe_filename

    with file_path.open("wb") as f:
        content = await file.read()
        f.write(content)

    # 2. Create DB records for resume and job description
    resume = Resume(
        filename=safe_filename,
        file_path=str(file_path),
        owner=current_user,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    jd = JobDescription(title=None, description_text=job_description)
    db.add(jd)
    db.commit()
    db.refresh(jd)

    # 3. Run RAG pipeline
    try:
        rag_result = analyze_resume_with_job_description(
            resume_path=file_path, job_description=job_description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during analysis: {e}",
        )

    raw_result = rag_result.get("raw_result", "")

    # 4. Persist analysis result
    analysis = AnalysisResult(
        resume_id=resume.id,
        match_score=None,  # Could be parsed from raw_result if needed
        analysis_report=raw_result,
        missing_skills=None,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "resume_id": resume.id,
        "analysis_id": analysis.id,
        "raw_result": raw_result,
    }

