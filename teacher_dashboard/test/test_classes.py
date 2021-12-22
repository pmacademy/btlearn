from fastapi.testclient import TestClient
import json
import requests
from main import app
from pathlib import Path
import os
from config.app_config import get_config

client = TestClient(app)
base_dir = Path(__file__).resolve().parent


def get_new_token():
    url = get_config().AUTH_URL + "/api/v1/user/login"

    payload = json.dumps({
        "provider": "local",
        "email": 'test.teacher@bytelearn.ai',
        "password": 'password',
        "token": "",
    })

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = response.json()
    # print(json_data['access_token'])
    if 'access_token' not in json_data:
        raise Exception(json.dumps(json_data))

    return json_data['access_token']

test_client_token = 'bearer '+get_new_token()
def test_create_class():
    
    response = client.post(
        "/api/v1/classes", params={'name': 'test_class'}, headers={'Authorization': test_client_token})
    assert response.status_code == 200
    assert 'name' in response.json()
    assert response.json()['name'] == 'test_class'


def test_create_class_not_authenticated():
    response = client.post("/api/v1/classes", params={'name': 'test_class'})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_class_bad_token():
    response = client.post(
        "/api/v1/classes", params={'name': 'test_class'}, headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_all_classes():
    response = client.get("/api/v1/classes/all",
                          headers={'Authorization': test_client_token})
    assert response.status_code == 200

    if len(response.json()) == 0:
        assert response.json() == []

    for _class in response.json():
        assert 'id' in _class
        assert 'code' in _class


def test_get_all_classes_not_authenticated():
    response = client.get("/api/v1/classes/all")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_all_classes_bad_token():
    response = client.get("/api/v1/classes/all",
                          headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_all_classes_and_all_students():
    response = client.get("/api/v1/classes/all/details",
                          headers={'Authorization': test_client_token})
    assert response.status_code == 200

    if len(response.json()) == 0:
        assert response.json() == []

    for _class in response.json():
        assert 'code' in _class
        assert 'students' in _class


def test_get_all_classes_and_all_students_not_authenticated():
    response = client.get("/api/v1/classes/all/details")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_all_classes_and_all_students_bad_token():
    response = client.get("/api/v1/classes/all/details",
                          headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_class_by_class_id():    
    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    classes = get_response.json()

    class_id = -1
    if len(classes) == 0:
        class_id = client.post(
            '/api/v1/classes', params={'name': 'test_class1'}, headers={'Authorization': test_client_token}).json()['id']

    class_id = classes[-1]['id']
    response = client.get("/api/v1/classes/id=" +
                          str(class_id), headers={'Authorization': test_client_token})

    assert response.status_code == 200
    assert 'id' in response.json()
    assert response.json()['id'] == class_id


def test_get_class_by_class_id_bad_request():
    response = client.get("/api/v1/classes/id=-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Class not found"}


def test_get_class_by_class_code():
    
    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    classes = get_response.json()

    class_code = ''
    if len(classes) == 0:
        class_code = client.post(
            '/api/v1/classes', params={'name': 'test_class2'}, headers={'Authorization': test_client_token}).json()['code']

    class_code = classes[-1]['code']

    response = client.get("/api/v1/classes/code=" +
                          str(class_code), headers={'Authorization': test_client_token})

    assert response.status_code == 200
    assert 'code' in response.json()
    assert response.json()['code'] == class_code


def test_get_class_by_class_code_bad_request():
    response = client.get("/api/v1/classes/code=hsa8hk")
    assert response.status_code == 404
    assert response.json() == {"detail": "Class not found"}


# test_upload_spreadsheet

def test_upload_spreadsheet_to_multiple_classes():

    class_ids = []
    class_ids.append(client.post(
        '/api/v1/classes', params={'name': 'test_spreadsheet1'}, headers={'Authorization': test_client_token}).json()['id'])

    class_ids.append(client.post(
        '/api/v1/classes', params={'name': 'test_spreadsheet2'}, headers={'Authorization': test_client_token}).json()['id'])

    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': class_ids}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 200
    assert 'updated_classes' in response.json()
    assert 'students' in response.json()


def test_upload_spreadsheet_to_multiple_classes_non_spreadsheet():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.pdf", f, "application/pdf")}, params={'class_id': '123'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {'detail': 'Uploaded file is not a spreadsheet'}


def test_upload_spreadsheet_to_multiple_classes_bad_format():
    spreadsheet_path = os.path.join(base_dir, 'students_bad_format.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_bad_format.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': '123'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'We were not able to process the spreadsheet. Check that you have filled the Email column and upload again.'}


def test_upload_spreadsheet_to_multiple_classes_missing_columns():
    spreadsheet_path = os.path.join(base_dir, 'students_invalid_columns.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_invalid_columns.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': '123'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert 'parse_error' in response.json()['detail']
    assert 'missing_columns' in response.json()['detail']
    assert 'Email' in response.json()['detail']['missing_columns']


def test_upload_spreadsheet_to_multiple_classes_excess_data():
    spreadsheet_path = os.path.join(base_dir, 'students_excess_data.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_excess_data.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': '123'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'You can add only 200 students at once.'}


def test_upload_spreadsheet_to_multiple_classes_duplicate_emails():
    spreadsheet_path = os.path.join(base_dir, 'students_duplicate_emails.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_duplicate_emails.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': '123'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'Duplicate entries found for this email - {}'.format('test@bytelearn.ai')}



def test_upload_spreadsheet_to_multiple_classes_existing_student():
    
    class_ids = []
    class_response = client.post(
        '/api/v1/classes', params={'name': 'test_spreadsheet1'}, headers={'Authorization': test_client_token}).json()
    
    class_name = class_response['name']
    class_ids.append(class_response['id'])

    spreadsheet_path = os.path.join(base_dir, 'students1.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': class_ids}, headers={'Authorization': test_client_token})
        f.close()

    assert response.status_code == 200
    assert 'updated_classes' in response.json()
    assert 'students' in response.json()

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': class_ids}, headers={'Authorization': test_client_token})
        f.close()

    assert response.status_code == 422
    assert response.json() == { "detail": 'A student with email id - {} is already registered for this class - {}'.format("st1@test.xyz",class_name)}


def test_upload_spreadsheet_to_multiple_classes_not_authenticated():
    response = client.put("/api/v1/classes/upload/spreadsheet")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_upload_spreadsheet_to_multiple_classes_bad_token():
    response = client.put("/api/v1/classes/upload/spreadsheet",
                          headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


# test_create_and_upload_spreadsheet


def test_create_class_and_upload_spreadsheet():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.post("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'Test_class'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 200
    assert 'class' in response.json()
    assert 'students' in response.json()


def test_create_class_and_upload_spreadsheet_non_spreadsheet():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.post("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students.pdf", f, "application/pdf")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {'detail': 'Uploaded file is not a spreadsheet'}


def test_create_class_and_upload_spreadsheet_bad_format():
    spreadsheet_path = os.path.join(base_dir, 'students_bad_format.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.post("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_bad_format.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'We were not able to process the spreadsheet. Check that you have filled the Email column and upload again.'}


def test_create_class_and_upload_spreadsheet_missing_columns():
    spreadsheet_path = os.path.join(base_dir, 'students_invalid_columns.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.post("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_invalid_columns.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert 'parse_error' in response.json()['detail']
    assert 'missing_columns' in response.json()['detail']
    assert 'Email' in response.json()['detail']['missing_columns']


def test_create_class_and_upload_spreadsheet_excess_data():
    spreadsheet_path = os.path.join(base_dir, 'students_excess_data.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.post("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_excess_data.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'You can add only 200 students at once.'}


def test_create_class_and_upload_spreadsheet_duplicate_emails():
    spreadsheet_path = os.path.join(base_dir, 'students_duplicate_emails.xlsx')

    with open(spreadsheet_path, 'rb') as f:
        response = client.put("/api/v1/classes/upload/spreadsheet", files={'file': (
            "students_duplicate_emails.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_id': '123'}, headers={'Authorization': test_client_token})
        f.close()
    assert response.status_code == 422
    assert response.json() == {
        'detail': 'Duplicate entries found for this email - {}'.format('test@bytelearn.ai')}


def test_create_class_and_upload_spreadsheet_not_authenticated():
    response = client.post("/api/v1/classes/upload/spreadsheet")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_class_and_upload_spreadsheet_bad_token():
    response = client.post("/api/v1/classes/upload/spreadsheet",
                           headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_class_students():
    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    assert get_response.status_code == 200
    classes = get_response.json()

    class_id = -1
    if len(classes) == 0:
        class_response = client.post(
            '/api/v1/classes', params={'name': 'test'}, headers={'Authorization': test_client_token})
        assert class_response.status_code == 200
        class_id = class_response.json()['id']

    class_id = classes[-1]['id']

    response = client.get('/api/v1/classes/'+str(class_id) +
                          '/students/all', headers={'Authorization': test_client_token})

    assert response.status_code == 200
    if len(response.json()) == 0:
        assert response.json() == []

    for student in response.json():
        assert 'uuid' in student
        assert 'class_id' in student
        assert student['class_id'] == class_id


def test_get_class_students_not_authenticated():
    response = client.get("/api/v1/classes/1/students/all")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_class_students_bad_token():
    response = client.get("/api/v1/classes/1/students/all",
                          headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_get_class_students_unauthorized_request():
    response = client.get("/api/v1/classes/-1/students/all",
                          headers={'Authorization': test_client_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_rename_class_student():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')
    
    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    assert get_response.status_code == 200
    classes = get_response.json()

    if len(classes) == 0:
        with open(spreadsheet_path, 'rb') as f:
            class_response = client.post('/api/v1/classes/upload/spreadsheet', files={'file': (
                "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
            assert class_response.status_code == 200
            class_id = class_response.json()['class']['id']
            f.close()
    else:
        class_id = classes[-1]['id']

    students_response = client.get(
        '/api/v1/classes/'+str(class_id)+'/students/all', headers={'Authorization': test_client_token})
    assert students_response.status_code == 200
    student_id = students_response.json()[0]['id']
    uuid = students_response.json()[0]['uuid']
    
    response = client.put('/api/v1/classes/'+str(class_id) +
                             '/students/rename/'+str(student_id), params={'first_name':'renamed','last_name':'renamed'}, headers={'Authorization': test_client_token})

    assert response.status_code == 200
    assert 'uuid' in response.json() and response.json()['uuid'] == uuid
    assert 'first_name' in response.json() and response.json()['first_name'] == 'renamed'
    assert 'last_name' in response.json() and response.json()['last_name'] == 'renamed'

def test_rename_class_student_not_authenticated():
    response = client.put("/api/v1/classes/1/students/rename/4")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_rename_class_student_bad_token():
    response = client.put("/api/v1/classes/1/students/rename/4",
                             headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_rename_class_student_unauthorized_request():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')
    
    response = client.put(
        "/api/v1/classes/-10/students/rename/46", params={'first_name':'renamed','last_name':'renamed'}, headers={'Authorization': test_client_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    assert get_response.status_code == 200
    classes = get_response.json()

    if len(classes) == 0:
        with open(spreadsheet_path, 'rb') as f:
            class_response = client.post('/api/v1/classes/upload/spreadsheet', files={'file': (
                "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
            print(class_response.text)
            assert class_response.status_code == 200
            class_id = class_response.json()['class']['id']
            f.close()
    else:
        class_id = classes[-1]['id']

    response = client.put('/api/v1/classes/'+str(class_id) +
                             '/students/rename/-10', params={'first_name':'renamed','last_name':'renamed'}, headers={'Authorization': test_client_token})

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_del_class_student():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')
    
    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    assert get_response.status_code == 200
    classes = get_response.json()

    if len(classes) == 0:
        with open(spreadsheet_path, 'rb') as f:
            class_response = client.post('/api/v1/classes/upload/spreadsheet', files={'file': (
                "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
            assert class_response.status_code == 200
            class_id = class_response.json()['class']['id']
            f.close()
    else:
        class_id = classes[-1]['id']

    students_response = client.get(
        '/api/v1/classes/'+str(class_id)+'/students/all', headers={'Authorization': test_client_token})
    assert students_response.status_code == 200
    student_id = students_response.json()[0]['id']
    response = client.delete('/api/v1/classes/'+str(class_id) +
                             '/students/delete/'+str(student_id), headers={'Authorization': test_client_token})

    assert response.status_code == 200
    assert response.json() == {"msg": '1 student deleted.'}


def test_del_class_student_not_authenticated():
    response = client.delete("/api/v1/classes/1/students/delete/4")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_del_class_student_bad_token():
    response = client.delete("/api/v1/classes/1/students/delete/4",
                             headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_del_class_student_unauthorized_request():
    spreadsheet_path = os.path.join(base_dir, 'students.xlsx')
    
    response = client.delete(
        "/api/v1/classes/-10/students/delete/46", headers={'Authorization': test_client_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    get_response = client.get('/api/v1/classes/all',
                              headers={'Authorization': test_client_token})
    assert get_response.status_code == 200
    classes = get_response.json()

    if len(classes) == 0:
        with open(spreadsheet_path, 'rb') as f:
            class_response = client.post('/api/v1/classes/upload/spreadsheet', files={'file': (
                "students.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, params={'class_name': 'test'}, headers={'Authorization': test_client_token})
            assert class_response.status_code == 200
            class_id = class_response.json()['class']['id']
            f.close()
    else:
        class_id = classes[-1]['id']

    response = client.delete("/api/v1/classes/"+str(class_id) +
                             "/students/delete/-10", headers={'Authorization': test_client_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_del_class():
    response = client.get("/api/v1/classes/all",
                          headers={'Authorization': test_client_token})
    assert response.status_code == 200
    classes = response.json()

    for _class in classes:
        response = client.delete(
            "/api/v1/classes/delete/"+str(_class['id']), headers={'Authorization': test_client_token})
        assert response.status_code == 200
        assert response.json() == {"msg": "1 class deleted."}


def test_del_class_unauthorized_request():
    response = client.delete("/api/v1/classes/delete/-1",
                             headers={'Authorization': test_client_token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_del_class_not_authenticated():
    response = client.delete("/api/v1/classes/delete/1")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_del_class_bad_token():
    response = client.delete("/api/v1/classes/delete/1",
                             headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}
