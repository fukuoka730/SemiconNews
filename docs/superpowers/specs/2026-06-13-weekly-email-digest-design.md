# 週刊メール発行機能 設計書

作成日: 2026-06-13

## 目的

既存の「月次Excelレポート生成」機能はそのまま維持しつつ、**週刊で半導体ニュースのHTMLダイジェストをメール送信する**機能を新規追加する。直近7日間に収集した記事を分類し、HTML本文のメールとして配信する。

## 非目標 (Non-Goals)

- 既存の月次機能（`main.py` / `generator.py` のExcel生成）の挙動変更
- メール本文へのExcel添付（今回はHTML本文のみ）
- 配信先のWeb UI管理（環境変数で十分）

## 制約・前提

- **機密情報を外部送信しない**: 配信対象はRSS由来の公開ニュースのみ。固有の社内資料は扱わない。
- **既存ファイルの挙動を変えない**: `classifier.py` / `generator.py` / `main.py` は変更しない（`collector.py` と `config.py` は後方互換を保った追記のみ）。
- **追加依存なし**: メール送信はPython標準ライブラリ（`smtplib` / `email`）のみで実装する。

## 実行起点

- 本番: クラウドのリモートエージェント（Claude Code Remote）が週次で `python weekly.py` を実行。
- ローカル: 手動で `python weekly.py` 実行可能（テスト用）。

### 認証情報・宛先の受け渡し（重要）

`.env` は `.gitignore` で除外されるためクラウドには届かない。コードは常に `os.environ` から読み、

- ローカルテスト → `.env` に記載（`load_dotenv()` が環境変数へ流し込む）
- クラウド本番 → リモートエージェントの環境変数として同名キーを設定

の二経路で同じキーを参照する（既存 `config.py` の `GEMINI_API_KEY` 読み込みと同じ作法）。

## アーキテクチャ

### 新規・変更ファイル

```
weekly.py          [新規] 週次の起点。収集→分類→HTML生成→送信を順に呼ぶ
src/digest.py      [新規] 分類済み記事リスト → HTML本文を組み立てる
src/mailer.py      [新規] HTML本文を汎用SMTPで送信する
src/collector.py   [追記] 期間指定の収集関数を追加。既存month関数はそのラッパに
config.py          [追記] SMTP設定・宛先を環境変数から読む定義を末尾に追加
.env.example       [追記] SMTP系のサンプル行を追加
TASK.md            [追記] 週次手順を月次とは別セクションで追記
```

`classifier.py` / `generator.py` / `main.py` は**変更しない**。

### データフロー

```
weekly.py
  ├─ 直近7日の期間を算出 (now-7日 〜 now, UTC)
  ├─ collector.collect_articles_between(start, end)   # 新関数
  ├─ classifier.classify_articles(articles)           # 既存をそのまま再利用
  ├─ 記事0件 → ログ出力して送信スキップ・正常終了
  ├─ digest.build_html(articles, start, end)          # HTML本文を返す
  └─ mailer.send(subject, html_body)                  # SMTP送信
```

## コンポーネント詳細

### collector.py のリファクタ（後方互換）

現在の `collect_articles(year, month)` の本体（フィード走査・日付フィルタ・重複排除・ソート）を、期間ベースの内部関数 `_collect_between(start, end)` に切り出す。

- 新規公開関数 `collect_articles_between(start: datetime, end: datetime) -> list[dict]` を追加。
- 既存 `collect_articles(year, month)` は、月初〜月末の期間を算出して `_collect_between` を呼ぶラッパにする。
- **月次の出力は現状と完全に同一**であること（回帰テストで担保）。
- 返す辞書の形式は不変: `{title, date, url, source}`。

### digest.py（HTML本文）

`build_html(articles: list[dict], start: datetime, end: datetime) -> tuple[str, str]`
（件名, HTML本文）を返す。

- 件名: `半導体ニュース週報 YYYY/MM/DD〜MM/DD（N件）`
- 本文:
  - 期間と件数のヘッダ
  - 記事リスト（日付降順）。各記事は **タイトル＝URLハイパーリンク**、`negative`（赤）/`positive`（緑）バッジ、日付・ソースを併記。
  - 分類カテゴリ（該当キーの表示名）を小さく添える。
- スマホでも読めるよう、インラインCSSのシンプルなHTML（テーブルまたはリスト）。
- 純粋関数（I/Oなし）にしてテスト容易にする。

### mailer.py（汎用SMTP）

`send(subject: str, html_body: str) -> None`

- 標準ライブラリ `smtplib` + `email.mime.text.MIMEText` のみ。
- 環境変数:
  | キー | 必須 | 説明 |
  |---|---|---|
  | `SMTP_HOST` | ○ | SMTPサーバホスト |
  | `SMTP_PORT` | ○ | ポート（例: 587） |
  | `SMTP_USER` | ○ | 認証ユーザ |
  | `SMTP_PASS` | ○ | 認証パスワード |
  | `SMTP_FROM` | ○ | 送信元アドレス |
  | `MAIL_TO` | ○ | 宛先（カンマ区切りで複数可） |
  | `SMTP_TLS` | 任意 | `starttls`(既定)/`ssl`/`none` |
- 必須変数が欠けていれば明確なエラーで停止。
- 送信失敗時はログに記録し、非ゼロ終了でクラウド側に失敗を伝える。

### config.py 追記

末尾に上記環境変数の読み込みを追加するのみ。既存の `RSS_FEEDS` / `CATEGORIES` / `HEADER_GROUPS` は不変更。

## エラーハンドリング

| 状況 | 挙動 |
|---|---|
| 記事0件 | ログ出力し、**メール送信せず正常終了**（exit 0） |
| SMTP環境変数の欠落 | エラーメッセージを出し非ゼロ終了 |
| SMTP送信失敗 | 例外内容をログに残し非ゼロ終了 |
| 一部RSS取得失敗 | 既存collector同様、警告ログを出してスキップ・継続 |

## テスト

- **collectorリファクタの回帰**: 既存の月次収集結果が変わらないこと（同一入力→同一出力）。
- **digest.build_html**: 既知の記事リストから、リンク・バッジ・件数・件名が想定通り生成されること。0件・negative/positive混在などのケース。
- **mailer.send**: `smtplib.SMTP` をモックし、宛先・件名・Content-Type(html)・本文が正しく渡ること。TLSモード分岐。環境変数欠落時のエラー。
- **weekly 全体**: collector と mailer をモックした結合テスト。0件時は送信が呼ばれないこと。

## TASK.md 追記内容（概要）

- 週次セクションを新設し、環境変数の設定（SMTP_*, MAIL_TO）、`python weekly.py` の実行、scheduleでの週次登録手順を記載。月次セクションは現状維持。
