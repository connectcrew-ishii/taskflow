"""Taskモデルの定義。"""
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utc_now() -> datetime:
    """タイムゾーン付きの現在時刻(UTC)を返す。"""
    return datetime.now(UTC)


class Task(Base):
    """タスクを表すモデル。"""

    __tablename__ = "task"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(
        String(10), nullable=False, default="中", index=True
    )
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="未着手", index=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now, onupdate=_utc_now
    )
