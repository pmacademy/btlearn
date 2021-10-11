

from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import  DateTime




class ClassesBase(BaseModel):

    name: str


class ClassesCreate(ClassesBase):
    name: str
    teacher_id: str
    

class GoogleClass(ClassesBase):
    name: str
    teacher_id: str
    google_id:str

class Classes(ClassesBase):
    id: int
    source:str
    google_id: str
    status: str
    code : str
    teacher_id : str
    created_at: datetime
    updated_at: datetime
    student_count: int

    class Config:
        orm_mode = True



class StudentsBase(BaseModel):
    first_name : str
    last_name: str
    




class StudentsCreate(StudentsBase):

    email: str
    class_id:int
    password: str
    parents_email : str

class Students(StudentsBase):
    
    id: int
    uuid:str
    email: str
    parents_email : str
    password: str
    class_id:int

    class Config:
        orm_mode = True



