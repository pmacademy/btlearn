from datetime import datetime
from sqlalchemy import func
from teacher_dashboard.models import Assignment, AssignmentStudent, AssignmentStudentQuestion
from teacher_dashboard.db_session import db_session
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum


class AssignmentStudentDao:
    def find_students_by_assignment_id_and_class_id(self, assignment_id, class_id):
        db = db_session.get()
        return db.query(AssignmentStudent).filter(
            AssignmentStudent.assignment_id == assignment_id).filter(
            AssignmentStudent.class_id == class_id).all()

    def find_students_by_assignment_id(self, assignment_id):
        db = db_session.get()
        return db.query(AssignmentStudent).filter(
            AssignmentStudent.assignment_id == assignment_id).all()

    def delete_assignment_by_class_id_and_student_id_and_submission_last_date_greater_than(self, class_id, student_id, email, time=datetime.utcnow()):
        db = db_session.get()
        deleted_count = db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.class_id == class_id
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudent.email == email
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.NOT_ATTEMPTED
        ).filter(
            AssignmentStudent.assignment_id == Assignment.id
        ).filter(
            Assignment.submission_last_date > time
        ).delete(synchronize_session=False)
        db.commit()
        return deleted_count

    def find_assignments_by_student_id_and_is_published_and_is_not_completed_order_by_submission_last_date(self, student_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).join(
            Assignment
        ).order_by(
            Assignment.submission_last_date, Assignment.id
        ).filter(
            Assignment.is_published == True
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudent.status != AssignmentStatusEnum.COMPLETED
        ).all()

    def count_assignments_by_student_id_and_is_published_and_is_not_completed_order_by_submission_last_date(self, student_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).join(
            Assignment
        ).order_by(
            Assignment.submission_last_date, Assignment.id
        ).filter(
            Assignment.is_published == True
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudent.status != AssignmentStatusEnum.COMPLETED
        ).count()

    def find_assignments_by_student_id_and_is_published_and_is_not_completed_and_is_limited_order_by_submission_last_date(self, student_id, start, limit):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).join(
            Assignment
        ).order_by(
            Assignment.submission_last_date, Assignment.id
        ).filter(
            Assignment.is_published == True
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudent.status != AssignmentStatusEnum.COMPLETED
        ).offset(
            start
        ).limit(
            limit
        ).all()
        # return db.query(AssignmentStudent).filter(AssignmentStudent.assignment.has(is_published=True)).filter(
        #     AssignmentStudent.student_id == student_id).offset(start).limit(limit).all()

    def find_assignments_by_student_id_and_is_published_and_is_completed_and_is_limited_order_by_submission_last_date(self, student_id, start, limit):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).join(
            Assignment
        ).order_by(
            Assignment.submission_last_date.desc(), Assignment.id
        ).filter(
            Assignment.is_published == True
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.COMPLETED
        ).offset(
            start
        ).limit(
            limit
        ).all()

    def count_assignments_by_student_id_and_is_published_and_is_completed_order_by_submission_last_date(self, student_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).join(
            Assignment
        ).order_by(
            Assignment.submission_last_date.desc(), Assignment.id
        ).filter(
            Assignment.is_published == True
        ).filter(
            AssignmentStudent.student_id == student_id
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.COMPLETED
        ).count()

    def find_assignment_student_by_assignment_id_and_student_id_and_is_published(self, assignment_id, student_id):
        db = db_session.get()
        return db.query(AssignmentStudent).filter(
            AssignmentStudent.assignment.has(is_published=True)).filter(
            AssignmentStudent.assignment_id == assignment_id).filter(
            AssignmentStudent.student_id == student_id).first()

    def save(self, assignment_student):
        db = db_session.get()
        db.add(assignment_student)
        db.commit()
        db.refresh(assignment_student)
        return assignment_student

    def find_students_by_assignment_id_and_class_id_and_is_not_complete_and_is_limited(self, assignment_id, class_id, start, limit):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudent.class_id == class_id
        ).filter(
            AssignmentStudent.status != AssignmentStatusEnum.COMPLETED
        ).offset(
            start
        ).limit(
            limit
        ).all()

    def count_students_by_assignment_id_and_class_id_and_is_not_complete(self, assignment_id, class_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudent.class_id == class_id
        ).filter(
            AssignmentStudent.status != AssignmentStatusEnum.COMPLETED
        ).count()

    def count_students_by_assignment_id_and_is_completed(self, assginment_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assginment_id
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.COMPLETED
        ).count()

    def count_students_by_assignment_id(self, assginment_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assginment_id
        ).count()

    def count_students_by_assignment_id_and_class_id_and_is_completed(self, assginment_id, class_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assginment_id
        ).filter(
            AssignmentStudent.class_id == class_id
        ).filter(
            AssignmentStudent.status == AssignmentStatusEnum.COMPLETED
        ).count()

    def count_students_by_assignment_id_and_class_id(self, assginment_id, class_id):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assginment_id
        ).filter(
            AssignmentStudent.class_id == class_id
        ).count()

    def find_by_assignment_id_and_class_id_list_order_by_class_id(self, assignment_id, class_id_list):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).order_by(
            AssignmentStudent.class_id
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudent.class_id.in_(class_id_list)
        ).all()

    def find_students_by_assignment_id_and_student_id_list(self, assignment_id, student_id_list):
        db = db_session.get()
        return db.query(
            AssignmentStudent
        ).filter(
            AssignmentStudent.assignment_id == assignment_id
        ).filter(
            AssignmentStudent.student_id.in_(student_id_list)
        ).all()


assignment_student_dao = AssignmentStudentDao()
