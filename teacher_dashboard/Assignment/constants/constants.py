
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum, QuestionStatusEnum, TutorUsedEnum


class ClassroomServiceConstants:
    ID = "id"
    UUID = 'uuid'
    LAST_NAME = "last_name"
    PASSWORD = "password"
    CLASS_ID = "class_id"
    FIRST_NAME = "first_name"
    EMAIL = "email"
    PARENT_EMAIL = "parents_email"


class QuestionDashboradServiceConstants:
    DATA = "data"
    TOTAL_QUESTIONS = "totalQuestions"

    class Data:
        ID = "id"
        SUBJECT = "subject"
        DESCRIPTION = "description"
        GRADE = "grade"
        CHAPTER = "chapter"
        TOPIC = "topic"
        DIFFICULTY = "difficulty"
        QUESTION_STATUS = "ques_status"
        ANNOTATION_STATUS = "annotation_status"
        BELONGS = "belongs"
        TYPE = "type"
        MPU_TEXT = "mpu_text"


class NotificationServiceTypes:
    EMAIL = "email"


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

class StudentAlreadyExistsAddedToClass:
    TEAMPLATE_NAME = "StudentAlreadyExistsAddedToClass"

    class Fields:
        class Body:
            STUDENT_FIRST_NAME = "student_first_name"
            STUDENT_LAST_NAME = "student_last_name"
            TEACHER_NAME = "teacher_name"
            BYETELEARN_SIGN_IN_URL = "bytelearn_sign_in_url"
            STUDENT_EMAIL = "student_email"

        class Subject:
            pass



class PerformanceConfigConstant:
    class AssignmentStudentQuestionConfig:
        class L3:
            HINT_MIN_NUMBER = 0
            HINT_MAX_NUMBER = 0
            INCORRECT_MIN_NUMBER = 0
            INCORRECT_MAX_NUMBER = 0
            INCORRECT_WITH_HINT_MIN_NUMBER = 0
            INCORRECT_WITH_HINT_MAX_NUMBER = 0
            STATUS = QuestionStatusEnum.CORRECT
            TUTOR_USED = set([TutorUsedEnum.USED, TutorUsedEnum.NOT_USED])
            LEVEL = 3

        class L2:
            HINT_MIN_NUMBER = 0
            HINT_MAX_NUMBER = 2
            INCORRECT_MIN_NUMBER = 0
            INCORRECT_MAX_NUMBER = 2
            INCORRECT_WITH_HINT_MIN_NUMBER = 0
            INCORRECT_WITH_HINT_MAX_NUMBER = 2
            STATUS = QuestionStatusEnum.CORRECT
            TUTOR_USED = set([TutorUsedEnum.USED, TutorUsedEnum.NOT_USED])
            LEVEL = 2

        class L1:
            HINT_MIN_NUMBER = 3
            HINT_MAX_NUMBER = float("inf")
            INCORRECT_MIN_NUMBER = 3
            INCORRECT_MAX_NUMBER = float("inf")
            INCORRECT_WITH_HINT_MIN_NUMBER = 3
            INCORRECT_WITH_HINT_MAX_NUMBER = float("inf")
            STATUS = QuestionStatusEnum.CORRECT
            TUTOR_USED = set([TutorUsedEnum.USED, TutorUsedEnum.NOT_USED])
            LEVEL = 1

        class L0:
            LEVEL = 0

    class AssignmentStudentConfig:
        STATUS = AssignmentStatusEnum.COMPLETED

        class L3:
            L3_MIN_PERCENT = 0.9
            L3_MAX_PERCENT = 1
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0
            L1_MAX_PERCENT = 1
            LEVEL = 3

        class L2:
            L3_MIN_PERCENT = 0
            L3_MAX_PERCENT = 0.9
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0
            L1_MAX_PERCENT = 0.3
            LEVEL = 2

        class L1:
            L3_MIN_PERCENT = 0
            L3_MAX_PERCENT = 1
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0.3
            L1_MAX_PERCENT = 1
            LEVEL = 1

        class L0:
            LEVEL = 0

    class AssignmentStudentListConfig:
        STATUS = AssignmentStatusEnum.COMPLETED
        DISABLED_MAX_PERCENT = 0.7

        class L3:
            L3_MIN_PERCENT = 0.9
            L3_MAX_PERCENT = 1
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0
            L1_MAX_PERCENT = 1
            LEVEL = 3

        class L2:
            L3_MIN_PERCENT = 0
            L3_MAX_PERCENT = 0.9
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0
            L1_MAX_PERCENT = 0.3
            LEVEL = 2

        class L1:
            L3_MIN_PERCENT = 0
            L3_MAX_PERCENT = 1
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0.3
            L1_MAX_PERCENT = 1
            LEVEL = 1

        class L0:
            LEVEL = 0

    class AssignmentStudentListQuestionConfig:
        class L3:
            L3_MIN_PERCENT = 0.9
            L3_MAX_PERCENT = 1
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0
            L1_MAX_PERCENT = 1
            LEVEL = 3

        class L2:
            L3_MIN_PERCENT = 0
            L3_MAX_PERCENT = 0.9
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0
            L1_MAX_PERCENT = 0.3
            LEVEL = 2

        class L1:
            L3_MIN_PERCENT = 0
            L3_MAX_PERCENT = 1
            L2_MIN_PERCENT = 0
            L2_MAX_PERCENT = 1
            L1_MIN_PERCENT = 0.3
            L1_MAX_PERCENT = 1
            LEVEL = 1

        class L0:
            LEVEL = 0
