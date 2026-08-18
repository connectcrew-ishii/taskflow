"""疎通確認用のヘルスチェックルーター。"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """アプリの起動状態を確認する。"""
    return {"status": "ok"}
