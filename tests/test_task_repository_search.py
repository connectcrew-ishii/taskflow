"""TaskRepository.searchのテスト。"""
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


def test_search_returns_only_matching_titles():
    """検索語に一致するタスクだけ返る。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="API設計書を作成する"))
    repo.create(Task(title="読書"))
    repo.create(Task(title="API仕様を確認する"))

    items, total = repo.search(q="API", limit=10, offset=0)

    assert total == 2
    assert {item.title for item in items} == {
        "API設計書を作成する",
        "API仕様を確認する",
    }


def test_search_returns_empty_when_no_match():
    """一致するタスクがなければ空を返す。"""
    session = _make_session()
    repo = TaskRepository(session)
    repo.create(Task(title="読書"))

    items, total = repo.search(q="存在しない語", limit=10, offset=0)

    assert items == []
    assert total == 0


def test_search_respects_limit_and_offset():
    """検索結果にもlimit/offsetが適用される。"""
    session = _make_session()
    repo = TaskRepository(session)
    for i in range(5):
        repo.create(Task(title=f"タスクA{i + 1}"))

    items, total = repo.search(q="タスクA", limit=2, offset=1)

    assert len(items) == 2
    assert total == 5