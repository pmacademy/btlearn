from config.app_config import get_config
from fastapi.exceptions import HTTPException
import jwt
from fastapi import  status
from teacher_dashboard.Constants.token_constants import TokenConstants, ErrorMessage

class TokenService:

    def decode_token(self, token):
        try:
            payload = jwt.decode(token,
                                 key=get_config().PUBLIC_KEY,
                                 algorithms=[TokenConstants.ENCODING_ALGORITHM])
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessage.EXPIRED_TOKEN_MESSAGE)

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessage.INVALID_TOKEN_MESSAGE)


token_service = TokenService()