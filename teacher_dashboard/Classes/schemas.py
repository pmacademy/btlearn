from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from pydantic.networks import EmailStr


class Student(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    email: EmailStr
    parents_email: Optional[EmailStr] = None
    class_id: int


class ClassStudentsRequest(BaseModel):
    students: List[Student]

class ClassResponse(BaseModel):
    id : int
    name : str
    code : str
    google_id :str
    source : str
    status : str
    teacher_id : str
    created_at : datetime
    updated_at : datetime
    student_count : int


class StudentResponse(BaseModel):
    id : int
    uuid : str
    first_name : str
    last_name : str
    email : str
    parents_email : str
    class_id : int

class ClassDetailResponse(ClassResponse):
    students : List[StudentResponse]

    class Config:
        orm_mode = True

class BasicClassResponse(BaseModel):
    id : int
    name : str

class BasicStudentResponse(BaseModel):
    uuid : str
    first_name : str
    last_name : str
    email : str
    parents_email : str


class UploadStudentSpreadsheetResponse(BaseModel):
    updated_classes : List[BasicClassResponse]
    students : List[BasicStudentResponse]

class BasicGoogleClassResponse(BaseModel):
    google_id : str
    name : str
    status : str

