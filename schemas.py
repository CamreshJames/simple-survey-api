from pydantic import BaseModel # type: ignore
from typing import List, Optional, Dict, Any, Union

# Question schemas
class QuestionOptionItem(BaseModel):
    """Schema for a single question option."""
    value: str
    text: str

class QuestionOptionList(BaseModel):
    """Schema for question options list."""
    multiple: str  # "yes" or "no"
    option: List[QuestionOptionItem]

class FileProperties(BaseModel):
    """Schema for file-type question properties."""
    format: str
    max_file_size: int
    max_file_size_unit: str
    multiple: str  # "yes" or "no"

class Question(BaseModel):
    """Schema for a survey question."""
    name: str
    type: str
    required: str  # "yes" or "no"
    text: str
    description: str = ""
    options: Optional[QuestionOptionList] = None
    file_properties: Optional[FileProperties] = None

class QuestionList(BaseModel):
    """Schema for list of questions."""
    question: List[Question]

# Response schemas
class CertificateItem(BaseModel):
    """Schema for a single certificate entry."""
    text: str

class CertificateItemWithId(BaseModel):
    """Schema for a certificate with ID."""
    id: int
    text: str

class CertificateList(BaseModel):
    """Schema for list of certificates."""
    certificate: List[str]

class CertificateListWithId(BaseModel):
    """Schema for list of certificates with IDs."""
    certificate: List[Dict[str, Any]]

class QuestionResponse(BaseModel):
    """Schema for a survey response."""
    full_name: str
    email_address: str
    description: str
    gender: str
    programming_stack: str
    certificates: Dict[str, List[str]]
    date_responded: str

class QuestionResponseWithId(BaseModel):
    """Schema for a survey response with ID."""
    response_id: int
    full_name: str
    email_address: str
    description: str
    gender: str
    programming_stack: str
    certificates: Dict[str, List[Dict[str, Any]]]
    date_responded: str

class QuestionResponseList(BaseModel):
    """Schema for paginated list of responses."""
    current_page: int
    last_page: int
    page_size: int
    total_count: int
    question_response: List[QuestionResponseWithId]