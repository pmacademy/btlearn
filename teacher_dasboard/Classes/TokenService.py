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


# token_service = TokenService()
# user = User(uuid='g8y8hiug6erdt5edrd',email='gfh@jkh.jiu',display_name="jgu hiuh")
# token=token_service.encode_token(user=user)
# print(token)
# if __name__=="__main__":
#     print(token_service.decode_token(token))