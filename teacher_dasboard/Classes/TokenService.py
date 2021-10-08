from yaml.tokens import Token
from config.app_config import get_config
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
from fastapi import Security, status
from teacher_dasboard.Classes.TokenConstants import TokenConstants, ErrorMessage
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization as crypto_serialization
from teacher_dasboard.Classes.User import User

class TokenService:

    def encode_token(self, user: User):

        config = get_config()

        payload = {
            TokenConstants.ISSUE_TIME: datetime.utcnow(),
            TokenConstants.EXPIRY_TIME: datetime.utcnow() + timedelta(days=config.TOKEN_VALIDITY_DAYS, hours=config.TOKEN_VALIDITY_HOURS, minutes=config.TOKEN_VALIDITY_MINUTES),
            TokenConstants.USER_ID: user.uuid,
            TokenConstants.USER_EMAIL: user.email,
            TokenConstants.DISPLAY_NAME: user.display_name,
            # TokenConstants.FULL_NAME: user.full_name,
            # TokenConstants.PROFILE_IMAGE: user.profile_image,
            # TokenConstants.DEFAULT_ROLE: user.default_role,
            # TokenConstants.USER_ROLES: [r.role for r in user.roles]
        }
        return jwt.encode(
            payload,
            key=get_config().PRIVATE_KEY,
            algorithm=TokenConstants.ENCODING_ALGORITHM
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token,
                                 key=get_config().PUBLIC_KEY,
                                 algorithms=[TokenConstants.ENCODING_ALGORITHM])
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessage.INVALID_TOKEN_MESSAGE)

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessage.INVALID_TOKEN_MESSAGE)


# token_service = TokenService()
# user = User(uuid='g8y8hiug6erdt5edrd',email='gfh@jkh.jiu',display_name="jgu hiuh")
# token=token_service.encode_token(user=user)
# print(token)
# if __name__=="__main__":
#     print(token_service.decode_token(token))