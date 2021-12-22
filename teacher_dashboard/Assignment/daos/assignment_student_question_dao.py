from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum
from teacher_dashboard.db_session import db_session
from teacher_dashboard.models import AssignmentStudent, AssignmentStudentQuestion


class AssignmentStudentQuestionDao:
    def find_by_assignment_id_and_question_id_and_is_complete(self, assignment_id, question_id):
        db = db_session.get()
        return db.query(
            AssignmentStudentQuestion
        ).join(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudentQuestion.question_id == question_id
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.COMPLETED
        ).all()

    def find_by_assignment_id_and_class_id_and_question_id_and_is_complete(self, assignment_id, class_id, question_id):
        db = db_session.get()
        return db.query(
            AssignmentStudentQuestion
        ).join(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudent.class_id == class_id
        ).filter(
            AssignmentStudentQuestion.question_id == question_id
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.COMPLETED
        ).all()

    def find_by_assignment_id_and_student_id_and_question_id(self, assignment_id, student_id, question_id):
        db = db_session.get()
        return db.query(
            AssignmentStudentQuestion
        ).join(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudentQuestion.question_id == question_id
        ).first()

    def save(self, assignment_student_question):
        db = db_session.get()
        db.add(assignment_student_question)
        db.commit()
        db.refresh(assignment_student_question)
        return assignment_student_question


assignment_student_question_dao = AssignmentStudentQuestionDao()
