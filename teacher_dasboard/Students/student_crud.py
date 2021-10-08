import random
import string
from sqlalchemy.orm import Session
from teacher_dasboard import models, schemas
from teacher_dasboard.Classes import class_crud

def generate_password(length: int):
    letters=string.ascii_letters
    password = ''.join(random.choice(letters) for i in range(length))
    return password

def get_students_by_class(db: Session, class_id: int):

    return db.query(models.Students).filter( models.Students.class_id == class_id).all()

def create_student(db: Session, Student: schemas.StudentsCreate):
    if len(Student.password)<6:
        Student.password=generate_password(8)
    db_student = models.Students(first_name=Student.first_name,last_name=Student.last_name,password=Student.password, email=Student.email,parents_email=Student.parents_email,class_id = Student.class_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    db.close()

    class_crud.increment_student_count(db=db,class_id=db_student.class_id)
    return db_student


def delete_class_student(db: Session,class_id:int, student_id: int):
    rows_affected = db.query(models.Students).filter(models.Students.id == student_id,models.Students.class_id == class_id).delete(synchronize_session='fetch')
    db.commit()
    db.close()
    class_crud.decrement_student_count(db=db,class_id=class_id)
    return rows_affected