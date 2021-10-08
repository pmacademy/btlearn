import datetime
from sqlalchemy.orm import Session
import string
from teacher_dasboard import models, schemas
import random


def get_class_by_id(db: Session, class_id: int):

    return db.query(models.Classes).filter( models.Classes.id == class_id).first()




def get_class_by_name(name: str,db: Session):
    return db.query(models.Classes).filter(models.Classes.name == name).all()




def get_my_classes(db: Session,teacher_id: str):

    return db.query(models.Classes).filter(models.Classes.teacher_id == teacher_id).all()

def get_class_by_code(db: Session, class_code: str):

    return db.query(models.Classes).filter(models.Classes.code == class_code).first()

#generating new class code
def generate_code(length=int):
    letters=string.ascii_uppercase
    code = ''.join(random.choice(letters) for i in range(length))
    return code


def create_class(db: Session, Class: schemas.ClassesCreate):
    class_code=generate_code(6)
    db_class = get_class_by_code(db, class_code=class_code)

    # if a class with code=class_code alredy exists generate new code
    while db_class:
        class_code=generate_code(6)
        db_class = get_class_by_code(db, class_code=class_code)
    
    created_at=datetime.datetime.now()
    db_class = models.Classes(name=Class.name,google_id="", teacher_id=Class.teacher_id,code=class_code,created_at=created_at,updated_at=created_at,status='manual',student_count=0)
    
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    db.close()
    return db_class

def delete_class(db: Session, class_id: int):
    rows_affected = db.query(models.Classes).filter(models.Classes.id == class_id).delete(synchronize_session='fetch')
    db.commit()
    db.close()
    return rows_affected

def update_editTime(db:Session, class_id: int):
    db_class=db.query(models.Classes).filter(models.Classes.id==class_id).first()
    if db_class is not None:
        db_class.updated_at=datetime.datetime.now()

        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        db.close()
    return db_class

def get_teacher_classes_by_google_id(db: Session,teacher_id: str,google_id:str):

    return db.query(models.Classes).filter(models.Classes.teacher_id == teacher_id,models.Classes.google_id == google_id).first()

def connect_google_class(db:Session, Class: schemas.GoogleClass):
    class_code=generate_code(6)
    db_class = get_class_by_code(db, class_code=class_code)

    # if a class with code=class_code alredy exists generate new code
    while db_class:
        class_code=generate_code(6)
        db_class = get_class_by_code(db, class_code=class_code)
    
    created_at=datetime.datetime.now()
    db_class = models.Classes(google_id=Class.google_id,name=Class.name, teacher_id=Class.teacher_id,code=class_code,created_at=created_at,updated_at=created_at,status='connected',student_count=0)
    
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    db.close()
    return db_class

def increment_student_count(db:Session,class_id:int):
    db_class=get_class_by_id(db=db,class_id=class_id)
    db_class.student_count+=1
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    db.close()
    return
def decrement_student_count(db:Session,class_id:int):
    db_class=get_class_by_id(db=db,class_id=class_id)
    db_class.student_count-=1
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    db.close()
    return

def get_teachers_class(db:Session,teacher_id:str,class_id:int):
    return db.query(models.Classes).filter(models.Classes.teacher_id == teacher_id,models.Classes.id==class_id).first()