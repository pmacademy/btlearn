import requests
from urllib3.util import timeout


class ClassroomService:
    base_url = "http://0.0.0.0:5000/api/v1/classes"
    timeout_sec = 500

    def get_students(self, class_id: int):
        request_url = ClassroomService.base_url + \
            "/{class_id}/students/all".format(class_id=class_id)

        return self.api_post_call(request_url)

    def validate_class(self, class_id: int):
        pass

    def validate_teacher(self):
        pass

    def api_post_call(self, request_url):
        try:
            response = requests.get(
                request_url, timeout=ClassroomService.timeout_sec)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as err:
            print(err)


classroom_service = ClassroomService()
