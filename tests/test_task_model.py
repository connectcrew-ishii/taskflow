"""Taskモデルのテスト。"""
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Task


def _make_session() -> Session:
    """テスト用のインメモリSQLiteセッションを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_task_created_with_defaults():
    """必須項目のみ指定した場合、既定値が設定される。"""
    session = _make_session()
    task = Task(title="設計書を書く")

    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.id is not None
    assert len(task.id) == 36
    assert task.priority == "中"
    assert task.status == "未着手"
    assert task.description is None
    assert task.due_date is None
    assert task.created_at is not None
    assert task.updated_at is not None


def test_task_with_all_fields():
    """全項目を指定して登録できる。"""
    session = _make_session()
    task = Task(
        title="API設計書を作成する",
        description="OpenAPI仕様を整備する",
        priority="高",
        status="対応中",
        due_date=date(2026, 9, 10),
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.title == "API設計書を作成する"
    assert task.description == "OpenAPI仕様を整備する"
    assert task.priority == "高"
    assert task.status == "対応中"
    assert task.due_date == date(2026, 9, 10)


def test_updated_at_changes_on_update():
    """更新時にupdated_atが変わる。"""
    session = _make_session()
    task = Task(title="読書")
    session.add(task)
    session.commit()
    session.refresh(task)
    original_updated_at = task.updated_at

    task.title = "読書する"
    session.commit()
    session.refresh(task)

    assert task.updated_at >= original_updated_at
