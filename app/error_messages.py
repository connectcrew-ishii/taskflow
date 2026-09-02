"""Pydanticのバリデーションエラーを画面表示用の日本語メッセージに変換する。"""

_FIELD_LABELS = {
    "title": "タイトル",
    "description": "説明",
    "priority": "優先度",
    "status": "状態",
    "due_date": "期限",
}


def _message_for(field_label: str, error_type: str) -> str:
    """エラー種別に応じた日本語メッセージを組み立てる。"""
    if "too_short" in error_type or error_type == "missing":
        return f"{field_label}を入力してください。"
    if "too_long" in error_type:
        return f"{field_label}は文字数の上限を超えています。"
    if "enum" in error_type:
        return f"{field_label}の値が正しくありません。"
    if "date" in error_type:
        return f"{field_label}の形式が正しくありません（YYYY-MM-DD）。"
    return f"{field_label}の入力内容を確認してください。"


def build_field_errors(errors: list[dict]) -> dict[str, str]:
    """Pydanticのerrors()結果を、項目名をキーとする日本語メッセージ辞書に変換する。

    Args:
        errors: pydantic.ValidationError.errors()の戻り値。

    Returns:
        項目名(title, description等)をキー、日本語エラーメッセージを値とする辞書。
    """
    field_errors: dict[str, str] = {}
    for error in errors:
        loc = error.get("loc", ())
        field = str(loc[0]) if loc else "unknown"
        label = _FIELD_LABELS.get(field, field)
        error_type = error.get("type", "")
        field_errors[field] = _message_for(label, error_type)
    return field_errors