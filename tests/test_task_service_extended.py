"""TaskServiceの検索・フィルタ・ソート・集計機能の単体テスト。"""

from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.repositories import TaskRepository
from app.schemas import TaskCreate
from app.services import TaskService


def _make_service() -> TaskService:
    """テスト用のインメモリDBを使うTaskServiceを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    return TaskService(TaskRepository(session))


def test_search_tasks_returns_only_matching_titles():
    """search_tasksがタイトル部分一致の結果のみ返す。"""
    service = _make_service()
    service.create_task(TaskCreate(title="API設計書を作成する"))
    service.create_task(TaskCreate(title="読書"))

    items, total = service.search_tasks(q="API", limit=10, offset=0)

    assert total == 1
    assert items[0].title == "API設計書を作成する"


def test_list_tasks_filters_by_status():
    """list_tasksがstatusで絞り込める。"""
    service = _make_service()
    service.create_task(TaskCreate(title="タスク1", status="対応中"))
    service.create_task(TaskCreate(title="タスク2", status="完了"))

    items, total = service.list_tasks(limit=10, offset=0, status="対応中")

    assert total == 1
    assert items[0].status == "対応中"


def test_list_tasks_filters_by_priority():
    """list_tasksがpriorityで絞り込める。"""
    service = _make_service()
    service.create_task(TaskCreate(title="タスク1", priority="高"))
    service.create_task(TaskCreate(title="タスク2", priority="低"))

    items, total = service.list_tasks(limit=10, offset=0, priority="高")

    assert total == 1
    assert items[0].priority == "高"


def test_list_tasks_filters_by_overdue():
    """list_tasksがoverdueで絞り込める。"""
    service = _make_service()
    yesterday = date.today() - timedelta(days=1)
    service.create_task(TaskCreate(title="期限切れ", due_date=yesterday, status="対応中"))
    service.create_task(TaskCreate(title="期限なし"))

    items, total = service.list_tasks(limit=10, offset=0, overdue=True)

    assert total == 1
    assert items[0].title == "期限切れ"


def test_list_tasks_sorts_by_priority_asc():
    """list_tasksがsort='priority_asc'で優先度順に並ぶ。"""
    service = _make_service()
    service.create_task(TaskCreate(title="低優先度", priority="低"))
    service.create_task(TaskCreate(title="重要", priority="重要"))

    items, _ = service.list_tasks(limit=10, offset=0, sort="priority_asc")

    assert items[0].title == "重要"
    assert items[-1].title == "低優先度"


def test_list_tasks_sorts_by_due_date_asc():
    """list_tasksがsort='due_date_asc'で期限が近い順に並ぶ。"""
    service = _make_service()
    today = date.today()
    service.create_task(TaskCreate(title="遠い", due_date=today + timedelta(days=10)))
    service.create_task(TaskCreate(title="近い", due_date=today + timedelta(days=1)))

    items, _ = service.list_tasks(limit=10, offset=0, sort="due_date_asc")

    assert items[0].title == "近い"
    assert items[-1].title == "遠い"


def test_get_status_counts_includes_all_four_statuses():
    """get_status_countsが4状態すべてを返す(0件含む)。"""
    service = _make_service()
    service.create_task(TaskCreate(title="タスク1", status="未着手"))

    counts = service.get_status_counts()

    assert counts["未着手"] == 1
    assert counts["対応中"] == 0
    assert counts["保留"] == 0
    assert counts["完了"] == 0


def test_get_upcoming_tasks_excludes_completed_and_sorts_by_due_date():
    """get_upcoming_tasksが完了済みを除外し、期限が近い順に返す。"""
    service = _make_service()
    today = date.today()
    service.create_task(TaskCreate(title="完了済み", due_date=today, status="完了"))
    service.create_task(TaskCreate(title="近い", due_date=today + timedelta(days=1)))
    service.create_task(TaskCreate(title="遠い", due_date=today + timedelta(days=5)))

    items = service.get_upcoming_tasks(limit=5)

    assert [item.title for item in items] == ["近い", "遠い"]


def test_get_upcoming_tasks_respects_limit():
    """get_upcoming_tasksがlimitで件数を制限する。"""
    service = _make_service()
    today = date.today()
    for i in range(5):
        service.create_task(TaskCreate(title=f"タスク{i + 1}", due_date=today + timedelta(days=i)))

    items = service.get_upcoming_tasks(limit=2)

    assert len(items) == 2
