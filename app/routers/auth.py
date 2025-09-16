from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import get_session
from core.security import get_passwords_hashed, check_password, authenticate_user, create_access_token
from core.config import settings
from models.user import User
from schemas.user import UserInDB
from schemas.token import Token


router = APIRouter(tags=["auth"])


@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[AsyncSession, Depends(get_session)]) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="UserName or password are wrong",
            headers={"WWW-Authenticate": "Bearer"},
            )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.user_name}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
    