from datetime import UTC, datetime
from typing import Union

import jwt
from decouple import config
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

JWT_SECRET_KEY = config("AUTH_JWT_SECRET_KEY")


class Payload(BaseModel):
    sub: str
    aud: str
    exp: int
    iat: int
    email: str
    phone: str
    app_metadata: dict
    user_metadata: dict
    role: str
    aal: str
    amr: list
    session_id: str
    is_anonymous: bool


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, req: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(req)

        if req.headers.get("Authorization") is not None:
            credentials = {}
            credentials["scheme"] = req.headers.get("Authorization").split(" ")[0]
            credentials["credentials"] = req.headers.get("Authorization").split(" ")[1]

            if not credentials["scheme"] == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication credentials"
                )

            if not self.verify_jwt(credentials["credentials"]):
                raise HTTPException(
                    status_code=403, detail="Could not validate credentials"
                )

            return credentials["credentials"]

        if credentials is None:
            raise HTTPException(status_code=403, detail="Not authenticated")

        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid token")

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(
                status_code=403, detail="Could not validate credentials"
            )

        return credentials.credentials

    def verify_jwt(self, token: str) -> tuple[bool, Union[Payload, None]]:
        is_token_valid: bool = False

        try:
            decoded_token = decode_jwt(token)

            exp = decoded_token.get("exp")
            if exp and datetime.now(UTC).timestamp() > exp:
                raise jwt.ExpiredSignatureError()

            decoded_token = Payload.model_validate(decoded_token)
        except Exception as e:
            print(e)
            decoded_token = None

        if decoded_token:
            is_token_valid = True

        return is_token_valid, decoded_token


def sign_jwt(payload: Payload) -> str:
    return jwt.encode(payload.model_dump(), JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt(token: str) -> Payload:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=["HS256", "HS512"],
        audience="authenticated",
    )


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZmU2YWYwNWEtYmQ2MC00MTQ2LWIwYzktZjgwOWJjYmI2YmI0IiwiY29tcGFueV9pZCI6Ijc1Yzk1ZGFjLWFlMWUtNGE4Zi04Yjg4LTExYTY2MTE5ZmJlMiJ9.fhJT01gCOYwPJmR6XemJtAJ6cNjp9V6a2z2hFAa4Xpk
