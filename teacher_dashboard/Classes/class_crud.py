import datetime
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
import string
from teacher_dashboard import models, schemas
import random
from teacher_dashboard.Classes.schemas import ClassResponse,ClassDetailResponse
from teacher_dashboard.Students import student_crud
import logging


logger = logging.getLogger(__name__)

def get_class_by_id(db: Session, class_id: int):

    db_class =  db.query(models.Classes).filter( models.Classes.id == class_id).first()

    if db_class is None:
        logger.debug('No class was found with class_id : {}'.format(class_id))
        raise HTTPException(status_code=404, detail="Class not found")

    class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
    return class_response


def get_my_classes(db: Session,teacher_id: str):

    db_classes = db.query(models.Classes).filter(models.Classes.teacher_id == teacher_id).all()
    classes = []
    for db_class in db_classes :
        class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
        classes.append(class_response)
    return classes

def get_class_by_code(db: Session, class_code: str):

    db_class =  db.query(models.Classes).filter(models.Classes.code == class_code).first()

    if db_class is None:
        logger.debug("No class was found with class code : {}".format(class_code))
        raise HTTPException(status_code=404, detail="Class not found")

    class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
    return class_response

#generating new class code
def generate_code(length=int):
    letters=string.ascii_uppercase
    code = ''.join(random.choice(letters) for i in range(length))
    return code


def create_class(db: Session, Class: schemas.ClassesCreate):
    class_code=generate_code(6)
    db_class = db.query(models.Classes).filter(models.Classes.code == class_code).first()

    # if a class with code=class_code alredy exists generate new code
    logger.debug('Generating a unique Class Code')
    while db_class:
        class_code=generate_code(6)
        db_class = db.query(models.Classes).filter(models.Classes.code == class_code).first()
    
    created_at=datetime.datetime.now()
    db_class = models.Classes(  source='manual',
                                name=Class.name.strip(),
                                google_id="", 
                                teacher_id=Class.teacher_id,
                                code=class_code,
                                created_at=created_at,
                                updated_at=created_at,
                                status=" ",
                                student_count=0 )
    try:
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        db.close()
    except Exception as e:
        logger.debug('unable to connect to classes in db')
        raise HTTPException(status_code = 503 ,detail="Couldn't connect to the classroom service.")

    class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
    return class_response

def delete_class(db: Session, class_id: int):

    try: 
        rows_affected = db.query(models.Classes).filter(models.Classes.id == class_id).delete(synchronize_session='fetch')   
        db.commit()
        db.close()
    except Exception as e:
        logger.debug('unable to connect to classes in db')
        raise HTTPException(status_code = 503 ,detail="Couldn't connect to the classroom service.")

    return rows_affected


def update_editTime(db:Session, class_id: int):
    db_class=db.query(models.Classes).filter(models.Classes.id==class_id).first()
    if db_class is not None:
        db_class.updated_at=datetime.datetime.now()

        try:
            db.add(db_class)
            db.commit()
            db.refresh(db_class)
            db.close()
        except Exception as e:
            logger.debug('unable to connect to classes in db')
            raise HTTPException(status_code = 503 ,detail="Couldn't connect to the classroom service.")

    return db_class

def get_teacher_classes_by_google_id(db: Session,teacher_id: str,google_id:str):

    db_class = db.query(models.Classes).filter(models.Classes.teacher_id == teacher_id,models.Classes.google_id == google_id).first()
    if db_class is None:
        return db_class

    class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
    return class_response

def connect_google_class(db:Session, Class: schemas.GoogleClass):
    class_code=generate_code(6)
    db_class = db.query(models.Classes).filter( models.Classes.code == class_code).first()

    # if a class with code=class_code alredy exists generate new code
    logger.debug('Generating a unique Class code')
    while db_class:
        class_code=generate_code(6)
        db_class = db.query(models.Classes).filter( models.Classes.code == class_code).first()
    
    created_at=datetime.datetime.now()
    db_class = models.Classes(source='google_classroom',google_id=Class.google_id,name=Class.name.strip(), teacher_id=Class.teacher_id,code=class_code,created_at=created_at,updated_at=created_at,status='connected',student_count=0)
    
    try:
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        db.close()
    except Exception as e:
        logger.debug('unable to connect to classes in db')
        raise HTTPException(status_code = 503 ,detail="Couldn't connect to the classroom service.")

    class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
    return class_response


def get_teachers_class(db:Session,teacher_id:str,class_id:int):

    db_class = db.query(models.Classes).filter(models.Classes.teacher_id == teacher_id,models.Classes.id==class_id).first()
    
    if db_class is None:
        return db_class
        
    class_response = ClassResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count)
    return class_response

def get_teacher_classes_details(db: Session, teacher_id: str):
    response = []
    db_classes = get_my_classes(db,teacher_id)
    for db_class in db_classes:
        class_students = student_crud.get_students_by_class(db,db_class.id)
        class_detail_response = ClassDetailResponse(id = db_class.id,
                                    name = db_class.name,
                                    code = db_class.code,
                                    google_id = db_class.google_id,
                                    source = db_class.source,
                                    status = db_class.status,
                                    teacher_id = db_class.teacher_id,
                                    created_at = db_class.created_at,
                                    updated_at = db_class.updated_at,
                                    student_count = db_class.student_count,
                                    students = class_students)

        response.append(class_detail_response)
    return response

def refresh_student_count(db:Session, class_id:int):

    db_students = db.query(models.Students).filter(models.Students.class_id == class_id).all()
    db_class = db.query(models.Classes).filter(models.Classes.id == class_id).first()

    student_count = len(db_students)
    if (db_class.student_count == student_count):
        return
    db_class.student_count = student_count

    try:
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        db.close()
    except Exception as e:
        logger.debug('unable to connect to classes in db')
        raise HTTPException(status_code = 503 ,detail="Couldn't connect to the classroom service.")
    return