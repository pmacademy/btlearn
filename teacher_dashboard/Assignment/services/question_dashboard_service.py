from fastapi.exceptions import HTTPException
import requests
from config.app_config import get_config

class QuestionDashboardService:
    base_url_parts = [get_config().QUESTIONS_DASHBOARD_URL, "/api/v1"]
    
    base_url = "/".join(url.strip("/") for url in base_url_parts)
    timeout_sec = 500

    def get_topic_name(self, topic_code):
        request_url = QuestionDashboardService.base_url + \
            "/topics?code={topic_code}".format(topic_code=topic_code)

        response = self.api_get_call(request_url)
        topics_arr = response.get("topic")

        if(len(topics_arr) == 1):
            topic_desc = topics_arr[0]
            return topic_desc.get("name")
        else:
            raise HTTPException(
                404, detail="Not able to find topic name")

    def get_question(self, question_id):
        request_url = QuestionDashboardService.base_url + \
            "/questions?id={question_id}".format(question_id=question_id)

        response = self.api_get_call(request_url)
        questions_arr = response.get("data")

        if(len(questions_arr) == 1 and str(questions_arr[0]["id"]) == question_id):
            question_desc = questions_arr[0]
            return question_desc
        else:
            raise HTTPException(
                404, detail="Not able to find question description")

    def api_get_call(self, request_url):
        try:
            response = requests.get(
                request_url, timeout=QuestionDashboardService.timeout_sec)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            raise HTTPException(
                401, detail="Not authorized to access the service")
        except requests.exceptions.ConnectionError as errc:
            raise HTTPException(
                401, detail="Not able to connect with the service-1")
        except requests.exceptions.Timeout as errt:
            raise errt
        except requests.exceptions.RequestException as err:
            raise err


question_dashboard_service = QuestionDashboardService()
