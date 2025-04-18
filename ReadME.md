# Survey Application Backend

This is the backend API for the Survey Application, built with FastAPI.

## Features

- RESTful API for survey questions and responses
- File upload capabilities for certificates
- Pagination and filtering for survey responses
- SQLAlchemy ORM for database interactions

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Seed the database with initial questions:
   ```
   python seed_db.py
   ```
4. Start the server:
   ```
   uvicorn app:app --reload
   ```

The API will be available at http://localhost:8000

## API Documentation

After starting the server, you can access the automatic API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

### GET /api/questions
Fetches the list of survey questions.

### PUT /api/questions/responses
Submits a response to the survey.

### GET /api/questions/responses
Fetches submitted responses with pagination and filtering options.

### GET /api/questions/responses/certificates/{id}
Downloads a certificate file by its ID.

## Database

The application uses SQLite by default, but you can configure it to use any SQL database supported by SQLAlchemy (MySQL, PostgreSQL, etc.) by updating the `DATABASE_URL` in `database.py`.

## Project Structure

- `app.py`: Main FastAPI application
- `database.py`: Database connection setup
- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic schema models for request/response validation
- `seed_db.py`: Script to seed the database with initial questions
- `requirements.txt`: Python dependencies
- `uploads/`: Directory for storing uploaded certificate files