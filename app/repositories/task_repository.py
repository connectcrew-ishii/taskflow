"""TaskのDBアクセスを担当するリポジトリ。"""
from __future__ import annotations

from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus

_PRIORITY_ORDER = case(
    (Task.priority == "重要", 1),
    (Task.priority == "高", 2),
    (Task.priority == "中", 3),
    (Task.priority == "低", 4),
)


def _resolve_order_by(sort: str):
    """sort文字列に対応するSQLAlchemyの並び替え式を返す。"""
    if sort == "created_at_asc":
        return Task.created_at.asc()
    if sort == "due_date_asc":
        return Task.due_date.asc().nulls_last()
    if sort == "priority_asc":
        return _PRIORITY_ORDER.asc()
    return Task.created_at.desc()


class TaskRepository:
    """Taskテーブルへのアクセスを提供する。"""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        limit: int,
        offset: int,
        sort: str = "created_at_desc",
        status: str | None = None,
        priority: str | None = None,
        overdue: bool = False,
    ) -> tuple[list[Task], int]:
        """タスク一覧を取得する。

        Args:
            limit: 取得件数の上限。
            offset: 取得開始位置。
            sort: "created_at_desc"(既定), "created_at_asc",
                "due_date_asc", "priority_asc" のいずれか。
            status: 指定した場合、そのstatusのみに絞り込む。
            priority: 指定した場合、そのpriorityのみに絞り込む。
            overdue: Trueの場合、期限切れ（due_date < 今日 かつ 未完了）のみに絞り込む。

        Returns:
            (該当ページのタスク一覧, 絞り込み後の全件数) のタプル。
        """
        base_stmt = select(Task)
        count_stmt = select(func.count()).select_from(Task)

        if status is not None:
            base_stmt = base_stmt.where(Task.status == status)
            count_stmt = count_stmt.where(Task.status == status)

        if priority is not None:
            base_stmt = base_stmt.where(Task.priority == priority)
            count_stmt = count_stmt.where(Task.priority == priority)

        if overdue:
            today = date.today()
            overdue_condition = (
                (Task.due_date.is_not(None))
                & (Task.due_date < today)
                & (Task.status != "完了")
            )
            base_stmt = base_stmt.where(overdue_condition)
            count_stmt = count_stmt.where(overdue_condition)

        order_by = _resolve_order_by(sort)
        items_stmt = base_stmt.order_by(order_by).limit(limit).offset(offset)
        items = list(self._db.scalars(items_stmt).all())

        total = self._db.scalar(count_stmt) or 0

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

    def update(self, task: Task) -> Task:
        """既存タスクの変更を永続化する。

        Args:
            task: 属性を変更済みのTaskインスタンス（get_by_id等で取得したもの）。

        Returns:
            updated_atが更新された状態のTask。
        """
        self._db.commit()
        self._db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        """タスクを削除する。

        Args:
            task: 削除するTaskインスタンス（get_by_id等で取得したもの）。
        """
        self._db.delete(task)
        self._db.commit()

    def search(self, q: str, limit: int, offset: int) -> tuple[list[Task], int]:
        """タイトルの部分一致でタスクを検索する（登録日新しい順）。

        Args:
            q: 検索語（タイトルに部分一致するもの）。
            limit: 取得件数の上限。
            offset: 取得開始位置。

        Returns:
            (該当ページのタスク一覧, 検索条件に一致する全件数) のタプル。
        """
        condition = Task.title.contains(q)

        items_stmt = (
            select(Task)
            .where(condition)
            .order_by(Task.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(self._db.scalars(items_stmt).all())

        total_stmt = select(func.count()).select_from(Task).where(condition)
        total = self._db.scalar(total_stmt) or 0

        return items, total

    def count_by_status(self) -> dict[str, int]:
        """状態ごとのタスク件数を集計する（0件の状態も含む）。

        Returns:
            状態表示値をキー、件数を値とする辞書（TaskStatusの定義順）。
        """
        counts = {s.value: 0 for s in TaskStatus}

        rows = self._db.execute(
            select(Task.status, func.count()).group_by(Task.status)
        ).all()
        for status_value, count in rows:
            counts[status_value] = count

        return counts

    def upcoming(self, limit: int = 5) -> list[Task]:
        """期限が近い未完了タスクを取得する（期限昇順）。

        Args:
            limit: 取得件数の上限。

        Returns:
            期限が設定されており、かつ未完了のタスク一覧（期限が近い順）。
        """
        stmt = (
            select(Task)
            .where(Task.due_date.is_not(None))
            .where(Task.status != "完了")
            .order_by(Task.due_date.asc())
            .limit(limit)
        )
        return list(self._db.scalars(stmt).all())