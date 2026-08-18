"""Task Pydanticスキーマのテスト。"""
from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import Task, TaskCreate, TaskListResponse, TaskUpdate


def test_task_create_with_required_fields_only():
    """titleのみ指定した場合、既定値が適用される。"""
    task = TaskCreate(title="設計書を書く")

    assert task.title == "設計書を書く"
    assert task.priority == "中"
    assert task.status == "未着手"
    assert task.description is None
    assert task.due_date is None


def test_task_create_with_all_fields():
    """全項目を指定して作成できる。"""
    task = TaskCreate(
        title="API設計書を作成する",
        description="OpenAPI仕様を整備する",
        priority="高",
        status="対応中",
        due_date=date(2026, 9, 10),
    )

    assert task.priority == "高"
    assert task.status == "対応中"
    assert task.due_date == date(2026, 9, 10)


def test_task_create_rejects_empty_title():
    """titleが空文字の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_task_create_rejects_title_over_100_chars():
    """titleが101文字の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskCreate(title="あ" * 101)


def test_task_create_accepts_title_at_100_chars_boundary():
    """titleがちょうど100文字は許容される。"""
    task = TaskCreate(title="あ" * 100)

    assert len(task.title) == 100


def test_task_create_rejects_description_over_5000_chars():
    """descriptionが5001文字の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskCreate(title="タスク", description="あ" * 5001)


def test_task_create_rejects_invalid_priority():
    """priorityが許可値以外の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskCreate(title="タスク", priority="不明")


def test_task_create_rejects_invalid_status():
    """statusが許可値以外の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskCreate(title="タスク", status="不明")


def test_task_create_rejects_invalid_date_format():
    """due_dateが不正な日付形式の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskCreate(title="タスク", due_date="2026-13-40")


def test_task_update_requires_title():
    """TaskUpdateもtitleが必須。"""
    with pytest.raises(ValidationError):
        TaskUpdate(priority="高", status="対応中")


def test_task_response_from_attributes():
    """ORM風オブジェクトからTaskスキーマへ変換できる。"""

    class FakeOrmTask:
        id = "11111111-1111-1111-1111-111111111111"
        title = "読書"
        description = None
        priority = "中"
        status = "未着手"
        due_date = None
        created_at = "2026-08-01T00:00:00"
        updated_at = "2026-08-01T00:00:00"

    task = Task.model_validate(FakeOrmTask())

    assert task.id == "11111111-1111-1111-1111-111111111111"
    assert task.title == "読書"


def test_task_list_response_structure():
    """TaskListResponseがitems/total/limit/offsetを持つ。"""
    response = TaskListResponse(items=[], total=0, limit=50, offset=0)

    assert response.items == []
    assert response.total == 0


def test_task_list_response_rejects_negative_total():
    """totalが負数の場合はエラーになる。"""
    with pytest.raises(ValidationError):
        TaskListResponse(items=[], total=-1, limit=50, offset=0)
