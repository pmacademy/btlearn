from enum import Enum


class TutorAvailableEnum(str, Enum):
    AVAILABLE = "available"
    REQUIRED = "required"
    OFF = "off"


class TutorUsedEnum(str, Enum):
    USED = "used"
    NOT_USED = "not_used"
    NOT_UPDATED = "not_updated"


class QuestionStatusEnum(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    SKIPPED = "skipped"
    COMPLETED = "completed"


class QuestionEvalStatusEnum(str, Enum):
    NOT_UPDATED = "not_updated"
    CORRECT = "correct"
    INCORRECT = "incorrect"


class DataDownloadFormatEnum(str, Enum):
    CSV = "csv"


class AssignmentStatusEnum(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AssignmentStudentStatusEnum(str, Enum):
    STRUGGLING = "struggling"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    ALL = "all"


# class PerformanceColorEnum(str, Enum):
#     GREEN = "green"
#     YELLOW = "yellow"
#     RED = "red"
