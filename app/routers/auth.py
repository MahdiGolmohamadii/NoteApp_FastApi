from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import get_session
from core.security import get_passwords_hashed, check_password
from models.user import User
from schemas.user import UserInDB


router = APIRouter(tags=["auth"])


@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(select(User).where(User.user_name == form_data.username))
    user_in_db = result.scalar_one_or_none()
    if user_in_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="username not exists")
    user_in_db = UserInDB(user_name=user_in_db.user_name, password=user_in_db.user_password)
    if not check_password(form_data.password, user_in_db.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password is incorrect")
    
    return {"access_token" : user_in_db.user_name, "token_type": "bearer"}
    