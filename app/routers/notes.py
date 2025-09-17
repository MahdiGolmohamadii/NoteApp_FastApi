from fastapi import APIRouter, Depends, Body
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..core.security import get_current_user
from ..core.database import get_session
from ..schemas.user import UserInDB
from ..schemas.notes import NoteInput, NoteOut
from ..models.user import User
from ..models.notes import Note


router = APIRouter(tags=["notes"])



@router.get("/notes")
async def get_all_notes(user: Annotated[UserInDB, Depends(get_current_user)], session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(
        select(User).options(selectinload(User.notes)).where(User.user_name == user.user_name)
    )
    user_obj = result.scalar_one_or_none()
    
    if not user_obj:
        return []

    notes_list = [
        NoteOut(title=note.title, description = note.description, owner_id=note.owner_id) for note in user_obj.notes
    ]
    return notes_list
    


@router.post("/notes")
async def add_new_note(
            note_input: Annotated[NoteInput, Body()], 
            user: Annotated[UserInDB, Depends(get_current_user)],
            session: Annotated[AsyncSession, Depends(get_session)]
            ):
    user_db_row = await session.execute(select(User).where(User.user_name == user.user_name))
    user_db = user_db_row.scalar_one()
    new_note = Note(title = note_input.title, 
                    description= note_input.description, 
                    owner_id = user_db.user_id)
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return new_note.note_id