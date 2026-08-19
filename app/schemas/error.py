"""エラー応答用のPydanticスキーマ。"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """統一エラー応答形式。"""

    code: str
    message: str
    details: list[dict] | None = None