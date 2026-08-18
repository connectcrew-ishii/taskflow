"""Task関連のPydanticスキーマ。"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Taskの共通項目。"""

    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.NOT_STARTED
    due_date: date | None = None


class TaskCreate(TaskBase):
    """タスク登録用スキーマ。"""


class TaskUpdate(TaskBase):
    """タスク更新用スキーマ（全項目更新）。"""


class Task(TaskBase):
    """タスク応答用スキーマ。"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """タスク一覧応答用スキーマ。"""

    items: list[Task]
    total: int = Field(ge=0)
    limit: int
    offset: int
