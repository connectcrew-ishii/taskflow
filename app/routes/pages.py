"""HTML画面用のルーター。"""
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.dependencies import get_task_service
from app.schemas import TaskCreate
from app.services import TaskService
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
        request, "task_form.html", {"mode": "create", "errors": [], "values": {}}
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
                "errors": exc.errors(),
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