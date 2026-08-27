"""Task関連のAPIルーター。"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import TaskRepository
from app.schemas import Task, TaskCreate, TaskListResponse, TaskUpdate
from app.services import TaskNotFoundError, TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

SortOption = Literal[
    "created_at_desc", "created_at_asc", "due_date_asc", "priority_asc"
]


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """依存注入用: TaskServiceを組み立てる。"""
    return TaskService(TaskRepository(db))


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    overdue: bool = Query(default=False),
    sort: SortOption = Query(default="created_at_desc"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    """タスク一覧を取得する。"""
    items, total = service.list_tasks(
        limit=limit,
        offset=offset,
        sort=sort,
        status=status_filter,
        priority=priority,
        overdue=overdue,
    )
    return TaskListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    """タスクを新規登録する。"""
    return service.create_task(data)


@router.get("/search", response_model=TaskListResponse)
def search_tasks(
    q: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    """タイトルの部分一致でタスクを検索する。"""
    items, total = service.search_tasks(q=q, limit=limit, offset=offset)
    return TaskListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> Task:
    """指定したIDのタスクを取得する。"""
    try:
        return service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> Task:
    """指定したIDのタスクを更新する（全項目更新）。"""
    try:
        return service.update_task(task_id, data)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> None:
    """指定したIDのタスクを削除する。"""
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc