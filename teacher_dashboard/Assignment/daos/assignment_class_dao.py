from teacher_dashboard.db_session import db_session
from teacher_dashboard.models import AssignmentClass


class AssignmentClassDao:

    def find_by_class_id(self, class_id):
        db = db_session.get()
        return db.query(
            AssignmentClass
        ).filter(
            AssignmentClass.class_id == class_id
        ).all()

    def find_by_assignment_id(self, assignment_id):
        db = db_session.get()
        return db.query(
            AssignmentClass
        ).filter(
            AssignmentClass.assignment_id == assignment_id
        ).all()


assignment_class_dao = AssignmentClassDao()
