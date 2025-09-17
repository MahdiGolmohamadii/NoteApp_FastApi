from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True)
    user_password: Mapped[str] = mapped_column()

    notes = relationship('Note', back_populates='owner')