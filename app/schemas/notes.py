from pydantic import BaseModel


class NoteInput(BaseModel):
    title: str
    description: str | None = None


class NoteInDb(NoteInput):
    note_id: int
    owner_id: int

class NoteOut(NoteInput):
    owner_id: int

