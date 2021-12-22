from datetime import datetime
from sqlalchemy.orm.session import make_transient, make_transient_to_detached
from teacher_dashboard.db_session import db_session
from teacher_dashboard.models import Assignment, AssignmentClass, AssignmentStudent
from teacher_dashboard.db_session import DatabaseSession


class AssignmentDao:

    def find_by_id(self, id):
        db = db_session.get()
        return db.query(Assignment).filter(Assignment.id == id).first()

    def find_by_teacher_id(self, teacher_id):
        db = db_session.get()
        return db.query(Assignment).filter(Assignment.teacher_id == teacher_id).all()

    def find_assignments_by_class_id_and_is_published(self, class_id):
        db = db_session.get()
        return db.query(
            Assignment
        ).join(
            AssignmentClass
        ).filter(
            AssignmentClass.class_id == class_id
        ).filter(
            Assignment.is_published == True
        ).all()

    def find_assignment_by_class_id_and_submission_last_date_greater_than(self, class_id, time=datetime.utcnow()):
        db = db_session.get()
        return db.query(
            Assignment
        ).join(
            AssignmentClass
        ).filter(
            AssignmentClass.class_id == class_id
        ).filter(
            Assignment.submission_last_date > time
        ).all()

    def save(self, assignment):
        db = db_session.get()
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def save_all(self, assignment_list):
        db = db_session.get()
        db.bulk_save_objects(assignment_list)
        db.commit()
        [db.refresh(assignment) for assignment in assignment_list]
        return assignment_list

    def update(self, assignment):
        db = db_session.get()
        # todo: update it to do it in single query withgout retrieving it
        assignment_in_db = db.query(Assignment).filter(
            Assignment.id == assignment.id).first()
        for key, val in assignment.dict().items():
            if(hasattr(assignment_in_db, key)):
                setattr(assignment_in_db, key, val)
        db.commit()
        db.refresh(assignment_in_db)
        return assignment_in_db

    def new_update(self, assignment):
        db = db_session.get()
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def clone(self, assignment):
        db = db_session.get()

        questions = assignment.questions
        classes = assignment.classes
        students = assignment.students
        student_questions = {}
        for student in assignment.students:
            student_questions[student.student_id] = student.questions

        db.expunge_all()
        make_transient(assignment)
        assignment.id = None
        assignment.is_published = False

        for q in questions:
            make_transient(q)
            q.id = None
            q.assignment_id = None

        for c in classes:
            make_transient(c)
            c.id = None
            c.assignment_id = None

        for s in students:
            make_transient(s)
            s.id = None
            s.assignment_id = None
            l = []
            for q in student_questions[s.student_id]:
                make_transient(q)
                q.id = None
                q.assignment_student_id = None
                l.append(q)
            s.questions = l

        assignment.questions = questions
        assignment.classes = classes
        assignment.students = students
        # for student in assignment.students:
        #     student.questions = student_questions[student.student_id]

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment

    def delete(self, id):
        db = db_session.get()
        assignment_in_db = db.query(Assignment).filter(
            Assignment.id == id).first()
        db.delete(assignment_in_db)
        db.commit()
        return


assignment_dao = AssignmentDao()
