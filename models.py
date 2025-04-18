from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from database import Base

class Question(Base):
    """
    Database model for survey questions.
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    type = Column(String(20), nullable=False)  # short_text, long_text, email, choice, file
    required = Column(Boolean, default=True)
    text = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # For choice-type questions
    multiple_choice = Column(Boolean, default=False)
    
    # For file-type questions
    file_format = Column(String(20), nullable=True)
    max_file_size = Column(Integer, nullable=True)
    max_file_size_unit = Column(String(5), nullable=True)
    multiple_files = Column(Boolean, default=False)
    
    # Relationships
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")

class QuestionOption(Base):
    """
    Database model for options of choice-type questions.
    """
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    value = Column(String(100), nullable=False)
    text = Column(String(200), nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")

class Response(Base):
    """
    Database model for survey responses.
    """
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    email_address = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    gender = Column(String(20), nullable=False)
    programming_stack = Column(String(500), nullable=False)
    date_responded = Column(DateTime, nullable=False)
    
    # Relationships
    certificates = relationship("Certificate", back_populates="response", cascade="all, delete-orphan")

class Certificate(Base):
    """
    Database model for uploaded certificates.
    """
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id", ondelete="CASCADE"))
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    
    # Relationships
    response = relationship("Response", back_populates="certificates")