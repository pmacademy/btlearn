from typing import List, Optional
from fastapi.param_functions import Depends, Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from teacher_dashboard.Assignment.dependencies.token_dependency import token_dependency
from teacher_dashboard.notification.notofication_constants import NotificationServiceTypesEnum


class NotificationRequest(BaseModel):
    template_name: str
    field_values: dict
    reciever_email: Optional[EmailStr] = None
    reciever_phone: Optional[str] = None
    modes: List[NotificationServiceTypesEnum]