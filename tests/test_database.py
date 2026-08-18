"""DB接続とセッション管理のテスト。"""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.database import get_db


def test_get_db_yields_a_session():
    """get_dbはSQLAlchemyのSessionを1つ返す。"""
    gen = get_db()

    db = next(gen)

    assert isinstance(db, Session)

    gen.close()


def test_get_db_closes_session_after_use():
    """ジェネレータ終了時にセッションのcloseが呼ばれる。"""
    gen = get_db()
    db = next(gen)
    db.close = MagicMock()

    with pytest.raises(StopIteration):
        next(gen)

    db.close.assert_called_once()
