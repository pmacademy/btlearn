from config.app_config import get_config


class TestConstants:
    LOGIN_URL = get_config().AUTH_URL + "/api/v1/user/login"
    TEST_TEACHER_EMAIL = "test.teacher@bytelearn.ai"
    TEST_TEACHER_PASSWORD = "password"
    TEST_STUDENT_EMAIL = "test.student@bytelearn.ai"
    TEST_STUDENT_PASSWORD = "password"
