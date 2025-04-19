"""
Survey API

FastAPI application for handling survey questions and responses, including file uploads.
Files are stored in Vercel's writable `/tmp/uploads` directory.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import os
import shutil
import uuid

# Import database session, models, and schemas
from database import get_db, Base, engine
import models
import schemas

# Define uploads directory in Vercel's temp space
UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title="Survey API",
    description="API for survey application"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Create database tables on startup
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    """
    Root endpoint to verify API is running.
    Returns a simple JSON message.
    """
    return {"message": "Survey API is running"}

@app.get("/api/questions", response_model=schemas.QuestionList)
def get_questions(db: Session = Depends(get_db)):
    """
    Fetch all survey questions from the database.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Dictionary containing list of questions with options or file properties.
    """
    db_questions = db.query(models.Question).order_by(models.Question.id).all()
    questions = []

    for q in db_questions:
        item = {
            "name": q.name,
            "type": q.type,
            "required": "yes" if q.required else "no",
            "text": q.text,
            "description": q.description or ""
        }

        if q.type == "choice":
            opts = db.query(models.QuestionOption).filter_by(question_id=q.id).all()
            item["options"] = {
                "multiple": "yes" if q.multiple_choice else "no",
                "option": [{"value": o.value, "text": o.text} for o in opts]
            }

        if q.type == "file":
            item["file_properties"] = {
                "format": q.file_format,
                "max_file_size": q.max_file_size,
                "max_file_size_unit": q.max_file_size_unit,
                "multiple": "yes" if q.multiple_files else "no"
            }

        questions.append(item)

    return {"question": questions}

@app.put("/api/questions/responses", response_model=schemas.QuestionResponse)
async def submit_response(
    full_name: str = Form(...),
    email_address: str = Form(...),
    description: str = Form(...),
    gender: str = Form(...),
    programming_stack: str = Form(...),
    certificates: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit a survey response and save uploaded PDF certificates.

    Args:
        full_name (str): Respondent's full name.
        email_address (str): Respondent's email address.
        description (str): Self-description text.
        gender (str): Respondent's gender.
        programming_stack (str): Comma-separated programming technologies.
        certificates (List[UploadFile]): List of PDF files uploaded.
        db (Session): SQLAlchemy database session.

    Raises:
        HTTPException: If uploaded file is not a PDF.

    Returns:
        dict: Submitted response data including saved certificate filenames.
    """
    resp = models.Response(
        full_name=full_name,
        email_address=email_address,
        description=description,
        gender=gender,
        programming_stack=programming_stack,
        date_responded=datetime.utcnow()
    )
    db.add(resp)
    db.flush()

    saved_filenames = []
    for cert in certificates:
        ext = os.path.splitext(cert.filename)[1].lower()
        if ext != ".pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        unique_name = f"{uuid.uuid4()}{ext}"
        dest = UPLOAD_DIR / unique_name
        with open(dest, "wb") as out:
            shutil.copyfileobj(cert.file, out)

        cert_record = models.Certificate(
            response_id=resp.id,
            filename=cert.filename,
            filepath=str(dest)
        )
        db.add(cert_record)
        saved_filenames.append(cert.filename)

    db.commit()

    return {
        "full_name": full_name,
        "email_address": email_address,
        "description": description,
        "gender": gender,
        "programming_stack": programming_stack,
        "certificates": {"certificate": saved_filenames},
        "date_responded": resp.date_responded.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/questions/responses", response_model=schemas.QuestionResponseList)
def get_responses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    email_address: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of submitted survey responses.

    Args:
        page (int): Page number (starts at 1).
        page_size (int): Number of items per page.
        email_address (Optional[str]): Filter responses by email.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Pagination info and list of responses.
    """
    query = db.query(models.Response)
    if email_address:
        query = query.filter(models.Response.email_address == email_address)

    total = query.count()
    offset = (page - 1) * page_size
    last_page = (total + page_size - 1) // page_size

    records = (
        query
        .order_by(models.Response.date_responded.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    result = []
    for r in records:
        certs = db.query(models.Certificate).filter_by(response_id=r.id).all()
        cert_data = [{"id": c.id, "text": c.filename} for c in certs]
        result.append({
            "response_id": r.id,
            "full_name": r.full_name,
            "email_address": r.email_address,
            "description": r.description,
            "gender": r.gender,
            "programming_stack": r.programming_stack,
            "certificates": {"certificate": cert_data},
            "date_responded": r.date_responded.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "current_page": page,
        "last_page": last_page,
        "page_size": page_size,
        "total_count": total,
        "question_response": result
    }

@app.get("/api/questions/responses/certificates/{id}")
def download_certificate(id: int, db: Session = Depends(get_db)):
    """
    Download a previously uploaded certificate by ID.

    Args:
        id (int): Certificate database ID.
        db (Session): SQLAlchemy database session.

    Raises:
        HTTPException: If certificate is not found.

    Returns:
        FileResponse: PDF file response.
    """
    cert = db.query(models.Certificate).filter_by(id=id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return FileResponse(path=cert.filepath, filename=cert.filename, media_type="application/pdf")