from typing import List, Optional
import os.path
from fastapi import Depends, APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from requests.models import DecodeError
from sqlalchemy.orm import Session
from teacher_dashboard.Classes import class_crud
from teacher_dashboard.Classes.token_dependency import token_dependency
from teacher_dashboard.Students import student_crud
from teacher_dashboard.database import SessionLocal, engine
from teacher_dashboard import models
from teacher_dashboard.models import Classes, Students
from pathlib import Path
import json
import random
from starlette import status
from teacher_dashboard.Classes.classes import add_relation
import logging
from fastapi import BackgroundTasks


logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.rosters.readonly',
          'https://www.googleapis.com/auth/classroom.profile.emails']
router = APIRouter(
    tags=["Classes"],
    responses={500: {"description": "Not found"}},
)
models.Base.metadata.create_all(bind=engine)
# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



base_dir = Path(__file__).resolve().parent
cred_path = os.path.join(base_dir, 'credentials.json')
token_path = os.path.join(base_dir, 'token.json')
static_courses = os.path.join(base_dir, 'static_courses.json')
static_students = os.path.join(base_dir, 'static_students.json')


def google_classroom_courses(teacher_id: str, fetch_students: bool, db: Session = Depends(get_db),):

    logger.debug('Fetching courses from google classroom')
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('classroom', 'v1', credentials=creds)

    # Call the Classroom API
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])
    print(courses)
    
    # print(courses)

    courses_list = []
    if len(courses) == 0:
        return []
    for course in courses:
        courses_list.append({})
        courses_list[-1]['google_id'] = course['id']
        courses_list[-1]['name'] = course['name']

        if class_crud.get_teacher_classes_by_google_id(db=db, teacher_id=teacher_id, google_id=course['id']) is not None:
            courses_list[-1]['status'] = 'connected'
        else:
            courses_list[-1]['status'] = 'not_connected'

        if fetch_students == False:
            continue

        students=service.courses().students().list(courseId=course['id'], pageSize=100).execute()
        students=students.get('students',[])

        allStudents = []
        for student in students:
            name = student['profile']['name']['fullName'].split(" ")
            student_dict = {}
            student_dict['firstname'] = ""
            student_dict['lastname'] = ""

            if len(name) >= 1:
                student_dict['firstname'] = name[0]
            if len(name) > 1:
                student_dict['lastname'] = name[-1]


            student_dict['email'] = student['profile']['emailAddress']
            # print(student)

            allStudents.append(student_dict)

        courses_list[-1]['students'] = allStudents

    # print(courses_list)
    return courses_list


@router.get('/api/v1/classes/gclassroom/list/all', dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def list_google_courses(teacher_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):

    logger.debug("data recieved : user_id: {}".format(teacher_id))
    courses_list = google_classroom_courses(
        teacher_id, db=db, fetch_students=True)
    if len(courses_list) == 0:
        return {"msg": "No Courses Found"}

    logger.debug("response : {}".format(courses_list))
    return courses_list


@router.post('/api/v1/classes/gclassroom/connect/selected', dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def connect_google_courses(background_task: BackgroundTasks, teacher_name: str = Depends(token_dependency.get_display_name), teacher_id: str = Depends(token_dependency.get_user_id), course_ids: Optional[List[str]] = Query(None), db: Session = Depends(get_db)):

    logger.debug("data recieved : teacher_id: {}, google_course_ids:{}".format(
        teacher_id, course_ids))
    courses_list = google_classroom_courses(
        teacher_id, db=db, fetch_students=True)
    if len(course_ids) == 0:
        return {"msg": "No class selected"}

    created_courses = []
    for course in courses_list:
        if course['status'] == 'connected':
            continue
        if course['google_id'] not in course_ids:
            continue

        logger.debug("connecting classes to google classroom")
        Class = Classes(
            name=course['name'], teacher_id=teacher_id, google_id=course['google_id'])
        class_response = class_crud.connect_google_class(db=db, Class=Class)

        logger.debug("Adding students from google classroom")
        student_uuid_list = []
        for student in course['students']:
            Student = Students(first_name=student['firstname'], last_name=student['lastname'],
                               password="", email=student['email'], class_id=class_response.id, parents_email="")
            _student = student_crud.create_student(
                db=db, Student=Student, background_task=background_task, teacher_name=teacher_name)
            student_uuid_list.append(_student.uuid)

        logger.debug("Addding parent child relation")
        add_relation(parent_user_id=teacher_id,
                     child_user_id_list=student_uuid_list)
        class_response.student_count = len(course['students'])
        created_courses.append(class_response)

    logger.debug("connected classes : {}".format(created_courses))
    return created_courses
