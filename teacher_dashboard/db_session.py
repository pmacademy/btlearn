from teacher_dashboard.database import SessionLocal
from fastapi.security.http import HTTPAuthorizationCredentials
from teacher_dashboard.database import SessionLocal
from contextvars import ContextVar
from sqlalchemy.orm import sessionmaker, Session
from fastapi import BackgroundTasks
from fastapi import Request


class DatabaseSession:
    def __init__(self):
        print("creating db session")
        self.db = SessionLocal()

    def get(self):
        try:
            yield self.db
        except Exception as e:
            self.db.rollback()
            raise e

    def __del__(self):
        print("closing db session")
        self.db.close()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
    finally:
        print("closing session", db)
        db.close()


db_session: ContextVar[Session] = ContextVar('db_session')

request_auth_token: ContextVar[HTTPAuthorizationCredentials] = ContextVar(
    'request_auth_token')

background_task_context_var: ContextVar[BackgroundTasks] = ContextVar(
    'background_task_context_var')

context_request: ContextVar[Request] = ContextVar('request')
