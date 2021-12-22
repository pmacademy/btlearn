from contextvars import ContextVar
from datetime import datetime
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import FastAPI
from enum import Enum
import jwt
from starlette import status
from functools import lru_cache
from config.app_config import get_config
from teacher_dashboard.db_session import request_auth_token


class TokenConstants:
    ISSUE_TIME = "iat"
    EXPIRY_TIME = "exp"
    DEFAULT_ROLE = "default_role"
    USER_ROLES = "roles"
    USER_EMAIL = "email"
    DISPLAY_NAME = "display_name"
    FULL_NAME = "full_name"
    PROFILE_IMAGE = "profile_image"
    USER_ID = "user_id"
    ENCODING_ALGORITHM = "RS256"


class UserRoleEnum(str, Enum):
    USER = "user"
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
    DEVELOPER = "developer"
    ADMIN = "admin"
    CLIENT = "client"
    QA = "qa"
    QUESTION_CREATOR = "question_creator"
    QUESTION_APPROVER = "question_approver"
    ANNOTATION_CREATOR = "annotation_creator"
    ANNOTATION_APPROVER = "annotation_approver"




class TokenDependency:
    security = HTTPBearer()

    @lru_cache(maxsize=100)
    def decode_token(self, token):
        try:
            payload = jwt.decode(token,
                                 key=get_config().PUBLIC_KEY,
                                 algorithms=[TokenConstants.ENCODING_ALGORITHM])
            return payload

        except jwt.ExpiredSignatureError:
            print("ExpiredSignatureError")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token")

        except jwt.InvalidTokenError:
            print("InvalidTokenError")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token")

    def validate_token(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)

        if(payload[TokenConstants.ISSUE_TIME] <= datetime.utcnow().timestamp() < payload[TokenConstants.EXPIRY_TIME]):
            return True

        return False

    def get_roles(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)
        return payload.get(TokenConstants.USER_ROLES, [])

    def role_teacher(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)
        if(UserRoleEnum.TEACHER not in payload.get(TokenConstants.USER_ROLES, [])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    def role_student(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)
        if (UserRoleEnum.STUDENT not in payload.get(TokenConstants.USER_ROLES, [])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    def role_client(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)
        if (UserRoleEnum.CLIENT not in payload.get(TokenConstants.USER_ROLES, [])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    # def role_teacher_or_student(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    #     payload = self.decode_token(token.credentials)
    #     if(UserRoleEnum.USER not in payload.get(TokenConstants.USER_ROLES, []) and UserRoleEnum.TEACHER not in payload.get(TokenConstants.USER_ROLES, [])):
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    #     return True

    def role_any(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)
        for role_in_payload in payload.get(TokenConstants.USER_ROLES, []):
            for role in UserRoleEnum:
                if(role_in_payload==role.value):
                    return True
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
    def get_user_id(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = self.decode_token(token.credentials)
        return payload[TokenConstants.USER_ID]


token_dependency = TokenDependency()
