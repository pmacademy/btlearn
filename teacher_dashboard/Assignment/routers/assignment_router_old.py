from teacher_dashboard.db_session import db_session
from teacher_dashboard.Assignment.services.assignment_service_old import assignment_service
from teacher_dashboard.Assignment.schemas.assignment_schema_old import CreateAssignmentRequest, UpdateAssignmentPublishStatusRequest, UpdateAssignmentRequest, AssignmentResponse
from teacher_dashboard.database import SessionLocal, engine
from teacher_dashboard.db_session import get_db
from teacher_dashboard.custom_api_router import CustomAPIRouter
from teacher_dashboard import models
from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session, query_expression

models.Base.metadata.create_all(bind=engine)


router = CustomAPIRouter(
    prefix="/assignment",
    tags=["Assignment-Old"]
)


@router.get("", response_model=AssignmentResponse)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.get_assignment(assignment_id)


@router.post("", response_model=AssignmentResponse)
async def create_assignment(assignment: CreateAssignmentRequest, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.create_assignment(assignment)


@router.put("", response_model=AssignmentResponse)
async def update_assignment(assignment: UpdateAssignmentRequest, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.update_assignment(assignment)


@router.delete("")
async def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.delete_assignment(assignment_id)


@router.post("/question/complete")
async def student_complete_assignment_question(assignment_id: int, question_id: str, student_id: int,  db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.complete_question(assignment_id, question_id, student_id)


@router.get("/all")
async def get_all_teacher_assignments(teacher_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.get_all_teacher_assignments(teacher_id)


@router.get("/student/all")
async def get_all_student_assignments(student_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.get_all_student_assignments(student_id)


@router.get("/copy", response_model=AssignmentResponse)
async def copy_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.copy_assignment(assignment_id)


@router.post("/publish-status", response_model=AssignmentResponse)
async def publish_status(updateAssignmentPublishStatusRequest: UpdateAssignmentPublishStatusRequest, db: Session = Depends(get_db)):
    db_session.set(db)
    return assignment_service.updateAssignmentStatus(updateAssignmentPublishStatusRequest)
