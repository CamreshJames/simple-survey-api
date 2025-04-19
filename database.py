from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
import os
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres.dwjtyedtetjfduyvoelh:I-Love-Money+100%@aws-0-us-east-2.pooler.supabase.com:5432/postgres"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Dependency function to get a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Notes:
        The session is closed after the request is processed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()