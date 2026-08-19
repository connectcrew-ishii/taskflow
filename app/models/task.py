"""Taskモデルの定義。"""
from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.database import Base
from app.models.enums import TaskPriority, TaskStatus


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
        String(10), nullable=False, default=TaskPriority.MEDIUM.value, index=True
    )
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default=TaskStatus.NOT_STARTED.value, index=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utc_now, onupdate=_utc_now
    )

    @validates("priority")
    def validate_priority(self, key: str, value: str) -> str:
        """priorityが許可値のいずれかであることを検証する。"""
        if value not in {item.value for item in TaskPriority}:
            raise ValueError(f"不正なpriorityです: {value}")
        return value

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        """statusが許可値のいずれかであることを検証する。"""
        if value not in {item.value for item in TaskStatus}:
            raise ValueError(f"不正なstatusです: {value}")
        return value