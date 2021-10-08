from sqlalchemy import  Column, ForeignKey, Integer, String,DateTime


from teacher_dasboard.database import Base


class Classes(Base):

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    google_id = Column(String(250))
    status = Column(String(50))
    name = Column(String(50))
    code = Column(String(6), unique=True)
    teacher_id = Column(String(250))
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    student_count=Column(Integer)

class Students(Base):

    __tablename__ = "class_students"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    first_name = Column(String(50))
    last_name=Column(String(50))
    email = Column(String(50))
    password = Column(String(100))
    parents_email = Column(String(50))
    class_id=Column(Integer, ForeignKey("classes.id",ondelete='CASCADE'))

    