from teacher_dashboard.db_session import request_auth_token
from teacher_dashboard.Assignment.dependencies.token_dependency import token_dependency
from teacher_dashboard.db_session import db_session
from teacher_dashboard.Assignment.schemas.assignment_schema import AssignmentResponse, ClassStudentsRequest
from teacher_dashboard.Assignment.services.assignment_service import assignment_service
from teacher_dashboard.Assignment.schemas.assignment_schema import CreateAssignmentRequest, UpdateAssignmentPublishStatusRequest, UpdateAssignmentRequest
from teacher_dashboard.database import SessionLocal, engine
from teacher_dashboard.db_session import get_db
from teacher_dashboard.Assignment.constants.enums import QuestionStatusEnum
from teacher_dashboard import models
from contextvars import ContextVar
from typing import List
from fastapi import Depends, APIRouter
from fastapi.param_functions import Query, Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, query_expression
from teacher_dashboard.custom_api_router import CustomAPIRouter
import logging

models.Base.metadata.create_all(bind=engine)

router = CustomAPIRouter(
    prefix="/api/v1/assignment",
    tags=["Assignment-New"]
)

logger = logging.getLogger(__name__)


@router.get("/{assignment_id}", response_model=AssignmentResponse, dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_assignment(assignment_id: int, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  assignment_id:{}".format(assignment_id))

    response = assignment_service.get_assignment(assignment_id, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.post("", response_model=AssignmentResponse, dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def create_assignment(assignment: CreateAssignmentRequest, user_id: str = Depends(token_dependency.get_user_id), auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer()), db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved: {}".format(assignment.dict()))

    response = assignment_service.create_assignment(assignment, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.put("", response_model=AssignmentResponse, dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def update_assignment(assignment: UpdateAssignmentRequest, user_id: str = Depends(token_dependency.get_user_id), auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer()),  db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(assignment.dict()))

    response = assignment_service.update_assignment(assignment, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.delete("/{assignment_id}", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def delete_assignment(assignment_id: int, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  assignment_id:{}".format(assignment_id))

    response = assignment_service.delete_assignment(assignment_id, user_id)

    logger.debug("response: {}".format(response))

    return response


@router.post("/add-students", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def add_students(class_students: ClassStudentsRequest, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(class_students.dict()))

    response = assignment_service.add_students(class_students)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.post("/delete-students", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def delete_new_students(class_students: ClassStudentsRequest, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(class_students.dict()))

    response = assignment_service.delete_students(class_students)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/teacher/all", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_all_teacher_assignments(user_id: str = Depends(token_dependency.get_user_id), auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer()),  db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(auth_token)

    logger.debug("user_id: {}".format(user_id))

    response = assignment_service.get_all_teacher_assignments(user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


# @router.get("/student/all", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_student)])
# async def get_all_student_assignments(user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
#     db_session.set(db)

#     logger.debug("user_id: {}".format(user_id))

#     return assignment_service.get_all_student_assignments(user_id)


@router.get("/copy/{assignment_id}", response_model=AssignmentResponse, dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def copy_assignment(assignment_id: int, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  assignment_id:{}".format(assignment_id))

    response = assignment_service.copy_assignment(assignment_id, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.post("/publish-status", response_model=AssignmentResponse, dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def publish_status(updateAssignmentPublishStatusRequest: UpdateAssignmentPublishStatusRequest, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug(
        "data recieved:  {}".format(updateAssignmentPublishStatusRequest.dict()))

    response = assignment_service.updateAssignmentStatus(
        updateAssignmentPublishStatusRequest, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


# async def get_students(class_id: int, db: Session = Depends(get_db)):
#     students = student_crud.get_students_by_class(db, class_id)
#     return students

@router.get("/student/active", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_student)])
async def get_all_student_active_assignments(all: bool = False, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  all:{}".format(all))

    response = assignment_service.get_all_student_active_assignments(
        user_id, all)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/student/completed", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_student)])
async def get_all_student_completed_assignments(start: int = 0, limit: int = 10, user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  start:{} limit:{}".format(start, limit))

    response = assignment_service.get_all_student_completed_assignments(
        user_id, start, limit)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/{assignment_id}/question", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_student)])
async def student_get_assignment_question(assignment_id: int = 0, user_id: str = Depends(token_dependency.get_user_id),  db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  assignment_id:{}".format(assignment_id))

    response = assignment_service.get_next_question(assignment_id, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.post("/{assignment_id}/question/complete", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_student)])
async def student_complete_assignment_question(assignment_id: int, status: QuestionStatusEnum = QuestionStatusEnum.NOT_ATTEMPTED, user_id: str = Depends(token_dependency.get_user_id),  db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  assignment_id:{}".format(assignment_id))

    response = assignment_service.complete_next_question(
        assignment_id, status, user_id)

    logger.debug("response: {}".format(response.dict()))

    return response
