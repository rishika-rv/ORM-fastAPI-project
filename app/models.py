from datetime import datetime

from sqlalchemy import String, DateTime , Integer, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(
    String(20),
    nullable=True
)

    email: Mapped[str] = mapped_column(
    String(150),
    unique=True,
    nullable=False)

    age: Mapped[int] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String)
    price = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="orders")



