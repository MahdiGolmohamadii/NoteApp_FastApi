from pydantic import BaseModel


class NoteInput(BaseModel):
    title: str
    description: str | None = None


class NoteInDb(NoteInput):
    note_id: int
    owner_id: int

class NoteUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class NoteOut(NoteInput):
    owner_id: int

