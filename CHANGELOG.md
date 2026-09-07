# Changelog

このプロジェクトの変更履歴です。[Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) の形式に従います。

## [1.0.0] - 2026-09-07

### Added

- リポジトリ初期化、Python環境・依存関係の設定
- FastAPIエントリーポイント、SQLite接続とセッション管理
- Taskモデル、priority/status列挙型、Alembicマイグレーション
- Task Pydanticスキーマ（文字数・Enum・日付のバリデーション）
- TaskRepository・TaskServiceによるCRUD、検索、フィルタ、ソート、ダッシュボード集計
- JSON API 6エンドポイント（一覧・登録・検索・詳細・更新・削除）
- エラー応答のErrorResponse形式（code/message/details）への統一
- 共通レイアウト、ダッシュボード、タスク一覧（PC表テーブル/モバイルカード）、検索・フィルタUI
- タスク登録・編集フォーム、削除確認モーダル、項目別の日本語バリデーションエラー表示
- Repository/Service単体テスト、API統合テスト
- Ruff/Black設定、GitHub Actions CI
- README（概要・機能・セットアップ手順・スクリーンショット）

[1.0.0]: https://github.com/connectcrew-ishii/taskflow/releases/tag/v1.0.0