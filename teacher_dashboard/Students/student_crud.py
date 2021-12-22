import datetime
import json
import random
import string
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import Null
from config.app_config import get_config
from teacher_dashboard import models, schemas
from teacher_dashboard.Assignment.constants.constants import NotificationServiceTypes, StudentAccountCreateEmailConstant, StudentAlreadyExistsAddedToClass
from teacher_dashboard.Classes import class_crud
import requests
from teacher_dashboard.Classes.schemas import ClassStudentsRequest, Student
from teacher_dashboard.Classes.assignment_service import assignment_service
from teacher_dashboard.Classes.schemas import StudentResponse
import logging
from fastapi import BackgroundTasks

from teacher_dashboard.notification.notification_service import Notification


logger = logging.getLogger(__name__)
AUTH_URL = get_config().AUTH_URL
email_notification_service = Notification.get(
    NotificationServiceTypes.EMAIL)


def get_client_token():

    logger.debug('Authenticating teacher_tool_client')
    url = get_config().AUTH_URL + "/api/v1/user/login"
    payload = json.dumps(
        {
            "provider": "local",
            "email": get_config().TEACHER_TOOL_CLIENT_ID,
            "password": get_config().TEACHER_TOOL_CLIENT_PASSWORD,
            "token": "",
        }
    )

    headers = {"accept": "application/json",
               "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code != 200):
        logger.debug('Unable to authenticate teacher_tool_client. status_code :{} , detail :{}'.format(
            response.status_code, response.json()))
        raise HTTPException(
            status_code=503, detail="unable to authenticate teacher_tool_client")

    access_token = response.json()["access_token"]
    return "Bearer " + access_token


def get_user_detail(email: str, client_token):

    url = AUTH_URL + "/api/v1/user/check/details"
    payload = json.dumps({"email": email})

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": client_token,
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code != 200):
        logger.debug('unable to get user details from auth. status_code :{} , detail :{}'.format(
            response.status_code, response.json()))
        raise HTTPException(
            status_code=503, detail="unable to get user details from auth")

    return response


def invite_student(email: str, client_token: str):

    url = AUTH_URL + "/api/v1/user/invite"
    payload = json.dumps({"user_email": email, "roles": ["student"]})

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": client_token,
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code != 200):
        logger.debug('unable to invite user. status_code :{} , detail :{}'.format(
            response.status_code, response.json()))
        raise HTTPException(status_code=503, detail="unable to invite user")

    return response


def get_students_by_class(db: Session, class_id: int):

    logger.debug('reading students of class :{}'.format(class_id))
    db_students = db.query(models.Students).filter(
        models.Students.class_id == class_id).all()

    class_students_response = []
    for db_student in db_students:
        student_response = StudentResponse(id=db_student.id,
                                           uuid=db_student.uuid,
                                           first_name=db_student.first_name,
                                           last_name=db_student.last_name,
                                           email=db_student.email,
                                           parents_email= (db_student.parents_email if db_student.parents_email else ""),
                                           class_id=db_student.class_id)

        class_students_response.append(student_response)
    class_crud.refresh_student_count(db=db, class_id=class_id)
    return class_students_response


def create_student(db: Session, Student: schemas.StudentsCreate, background_task: BackgroundTasks, teacher_name: str):

    logger.debug('Adding new student')
    client_token = get_client_token()

    logger.debug('inviting student :{}'.format(Student.email))
    invite_response = invite_student(
        email=Student.email, client_token=client_token)

    url = AUTH_URL + "/api/v1/user"
    payload = json.dumps(
        {
            "provider": "local",
            "email": str(Student.email),
            "display_name": Student.first_name + " " + Student.last_name,
            "password": Student.password,
            "token": "",
            "default_role": "student",
            "roles": ["student"],
        }
    )
    headers = {"accept": "application/json",
               "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = response.json()

    if response.status_code not in [200, 401]:
        logger.debug('Unable to create new user. status_code :{} , detail :{}'.format(
            response.status_code, response.json()))
        raise HTTPException(
            status_code=503, detail="unable to create new user")

    if response.status_code == 200 and 'user_id' in response.json():
        uuid = json_data["user_id"]
        logger.debug('new user created. user_id:{}'.format(uuid))

        logger.debug("sending 'new account creation' notification to students through email")
        background_task.add_task(email_notification_service.notify, StudentAccountCreateEmailConstant.TEAMPLATE_NAME, {
            StudentAccountCreateEmailConstant.Fields.Body.STUDENT_LAST_NAME: Student.last_name,
            StudentAccountCreateEmailConstant.Fields.Body.TEACHER_NAME: teacher_name,
            StudentAccountCreateEmailConstant.Fields.Body.BYETELEARN_SIGN_IN_URL: get_config().STUDENT_SIGN_IN_URL,
            StudentAccountCreateEmailConstant.Fields.Body.STUDENT_EMAIL: Student.email,
            StudentAccountCreateEmailConstant.Fields.Body.STUDENT_PASSWORD: Student.password
        }, Student.email)

    else:
        logger.debug('user already exists. fetching data')
        user_detail = get_user_detail(
            email=Student.email, client_token=client_token).json()
        uuid = user_detail['user_details']['user_id']
        name = user_detail['user_details']['display_name'].split()
        Student.first_name = name[0].strip()
        Student.last_name = ""
        if len(name) > 1:
            Student.last_name = name[-1].strip()
        Student.parents_email = user_detail['user_details']['parent_email']

        logger.debug("sending 'adding to a new class' notification to students through email.")
        background_task.add_task(email_notification_service.notify, StudentAlreadyExistsAddedToClass.TEAMPLATE_NAME, {
            StudentAlreadyExistsAddedToClass.Fields.Body.STUDENT_FIRST_NAME: Student.first_name,
            StudentAlreadyExistsAddedToClass.Fields.Body.STUDENT_LAST_NAME: Student.last_name,
            StudentAlreadyExistsAddedToClass.Fields.Body.TEACHER_NAME: teacher_name,
            StudentAlreadyExistsAddedToClass.Fields.Body.BYETELEARN_SIGN_IN_URL: get_config().STUDENT_SIGN_IN_URL,
            StudentAlreadyExistsAddedToClass.Fields.Body.STUDENT_EMAIL: Student.email
        }, Student.email)

    db_student = models.Students(
        uuid=uuid,
        first_name=Student.first_name,
        last_name=Student.last_name,
        password=Student.password,
        email=Student.email,
        parents_email=Student.parents_email,
        class_id=Student.class_id,
    )

    logger.debug('Adding user to class_student db')
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        db.close()
    except Exception as e:
        logger.debug('unable to connect to class_student in db')
        raise HTTPException(
            status_code=503, detail="Couldn't connect to the classroom service.")

    class_crud.refresh_student_count(db=db, class_id=db_student.class_id)

    student_response = StudentResponse(id=db_student.id,
                                       uuid=db_student.uuid,
                                       first_name=db_student.first_name,
                                       last_name=db_student.last_name,
                                       email=db_student.email,
                                       parents_email=(db_student.parents_email if db_student.parents_email else ""),
                                       class_id=db_student.class_id)
    logger.debug('new student added. data:{}'.format(student_response))
    return student_response


def rename_class_student(db: Session, class_id: int, student_id: int, teacher_id: str, first_name: str, last_name: str):

    db_student = db.query(models.Students).filter(
        models.Students.id == student_id, models.Students.class_id == class_id).first()

    first_name = first_name.strip()
    last_name = last_name.strip()

    if db_student is None:
        logger.debug('user is not authorized to access the student data. teacher_id:{}, student_id:{}'.format(
            teacher_id, student_id))
        raise HTTPException(status_code=401, detail='Unauthorized')

    db_student.first_name = first_name
    db_student.last_name = last_name

    class_students = (
        db.query(models.Students)
        .filter(
            models.Students.uuid == db_student.uuid,
        )
        .all()
    )

    try:
        for student in class_students:
            student.first_name = first_name
            student.last_name = last_name
            db.add(student)
            db.commit()
            db.refresh(student)

    except Exception as e:
        logger.debug('unable to connect to class_student in db')
        raise HTTPException(
            status_code=503, detail="Couldn't connect to the classroom service.")

    assignment_students = (
        db.query(models.AssignmentStudent)
        .filter(
            models.AssignmentStudent.student_id == db_student.uuid,
        )
        .all()
    )

    try:
        for student in assignment_students:
            student.first_name = first_name
            student.last_name = last_name
            db.add(student)
            db.commit()
            db.refresh(student)
        db.close()

    except Exception as e:
        logger.debug('unable to connect to assignment_student in db')
        raise HTTPException(
            status_code=503, detail="Couldn't connect to the classroom service.")

    student_response = StudentResponse(id=db_student.id,
                                       uuid=db_student.uuid,
                                       first_name=db_student.first_name,
                                       last_name=db_student.last_name,
                                       email=db_student.email,
                                       parents_email=(db_student.parents_email if db_student.parents_email else ""),
                                       class_id=db_student.class_id)

    return student_response


def delete_class_student(db: Session, class_id: int, student_id: int):
    row_data = (
        db.query(models.Students)
        .filter(models.Students.id == student_id, models.Students.class_id == class_id)
        .first()
    )
    if row_data == None:
        logger.debug('user is not authorized to access the student data')
        raise HTTPException(status_code=401, detail='Unauthorized')
    else:
        assignment_service.delete_students(
            ClassStudentsRequest(
                students=[
                    Student(
                        student_id=row_data.uuid,
                        first_name=row_data.first_name,
                        last_name=row_data.last_name,
                        email=row_data.email,
                        parents_email=(
                            None
                            if (row_data.parents_email == "nan")
                            else row_data.parents_email
                        ),
                        class_id=row_data.class_id,
                    )
                ]
            )
        )

        try:
            db.delete(row_data)
            db.commit()
            db.close()
        except Exception as e:
            logger.debug('unable to connect to class_student in db')
            raise HTTPException(
                status_code=503, detail="Couldn't connect to the classroom service.")

        class_crud.refresh_student_count(db=db, class_id=class_id)
        return row_data
