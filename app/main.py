"""TaskFlowアプリケーションのエントリーポイント。"""
from fastapi import FastAPI

from app.routes import health, task

app = FastAPI(title="TaskFlow")

app.include_router(health.router)
app.include_router(task.router)