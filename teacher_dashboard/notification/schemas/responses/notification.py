from typing import List, Optional
from pydantic import BaseModel
from pydantic.errors import EmailError
from pydantic.networks import EmailStr
from teacher_dashboard.notification.notofication_constants import NotificationServiceTypesEnum

class NotificationModeResponse(BaseModel):
    reciever_email: Optional[EmailStr] = None
    reciever_phone: Optional[str] = None
    mode: NotificationServiceTypesEnum
    notification_id: str 


class NotificationResponse(BaseModel):
    all_notification_response: List[NotificationModeResponse]