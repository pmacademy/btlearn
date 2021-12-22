from fastapi.testclient import TestClient
import json
import requests
from main import app
from pathlib import Path
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
    print(json_data['access_token'])
    if 'access_token' not in json_data:
        raise Exception(json.dumps(json_data))

    return json_data['access_token']


def test_list_google_courses():
    token = 'bearer '+get_new_token()
    response = client.get("/api/v1/classes/gclassroom/list/all",
                          headers={"Authorization": token})
    assert response.status_code == 200
    for course in response.json():
        assert 'google_id' in course


def test_list_google_courses_not_authenticated():
    response = client.get("/api/v1/classes/gclassroom/list/all")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_list_google_courses_bad_token():
    response = client.get("/api/v1/classes/gclassroom/list/all",
                          headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_connect_google_courses():

    token = 'bearer '+get_new_token()
    response = client.get("/api/v1/classes/gclassroom/list/all",
                          headers={'Authorization': token})
    assert response.status_code == 200
    courses = response.json()

    course_ids = []
    for course in courses:
        if len(course_ids) >= 2:
            break
        course_ids.append(course['google_id'])

    response = client.post("/api/v1/classes/gclassroom/connect/selected",
                           params={'course_ids': course_ids}, headers={"Authorization": token})
    assert response.status_code == 200
    for _course in response.json():
        assert 'status' in _course
        assert _course['status'] == 'connected'


def test_connect_google_courses_not_authenticated():
    response = client.post("/api/v1/classes/gclassroom/connect/selected")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_connect_google_courses_bad_token():
    response = client.post("/api/v1/classes/gclassroom/connect/selected",
                           headers={'Authorization': 'bearer bad_token'})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_del_class():
    token = 'bearer '+get_new_token()
    response = client.get("/api/v1/classes/all",
                          headers={'Authorization': token})
    assert response.status_code == 200
    classes = response.json()

    for _class in classes:
        response = client.delete(
            "/api/v1/classes/delete/"+str(_class['id']), headers={'Authorization': token})
        assert response.status_code == 200
        assert response.json() == {"msg": "1 class deleted."}
