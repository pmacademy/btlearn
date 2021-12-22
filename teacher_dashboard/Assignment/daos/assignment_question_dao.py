from teacher_dashboard.db_session import db_session
from teacher_dashboard.models import AssignmentQuestion


class AssignmentQuestionDao:
    def find_questions_by_assignment_id_and_question_id(self, assignment_id, question_id):
        db = db_session.get()
        return db.query(
            AssignmentQuestion
        ).filter(
            AssignmentQuestion.assignment_id == assignment_id
        ).filter(
            AssignmentQuestion.question_id == question_id
        ).all()

    def find_questions_by_assignment_id_order_by_sequence_number(self, assignment_id):
        db = db_session.get()
        return db.query(
            AssignmentQuestion
        ).order_by(
            AssignmentQuestion.topic_sequence_num, AssignmentQuestion.sequence_num
        ).filter(
            AssignmentQuestion.assignment_id == assignment_id
        ).all()

    def find_questions_by_assignment_id_and_is_limited_order_by_sequence_number(self, assignment_id, start, limit):
        db = db_session.get()
        return db.query(
            AssignmentQuestion
        ).order_by(
            AssignmentQuestion.topic_sequence_num, AssignmentQuestion.sequence_num
        ).filter(
            AssignmentQuestion.assignment_id == assignment_id
        ).offset(
            start
        ).limit(
            limit
        ).all()

    def count_questions_by_assignment_id(self, assignment_id):
        db = db_session.get()
        return db.query(
            AssignmentQuestion
        ).filter(
            AssignmentQuestion.assignment_id == assignment_id
        ).count()


assignment_question_dao = AssignmentQuestionDao()
