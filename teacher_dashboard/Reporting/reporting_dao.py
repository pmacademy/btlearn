from teacher_dashboard.db_session import db_session
from sqlalchemy import and_
import logging

from teacher_dashboard.models import ReportLogs, Topic, Questions, Users, MisconceptionDetails, Misconception, EeTerms

logger = logging.getLogger(__name__)


class ReportingDao:
    @staticmethod
    def save(report):
        db = db_session.get()
        db.add(report)
        db.commit()
        db.refresh(report)
        logger.info(report)
        return report

    def get_assignment_questions(self, assignment_id):
        db = db_session.get()
        question_details = db.query(ReportLogs.question_id, Topic.name, Questions.ques_difficulty,
                                    ReportLogs.student_id, Questions.ques_desc, Users.display_name).join(
            Questions, Questions.id == ReportLogs.question_id).join(
            Topic, Questions.ques_topic == Topic.code).join(Users, Users.uuid == ReportLogs.student_id).filter(
            ReportLogs.assignment_id == assignment_id).distinct().all()
        return question_details

    def get_kg_desc(self, assignment_id):
        db = db_session.get()
        reports = db.query(MisconceptionDetails.m_desc, Misconception.m_code, ReportLogs.student_id,
                           ReportLogs.question_id, Questions.ques_desc, Users.display_name).join(
            Questions, Questions.id == ReportLogs.question_id).join(
            Misconception,
            and_(Misconception.main_category == ReportLogs.main_cat, Misconception.IDH == ReportLogs.hint_code,
                 Misconception.step_id == ReportLogs.step_number, Misconception.sub_category == ReportLogs.sub_cat)).join(
            MisconceptionDetails,
            MisconceptionDetails.id == Misconception.m_code).join(
            Users,
            Users.uuid == ReportLogs.student_id).filter(
            and_(ReportLogs.assignment_id == assignment_id, ReportLogs.is_correct == False)).distinct().all()

        return reports

    def get_student_logs(self, question_id, assignment_id, student_id):
        db = db_session.get()
        question_logs = db.query(ReportLogs).filter(
            and_(ReportLogs.assignment_id == assignment_id, ReportLogs.question_id == question_id,
                 ReportLogs.student_id == student_id)).all()
        return question_logs

    def get_term_code(self, term_code):
        db = db_session.get()
        logger.info(db.bind.url)
        term_details = db.query(EeTerms).filter(EeTerms.term_code == term_code).all()
        return term_details


    def get_students_needed_help(self, question_id, assignment_id):
        db = db_session.get()
        students = db.query(Users.uuid, Users.display_name).join(
            ReportLogs, ReportLogs.student_id == Users.uuid).filter(
            and_(ReportLogs.assignment_id == assignment_id, ReportLogs.question_id == question_id,
                 ReportLogs.interaction_type == "EXPLICIT_HINT")).distinct().all()
        return students

    def find_by_assignment_id_and_class_id(self, assignment_id, class_id):
        db = db_session.get()
        return db.query(
            ReportLogs
        ).filter(
            ReportLogs.assignment_id == assignment_id
        ).filter(
            ReportLogs.class_id == class_id
        ).all()

    def find_by_assignment_id(self, assignment_id):
        db = db_session.get()
        return db.query(
            ReportLogs
        ).filter(
            ReportLogs.assignment_id == assignment_id
        ).all()

    def find_by_assignment_id_and_class_id_and_question_id(self, assignment_id, class_id, question_id):
        db = db_session.get()
        return db.query(
            ReportLogs
        ).filter(
            ReportLogs.assignment_id == assignment_id
        ).filter(
            ReportLogs.class_id == class_id
        ).filter(
            ReportLogs.question_id == question_id
        ).all()

    def find_by_assignment_id_and_studnet_id(self, assignment_id, student_id):
        db = db_session.get()
        return db.query(
            ReportLogs
        ).filter(
            ReportLogs.assignment_id == assignment_id
        ).filter(
            ReportLogs.student_id == student_id
        ).all()

    def find_by_assignment_id_and_class_id_and_studnet_id_and_question_id(self, assignment_id, class_id, student_id, question_id):
        db = db_session.get()
        return db.query(
            ReportLogs
        ).filter(
            ReportLogs.assignment_id == assignment_id
        ).filter(
            ReportLogs.class_id == class_id
        ).filter(
            ReportLogs.student_id == student_id
        ).filter(
            ReportLogs.question_id == question_id
        ).all()


reporting_dao = ReportingDao()
