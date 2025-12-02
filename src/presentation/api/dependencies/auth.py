from typing import Annotated

from fastapi import Depends, HTTPException, Request

from src.presentation.api.auth.bearer import JWTBearer, decode_jwt


async def user_role(req: Request):
    if not (token := req.headers.get("Authorization").split(" ")[1]):
        raise HTTPException(status_code=500, detail="No token provided")

    payload = decode_jwt(token)
    return payload.user_role


async def user_id(req: Request):
    raw_token = req.headers.get("Authorization")
    if not raw_token or not (token := raw_token.split(" ")[1]):
        raise HTTPException(status_code=401, detail="No token provided")

    payload = decode_jwt(token)
    return payload.get("sub")


UserRole = Annotated[str, Depends(user_role)]
UserId = Annotated[str, Depends(user_id)]
Auth = Depends(JWTBearer(auto_error=False))
