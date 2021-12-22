from fastapi.param_functions import Depends, Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from teacher_dashboard.Assignment.constants.enums import AssignmentStudentStatusEnum, DataDownloadFormatEnum
from typing import Optional
from teacher_dashboard.Assignment.dependencies.token_dependency import token_dependency


class BaseRequest(BaseModel):
    user_id: str = Depends(token_dependency.get_user_id)
    auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer())

#################################
# Assignment Insights Download  #
#################################

class InsightsDownloadRequest(BaseRequest):
    assignment_id: Optional[int]
    class_id: Optional[int]
    format: DataDownloadFormatEnum = DataDownloadFormatEnum.CSV

########################
# Assignment Insights  #
########################


class InsightsRequest(BaseRequest):
    assignment_id: Optional[int]
    class_id: Optional[int]


########################
# Assignment Overview  #
########################

class AssignmentClassOverviewRequest(BaseRequest):
    assignemnt_id: int
    class_id: Optional[int]


########################
# Assignment Students  #
########################

class AssignmentStudentsRequest(BaseRequest):
    assignment_id: int
    class_id: Optional[int]
    status: Optional[AssignmentStudentStatusEnum] = AssignmentStudentStatusEnum.ALL
    progress: bool = False
    start: int = 0
    limit: int = 10


########################
# Assignment Questions #
########################

class AssignmentQuestionsRequest(BaseRequest):
    assignment_id: int
    class_id: Optional[int]
    question_id: Optional[str]
    start: int = 0
    limit: int = 10

########################
# Log Report #
########################


class ReportingResponse(BaseModel):
    id: Optional[int] = None  # ..
    question_session_id: Optional[str] = None
    student_id: Optional[str] = None
    assignment_id: Optional[int] = None
    step_number: Optional[str] = None
    student_input_dict: Optional[dict] = None
    is_correct: Optional[bool] = None
    is_partially_correct: Optional[bool] = None
    is_complete: Optional[bool] = None
    hint_code: Optional[str] = None
    mode: Optional[str] = None  # ..
    question_id: Optional[str] = None
    class_id: Optional[int] = None  # ..
    interaction_type: Optional[str] = None
    main_cat: Optional[str] = None
    sub_cat: Optional[str] = None

    class Config:
        orm_mode = True


class LogReport(BaseModel):
    question_session_id: Optional[str] = None
    student_id: Optional[str] = None
    assignment_id: Optional[int] = None
    step_number: Optional[str] = None
    student_input_dict: Optional[dict] = None
    is_correct: Optional[bool] = None
    is_partially_correct: Optional[bool] = None
    is_complete: Optional[bool] = False
    hint_code: Optional[str] = None
    mode: Optional[str] = None  # ..
    question_id: Optional[str] = None
    class_id: Optional[int] = None  # ..
    interaction_type: Optional[str] = None
    problem_type: Optional[str] = None
    subtype1: Optional[str] = None

    class Config:
        orm_mode = True
