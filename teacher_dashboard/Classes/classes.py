import json
import json
from os import name
import random
import string
from typing import List, Optional
from fastapi import Depends, HTTPException, APIRouter, File, UploadFile, Request, BackgroundTasks
from fastapi.param_functions import Query, Security
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true
from starlette import status
from config.app_config import get_config
from teacher_dashboard import models, schemas
from teacher_dashboard.Classes.constants import StudentAccountCreateEmailConstant
from teacher_dashboard.database import SessionLocal, engine
from teacher_dashboard.Classes import class_crud
from teacher_dashboard.Classes.token_dependency import token_dependency
from teacher_dashboard.Students import student_crud
import pandas as pd
import re
from teacher_dashboard.notification.notification_service import Notification
from teacher_dashboard.notification.notofication_constants import NotificationServiceTypesEnum
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from teacher_dashboard.db_session import request_auth_token
from teacher_dashboard.Classes.schemas import ClassStudentsRequest, Student
from teacher_dashboard.Classes.assignment_service import assignment_service
from config.app_config import get_config
import requests
import logging
from teacher_dashboard.Classes.schemas import BasicClassResponse, BasicStudentResponse, UploadStudentSpreadsheetResponse
from teacher_dashboard.Classes.spreadsheet_util import spreadsheet_util

logger = logging.getLogger(__name__)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
models.Base.metadata.create_all(bind=engine)
email_notification_service = Notification.get(
    NotificationServiceTypesEnum.EMAIL)

router = APIRouter(
    tags=["Classes"],
    responses={500: {"description": "Not found"}},
)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check(email):
    logger.debug('validating email')
    if(re.fullmatch(regex, email)):
        return True
    return False


def generate_password(length: int):
    letters = string.ascii_letters
    password = ''.join(random.choice(letters) for i in range(length))
    return password


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


def add_relation(parent_user_id: str, child_user_id_list: List[str]):

    url = get_config().AUTH_URL + "/api/v1/relation"
    payload = json.dumps({"parent_user_id": parent_user_id,
                         "child_user_id_list": child_user_id_list})

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": get_client_token(),
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if(response.status_code != 200):
        logger.debug('Unable to authenticate teacher_tool_client. status_code :{} , detail :{}'.format(
            response.status_code, response.json()))
        raise HTTPException(
            status_code=503, detail="Unable to connect to the relation api of Auth System.")
    return response

@router.post("/api/v1/classes", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def create_class(name: str, teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved:  class_name:{}".format(name))

    Class = schemas.ClassesCreate(name=name, teacher_id=teacher_id)
    response = class_crud.create_class(db=db, Class=Class)

    logger.debug("response: {}".format(response.dict()))
    return response


@router.get("/api/v1/classes/all", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_all_classes(teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("user_id: {}".format(teacher_id))
    classes = class_crud.get_my_classes(db=db, teacher_id=teacher_id)

    logger.debug("response: {}".format(classes))
    return classes


@router.get("/api/v1/classes/all/details", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_all_classes_and_all_students(teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("user_id: {}".format(teacher_id))
    classes_response = class_crud.get_teacher_classes_details(
        db=db, teacher_id=teacher_id)

    logger.debug("response: {}".format(classes_response))
    return classes_response


@router.get("/api/v1/classes/id={class_id}", response_model=schemas.Classes)
async def get_class_by_class_id(class_id: int, db: Session = Depends(get_db)):

    logger.debug("data recieved : class_id: {}".format(class_id))
    class_response = class_crud.get_class_by_id(db, class_id)

    logger.debug("response: {}".format(class_response))
    return class_response


@router.get("/api/v1/classes/code={class_code}", response_model=schemas.Classes)
async def get_class_by_class_code(class_code: str, db: Session = Depends(get_db)):

    logger.debug("data recieved : class_code: {}".format(class_code))
    class_response = class_crud.get_class_by_code(db, class_code=class_code)

    logger.debug("response: {}".format(class_response))
    return class_response


@router.get("/api/v1/classes/{class_id}/students/all", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_class_students(class_id: int, teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved : class_id: {}".format(class_id))

    if class_crud.get_teachers_class(db, teacher_id, class_id) is not None:
        class_students_response = student_crud.get_students_by_class(
            db, class_id=class_id)

        logger.debug("response: {}".format(class_students_response))
        return class_students_response
    else:
        logger.debug("user is not authorized to access the class data")
        raise HTTPException(status_code=401, detail='Unauthorized')


@router.put("/api/v1/classes/{class_id}/students/rename/{student_id}", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def rename_class_student(class_id: int, student_id: int, first_name: str, last_name: str, access_token: str = Depends(token_dependency.get_token), teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved : [class_id: {} , student_id: {}, first_name: {}, last_name: {}]".format(
        class_id, student_id, first_name, last_name))

    if class_crud.get_teachers_class(db=db, teacher_id=teacher_id, class_id=class_id) is None:
        logger.debug("user is not authorized to access the student data")
        raise HTTPException(status_code=401, detail='Unauthorized')

    student_response = student_crud.rename_class_student(
        db, class_id=class_id, student_id=student_id, teacher_id=teacher_id, first_name=first_name, last_name=last_name)

    logger.debug("sending request to relation api to edit user details")

    url = get_config().AUTH_URL + "/api/v1/relation/user"
    payload = json.dumps(
        {
            "user_id": student_response.uuid,
            "display_name": first_name + ' ' + last_name
        }
    )
    headers = {"accept": "application/json", "Content-Type": "application/json",
               "Authorization": "Bearer " + access_token}

    response = requests.request("PUT", url, headers=headers, data=payload)
    if response.status_code != 200:
        logger.debug("Following error occured while connecting to auth service : status_code :{}, detail :{}".format(
            response.status_code, response.json()))
        raise HTTPException(
            status_code=503, detail="Unable to connect to the relation api of Auth System.")

    logger.debug("student was renamed succesfuly. updated_student_data :{}".format(
        student_response))
    return student_response


@router.delete("/api/v1/classes/{class_id}/students/delete/{student_id}", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def del_class_student(class_id: int, student_id=int, teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db), auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer())):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved : [class_id: {} , student_id: {}]".format(
        class_id, student_id))

    request_auth_token.set(auth_token)
    if class_crud.get_teachers_class(db=db, teacher_id=teacher_id, class_id=class_id) is None:

        logger.debug("user is not authorized to access the class data")
        raise HTTPException(status_code=401, detail='Unauthorized')

    row_data = student_crud.delete_class_student(
        db, class_id=class_id, student_id=student_id)

    logger.debug(
        "response: 1 student deleted. deleted_data:{}".format(row_data))
    return {"msg": "1 student deleted."}


@router.put("/api/v1/classes/upload/spreadsheet", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def upload_spreadsheet_to_multiple_classes(request: Request, background_task: BackgroundTasks, teacher_id: str = Depends(token_dependency.get_user_id), teacher_name: str = Depends(token_dependency.get_display_name), class_id: Optional[List[str]] = Query(None), file: UploadFile = File(default="abc.csv"), db: Session = Depends(get_db), auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer())):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved : [class_ids: {} , file_type: {}]".format(
        class_id, file.content_type))

    request_auth_token.set(auth_token)

    spreadsheet_util.file = file
    valid_students = await spreadsheet_util.extract()

    logger.debug("Data extracted successfully. Adding students.")
    updated_classes = []
    added_students = []
    flag = False
    student_uuid_list = []

    for id in class_id:
        class_students = student_crud.get_students_by_class(db,id)
        email_list = [st.email for st in class_students]

        for st in valid_students:
            if st['Email'] in email_list:
                _class = class_crud.get_teachers_class(db=db, teacher_id=teacher_id, class_id=id)
                logger.debug('A student with email id - {} is already registered for this class - {}'.format(st['Email'],_class))
                raise HTTPException(status_code=422, detail='A student with email id - {} is already registered for this class - {}'.format(st['Email'],_class.name))

    for id in class_id:
        db_class = class_crud.get_teachers_class(
            db=db, teacher_id=teacher_id, class_id=id)
        if db_class is None:
            continue
        class_crud.update_editTime(db=db, class_id=id)

        updated_classes.append(BasicClassResponse(id=db_class.id,
                                                  name=db_class.name))

        new_students_list = []
        for student in valid_students:
            if str(student['Parent email']) == "nan":
                student['Parent email'] = ""

            db_student = models.Students(first_name=str(student['First name']), last_name=str(student['Last name']), email=str(
                student['Email']), password=str(student['Password']), parents_email=str(student['Parent email']), class_id=id)
            db_student = student_crud.create_student(db=db, Student=db_student, background_task=background_task, teacher_name=teacher_name)
            new_students_list.append(Student(
                student_id=db_student.uuid,
                first_name=db_student.first_name,
                last_name=db_student.last_name,
                email=db_student.email,
                parents_email=None if(
                    db_student.parents_email == "nan" or db_student.parents_email == "") else db_student.parents_email,
                class_id=db_student.class_id
            ))

            if flag:
                continue
            student_uuid_list.append(db_student.uuid)

            basic_student_response = BasicStudentResponse(uuid=db_student.uuid,
                                                          first_name=db_student.first_name,
                                                          last_name=db_student.last_name,
                                                          email=db_student.email,
                                                          parents_email=db_student.parents_email)
            added_students.append(basic_student_response)

        new_students_request_body = ClassStudentsRequest(
            students=new_students_list)

        assignment_service.add_students(new_students_request_body)

        flag = True

    logger.debug("Adding parent child relation")
    add_relation(parent_user_id=teacher_id,
                 child_user_id_list=student_uuid_list)

    response = UploadStudentSpreadsheetResponse(updated_classes=updated_classes,
                                                students=added_students)
    logger.debug("response: {}".format(response))
    return response


@router.post("/api/v1/classes/upload/spreadsheet", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def create_class_and_upload_spreadsheet(class_name: str, background_task: BackgroundTasks, teacher_id: str = Depends(token_dependency.get_user_id), teacher_name: str = Depends(token_dependency.get_display_name),  file: UploadFile = File(default="abc.csv"), db: Session = Depends(get_db), auth_token: HTTPAuthorizationCredentials = Security(HTTPBearer())):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved : [class_name: {} , file_type: {}]".format(
        class_name, file.content_type))

    request_auth_token.set(auth_token)
    
    spreadsheet_util.file = file
    valid_students = await spreadsheet_util.extract()
    student_count = len(valid_students)
    
    logger.debug("Data extracted successfully. Creating new class")
    new_class = class_crud.create_class(
        db, schemas.ClassesCreate(name=class_name, teacher_id=teacher_id))

    new_class.student_count = student_count
    response = {}
    response['class'] = new_class
    response['students'] = []

    logger.debug("Adding students to class")
    student_uuid_list = []
    for student in valid_students:
        if str(student['Parent email']) == "nan":
            student['Parent email'] = ""

        db_student = models.Students(first_name=str(student['First name']), last_name=str(student['Last name']), email=str(
            student['Email']), password=str(student['Password']), parents_email=str(student['Parent email']), class_id=new_class.id)
        db_student = student_crud.create_student(db=db, Student=db_student, background_task=background_task, teacher_name=teacher_name)

        student_uuid_list.append(db_student.uuid)
        response['students'].append(db_student)

    logger.debug("Adding parent child relation")
    add_relation(parent_user_id=teacher_id,
                 child_user_id_list=student_uuid_list)
    logger.debug("response: {}".format(response))

    return response


@router.delete("/api/v1/classes/delete/{class_id}", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def del_class(class_id: int, teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("user_id: {}".format(teacher_id))
    logger.debug("data recieved : class_id: {}".format(class_id))

    if class_crud.get_teachers_class(db, teacher_id, class_id) is None:
        logger.debug("user is not authorized to access the class data")
        raise HTTPException(status_code=401, detail='Unauthorized')

    affected_rows = class_crud.delete_class(db, class_id=class_id)
    logger.debug("{} class deleted succesfully".format(affected_rows))
    return {"msg": str(affected_rows)+" class deleted."}
