"""TaskFlowアプリケーションのエントリーポイント。"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes import health, task
from app.schemas import ErrorResponse

app = FastAPI(title="TaskFlow")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health.router)
app.include_router(task.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTPExceptionをErrorResponse形式に変換する。"""
    code = "TASK_NOT_FOUND" if exc.status_code == 404 else "ERROR"
    body = ErrorResponse(code=code, message=str(exc.detail), details=None)
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """バリデーションエラーをErrorResponse形式に変換する。"""
    body = ErrorResponse(
        code="VALIDATION_ERROR",
        message="入力内容を確認してください。",
        details=exc.errors(),
    )
    return JSONResponse(status_code=422, content=body.model_dump())