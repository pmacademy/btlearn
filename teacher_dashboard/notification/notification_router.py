from fastapi import Depends
from sqlalchemy.orm.session import Session
from teacher_dashboard.Students.student_crud import get_user_detail
from teacher_dashboard.database import SessionLocal, engine
from teacher_dashboard import models
from teacher_dashboard.custom_api_router import CustomAPIRouter
import logging
from teacher_dashboard.db_session import db_session, get_db
from teacher_dashboard.Assignment.dependencies.token_dependency import token_dependency
from teacher_dashboard.notification.notification_service import notification_service
from teacher_dashboard.notification.schemas.requests.notification import NotificationRequest


models.Base.metadata.create_all(bind=engine)

router = CustomAPIRouter(
    prefix="/api/v1/notify",
    tags=["Notification"]
)

logger = logging.getLogger(__name__)


@router.post("", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_client)])
async def send_notification(notificationRequest: NotificationRequest, user_id: str = Depends(token_dependency.get_user_id),  db: Session = Depends(get_db)):
    db_session.set(db)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  notificationRequest:{}".format(
        notificationRequest.dict()))

    response = notification_service.send_notification(notificationRequest)

    logger.debug("response: {}".format(response))

    return response
