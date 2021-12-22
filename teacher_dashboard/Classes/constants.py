class StudentAccountCreateEmailConstant:
    TEAMPLATE_NAME = "StudentAccountCreateEmail"

    class Fields:
        class Body:
            STUDENT_FIRST_NAME = "student_first_name"
            STUDENT_LAST_NAME = "student_last_name"
            TEACHER_NAME = "teacher_name"
            BYETELEARN_SIGN_IN_URL = "bytelearn_sign_in_url"
            STUDENT_EMAIL = "student_email"
            STUDENT_PASSWORD = "student_password"

        class Subject:
            pass
