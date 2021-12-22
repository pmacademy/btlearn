from fastapi.exceptions import HTTPException
import requests
from urllib3.util import timeout
from teacher_dashboard.db_session import request_auth_token
from config.app_config import get_config


class ClassroomService:
    base_url_parts = [get_config().TEACHER_DASHBOARD_URL, "/api/v1/classes"]
    
    base_url = "/".join(url.strip("/") for url in base_url_parts)
    timeout_sec = 500

    def get_students(self, class_id: int):
        auth_token = request_auth_token.get()
        request_url = ClassroomService.base_url + \
            "/{class_id}/students/all".format(class_id=class_id)
        headers = {"Authorization": "{} {}".format(
            auth_token.scheme, auth_token.credentials)}
        return self.api_get_call(request_url, headers)

    def validate_class(self, class_id: int):
        pass

    def validate_teacher(self):
        pass

    def api_get_call(self, request_url, headers):
        try:
            response = requests.get(
                request_url, headers=headers, timeout=ClassroomService.timeout_sec)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            raise HTTPException(
                401, detail="Not authorized to access the class")
        except requests.exceptions.ConnectionError as errc:
            raise HTTPException(
                401, detail="Not able to connect with the service")
        except requests.exceptions.Timeout as errt:
            raise errt
        except requests.exceptions.RequestException as err:
            raise err


classroom_service = ClassroomService()
