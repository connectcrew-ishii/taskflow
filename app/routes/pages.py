"""HTML画面用のルーター。"""
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.dependencies import get_task_service
from app.error_messages import build_field_errors
from app.schemas import TaskCreate, TaskUpdate
from app.services import TaskNotFoundError, TaskService
from app.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    """ダッシュボード画面を表示する。"""
    counts = service.get_status_counts()
    upcoming = service.get_upcoming_tasks(limit=5)
    return templates.TemplateResponse(
        request, "dashboard.html", {"counts": counts, "upcoming": upcoming}
    )


@router.get("/tasks-list", response_class=HTMLResponse)
def task_list_page(
    request: Request,
    q: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    overdue: bool = Query(default=False),
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    """タスク一覧画面を表示する（検索・フィルタ対応）。"""
    if q:
        items, total = service.search_tasks(q=q, limit=100, offset=0)
    else:
        items, total = service.list_tasks(
            limit=100,
            offset=0,
            status=status_filter,
            priority=priority,
            overdue=overdue,
        )
    return templates.TemplateResponse(
        request,
        "task_list.html",
        {
            "items": items,
            "total": total,
            "q": q or "",
            "status_filter": status_filter or "",
            "priority": priority or "",
            "overdue": overdue,
        },
    )


@router.get("/tasks-list/new", response_class=HTMLResponse)
def new_task_form(request: Request) -> HTMLResponse:
    """タスク登録フォームを表示する。"""
    return templates.TemplateResponse(
        request,
        "task_form.html",
        {"mode": "create", "field_errors": {}, "values": {}},
    )


@router.post("/tasks-list/new")
def create_task_from_form(
    request: Request,
    title: str = Form(default=""),
    description: str = Form(default=""),
    priority: str = Form(default="中"),
    status_value: str = Form(default="未着手", alias="status"),
    due_date: str = Form(default=""),
    service: TaskService = Depends(get_task_service),
):
    """フォーム入力からタスクを登録し、一覧画面へリダイレクトする。"""
    try:
        data = TaskCreate(
            title=title,
            description=description or None,
            priority=priority,
            status=status_value,
            due_date=due_date or None,
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "task_form.html",
            {
                "mode": "create",
                "field_errors": build_field_errors(exc.errors()),
                "values": {
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "status": status_value,
                    "due_date": due_date,
                },
            },
            status_code=422,
        )

    service.create_task(data)
    return RedirectResponse(url="/tasks-list", status_code=303)


@router.get("/tasks-list/{task_id}/edit", response_class=HTMLResponse)
def edit_task_form(
    request: Request,
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> HTMLResponse:
    """既存値を表示するタスク編集フォームを表示する。"""
    try:
        task = service.get_task(task_id)
    except TaskNotFoundError:
        return HTMLResponse(
            content="<h1>タスクが見つかりません</h1>", status_code=404
        )

    return templates.TemplateResponse(
        request,
        "task_edit.html",
        {
            "task_id": task.id,
            "field_errors": {},
            "values": {
                "title": task.title,
                "description": task.description or "",
                "priority": task.priority,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else "",
            },
        },
    )


@router.post("/tasks-list/{task_id}/edit")
def update_task_from_form(
    request: Request,
    task_id: str,
    title: str = Form(default=""),
    description: str = Form(default=""),
    priority: str = Form(default="中"),
    status_value: str = Form(default="未着手", alias="status"),
    due_date: str = Form(default=""),
    service: TaskService = Depends(get_task_service),
):
    """フォーム入力からタスクを更新し、一覧画面へリダイレクトする。"""
    try:
        data = TaskUpdate(
            title=title,
            description=description or None,
            priority=priority,
            status=status_value,
            due_date=due_date or None,
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "task_edit.html",
            {
                "task_id": task_id,
                "field_errors": build_field_errors(exc.errors()),
                "values": {
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "status": status_value,
                    "due_date": due_date,
                },
            },
            status_code=422,
        )

    try:
        service.update_task(task_id, data)
    except TaskNotFoundError:
        return HTMLResponse(
            content="<h1>タスクが見つかりません</h1>", status_code=404
        )

    return RedirectResponse(url="/tasks-list", status_code=303)