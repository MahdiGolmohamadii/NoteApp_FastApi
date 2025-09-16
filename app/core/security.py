from typing import Annotated
from fastapi import Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from .config import settings
from schemas.user import UserBase



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_passwords_hashed(password: str):
    return pwd_context.hash(password)


def check_password(password_entered: str, password_in_Db: str):
    return pwd_context.verify(password_entered, password_in_Db)

def decode_toke(token):
    return UserBase(
        user_name=token+"this should change"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = decode_toke(token=token)
    return user
