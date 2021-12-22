from abc import ABC, abstractmethod
import boto3
from string import Template

from requests.models import HTTPError
from config.app_config import get_config
from teacher_dashboard.notification.notofication_constants import EmailNoticationServiceConstants, NotificationServiceTypesEnum
from teacher_dashboard.notification.schemas.requests.notification import NotificationRequest
from sqlalchemy.orm.session import Session
from fastapi.exceptions import HTTPException
import logging
from botocore.exceptions import ClientError

from teacher_dashboard.notification.schemas.responses.notification import NotificationModeResponse, NotificationResponse

logger = logging.getLogger(__name__)


class Notification(ABC):

    @abstractmethod
    def notify(self,
               template_name: str,
               field_values: dict,
               reciever_email: str = None,
               reciever_phone: str = None):
        pass

    @staticmethod
    def get(notification_service_type: NotificationServiceTypesEnum):
        logger.debug("looking for notification system with mode:{}".format(
            notification_service_type))
        for subclass in Notification.__subclasses__():
            if(subclass.name() == notification_service_type):
                logger.debug("notification mode found")
                return subclass()
        logger.error("notification mode not found. mode:{}".format(
            notification_service_type))


class EmailNotfication(Notification):
    def __init__(self):
        logger.debug("Initializing Email Notification service")

        credentials = get_config()
        session = boto3.Session(
            region_name=credentials.REGION,
            aws_access_key_id=credentials.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY,
        )
        self.ses = session.client("ses")

    @staticmethod
    def name():
        return NotificationServiceTypesEnum.EMAIL

    def notify(self, template_name: str, field_values: dict, reciever_email: str = None, reciever_phone: str = None):
        logger.debug("EmailNotification Notify")

        if(reciever_email == None):
            logger.error("no email id recieved")
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        try:
            header_data = Template(
                EmailNoticationServiceConstants.TEMPLATE_SUBJECT[template_name]).substitute(field_values)
            body_text_data = Template(
                EmailNoticationServiceConstants.TEAMPLATE_BODY[template_name]).substitute(field_values)
            body_html_data = Template(
                EmailNoticationServiceConstants.TEAMPLATE_HTML[template_name]).substitute(field_values)
        except:
            raise HTTPException(500,"enough field values for the template not provided")

        logger.debug("copying base template of email")
        email_message = EmailNoticationServiceConstants.BASE_TEMPLATE.copy()

        logger.debug("updating email text content")
        email_message["Body"]["Text"]["Data"] = body_text_data

        logger.debug("updating email html content")
        email_message["Body"]["Html"]["Data"] = body_html_data

        logger.debug("updating email subject")
        email_message["Subject"]["Data"] = header_data

        email_source = EmailNoticationServiceConstants.SOURCE_EMAIL_ADDRESS[template_name]

        logger.debug("sending email to the user")

        try:
            response = self.ses.send_email(
                Destination={
                    "ToAddresses": [
                        reciever_email
                    ]
                },
                Message=email_message,
                Source=email_source
            )
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
            raise HTTPException(detail="Unable to send email")
        else:
            logger.debug("Email sent! Message ID:")
            return NotificationModeResponse(
                reciever_email =  reciever_email,
                reciever_phone = None,
                mode = self.name(),
                notification_id = response.get("MessageId")
            )


class NotifiicationService:
    def send_notification(self, notificationRequest: NotificationRequest):
        logger.debug("sending notification")

        notification_response = []
        for notification_mode in notificationRequest.modes:
            logger.debug(
                "getting notification system for mode:{}".format(notification_mode))

            notification = Notification.get(notification_mode)

            try:
                response = notification.notify(notificationRequest.template_name,
                                               notificationRequest.field_values,
                                               notificationRequest.reciever_email,
                                               notificationRequest.reciever_phone)
                logger.debug("notification service response response: {}".format(response))
                notification_response.append(response)
            except:
                logger.error("ubnable to notify the user.")
                raise HTTPException(500,detail="unable to notify the user.")

        return NotificationResponse(all_notification_response = notification_response)


notification_service = NotifiicationService()
