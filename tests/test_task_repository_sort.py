"""TaskRepository.listのソート機能テスト。"""
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


def test_sort_by_due_date_asc():
    """due_date_ascは期限が近い順に並ぶ。"""
    session = _make_session()
    repo = TaskRepository(session)
    today = date.today()
    repo.create(Task(title="遠い", due_date=today + timedelta(days=10)))
    repo.create(Task(title="近い", due_date=today + timedelta(days=1)))
    repo.create(Task(title="中間", due_date=today + timedelta(days=5)))

    items, _ = repo.list(limit=10, offset=0, sort="due_date_asc")

    assert [item.title for item in items] == ["近い", "中間", "遠い"]


def test_sort_by_due_date_asc_places_null_last():
    """due_date_ascでは期限未設定が最後に来る。"""
    session = _make_session()
    repo = TaskRepository(session)
    today = date.today()
    repo.create(Task(title="期限あり", due_date=today))
    repo.create(Task(title="期限なし"))

    items, _ = repo.list(limit=10, offset=0, sort="due_date_asc")

    assert items[0].title == "期限あり"
    assert items[-1].title == "期限なし"


def test_sort_by_priority_asc():
    """priority_ascは重要→高→中→低の順に並ぶ。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="低優先度", priority="低"))
    repo.create(Task(title="重要", priority="重要"))
    repo.create(Task(title="中優先度", priority="中"))
    repo.create(Task(title="高優先度", priority="高"))

    items, _ = repo.list(limit=10, offset=0, sort="priority_asc")

    assert [item.title for item in items] == [
        "重要",
        "高優先度",
        "中優先度",
        "低優先度",
    ]


def test_sort_default_is_created_at_desc():
    """sort未指定時は登録日新しい順（既定）になる。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="タスク1"))
    repo.create(Task(title="タスク2"))

    items, _ = repo.list(limit=10, offset=0)

    assert items[0].title == "タスク2"
    assert items[-1].title == "タスク1"