import jwt
import time
from fastapi import HTTPException
import secrets

from plyer import email

jwt_Secret_key = secrets.token_hex(16)
jwt_Algorithm = "HS256"
access_token_expiry  = 15 * 60 # 30min
refresh_token_expiry = 7 * 24 * 60 * 60  # 7 days


print(jwt_Secret_key)


# Generate access and refresh tokens
def create_access_token(email: str):
    payload = {
        "email": email,
        "exp": time.time() + access_token_expiry,
        "type": "access"
    }

    token = jwt.encode(payload, jwt_Secret_key, algorithm=jwt_Algorithm)

    return token

def create_refresh_token(email: str):
    payload = {
        "email" : email,
        "exp" : time.time() + refresh_token_expiry,
        "type" : "refresh"
    }
    re_fresh_token = jwt.encode(payload, jwt_Secret_key, algorithm=jwt_Algorithm)

    return re_fresh_token


def decode(token):
    try:
        decoded_token = jwt.decode(token, jwt_Secret_key, algorithm=[jwt_Algorithm])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

