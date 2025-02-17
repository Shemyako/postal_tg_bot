from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .dbhelper import Base


class Customer(Base):
    __tablename__ = "customers"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[int] = mapped_column(default=0)


class Mail(Base):
    __tablename__ = "mails"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    owner: Mapped[int] = mapped_column(ForeignKey("customers.tg_id"))
    is_active: Mapped[bool] = mapped_column(default=True)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mail_id: Mapped[int] = mapped_column(ForeignKey("mails.id"))
    text: Mapped[str] = mapped_column(String(255))
    from_user: Mapped[str] = mapped_column(String(255))
    date: Mapped[datetime]
