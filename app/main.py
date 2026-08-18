"""TaskFlowアプリケーションのエントリーポイント。"""
from fastapi import FastAPI

from app.routes import health

app = FastAPI(title="TaskFlow")

app.include_router(health.router)
