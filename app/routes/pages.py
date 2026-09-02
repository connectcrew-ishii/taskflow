"""HTML画面用のルーター。"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.dependencies import get_task_service
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