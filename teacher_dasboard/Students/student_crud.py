import datetime
import json
import random
import string
from pydantic.types import StrBytes
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import Null
from teacher_dasboard import models, schemas
from teacher_dasboard.Classes import class_crud
import requests

def generate_password(length: int):
    letters=string.ascii_letters
    password = ''.join(random.choice(letters) for i in range(length))
    return password

def get_students_by_class(db: Session, class_id: int):

    return db.query(models.Students).filter( models.Students.class_id == class_id).all()

def create_student(db: Session, Student: schemas.StudentsCreate):
    if len(Student.password)<6:
        Student.password=generate_password(8)
    
    query = 'select email from invited_user where email = '+"'"+str(Student.email)+"' ;"
    _email=db.execute(query)

    created_at=str(datetime.datetime.now())
    query = 'insert into invited_user (email,role,created_at) values '   
    query += '( '+"'"+str(Student.email)+"'"+', '+"'"+'student'+"'"+', '+"'"+created_at+"'"+' );'

    flag=False
    for row in _email:
        if row.email == str(Student.email) :
            flag=True
            break
        else:
            db.execute(query)
            db.commit()
    if flag==False:
        db.execute(query)
        db.commit()
        
    db.commit()
    db.close()

    url = "http://13.127.95.183:8000/api/v1/user"

    payload = json.dumps({
    "provider": "local",
    "email": str(Student.email),
    "display_name": Student.first_name+' '+Student.last_name,
    "password": Student.password,
    "token": "",
    "default_role": "student",
    "roles": [
        "student"
    ]
    })
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = response.json()
    
    uuid=""

    # print(response.status_code)
    # print(response.text)
    if response.status_code == 200:
        uuid=json_data['user_id']

    if uuid == "":
        query = 'select uuid from user where user.email = '+"'"+str(Student.email)+"'"+' ;'
        _uuid=db.execute(query)
        for row in _uuid:
                uuid=row.uuid
    

    db_student = models.Students(uuid=uuid,first_name=Student.first_name,last_name=Student.last_name,password=Student.password, email=Student.email,parents_email=Student.parents_email,class_id = Student.class_id)
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