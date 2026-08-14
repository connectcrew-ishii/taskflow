"""TaskFlowアプリケーションのエントリーポイント（最小構成）。

ルーター登録などの実装はIssue #05で行う。
"""
from fastapi import FastAPI

app = FastAPI(title="TaskFlow")
