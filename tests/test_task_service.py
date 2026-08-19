"""TaskServiceのテスト。"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate
from app.services import TaskNotFoundError, TaskService


def _make_service() -> TaskService:
    """テスト用のインメモリDBを使うTaskServiceを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    return TaskService(TaskRepository(session))


def test_create_task_persists_and_returns_task():
    """タスクを登録すると、id等が設定された状態で返る。"""
    service = _make_service()
    data = TaskCreate(title="設計書を書く", priority="高")

    task = service.create_task(data)

    assert task.id is not None
    assert task.title == "設計書を書く"
    assert task.priority == "高"


def test_get_task_returns_created_task():
    """登録したタスクをget_taskで取得できる。"""
    service = _make_service()
    created = service.create_task(TaskCreate(title="読書"))

    task = service.get_task(created.id)

    assert task.title == "読書"


def test_get_task_raises_not_found_for_missing_id():
    """存在しないIDの場合、TaskNotFoundErrorが発生する。"""
    service = _make_service()

    with pytest.raises(TaskNotFoundError):
        service.get_task("11111111-1111-1111-1111-111111111111")


def test_list_tasks_returns_items_and_total():
    """一覧取得でitemsとtotalを返す。"""
    service = _make_service()
    service.create_task(TaskCreate(title="タスク1"))
    service.create_task(TaskCreate(title="タスク2"))

    items, total = service.list_tasks(limit=10, offset=0)

    assert len(items) == 2
    assert total == 2


def test_update_task_changes_fields():
    """更新するとフィールドが変わる。"""
    service = _make_service()
    created = service.create_task(TaskCreate(title="ジムに行く"))
    update_data = TaskUpdate(title="ジムで筋トレ", status="対応中")

    updated = service.update_task(created.id, update_data)

    assert updated.title == "ジムで筋トレ"
    assert updated.status == "対応中"


def test_update_task_raises_not_found_for_missing_id():
    """存在しないIDの更新はTaskNotFoundErrorになる。"""
    service = _make_service()
    update_data = TaskUpdate(title="タスク")

    with pytest.raises(TaskNotFoundError):
        service.update_task("11111111-1111-1111-1111-111111111111", update_data)


def test_delete_task_removes_it():
    """削除後、get_taskでTaskNotFoundErrorになる。"""
    service = _make_service()
    created = service.create_task(TaskCreate(title="英語学習"))

    service.delete_task(created.id)

    with pytest.raises(TaskNotFoundError):
        service.get_task(created.id)


def test_delete_task_raises_not_found_for_missing_id():
    """存在しないIDの削除はTaskNotFoundErrorになる。"""
    service = _make_service()

    with pytest.raises(TaskNotFoundError):
        service.delete_task("11111111-1111-1111-1111-111111111111")
