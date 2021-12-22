from typing import List
from fastapi import Depends,APIRouter
from sqlalchemy.orm import Session

from teacher_dashboard import  models, schemas
from teacher_dashboard.database import SessionLocal, engine
from teacher_dashboard.Students import student_crud

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    tags=["Student"],
    responses={500: {"description": "Not found"}},
)



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.get("/students/", response_model=List[schemas.Students] ,tags=['Student'])
# async def get_students(class_id: int, db: Session = Depends(get_db)):
#     students = student_crud.get_students_by_class(db, class_id)
#     return students

# @router.post("/students/", response_model=schemas.Students , tags=['Student'])
# async def create_student(Student: schemas.StudentsCreate, db: Session = Depends(get_db)):

#     return student_crud.create_student(db=db, Student=Student)

# @router.delete("/delete_student/" )
# async def del_student(student_id: int, db: Session = Depends(get_db)):
#     affected_rows=student_crud.delete_student(db, student_id=student_id)
#     return {"message": str(affected_rows)+" Student deleted."}