from fastapi import APIRouter, Depends, Body, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.core.database import get_session
from app.schemas.user import UserInDB
from app.schemas.notes import NoteInput, NoteOut, NoteUpdate
from app.models.user import User
from app.models.notes import Note


router = APIRouter(tags=["notes"])



@router.get("/notes", response_model=list[NoteOut], status_code=status.HTTP_200_OK)
async def get_all_notes(
                user: Annotated[UserInDB, Depends(get_current_user)], 
                session: Annotated[AsyncSession, Depends(get_session)],):
    result = await session.execute(
        select(User).options(selectinload(User.notes)).where(User.user_name == user.user_name)
    )
    user_obj = result.scalar_one_or_none()
    
    if not user_obj:
        return []
    
    return user_obj.notes
    


@router.post("/notes", status_code=status.HTTP_201_CREATED)
async def add_new_note(
            note_input: Annotated[NoteInput, Body()], 
            user: Annotated[UserInDB, Depends(get_current_user)],
            session: Annotated[AsyncSession, Depends(get_session)]):
    user_db_row = await session.execute(select(User).where(User.user_name == user.user_name))
    user_db = user_db_row.scalar_one()
    new_note = Note(title = note_input.title, 
                    description= note_input.description, 
                    owner_id = user_db.user_id)
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return new_note.note_id


@router.get("/notes/{note_id}", response_model=NoteOut, status_code=status.HTTP_200_OK)
async def get_one_note(
            note_id: int, 
            user: Annotated[UserInDB, Depends(get_current_user)], 
            session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(
        select(Note).where(Note.note_id == note_id, Note.owner_id == user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found in users notes.")
    return note

@router.patch("/notes/{note_id}", response_model=NoteOut, status_code=status.HTTP_202_ACCEPTED)
async def update_note(
                note_id: int, 
                user: Annotated[UserInDB, Depends(get_current_user)], 
                session: Annotated[AsyncSession, Depends(get_session)],
                note_update: Annotated[NoteUpdate, Body()]):
    result = await session.execute(
        select(Note).where(Note.note_id==note_id, Note.owner_id==user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found")
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.description is not None:
        note.description = note_update.description

    await session.commit()
    await session.refresh(note)

    return note

@router.delete("/notes/{note_id}", status_code=status.HTTP_200_OK)
async def delete_note(
                note_id: int, 
                user: Annotated[UserInDB, Depends(get_current_user)], 
                session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(select(Note).where(Note.note_id == note_id, Note.owner_id == user.id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found")
    await session.delete(note)
    await session.commit()
    return {"note id deleted:", note.note_id}

    
    
