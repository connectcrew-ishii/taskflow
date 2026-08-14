"""アプリケーション設定モジュール。

環境変数からDB接続情報等を読み込む。
"""

from dataclasses import dataclass
from functools import lru_cache
import os

DEFAULT_DATABASE_URL = "sqlite:///./taskflow.db"


@dataclass(frozen=True)
class Settings:
    """アプリケーション全体の設定値。"""

    database_url: str


@lru_cache
def get_settings() -> Settings:
    """環境変数から設定を読み込む。

    未設定の場合は開発用の既定値を使用する。
    """
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    return Settings(database_url=database_url)
