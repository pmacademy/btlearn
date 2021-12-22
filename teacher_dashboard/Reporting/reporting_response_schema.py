from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from typing import List
from datetime import datetime

from teacher_dashboard.Assignment.constants.enums import AssignmentStudentStatusEnum, QuestionStatusEnum, TutorUsedEnum
from teacher_dashboard.Reporting.reporting_request_schema import BaseRequest


########################
# Insights             #
########################

class InsightsClassStudentsResponse(BaseModel):
    student_id: str
    first_name: str
    last_name: str


class InsightsAssignmentClassStudentsResponse(BaseModel):
    student_id: str
    completed: bool
    late: bool
    questions_completed: int
    total_questions: int
    student_performance: int


class InsightsAssignmentClassResponse(BaseModel):
    class_id: int
    class_performance: int
    class_students: List[InsightsAssignmentClassStudentsResponse]


class InsightsAssignmentResponse(BaseModel):
    assignment_id: int
    assignment_title: str
    due_date: datetime
    total_questions_count: int
    classes: List[InsightsAssignmentClassResponse]


class InsightsClassResponse(BaseModel):
    class_id: int
    class_students: List[InsightsClassStudentsResponse]


class InsightsResponse(BaseModel):
    teacher_id: str
    class_id: Optional[int]
    assignment_id: Optional[int]
    classes: List[InsightsClassResponse]
    assignments: List[InsightsAssignmentResponse]

########################
# Assignment Overview  #
########################


class AssignmentQuestionBasicDetailsResponse(BaseModel):
    question_id: str
    question_sequence_number: int


class AssignmentClassOverviewResponse(BaseModel):
    teacher_id: str
    assignment_id: int
    class_id: Optional[int]
    assignment_title: str
    total_questions: int
    completed_students_count: int
    total_students_count: int
    class_performance: int
    assignment_questions: List[AssignmentQuestionBasicDetailsResponse]


########################
# Assignment Students  #
########################

class StudentQuestionsResponse(BaseModel):
    question_id: str
    question_sequence_num: int
    tutor_used: bool
    question_status: QuestionStatusEnum
    question_performance: int


class StudentDetailsResponse(BaseModel):
    student_id: str
    class_id: int
    first_name: str
    last_name: str
    completed_questions_count: int
    total_questions_count: int
    assignment_complete: bool
    performance: int
    progress: Optional[List[StudentQuestionsResponse]] = None


class AssignmentStudentsResponse(BaseModel):
    teacher_id: str
    assignment_id: int
    class_id: Optional[int]
    status: AssignmentStudentStatusEnum
    students: List[StudentDetailsResponse]
    start: int
    limit: int
    total_count: int

########################
# Assignment Questions #
########################


class StudentsResponse(BaseModel):
    student_id: str
    first_name: str
    last_name: str


class QuestionsResponse(BaseModel):
    question_id: str
    question_desc: str
    question_difficulty: str
    topic_name: str
    question_sequence_number: int
    performance: int
    students_tutor_used_count: int
    students_tutor_used: List[StudentsResponse]
    students_incomplete_count: int
    students_incomplete: List[StudentsResponse]
    students_complete_count: int
    students_complete: List[StudentsResponse]


class AssignmentQuestionsResponse(BaseModel):
    teacher_id: str
    assignment_id: int
    class_id: Optional[int]
    question_id: Optional[str]
    questions: List[QuestionsResponse]
    start: int = 0
    size: int = 10
    total_count: int
