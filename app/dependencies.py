"""ルーター間で共有する依存注入関数。"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import TaskRepository
from app.services import TaskService


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """依存注入用: TaskServiceを組み立てる。"""
    return TaskService(TaskRepository(db))