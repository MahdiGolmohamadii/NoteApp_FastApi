from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base
from .user import User


class Note(Base):
    __tablename__ = "notes"

    note_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)

    owner = relationship('User', back_populates='notes')
