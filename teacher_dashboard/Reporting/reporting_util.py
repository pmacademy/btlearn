from teacher_dashboard.Assignment.constants.constants import PerformanceConfigConstant
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum, QuestionEvalStatusEnum, QuestionStatusEnum, TutorUsedEnum
from teacher_dashboard.Assignment.daos.assignment_student_dao import assignment_student_dao
from teacher_dashboard.Assignment.daos.assignment_question_dao import assignment_question_dao
from teacher_dashboard.Assignment.services.performance_v2 import performance_service
import logging
from teacher_dashboard.models import AssignmentStudent

class ReportingUtil:
    def student_assignment_struggling(self, student:AssignmentStudent):
        if performance_service.calculate_performance_assignment_id_and_studnet_id(student.assignment_id, student.student_id)==PerformanceConfigConstant.AssignmentStudentConfig.L1.LEVEL:
            return True
        else:
            return False

    def student_assignment_complete(self, student):
        if student.status in {AssignmentStatusEnum.COMPLETED}:
            return True
        else:
            return False

    def student_assignment_incomplete(self, student):
        if student.status in {AssignmentStatusEnum.NOT_ATTEMPTED, AssignmentStatusEnum.IN_PROGRESS}:
            return True
        else:
            return False

    def assignment_score(self, assignment_id, class_id):
        if class_id == None:
            completed_students_count = assignment_student_dao.count_students_by_assignment_id_and_is_completed(
                assignment_id)
            total_students_count = assignment_student_dao.count_students_by_assignment_id(
                assignment_id)
        else:
            completed_students_count = assignment_student_dao.count_students_by_assignment_id_and_class_id_and_is_completed(
                assignment_id, class_id)
            total_students_count = assignment_student_dao.count_students_by_assignment_id_and_class_id(
                assignment_id, class_id)

        return completed_students_count, total_students_count

    def student_assignment_score(self, student_questions):
        total_questions_count = 0
        completed_questions_count = 0
        for assignment_student_questions_in_db in student_questions:
            total_questions_count += 1
            if assignment_student_questions_in_db.status != QuestionStatusEnum.NOT_ATTEMPTED:
                completed_questions_count += 1
        return completed_questions_count, total_questions_count

    def get_question_id_sequence_mapping(self, assignment_id):
        assignment_questions = assignment_question_dao.find_questions_by_assignment_id_order_by_sequence_number(
            assignment_id)
        question_id_seuqence_map = {}

        sequence_number = 1
        for question in assignment_questions:
            question_id_seuqence_map[question.question_id] = sequence_number
            sequence_number += 1

        return question_id_seuqence_map

    def update_incorrect_count(self, report_in_db, assignment_studnet_question):
        # if(assignment_studnet_question.incorrect_count == None):
        #     assignment_studnet_question.incorrect_count = 0

        if report_in_db.is_correct == False:
            assignment_studnet_question.incorrect_count += 1

        return assignment_studnet_question

    def update_hint_count(self, report_in_db, assignment_studnet_question):
        # assignment_studnet_question.hint_count =

        if report_in_db.interaction_type == "EXPLICIT_HINT":
            assignment_studnet_question.hint_count += 1

        return assignment_studnet_question

    def update_question_complete(self, report_in_db, assignment_studnet_question):
        # assignment_studnet_question.hint_count =

        # previous_step_log = reporting_dao.find_previous_not_completed_log(
        #     report_in_db.id,
        #     report_in_db.student_id,
        #     report_in_db.assignment_id,
        #     report_in_db.class_id,
        #     report_in_db.question_id
        # )

        if(report_in_db.is_complete == True):
            assignment_studnet_question.eval_status = QuestionEvalStatusEnum.CORRECT

        return assignment_studnet_question

    def update_tutor_used(self, report_in_db, assignment_studnet_question):
        if(report_in_db.mode == "SOLVE_WITH_ME"):
            assignment_studnet_question.tutor_used = TutorUsedEnum.USED

        return assignment_studnet_question

    # def update_assignment_student_status(self, assignment_studnet_question):
    #     if(assignment_studnet_question.assignment_student.status == AssignmentStatusEnum.NOT_ATTEMPTED):
    #         assignment_studnet_question.assignment_student.status = AssignmentStatusEnum.IN_PROGRESS
    #     return assignment_studnet_question


reporting_util = ReportingUtil()
