from os import name
import random
import string
from typing import List, Optional
from fastapi import Depends, HTTPException, APIRouter,File, UploadFile,Request
from fastapi.param_functions import Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true
from starlette import status
from teacher_dasboard import models, schemas
from teacher_dasboard.database import SessionLocal, engine
from teacher_dasboard.Classes import class_crud,TokenDependency
from teacher_dasboard.Students import student_crud
import pandas as pd
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
models.Base.metadata.create_all(bind=engine)
token_dependency = TokenDependency.token_dependency

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
    if(re.fullmatch(regex, email)):
        return True
    return False
    
def generate_password(length: int):
    letters=string.ascii_letters
    password = ''.join(random.choice(letters) for i in range(length))
    return password


@router.post("/api/v1/classes", dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def create_class( name:str, teacher_id:str = Depends(token_dependency.get_user_id ), db: Session = Depends(get_db)):
    Class=schemas.ClassesCreate(name=name,teacher_id=teacher_id)
    return class_crud.create_class(db=db, Class=Class)

@router.get("/api/v1/classes/all", dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def get_classes_by_teacher_id(teacher_id:str = Depends(token_dependency.get_user_id ), db: Session = Depends(get_db)):
    classes = class_crud.get_my_classes(db=db,teacher_id=teacher_id)
    return classes


@router.get("/api/v1/classes/all/details", dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def get_all_classes_and_all_students(teacher_id:str = Depends(token_dependency.get_user_id ), db: Session = Depends(get_db)):
    classes = class_crud.get_my_classes(db=db,teacher_id=teacher_id)
    responseObject=[]
    for _class in classes:
        students=student_crud.get_students_by_class(db,_class.id)
        _students=[]
        class_dict=_class.__dict__
        for student in students:
            student.__delattr__('password')
            _students.append(student)
        class_dict['students']=_students
        responseObject.append(class_dict)
    return responseObject


@router.get("/api/v1/classes/id={class_id}", response_model=schemas.Classes )
async def get_class_by_class_id(class_id: int, db: Session = Depends(get_db)):
    db_class = class_crud.get_class_by_id(db, class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@router.get("/api/v1/classes/code={class_code}", response_model=schemas.Classes )
async def get_class_by_class_code(class_code: str, db: Session = Depends(get_db)):
    db_class = class_crud.get_class_by_code(db, class_code=class_code)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@router.get("/api/v1/classes/name={name}", response_model=List[schemas.Classes] )
async def get_class_by_name(name: str, db: Session = Depends(get_db)):
    db_class = class_crud.get_class_by_name(name,db)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class


@router.get("/api/v1/classes/{class_id}/students/all" , dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def get_students(class_id: int, teacher_id:str = Depends(token_dependency.get_user_id ), db: Session = Depends(get_db)):
  
    if class_crud.get_teachers_class(db,teacher_id,class_id) is not None:
        db_students = student_crud.get_students_by_class(db, class_id=class_id)
        if db_students is None:
            raise HTTPException(status_code=404, detail="No students found")
        return db_students
    else:
        raise HTTPException(status_code=401, detail='Invalid Request')

@router.delete("/api/v1/classes/{class_id}/students/delete/{student_id}", dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def del_student(class_id: int, student_id=int, teacher_id:str = Depends(token_dependency.get_user_id ), db: Session = Depends(get_db)):
    if class_crud.get_teachers_class(db=db,teacher_id=teacher_id,class_id=class_id) is not None:
        affected_rows = student_crud.delete_class_student(db, class_id=class_id,student_id=student_id)
    else:
        raise HTTPException(status_code=401, detail='Invalid Request')
    return {"message": str(affected_rows)+" Students deleted."}

@router.put("/api/v1/classes/upload/spreadsheet", dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def upload_student_spreadsheet_to_selected_classes(teacher_id:str = Depends(token_dependency.get_user_id ),class_id: Optional[List[str]]=Query(None), file: UploadFile = File( default="abc.csv"), db: Session = Depends(get_db)):
    extension=file.content_type
    if extension not in ['text/csv','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] :
        raise HTTPException(status_code=500, detail='Uploaded file is not a spreadsheet')
    data= await file.read()
    Students=[]
    try:
        if extension =='text/csv':
            Students=pd.read_csv(data)
        else:
            Students=pd.read_excel(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Something went wrong while parsing the spreadsheet')

    if len(Students)>200:
        raise HTTPException(status_code=500, detail='You can add only 200 students at once.')

    student_count=0
    valid_students=[]
    for index,student in Students.iterrows():
        if str(student['First name'])!="nan" and str(student['Last name'])!="nan" and str(student['Email address'])!="nan" and check(str(student['Email address'])):
            student_count+=1
            if len(str(student['Password']))<6:
                student['Password']=generate_password(8)
            valid_students.append(student)
            continue
        elif str(student['First name'])=="nan" and str(student['Last name'])=="nan" and str(student['Email address'])=="nan" :
            continue 
        else:
            invalid_columns=''
            if str(student['First name'])=="nan":
                invalid_columns+='First name'

            if str(student['Last name'])=="nan":
                if invalid_columns!='':
                    invalid_columns+=', '
                invalid_columns+='Last name'

            if str(student['Email address'])=="nan":
                if invalid_columns!='':
                    invalid_columns+=', '
                invalid_columns+='Email'

            raise HTTPException(status_code=500, detail= 'We were not able to process the spreadsheet. Check that you have filled the '+invalid_columns+' column and upload again.')    

    response={}
    response['updated_classes']=[]
    response['students']=[]
    flag=False
    for id in class_id:
        db_class=class_crud.get_teachers_class(db=db,teacher_id=teacher_id,class_id=id)
        if  db_class is None:
            continue
        class_crud.update_editTime(db=db,class_id=id)
        
        response['updated_classes'].append({'id':db_class.id,'name':db_class.name})
        
        for student in valid_students:
            db_student = models.Students(first_name=str(student['First name']),last_name=str(student['Last name']), email=str(student['Email address']),password=str(student['Password']),parents_email=str(student['Parent email']),class_id = id)
            db_student=student_crud.create_student(db=db,Student=db_student)
            if flag:
                continue
            db_student.__delattr__('password')
            db_student.__delattr__('id')
            db_student.__delattr__('class_id')
            response['students'].append(db_student)
        flag=True 

    return response


@router.post("/api/v1/classes/upload/spreadsheet", dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def create_class_and_upload_spreadsheet(class_name: str,teacher_id:str = Depends(token_dependency.get_user_id ), file: UploadFile = File( default="abc.csv"), db: Session = Depends(get_db)):
    extension=file.content_type
    if extension not in ['text/csv','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] :
        raise HTTPException(status_code=500, detail='Uploaded file is not a spreadsheet')
    data= await file.read()
    Students=[]
    try:
        if extension =='text/csv':
            Students=pd.read_csv(data)
        else:
            Students=pd.read_excel(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Something went wrong while parsing the spreadsheet')

    if len(Students)>200:
        raise HTTPException(status_code=500, detail='You can add only 200 students at once.')

    student_count=0
    valid_students=[]
    for index,student in Students.iterrows():
        if str(student['First name'])!="nan" and str(student['Last name'])!="nan" and str(student['Email address'])!="nan" and check(str(student['Email address'])):
            student_count+=1
            valid_students.append(student)
            continue
        elif str(student['First name'])=="nan" and str(student['Last name'])=="nan" and str(student['Email address'])=="nan" :
            continue 
        else:
            invalid_columns=''
            if str(student['First name'])=="nan":
                invalid_columns+='First name'

            if str(student['Last name'])=="nan":
                if invalid_columns!='':
                    invalid_columns+=', '
                invalid_columns+='Last name'

            if str(student['Email address'])=="nan":
                if invalid_columns!='':
                    invalid_columns+=', '
                invalid_columns+='Email'

            raise HTTPException(status_code=500, detail= 'We were not able to process the spreadsheet. Check that you have filled the '+invalid_columns+' column and upload again.')    

    new_class=class_crud.create_class(db,schemas.ClassesCreate(name=class_name,teacher_id=teacher_id))

    new_class.student_count=student_count
    response={}
    response['class']=new_class
    response['students']=[]
    for student in valid_students:
        db_student = models.Students(first_name=str(student['First name']),last_name=str(student['Last name']), email=str(student['Email address']),password=str(student['Password']),parents_email=str(student['Parent email']),class_id = new_class.id)
        db_student=student_crud.create_student(db=db,Student=db_student)
        db_student.__delattr__('password')
        response['students'].append(db_student)

    return response


@router.delete("/api/v1/classes/delete/{class_id}" , dependencies=[Depends(token_dependency.validate_token),Depends(token_dependency.role_teacher)])
async def del_class(class_id: int, teacher_id:str = Depends(token_dependency.get_user_id ), db: Session = Depends(get_db)):

    if class_crud.get_teachers_class(db,teacher_id,class_id) is not None:
        affected_rows = class_crud.delete_class(db, class_id=class_id)
    else:
        raise HTTPException(status_code=401, detail='Invalid Request')
    return {"message": str(affected_rows)+" Class deleted."}

