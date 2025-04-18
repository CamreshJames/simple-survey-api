from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query # type: ignore
from fastapi.responses import FileResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlalchemy.orm import Session # type: ignore
from typing import List, Optional
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path

# Import database and schema models
from database import get_db, Base, engine
import models
import schemas

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the FastAPI app
app = FastAPI(title="Survey API", description="API for survey application")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    """Root endpoint to check if API is running."""
    return {"message": "Survey API is running"}

@app.get("/api/questions", response_model=schemas.QuestionList)
def get_questions(db: Session = Depends(get_db)):
    """
    Fetch list of all survey questions.
    
    Returns:
        schemas.QuestionList: List of all questions with their options
    """
    # Get all questions from database
    db_questions = db.query(models.Question).order_by(models.Question.id).all()
    
    # Convert to schema format
    questions = []
    for q in db_questions:
        question_data = {
            "name": q.name,
            "type": q.type,
            "required": "yes" if q.required else "no",
            "text": q.text,
            "description": q.description or ""
        }
        
        # Add options for choice-type questions
        if q.type == "choice":
            options = db.query(models.QuestionOption).filter(
                models.QuestionOption.question_id == q.id
            ).all()
            
            question_data["options"] = {
                "multiple": "yes" if q.multiple_choice else "no",
                "option": [
                    {"value": opt.value, "text": opt.text}
                    for opt in options
                ]
            }
        
        # Add file properties for file-type questions
        if q.type == "file":
            question_data["file_properties"] = {
                "format": q.file_format,
                "max_file_size": q.max_file_size,
                "max_file_size_unit": q.max_file_size_unit,
                "multiple": "yes" if q.multiple_files else "no"
            }
            
        questions.append(question_data)
    
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
    Submit a response to the survey.
    
    Args:
        full_name: Full name of the respondent
        email_address: Email address of the respondent
        description: Self-description
        gender: Gender selection
        programming_stack: Comma-separated programming technologies
        certificates: List of certificate files
        
    Returns:
        schemas.QuestionResponse: The submitted response data
    """
    # Create new response in database
    new_response = models.Response(
        full_name=full_name,
        email_address=email_address,
        description=description,
        gender=gender,
        programming_stack=programming_stack,
        date_responded=datetime.now()
    )
    db.add(new_response)
    db.flush()  # Get ID without committing
    
    # Save uploaded certificates
    cert_filenames = []
    for cert in certificates:
        # Generate unique filename
        file_extension = os.path.splitext(cert.filename)[1]
        if file_extension.lower() != '.pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(cert.file, buffer)
        
        # Add to database
        new_certificate = models.Certificate(
            response_id=new_response.id,
            filename=cert.filename,
            filepath=str(file_path)
        )
        db.add(new_certificate)
        cert_filenames.append(cert.filename)
    
    db.commit()
    
    # Prepare response
    return {
        "full_name": full_name,
        "email_address": email_address,
        "description": description,
        "gender": gender,
        "programming_stack": programming_stack,
        "certificates": {
            "certificate": cert_filenames
        },
        "date_responded": new_response.date_responded.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/questions/responses", response_model=schemas.QuestionResponseList)
def get_responses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    email_address: Optional[str] = Query(None, description="Filter by email address"),
    db: Session = Depends(get_db)
):
    """
    Fetch all submitted responses with pagination.
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page
        email_address: Optional filter by email address
        
    Returns:
        schemas.QuestionResponseList: Paginated list of responses
    """
    # Build query
    query = db.query(models.Response)
    
    # Apply email filter if provided
    if email_address:
        query = query.filter(models.Response.email_address == email_address)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Calculate pagination parameters
    offset = (page - 1) * page_size
    last_page = (total_count + page_size - 1) // page_size  # Ceiling division
    
    # Get paginated responses
    responses = query.order_by(models.Response.date_responded.desc()).offset(offset).limit(page_size).all()
    
    # Build response data
    result = []
    for resp in responses:
        # Get certificates for this response
        certificates = db.query(models.Certificate).filter(
            models.Certificate.response_id == resp.id
        ).all()
        
        # Format certificates
        cert_data = [
            {"id": cert.id, "text": cert.filename} 
            for cert in certificates
        ]
        
        # Add response to result
        result.append({
            "response_id": resp.id,
            "full_name": resp.full_name,
            "email_address": resp.email_address,
            "description": resp.description,
            "gender": resp.gender,
            "programming_stack": resp.programming_stack,
            "certificates": {
                "certificate": cert_data
            },
            "date_responded": resp.date_responded.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Return paginated response
    return {
        "current_page": page,
        "last_page": last_page,
        "page_size": page_size,
        "total_count": total_count,
        "question_response": result
    }

@app.get("/api/questions/responses/certificates/{id}")
def download_certificate(id: int, db: Session = Depends(get_db)):
    """
    Download a certificate file by its ID.
    
    Args:
        id: Certificate ID
        
    Returns:
        FileResponse: The requested certificate file
    """
    # Get certificate from database
    certificate = db.query(models.Certificate).filter(models.Certificate.id == id).first()
    
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Return file as response
    return FileResponse(
        path=certificate.filepath,
        filename=certificate.filename,
        media_type="application/pdf"
    )