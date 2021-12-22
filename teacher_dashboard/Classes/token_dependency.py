from fastapi.exceptions import HTTPException
from fastapi.param_functions import Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from teacher_dashboard.Classes.token_service import token_service
from datetime import datetime
from teacher_dashboard.Constants.token_constants import TokenConstants

from enum import Enum


class UserRoleEnum(str, Enum):
    USER = "user"
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
    DEVELOPER = "developer"
    ADMIN = "admin"
    QUESTION_CREATOR = "question_creator"
    QUESTION_APPROVER = "question_approver"
    ANNOTATION_CREATOR = "annotation_creator"
    ANNOTATION_APPROVER = "annotation_approver"


class TokenDependency:
    security = HTTPBearer()

    def get_token(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        return token.credentials

    def validate_token(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)

        if(payload[TokenConstants.ISSUE_TIME] <= datetime.utcnow().timestamp() < payload[TokenConstants.EXPIRY_TIME]):
            return True

        return False

    def get_roles(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        return payload.get(TokenConstants.USER_ROLES, [])

    def role_teacher(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        if(UserRoleEnum.TEACHER not in payload.get(TokenConstants.USER_ROLES, [])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    def role_student(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        if (UserRoleEnum.STUDENT not in payload.get(TokenConstants.USER_ROLES, [])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    def role_user(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        if(UserRoleEnum.USER not in payload.get(TokenConstants.USER_ROLES, [])):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return True

    def get_email(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        return payload[TokenConstants.USER_EMAIL]

    def get_user_id(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        return payload[TokenConstants.USER_ID]

    def get_display_name(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        payload = token_service.decode_token(token.credentials)
        return payload[TokenConstants.DISPLAY_NAME]


token_dependency = TokenDependency()
