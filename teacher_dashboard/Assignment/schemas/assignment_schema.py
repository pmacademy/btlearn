from pydantic.networks import EmailStr
from teacher_dashboard.Assignment.constants.enums import QuestionStatusEnum, TutorAvailableEnum
from datetime import datetime
from re import L
from typing import List, Optional
from fastapi.param_functions import Query
from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import Boolean


class AssignmentStudent(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    email: EmailStr
    parents_email: Optional[EmailStr] = None
    class_id: int


class AssignmentClass(BaseModel):
    class_id: int

    class Config:
        orm_mode = True


class AssignmentQuestion(BaseModel):
    question_id: str
    sequence_num: int
    tutor_available: Optional[TutorAvailableEnum] = TutorAvailableEnum.AVAILABLE

    class Config:
        orm_mode = True


class AssignmentTopicsRequest(BaseModel):
    cluster_id: str
    topic_code: str
    topic_sequence_num: int
    tutor_available: Optional[TutorAvailableEnum] = TutorAvailableEnum.AVAILABLE
    questions: List[AssignmentQuestion]

    class Config:
        orm_mode = True


class CreateAssignmentRequest(BaseModel):
    title: str
    classes: List[AssignmentClass]
    topics: List[AssignmentTopicsRequest]
    is_published: Optional[bool] = False
    submission_last_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class ClassStudentsRequest(BaseModel):
    students: List[AssignmentStudent]

    class Config:
        orm_mode = True

class ClassStudentsResponse(BaseModel):
    students: List[AssignmentStudent]

    class Config:
        orm_mode = True

class UpdateAssignmentRequest(BaseModel):
    id: int
    title: str
    classes: List[AssignmentClass]
    topics: List[AssignmentTopicsRequest]
    is_published: Optional[bool] = False
    submission_last_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class UpdateAssignmentPublishStatusRequest(BaseModel):
    id: int
    is_published: bool

    class Config:
        orm_mode = True


class AssignmentTopicsResponse(BaseModel):
    cluster_id: str
    topic_code: str
    topic_name: str
    topic_sequence_num: int
    tutor_available: Optional[TutorAvailableEnum] = TutorAvailableEnum.AVAILABLE
    questions: List[AssignmentQuestion]

    class Config:
        orm_mode = True


class AssignmentResponse(BaseModel):
    id: int
    teacher_id: str
    title: str
    classes: List[AssignmentClass]
    topics: List[AssignmentTopicsResponse]
    # students: List[dict]
    is_published: bool
    submission_last_date: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None

    class Config:
        orm_mode = True


class BasicAssignementDetailsTeacherResponse(BaseModel):
    id: int
    title: str
    completion_status: str
    classes_count: int
    students_count: int
    questions_count: int
    is_published: bool
    submission_last_date: Optional[datetime] = None
    performance: int
    last_modified_time: datetime


class AllAssignmentTeacherResponse(BaseModel):
    teacher_id: str
    published: List[BasicAssignementDetailsTeacherResponse]
    not_published: List[BasicAssignementDetailsTeacherResponse]

    class Config:
        orm_mode = True


class BasicAssignementDetailsStudentResponse(BaseModel):
    assignment_id: int
    title: str
    progress: str
    due_date: str
    late: bool
    completed: bool
    has_started: bool
    nearby_day: Optional[str]
    utc_due_time: datetime


class AllAssignmentStudentResponse(BaseModel):
    student_id: str
    assignments: List[BasicAssignementDetailsStudentResponse]
    total_count: int


class StudentNextQuestionDetailsResponse(BaseModel):
    student_id: str
    class_id: int
    assignment_id: int
    question_id: Optional[str]
    question_str: Optional[str]
    question_complete_data: Optional[dict]
    tutor_available: Optional[TutorAvailableEnum]
    current_seq_number: Optional[int]
    total_questions: int
    assignment_complete: bool = False


class StudentQuestionCompleteResponse(BaseModel):
    student_id: str
    class_id: int
    assignment_id: int
    question_id: Optional[str]
    status: Optional[QuestionStatusEnum]
    current_seq_number: Optional[int]
    total_questions: int
    assignment_complete: bool = False
