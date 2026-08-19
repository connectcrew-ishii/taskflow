"""DB接続とセッション管理モジュール。

Engine/SessionLocalを定義し、リクエスト単位でセッションを
生成・終了するget_db依存関数を提供する。
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """全モデルの基底クラス。"""


def get_db() -> Generator[Session]:
    """リクエスト単位でDBセッションを生成し、終了時にクローズする。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()