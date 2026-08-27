"""TaskRepository一覧取得のテスト。"""
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


def _seed_tasks(session: Session, count: int) -> None:
    """順番の分かるタスクをcount件登録する。"""
    for i in range(count):
        session.add(Task(title=f"タスク{i + 1}"))
        session.commit()


def test_list_returns_empty_when_no_tasks():
    """タスクが0件の場合、空リストとtotal=0を返す。"""
    session = _make_session()
    repo = TaskRepository(session)

    items, total = repo.list(limit=50, offset=0)

    assert items == []
    assert total == 0


def test_list_respects_limit_and_offset():
    """limit/offsetに応じたページングが動作する。"""
    session = _make_session()
    _seed_tasks(session, 5)
    repo = TaskRepository(session)

    page1, total = repo.list(limit=2, offset=0)
    page2, _ = repo.list(limit=2, offset=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert total == 5
    assert {t.id for t in page1}.isdisjoint({t.id for t in page2})


def test_list_orders_by_created_at_desc_by_default():
    """既定では登録日の新しい順に並ぶ。"""
    session = _make_session()
    _seed_tasks(session, 3)
    repo = TaskRepository(session)

    items, _ = repo.list(limit=10, offset=0)

    assert items[0].title == "タスク3"
    assert items[-1].title == "タスク1"


def test_list_orders_by_created_at_asc_when_specified():
    """sort='created_at_asc'指定時は登録日の古い順に並ぶ。"""
    session = _make_session()
    _seed_tasks(session, 3)
    repo = TaskRepository(session)

    items, _ = repo.list(limit=10, offset=0, sort="created_at_asc")

    assert items[0].title == "タスク1"
    assert items[-1].title == "タスク3"


def test_list_total_reflects_full_count_regardless_of_paging():
    """totalはページングに関わらず全件数を返す。"""
    session = _make_session()
    _seed_tasks(session, 7)
    repo = TaskRepository(session)

    _, total = repo.list(limit=3, offset=6)

    assert total == 7