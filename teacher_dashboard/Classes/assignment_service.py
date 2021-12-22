import requests
from fastapi.exceptions import HTTPException
from teacher_dashboard.Classes.schemas import ClassStudentsRequest
from teacher_dashboard.db_session import request_auth_token
from config.app_config import get_config

class AssignmentService:
    base_url_parts = [get_config().TEACHER_DASHBOARD_URL, "/api/v1/assignment"]
    
    base_url = "/".join(url.strip("/") for url in base_url_parts)
    timeout_sec = 500

    def add_students(self, students_request_body):
        auth_token = request_auth_token.get()
        request_url = AssignmentService.base_url + "/add-students"
        headers = {"Authorization": "{} {}".format(
            auth_token.scheme, auth_token.credentials)}
        body = students_request_body

        return self.api_post_call(request_url, headers, body)

    def delete_students(self, students_request_body):
        auth_token = request_auth_token.get()
        request_url = AssignmentService.base_url + "/delete-students"
        headers = {"Authorization": "{} {}".format(
            auth_token.scheme, auth_token.credentials)}
        body = students_request_body

        return self.api_post_call(request_url, headers, body)

    def api_post_call(self, request_url, headers, body):
        try:
            response = requests.post(
                request_url, headers=headers, data=body.json(), timeout=AssignmentService.timeout_sec)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            raise HTTPException(
                401, detail="Not authorized to connect with the service")
        except requests.exceptions.ConnectionError as errc:
            raise HTTPException(
                401, detail="Not able to connect with the service")
        except requests.exceptions.Timeout as errt:
            raise errt
        except requests.exceptions.RequestException as err:
            raise err


assignment_service = AssignmentService()
