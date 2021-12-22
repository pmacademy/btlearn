import datetime
from fastapi.testclient import TestClient
import json
import requests
from sqlalchemy.sql.expression import true
from main import app
from pathlib import Path
from teacher_dashboard.Constants.test_constants import TestConstants
import os

client = TestClient(app)
base_dir = Path(__file__).resolve().parent


class Constants:
    test_class_id: int
    test_assignment_id: int


def get_new_token(email: str, password: str):
    login_url = TestConstants.LOGIN_URL

    payload = json.dumps({
        "provider": "local",
        "email": email,
        "password": password,
        "token": "",
    })

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", login_url, headers=headers, data=payload)
    json_data = response.json()
    # print(json_data['access_token'])
    if 'access_token' not in json_data:
        raise Exception(json.dumps(json_data))

    return json_data['access_token']


def test_create_assignment():
    token = 'bearer ' + get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                      password=TestConstants.TEST_TEACHER_PASSWORD)
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.post("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'Test_class'}, headers={'Authorization': token})
        f.close()
    assert response.status_code == 200
    Constants.test_class_id = response.json()['class']['id']
    new_assignment = json.dumps({
        "title": "test_assignment",
        "classes": [
            {
                "class_id": Constants.test_class_id
            }
        ],
        "topics": [
            {
                "cluster_id": "string",
                "topic_code": "5",
                "topic_sequence_num": 0,
                "tutor_available": "available",
                "questions": [
                    {
                        "question_id": "7.EE-1-010-01-1",
                        "sequence_num": 0,
                        "tutor_available": "available"
                    }
                ]
            }
        ],
        "is_published": False,
        "submission_last_date": str(datetime.datetime.now()+datetime.timedelta(hours=5))
    })
    response = client.post(
        "/api/v1/assignment", data=new_assignment, headers={'Authorization': token})

    print(response)
    assert response.status_code == 200
    print(response.json())
    assert 'id' in response.json()
    Constants.test_assignment_id = response.json()['id']
    assert 'title' in response.json()
    assert response.json()['title'] == 'test_assignment'


def test_create_assignemnt_not_authenticated():
    new_assignment = json.dumps({
        "title": "test_assignment",
        "classes": [
            {
                "class_id": Constants.test_class_id
            }
        ],
        "topics": [
            {
                "cluster_id": "string",
                "topic_code": "5",
                "topic_sequence_num": 0,
                "tutor_available": "available",
                "questions": [
                    {
                        "question_id": "7.EE-1-010-01-1",
                        "sequence_num": 0,
                        "tutor_available": "available"
                    }
                ]
            }
        ],
        "is_published": False,
        "submission_last_date": str(datetime.datetime.now()+datetime.timedelta(hours=5))
    })
    response = client.post("/api/v1/assignment", data=new_assignment)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_assignemnt_bad_token():
    new_assignment = json.dumps({
        "title": "test_assignment",
        "classes": [
            {
                "class_id": Constants.test_class_id
            }
        ],
        "topics": [
            {
                "cluster_id": "string",
                "topic_code": 5,
                "topic_sequence_num": 0,
                "tutor_available": "available",
                "questions": [
                    {
                        "question_id": "7.EE-1-010-01-1",
                        "sequence_num": 0,
                        "tutor_available": "available"
                    }
                ]
            }
        ],
        "is_published": False,
        "submission_last_date": str(datetime.datetime.now()+datetime.timedelta(hours=5))
    })

    response = client.post("/api/v1/assignment", data=new_assignment,
                           headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_all_teacher_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    response = client.get("/api/v1/assignment/teacher/all",
                          headers={'Authorization': token})

    assert response.status_code == 200
    assert 'teacher_id' in response.json()
    assert 'published' in response.json()
    assert 'not_published' in response.json()


def test_get_all_teacher_assignment_not_authenticated():
    response = client.get("/api/v1/assignment/teacher/all")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_all_teacher_assignment_bad_token():
    response = client.get("/api/v1/assignment/teacher/all",
                          headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)

    response = client.get(
        "/api/v1/assignment/"+str(Constants.test_assignment_id), headers={'Authorization': token})
    assert response.status_code == 200
    assert 'id' in response.json()
    assert response.json()['id'] == Constants.test_assignment_id


def test_get_assignment_not_authenticated():
    response = client.get("/api/v1/assignment/" +
                          str(Constants.test_assignment_id))
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_assignment_bad_token():
    response = client.get("/api/v1/assignment/"+str(Constants.test_assignment_id),
                          headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_update_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    get_response = client.get(
        "/api/v1/assignment/"+str(Constants.test_assignment_id), headers={'Authorization': token})
    assert get_response.status_code == 200

    assignment = get_response.json()
    time = str(datetime.datetime.now()+datetime.timedelta(hours=12))
    assignment['submission_last_date'] = time
    assignment['classes'][0]['class_id'] = Constants.test_class_id
    assignment = json.dumps(assignment)

    print(assignment)
    response = client.put("/api/v1/assignment",
                          data=assignment, headers={'Authorization': token})
    assert response.status_code == 200
    assert 'submission_last_date' in response.json()
    assert response.json()['submission_last_date'][:10] == time[:10]


def test_update_assignemnt_not_authenticated():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    get_response = client.get(
        "/api/v1/assignment/"+str(Constants.test_assignment_id), headers={'Authorization': token})
    assert get_response.status_code == 200

    assignment = get_response.json()
    time = str(datetime.datetime.now()+datetime.timedelta(hours=12))
    assignment['submission_last_date'] = time
    assignment['classes'][0]['class_id'] = Constants.test_class_id
    assignment = json.dumps(assignment)

    response = client.post("/api/v1/assignment", data=assignment)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_update_assignemnt_bad_token():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    get_response = client.get(
        "/api/v1/assignment/"+str(Constants.test_assignment_id), headers={'Authorization': token})
    assert get_response.status_code == 200

    assignment = get_response.json()
    time = str(datetime.datetime.now()++datetime.timedelta(hours=12))
    assignment['submission_last_date'] = time
    assignment['classes'][0]['class_id'] = Constants.test_class_id
    assignment = json.dumps(assignment)

    response = client.post("/api/v1/assignment", data=assignment,
                           headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_copy_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)

    response = client.get("/api/v1/assignment/copy/" +
                          str(Constants.test_assignment_id), headers={'Authorization': token})
    assert response.status_code == 200
    assert 'id' in response.json()
    assert response.json()['classes'][0]['class_id'] == Constants.test_class_id


def test_copy_assignment_unauthorized():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    response = client.get("/api/v1/assignment/copy/-1",
                          headers={'Authorization': token})
    assert response.status_code == 401
    assert response.json() == {
        "detail": "No assignment exists with the given id"}


def test_copy_assignment_not_authenticated():
    response = client.get("/api/v1/assignment/copy/" +
                          str(Constants.test_assignment_id))
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_copy_assignment_bad_token():
    response = client.get("/api/v1/assignment/copy/"+str(
        Constants.test_assignment_id), headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_publish_status():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    data = json.dumps({
        "id": Constants.test_assignment_id,
        "is_published": True
    })
    response = client.post("/api/v1/assignment/publish-status",
                           data=data, headers={'Authorization': token})

    print(response.json())
    assert response.status_code == 200
    assert 'id' in response.json()
    assert response.json()['id'] == Constants.test_assignment_id
    assert 'is_published' in response.json()
    assert response.json()['is_published'] == 1


def test_publish_status_not_authenticated():
    data = json.dumps({
        "id": Constants.test_assignment_id,
        "is_published": True
    })
    response = client.post("/api/v1/assignment/publish-status", data=data)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_publish_status_bad_token():
    data = json.dumps({
        "id": Constants.test_assignment_id,
        "is_published": True
    })
    response = client.get("/api/v1/assignment/publish-status",
                          data=data, headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_all_student_active_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_STUDENT_EMAIL,
                                    password=TestConstants.TEST_STUDENT_PASSWORD)

    response = client.get("/api/v1/assignment/student/active",
                          params={'all': True}, headers={'Authorization': token})
    assert response.status_code == 200
    assert 'student_id' in response.json()
    assert 'assignments' in response.json()

    response = client.get("/api/v1/assignment/student/active",
                          params={'all': False}, headers={'Authorization': token})
    assert response.status_code == 200
    assert 'student_id' in response.json()
    assert 'assignments' in response.json()


def test_get_all_student_active_assignment_not_authenticated():
    response = client.get(
        "/api/v1/assignment/student/active", params={'all': True})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_all_student_active_assignment_bad_token():
    response = client.get("/api/v1/assignment/student/active",
                          params={'all': True}, headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_all_student_completed_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_STUDENT_EMAIL,
                                    password=TestConstants.TEST_STUDENT_PASSWORD)

    response = client.get("/api/v1/assignment/student/completed",
                          params={"start": 0, "limit": 10}, headers={'Authorization': token})

    assert response.status_code == 200
    assert 'student_id' in response.json()
    assert 'assignments' in response.json()


def test_get_all_student_completed_assignment_not_authenticated():
    response = client.get(
        "/api/v1/assignment/student/completed", params={"start": 0, "limit": 10})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_all_student_completed_assignment_bad_token():
    response = client.get("/api/v1/assignment/student/completed", params={
                          "start": 0, "limit": 10}, headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_student_get_assignment_question():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_STUDENT_EMAIL,
                                    password=TestConstants.TEST_STUDENT_PASSWORD)

    response = client.get("/api/v1/assignment/"+str(Constants.test_assignment_id) +
                          "/question", headers={'Authorization': token})
    
    print(response.json())
    assert response.status_code == 200
    assert 'question_id' in response.json()
    assert 'total_questions' in response.json()


def test_student_get_assignment_question_unauthorized():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_STUDENT_EMAIL,
                                    password=TestConstants.TEST_STUDENT_PASSWORD)
    response = client.get("/api/v1/assignment/-1/question",
                          headers={'Authorization': token})
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not able to find assignment assigned to the student"}


def test_student_get_assignment_question_not_authenticated():
    response = client.get("/api/v1/assignment/" +
                          str(Constants.test_assignment_id)+"/question")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_student_get_assignment_question_bad_token():
    response = client.get("/api/v1/assignment/"+str(Constants.test_assignment_id) +
                          "/question", headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_student_complete_assignment_question():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_STUDENT_EMAIL,
                                    password=TestConstants.TEST_STUDENT_PASSWORD)

    response = client.post("/api/v1/assignment/"+str(Constants.test_assignment_id) +
                           "/question/complete", params={"status": "correct"}, headers={'Authorization': token})
    
    print(response.json())
    assert response.status_code == 200
    assert 'question_id' in response.json()
    assert 'total_questions' in response.json()


def test_student_complete_assignment_question_unauthorized():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_STUDENT_EMAIL,
                                    password=TestConstants.TEST_STUDENT_PASSWORD)
    response = client.post("/api/v1/assignment/-1/question/complete",
                           params={"status": "correct"}, headers={'Authorization': token})
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not able to find assignment assigned to the student"}


def test_student_complete_assignment_question_not_authenticated():
    response = client.post("/api/v1/assignment/"+str(Constants.test_assignment_id) +
                           "/question/complete", params={"status": "correct"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_student_complete_assignment_question_bad_token():
    response = client.post("/api/v1/assignment/"+str(Constants.test_assignment_id)+"/question/complete",
                           params={"status": "correct"}, headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_delete_assignment():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)
    get_response = client.get(
        "/api/v1/assignment/teacher/all", headers={'Authorization': token})
    assert get_response.status_code == 200

    for assignment in get_response.json()['published']:
        response = client.delete(
            "/api/v1/assignment/"+str(assignment['id']), headers={'Authorization': token})
        assert response.status_code == 200
        assert response.json()['detail'] == "resource deleted successfully"

    for assignment in get_response.json()['not_published']:
        response = client.delete(
            "/api/v1/assignment/"+str(assignment['id']), headers={'Authorization': token})
        assert response.status_code == 200
        assert response.json()['detail'] == "resource deleted successfully"


def test_delete_assignment_unauthorized_request():
    token = 'bearer '+get_new_token(email=TestConstants.TEST_TEACHER_EMAIL,
                                    password=TestConstants.TEST_TEACHER_PASSWORD)

    response = client.delete("/api/v1/assignment/0",
                             headers={'Authorization': token})
    assert response.status_code == 401
    assert (response.json() == {"detail": "Not Authorized"} or response.json() == {
            "detail": "No assignment exists with the given id"})


def test_delete_assignment_not_authenticated():
    response = client.delete("/api/v1/assignment/0")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_assignment_bad_token():
    response = client.delete("/api/v1/assignment/0",
                             headers={'Authorization': "bearer bad_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}
