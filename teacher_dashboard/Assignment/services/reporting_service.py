
from fastapi.exceptions import HTTPException
import requests
from urllib3.util import timeout
from teacher_dashboard.db_session import request_auth_token
from config.app_config import get_config


class ReportingService:
    base_url_parts = [get_config().REPORTING_SERVICE_URL,
                      "/api/v1/reporting/assignment"]
    
    base_url = "/".join(url.strip("/") for url in base_url_parts)
    timeout_sec = 500
    
    

    def get_overview(self, assignment_id: int, class_id: int = None):
        auth_token = request_auth_token.get()
        
        request_url = ReportingService.base_url + \
            "/overview?assignemnt_id={assignment_id}".format(
                assignment_id=assignment_id)

        if(class_id != None):
            request_url += "&class_id={class_id}".format(class_id=class_id)        

        headers = {"Authorization": "{} {}".format(
            auth_token.scheme, auth_token.credentials)}
        
        return self.api_get_call(request_url, headers)

    def api_get_call(self, request_url, headers):
        try:
            response = requests.get(
                request_url, headers=headers, timeout=ReportingService.timeout_sec)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            raise HTTPException(
                401, detail="Not able to access the insights of the class.")
        except requests.exceptions.ConnectionError as errc:
            raise HTTPException(
                401, detail="Not able to connect with the service.")
        except requests.exceptions.Timeout as errt:
            raise errt
        except requests.exceptions.RequestException as err:
            raise err


reporting_service = ReportingService()
