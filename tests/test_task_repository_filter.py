"""TaskRepository.listのフィルタ機能テスト。"""
from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Task
from app.repositories import TaskRepository


def _make_session() -> Session:
    """テスト用のインメモリSQLiteセッションを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_filter_by_status():
    """statusで絞り込める。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="タスク1", status="対応中"))
    repo.create(Task(title="タスク2", status="完了"))

    items, total = repo.list(limit=10, offset=0, status="対応中")

    assert total == 1
    assert items[0].status == "対応中"


def test_filter_by_priority():
    """priorityで絞り込める。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="タスク1", priority="高"))
    repo.create(Task(title="タスク2", priority="低"))

    items, total = repo.list(limit=10, offset=0, priority="高")

    assert total == 1
    assert items[0].priority == "高"


def test_filter_by_overdue_excludes_completed():
    """overdueは期限切れかつ未完了のもののみ返す。"""
    session = _make_session()
    repo = TaskRepository(session)
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
    repo.create(Task(title="期限切れ未完了", due_date=yesterday, status="対応中"))
    repo.create(Task(title="期限切れ完了済み", due_date=yesterday, status="完了"))
    repo.create(Task(title="期限内", due_date=tomorrow, status="対応中"))
    repo.create(Task(title="期限なし"))

    items, total = repo.list(limit=10, offset=0, overdue=True)

    assert total == 1
    assert items[0].title == "期限切れ未完了"


def test_filter_combines_status_and_priority():
    """statusとpriorityを組み合わせて絞り込める。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="対象", status="対応中", priority="高"))
    repo.create(Task(title="status違い", status="完了", priority="高"))
    repo.create(Task(title="priority違い", status="対応中", priority="低"))

    items, total = repo.list(limit=10, offset=0, status="対応中", priority="高")

    assert total == 1
    assert items[0].title == "対象"


def test_no_filter_returns_all():
    """フィルタ未指定の場合は全件返る。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="タスク1"))
    repo.create(Task(title="タスク2"))

    items, total = repo.list(limit=10, offset=0)

    assert total == 2