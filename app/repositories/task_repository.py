"""TaskのDBアクセスを担当するリポジトリ。"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    """Taskテーブルへのアクセスを提供する。"""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self, limit: int, offset: int, order: str = "desc"
    ) -> tuple[list[Task], int]:
        """タスク一覧を登録日順で取得する。

        Args:
            limit: 取得件数の上限。
            offset: 取得開始位置。
            order: "desc"（新しい順、既定）または"asc"（古い順）。

        Returns:
            (該当ページのタスク一覧, 全件数) のタプル。
        """
        order_column = (
            Task.created_at.desc() if order == "desc" else Task.created_at.asc()
        )

        items_stmt = select(Task).order_by(order_column).limit(limit).offset(offset)
        items = list(self._db.scalars(items_stmt).all())

        total_stmt = select(func.count()).select_from(Task)
        total = self._db.scalar(total_stmt) or 0

        return items, total

    def get_by_id(self, task_id: str) -> Task | None:
        """指定したIDのタスクを取得する。

        Args:
            task_id: タスクのUUID文字列。

        Returns:
            該当するTask。存在しない場合はNone。
        """
        return self._db.get(Task, task_id)

    def create(self, task: Task) -> Task:
        """タスクを新規登録する。

        Args:
            task: 永続化するTaskインスタンス（id/created_at/updated_atは未設定でよい）。

        Returns:
            id・created_at・updated_atが確定した状態のTask。
        """
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task
