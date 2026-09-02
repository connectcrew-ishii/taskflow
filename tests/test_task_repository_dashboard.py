"""TaskRepositoryのダッシュボード集計機能のテスト。"""
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


def test_count_by_status_includes_zero_counts():
    """タスクがなくても4状態すべてが0件として返る。"""
    session = _make_session()
    repo = TaskRepository(session)

    counts = repo.count_by_status()

    assert counts == {"未着手": 0, "対応中": 0, "保留": 0, "完了": 0}


def test_count_by_status_reflects_actual_counts():
    """実際の件数が状態別に集計される。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="タスク1", status="未着手"))
    repo.create(Task(title="タスク2", status="未着手"))
    repo.create(Task(title="タスク3", status="完了"))

    counts = repo.count_by_status()

    assert counts["未着手"] == 2
    assert counts["完了"] == 1
    assert counts["対応中"] == 0
    assert counts["保留"] == 0


def test_upcoming_returns_tasks_ordered_by_due_date():
    """期限が近い順に未完了タスクが返る。"""
    session = _make_session()
    repo = TaskRepository(session)
    today = date.today()
    repo.create(Task(title="遠い", due_date=today + timedelta(days=10)))
    repo.create(Task(title="近い", due_date=today + timedelta(days=1)))

    items = repo.upcoming(limit=5)

    assert [item.title for item in items] == ["近い", "遠い"]


def test_upcoming_excludes_completed_tasks():
    """完了済みタスクは期限が近いタスクに含まれない。"""
    session = _make_session()
    repo = TaskRepository(session)
    today = date.today()
    repo.create(Task(title="完了済み", due_date=today, status="完了"))
    repo.create(Task(title="未完了", due_date=today, status="対応中"))

    items = repo.upcoming(limit=5)

    assert [item.title for item in items] == ["未完了"]


def test_upcoming_excludes_tasks_without_due_date():
    """期限未設定のタスクは含まれない。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="期限なし"))

    items = repo.upcoming(limit=5)

    assert items == []


def test_upcoming_respects_limit():
    """limitで件数が制限される。"""
    session = _make_session()
    repo = TaskRepository(session)
    today = date.today()
    for i in range(10):
        repo.create(Task(title=f"タスク{i + 1}", due_date=today + timedelta(days=i)))

    items = repo.upcoming(limit=3)

    assert len(items) == 3