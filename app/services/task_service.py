"""Taskの業務ロジックを担当するサービス。"""
from app.models import Task
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate
from app.services.exceptions import TaskNotFoundError


class TaskService:
    """Taskに関する業務処理と例外変換を担う。"""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def list_tasks(
        self,
        limit: int,
        offset: int,
        sort: str = "created_at_desc",
        status: str | None = None,
        priority: str | None = None,
        overdue: bool = False,
    ) -> tuple[list[Task], int]:
        """タスク一覧を取得する。"""
        return self._repository.list(
            limit=limit,
            offset=offset,
            sort=sort,
            status=status,
            priority=priority,
            overdue=overdue,
        )

    def search_tasks(self, q: str, limit: int, offset: int) -> tuple[list[Task], int]:
        """タイトルの部分一致でタスクを検索する。"""
        return self._repository.search(q=q, limit=limit, offset=offset)

    def get_task(self, task_id: str) -> Task:
        """指定したIDのタスクを取得する。

        Raises:
            TaskNotFoundError: タスクが存在しない場合。
        """
        task = self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, data: TaskCreate) -> Task:
        """タスクを新規登録する。"""
        task = Task(
            title=data.title,
            description=data.description,
            priority=data.priority.value,
            status=data.status.value,
            due_date=data.due_date,
        )
        return self._repository.create(task)

    def update_task(self, task_id: str, data: TaskUpdate) -> Task:
        """既存タスクを更新する。

        Raises:
            TaskNotFoundError: タスクが存在しない場合。
        """
        task = self.get_task(task_id)
        task.title = data.title
        task.description = data.description
        task.priority = data.priority.value
        task.status = data.status.value
        task.due_date = data.due_date
        return self._repository.update(task)

    def delete_task(self, task_id: str) -> None:
        """タスクを削除する。

        Raises:
            TaskNotFoundError: タスクが存在しない場合。
        """
        task = self.get_task(task_id)
        self._repository.delete(task)