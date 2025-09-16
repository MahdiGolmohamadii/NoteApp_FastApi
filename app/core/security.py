import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from .config import settings
from.database import get_session
from schemas.user import UserBase
from schemas.token import Token, TokenData
from models.user import User
from schemas.user import UserInDB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_passwords_hashed(password: str):
    return pwd_context.hash(password)


def check_password(plain_password: str, hased_password: str):
    return pwd_context.verify(plain_password, hased_password)


async def get_user(session: AsyncSession, username:str):
    user = await session.execute(select(User).where(User.user_name == username))
    user_db = user.scalar_one_or_none()
    if user_db is None:
        return None
    return UserInDB(user_name=user_db.user_name, password=user_db.user_passwor)


async def authenticate_user (user_name: str, password: str, session: AsyncSession):
    result = await session.execute(select(User).where(User.user_name == user_name))
    user_in_db = result.scalar_one_or_none()
    if user_in_db is None:
        return False
    user_in_db = UserInDB(user_name=user_in_db.user_name, password=user_in_db.user_password)
    if not check_password(password, user_in_db.password):
       return False
    return user_in_db


def create_access_token(data: dict, expires_delta: timedelta | None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRETE_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


def decode_toke(token):
    return UserBase(
        user_name=token+"this should change"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[AsyncSession, Depends(get_session)]):
    credential_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRETE_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credential_exception
    user = get_current_user(session=session, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

