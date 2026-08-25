from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
    String(150),
    unique=True,
    nullable=False)

    age: Mapped[int] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=datetime.utcnow)

 