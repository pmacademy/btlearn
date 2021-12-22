from teacher_dashboard.Assignment.constants.enums import TutorAvailableEnum
from datetime import datetime
from typing import List, Optional
from fastapi.param_functions import Query
from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import Boolean



class AssignmentClass(BaseModel):
    class_id: int

    class Config:
        orm_mode = True


class AssignmentQuestionSchema(BaseModel):
    question_id: str
    sequence_num: int
    tutor_available: Optional[TutorAvailableEnum] = TutorAvailableEnum.AVAILABLE

    class Config:
        orm_mode = True


class AssignmentTopics(BaseModel):
    topic_code: str
    topic_sequence_num: int
    tutor_available: Optional[TutorAvailableEnum] = TutorAvailableEnum.AVAILABLE
    questions: List[AssignmentQuestionSchema]

    class Config:
        orm_mode = True


class CreateAssignmentRequest(BaseModel):
    teacher_id: int
    title: str
    classes: List[AssignmentClass]
    topics: List[AssignmentTopics]
    is_published: Optional[bool] = False
    submission_last_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class UpdateAssignmentRequest(BaseModel):
    id: int
    teacher_id: int
    title: str
    classes: List[AssignmentClass]
    topics: List[AssignmentTopics]
    is_published: Optional[bool] = False
    submission_last_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class UpdateAssignmentPublishStatusRequest(BaseModel):
    id: int
    is_published: bool

    class Config:
        orm_mode = True


class AssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    title: str
    classes: List[AssignmentClass]
    topics: List[AssignmentTopics]
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
    questions_count: int
    is_published: bool
    submission_last_date: Optional[datetime] = None
    last_modified_time: datetime
    performance: int


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
    due_date: datetime
    late: bool
    completed: bool


class AllAssignmentStudentResponse(BaseModel):
    student_id: str
    active: List[BasicAssignementDetailsStudentResponse]
    completed: List[BasicAssignementDetailsStudentResponse]
