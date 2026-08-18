"""priority/statusの列挙型定義。"""
from enum import StrEnum


class TaskPriority(StrEnum):
    """タスクの優先度。表示順：重要→高→中→低。"""

    CRITICAL = "重要"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class TaskStatus(StrEnum):
    """タスクの状態。"""

    NOT_STARTED = "未着手"
    IN_PROGRESS = "対応中"
    ON_HOLD = "保留"
    COMPLETED = "完了"
