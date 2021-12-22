from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON, Date, func
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Integer, String, Boolean, Text
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum, QuestionEvalStatusEnum, QuestionStatusEnum, TutorUsedEnum
from sqlalchemy.dialects.mysql import LONGTEXT

from teacher_dashboard.database import Base


class Classes(Base):

    __tablename__ = "test_classes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    google_id = Column(String(250))
    source = Column(String(50))
    status = Column(String(50))
    name = Column(String(50))
    code = Column(String(6), unique=True)
    teacher_id = Column(String(250))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    student_count = Column(Integer)


class Students(Base):

    __tablename__ = "test_class_students"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid = Column(String(250))
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(50))
    password = Column(String(100), nullable=True)
    parents_email = Column(String(50))
    class_id = Column(Integer, ForeignKey(
        "test_classes.id", ondelete='CASCADE'))

# class Teacher(Base):

#     __tablename__ = "Teachers"

#     id = Column(Integer, primary_key=True, autoincrement=True, index=True)
#     first_name = Column(String(50))
#     last_name=Column(String(50))
#     email = Column(String(50))
#     hashed_password = Column(String(50))


class BaseDBModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)
    # is_deleted = Column(Boolean, default=False, nullable=False)
    # deleted_at = Column(DateTime, default=None, nullable=True)


class Assignment(BaseDBModel):
    __tablename__ = "assignment"

    title = Column(String(1000), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    submission_last_date = Column(DateTime, default=None, nullable=True)
    teacher_id = Column(String(400), nullable=False)

    questions = relationship(
        "AssignmentQuestion", back_populates="assignment", cascade="all, delete-orphan")
    classes = relationship(
        "AssignmentClass", back_populates="assignment", cascade="all, delete-orphan")
    students = relationship(
        "AssignmentStudent", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentQuestion(BaseDBModel):
    __tablename__ = "assignment_question"

    assignment_id = Column(Integer, ForeignKey(
        "assignment.id", ondelete='CASCADE'))
    question_id = Column(String(400), index=True, nullable=False)
    sequence_num = Column(Integer, nullable=False)
    tutor_available = Column(String(400), nullable=False, default=False)
    topic_code = Column(String(400), nullable=False, default=True)
    topic_sequence_num = Column(Integer, nullable=False)
    cluster_id = Column(String(400), nullable=False)
    topic_tutor_available = Column(String(400), nullable=False)

    assignment = relationship("Assignment", back_populates="questions")

    def __lt__(self, other):
        return self.sequence_num < other.sequence_num


class AssignmentClass(BaseDBModel):
    __tablename__ = "assignment_class"

    assignment_id = Column(Integer, ForeignKey(
        "assignment.id", ondelete='CASCADE'))
    class_id = Column(Integer, index=True, nullable=False)

    # students = relationship("AssignmentStudent", back_populates="student_class", cascade="all, delete-orphan")

    assignment = relationship("Assignment", back_populates="classes")


class AssignmentStudent(BaseDBModel):
    __tablename__ = "assignment_student"

    assignment_id = Column(Integer, ForeignKey(
        "assignment.id", ondelete='CASCADE'), primary_key=True)
    # class_id = Column(Integer, ForeignKey("assignment_class.class_id", ondelete='CASCADE'), index=True, nullable=False)

    class_id = Column(Integer, index=True, nullable=False)
    first_name = Column(String(400), nullable=False)
    last_name = Column(String(400), nullable=False)
    email = Column(String(400), index=True, nullable=False)
    parents_email = Column(String(400), index=True, nullable=True)

    student_id = Column(String(400), index=True,
                        nullable=False, primary_key=True)
    status = Column(
        String(400), default=AssignmentStatusEnum.NOT_ATTEMPTED, nullable=False)
    completed_at = Column(DateTime, default=None, nullable=True)

    assignment = relationship("Assignment", back_populates="students")
    questions = relationship(
        "AssignmentStudentQuestion", back_populates="assignment_student", cascade="all, delete-orphan")
    # student_class = relationship("AssignmentClass", back_populates="students")


class AssignmentStudentQuestion(BaseDBModel):
    __tablename__ = "assignment_student_question"

    assignment_student_id = Column(Integer, ForeignKey(
        "assignment_student.id", ondelete='CASCADE'), primary_key=True)
    question_id = Column(String(400), index=True,
                         nullable=False, primary_key=True)

    # completed = Column(Boolean, default=False, nullable=False)
    status = Column(
        String(400), default=QuestionStatusEnum.NOT_ATTEMPTED, nullable=False)

    eval_status = Column(
        String(400), default=QuestionEvalStatusEnum.NOT_UPDATED, nullable=False)

    tutor_used = Column(
        String(400), default=TutorUsedEnum.NOT_USED, nullable=False)

    incorrect_count = Column(Integer, default=0, nullable=False)

    hint_count = Column(Integer, default=0, nullable=False)

    assignment_student = relationship(
        "AssignmentStudent", back_populates="questions")


class ReportLogs(BaseDBModel):
    __tablename__ = "report_logs"
    is_correct = Column(Boolean, default=None, nullable=True)
    is_partially_correct = Column(Boolean, default=None, nullable=True)
    is_complete = Column(Boolean, default=False, nullable=True)
    student_input_dict = Column(JSON)
    step_number = Column(String(255), nullable=True, default=None)
    question_session_id = Column(String(400))
    mode = Column(String(400), nullable=False)
    hint_code = Column(String(255), nullable=True, default=None)
    question_id = Column(String(400))
    student_id = Column(String(400))
    assignment_id = Column(Integer)
    class_id = Column(Integer)
    interaction_type = Column(String(255))
    main_cat = Column(String(255))
    sub_cat = Column(String(255))


class EeTerms(BaseDBModel):
    __tablename__ = "ee_terms_updated"
    term_code = Column(String(255))
    name = Column(String(255))
    text_def = Column(String(800))
    example_1 = Column(String(800))
    example_2 = Column(String(800))
    example_3 = Column(String(800))
    visualisation_image = Column(String(255))
    trimmed_video_link = Column(String(255))
    video = Column(String(255))
    time = Column(String(255))
    vqc = Column(String(255))


class Users(BaseDBModel):
    __tablename__ = "user"
    uuid = Column(String(100), nullable=False)
    email = Column(String(400), nullable=False)
    parent_email = Column(String(400), default=None, nullable=True)
    display_name = Column(String(400), nullable=False)
    full_name = Column(String(400), default=None, nullable=True)
    profile_image = Column(String(400), default=None, nullable=True)
    hashed_password = Column(String(1000), default=None, nullable=True)
    auth_provider = Column(String(100), nullable=False)
    default_role = Column(String(400), nullable=False)


class Topic(Base):
    __tablename__ = "topic"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text)
    ccss = Column(String(255))
    code = Column(String(255))


class Questions(Base):
    __tablename__ = "Questions"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ques_id = Column(Text)
    ques_desc = Column(LONGTEXT)
    ptype = Column(String(255), default=None)
    stype = Column(String(255), default=None)
    stype_1 = Column(String(255), default=None)
    stype_2 = Column(String(255), default=None)
    ques_chapter = Column(Integer, default=None)
    ques_subject = Column(Text)
    state = Column(Text)
    mpuoutput_text = Column(Text)
    ques_topic = Column(Integer, default=None)
    ques_grade = Column(String(255), default=None)
    ques_status = Column(String(255), default=None)
    ques_difficulty = Column(Integer, default=None)
    userName = Column(Integer, default=None)
    createSource = Column(Text)
    belongs = Column(String(255), default=None)
    annotation_status = Column(String(255), default=None)
    CreatedOn = Column(Date, default=func.current_date())
    UpdatedOn = Column(DateTime, nullable=False,
                       default=func.now(), onupdate=func.now())


class Misconception(Base):
    __tablename__ = "misconceptions"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    unit = Column(String(255))
    main_category = Column(String(255))
    sub_category = Column(String(255))
    step_id = Column(String(255))
    KP_code = Column(String(255))
    IDH = Column(String(255))
    m_code = Column(Integer)


class MisconceptionDetails(Base):
    __tablename__ = "misconception_detail"
    id = Column(Integer, primary_key=True, nullable=False)
    m_desc = Column(String(255), default=None)


class KnowledgePoint(Base):
    __tablename__ = "knowledgePoint"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    unit = Column(String(255))
    main_category = Column(String(255))
    sub_category = Column(String(255))
    step_id = Column(String(255))
    KP_code = Column(String(255))


class KnowledgePointDetails(Base):
    __tablename__ = "knowledgePoint_detail"
    id = Column(Integer, primary_key=True, nullable=False)
    KP_Teacher_desc = Column(String(255))
    KP_desc = Column(String(255))
