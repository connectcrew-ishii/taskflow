"""Service層の例外定義。"""


class TaskNotFoundError(Exception):
    """指定されたタスクが存在しない場合の例外。"""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"タスクが見つかりません: {task_id}")
