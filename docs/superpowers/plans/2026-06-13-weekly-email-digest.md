# 週刊メール発行機能 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 既存の月次Excel機能はそのままに、直近7日間の半導体ニュースをHTMLダイジェストとして汎用SMTPでメール送信する週刊機能を追加する。

**Architecture:** 既存 `collector`/`classifier` を再利用し、新規に `weekly.py`（起点）・`src/digest.py`（HTML生成）・`src/mailer.py`（SMTP送信）を追加。`collector.py` は期間指定の収集関数を追加し既存month関数はそのラッパに、`config.py` はSMTP設定の読み込み関数を追記。`classifier.py`/`generator.py`/`main.py` は変更しない。

**Tech Stack:** Python 3.12（`py` ランチャ）、pytest、標準ライブラリ `smtplib`/`email`（メール送信に追加依存なし）、既存の feedparser/openpyxl/python-dotenv。

**Runner note:** このマシンでは `python` はMicrosoft Storeスタブ。**必ず `py` ランチャを使う**（例: `py -m pytest`）。

---

### Task 0: テスト基盤のセットアップ

**Files:**
- Create: `conftest.py`（プロジェクトルート、空ファイル。pytestがルートをsys.pathに載せるため）
- Create: `tests/__init__.py` は作らない（tests配下はパッケージ化しない）

- [ ] **Step 1: 開発・実行依存をインストール**

Run:
```bash
py -m pip install pytest feedparser openpyxl python-dotenv
```
Expected: `Successfully installed ... pytest ...`（既にある分はスキップ）

- [ ] **Step 2: ルートに空の conftest.py を作成**

`conftest.py`（内容は空でよい。存在することで pytest がプロジェクトルートを sys.path に追加し、`import config` / `import weekly` / `import src.collector` が解決できる）:
```python
# pytest がプロジェクトルートを sys.path に載せるためのマーカー
```

- [ ] **Step 3: tests ディレクトリを作成し、疎通テストを書く**

`tests/test_smoke.py`:
```python
def test_imports_work():
    import config
    import src.collector  # noqa: F401
    assert hasattr(config, "RSS_FEEDS")
```

- [ ] **Step 4: テスト実行して通ることを確認**

Run: `py -m pytest tests/test_smoke.py -v`
Expected: PASS（1 passed）

- [ ] **Step 5: Commit**

```bash
git add conftest.py tests/test_smoke.py
git commit -m "test: pytest基盤と疎通テストを追加"
```

---

### Task 1: collector に期間指定の収集関数を追加（後方互換）

**Files:**
- Modify: `src/collector.py:17-33`
- Test: `tests/test_collector.py`

- [ ] **Step 1: 失敗するテストを書く（月次ラッパの委譲＋期間フィルタ）**

`tests/test_collector.py`:
```python
import time
import types
from datetime import datetime, timezone

from src import collector


def test_collect_articles_delegates_with_month_bounds(monkeypatch):
    """既存の月次関数が、月初〜月末の期間で新関数に委譲することを保証（回帰）。"""
    captured = {}

    def fake_between(start, end):
        captured["start"] = start
        captured["end"] = end
        return ["sentinel"]

    monkeypatch.setattr(collector, "collect_articles_between", fake_between)

    result = collector.collect_articles(2026, 4)

    assert result == ["sentinel"]
    assert captured["start"] == datetime(2026, 4, 1, tzinfo=timezone.utc)
    assert captured["end"] == datetime(2026, 4, 30, 23, 59, 59, tzinfo=timezone.utc)


def _entry(title, y, m, d):
    return types.SimpleNamespace(
        title=title,
        link=f"http://example.com/{title}",
        published_parsed=time.struct_time((y, m, d, 12, 0, 0, 0, 0, 0)),
    )


def test_collect_between_filters_and_dedups(monkeypatch):
    feed = types.SimpleNamespace(entries=[
        _entry("in range", 2026, 6, 10),
        _entry("out of range", 2026, 5, 1),
        _entry("in range", 2026, 6, 11),  # タイトル重複
    ])
    monkeypatch.setattr(collector.feedparser, "parse", lambda url: feed)
    monkeypatch.setattr(collector, "RSS_FEEDS", [{"url": "x", "name": "test"}])

    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    end = datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc)
    result = collector.collect_articles_between(start, end)

    titles = [a["title"] for a in result]
    assert titles == ["in range"]  # 期間外除外＋重複排除で1件
```

- [ ] **Step 2: テスト実行して失敗を確認**

Run: `py -m pytest tests/test_collector.py -v`
Expected: FAIL（`AttributeError: module 'src.collector' has no attribute 'collect_articles_between'`）

- [ ] **Step 3: collector.py をリファクタ**

`src/collector.py` の現在の `collect_articles`（17〜33行）を、次の2関数に置き換える:
```python
def collect_articles_between(start: datetime, end: datetime) -> list[dict]:
    """指定期間 [start, end] のニュース記事をRSSから収集する。"""
    articles = []
    seen: set[str] = set()

    for feed_config in RSS_FEEDS:
        fetched = _fetch_feed(feed_config, start, end, seen)
        articles.extend(fetched)
        logger.info(f"{feed_config['name']}: {len(fetched)}件")

    articles.sort(key=lambda a: a["date"], reverse=True)
    logger.info(f"合計: {len(articles)}件収集")
    return articles


def collect_articles(year: int, month: int) -> list[dict]:
    """指定した年月のニュース記事をRSSから収集する。"""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return collect_articles_between(start, end)
```
（`_fetch_feed`/`_parse_date`/`_clean_title` と import 群は変更しない。）

- [ ] **Step 4: テスト実行して通ることを確認**

Run: `py -m pytest tests/test_collector.py -v`
Expected: PASS（2 passed）

- [ ] **Step 5: Commit**

```bash
git add src/collector.py tests/test_collector.py
git commit -m "feat: collectorに期間指定収集 collect_articles_between を追加"
```

---

### Task 2: config に SMTP 設定読み込み関数を追加

**Files:**
- Modify: `config.py`（末尾に追記）
- Test: `tests/test_config_mail.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_config_mail.py`:
```python
import config


def test_load_mail_config_parses_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASS", "secret")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.setenv("SMTP_TLS", "ssl")
    monkeypatch.setenv("MAIL_TO", "a@x.com, b@y.com ,")

    cfg = config.load_mail_config()

    assert cfg["host"] == "smtp.example.com"
    assert cfg["port"] == 465
    assert cfg["user"] == "user"
    assert cfg["password"] == "secret"
    assert cfg["sender"] == "from@example.com"
    assert cfg["tls"] == "ssl"
    assert cfg["to"] == ["a@x.com", "b@y.com"]  # 空要素は除去


def test_load_mail_config_defaults(monkeypatch):
    for k in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
              "SMTP_FROM", "SMTP_TLS", "MAIL_TO"):
        monkeypatch.delenv(k, raising=False)

    cfg = config.load_mail_config()

    assert cfg["port"] == 587          # 既定ポート
    assert cfg["tls"] == "starttls"    # 既定TLS
    assert cfg["to"] == []
```

- [ ] **Step 2: テスト実行して失敗を確認**

Run: `py -m pytest tests/test_config_mail.py -v`
Expected: FAIL（`AttributeError: module 'config' has no attribute 'load_mail_config'`）

- [ ] **Step 3: config.py の末尾に追記**

`config.py` の末尾（`HEADER_GROUPS` 定義の後）に追加:
```python


# ---- 週刊メール (SMTP) 設定 ----
# 値は環境変数から都度読む（ローカルは .env、クラウドはエージェントの環境変数）。
def load_mail_config() -> dict:
    """SMTP送信に必要な設定を環境変数から読み込んで返す。"""
    return {
        "host": os.environ.get("SMTP_HOST", ""),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASS", ""),
        "sender": os.environ.get("SMTP_FROM", ""),
        "tls": os.environ.get("SMTP_TLS", "starttls"),  # starttls / ssl / none
        "to": [a.strip() for a in os.environ.get("MAIL_TO", "").split(",") if a.strip()],
    }
```
（`import os` は既に1行目にあるため不要。既存定義は一切変更しない。）

- [ ] **Step 4: テスト実行して通ることを確認**

Run: `py -m pytest tests/test_config_mail.py -v`
Expected: PASS（2 passed）

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config_mail.py
git commit -m "feat: configにSMTP設定読み込み load_mail_config を追加"
```

---

### Task 3: digest.py（HTML本文生成）

**Files:**
- Create: `src/digest.py`
- Test: `tests/test_digest.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_digest.py`:
```python
from datetime import datetime

from src import digest


def test_subject_contains_period_and_count():
    start = datetime(2026, 6, 7)
    end = datetime(2026, 6, 13)
    subject, html = digest.build_html([], start, end)

    assert "0件" in subject
    assert "2026/06/07" in subject
    assert "06/13" in subject


def test_html_renders_link_badge_and_topics():
    articles = [{
        "title": "SiC増産を発表",
        "url": "http://example.com/1",
        "date": "2026-06-10",
        "source": "EE Times Japan",
        "categories": {"positive": True, "pwr_ic_ev": True},
    }]
    start = datetime(2026, 6, 7)
    end = datetime(2026, 6, 13)
    subject, html = digest.build_html(articles, start, end)

    assert "1件" in subject
    assert 'href="http://example.com/1"' in html
    assert "SiC増産を発表" in html
    assert "Positive" in html
    assert "Pwr IC/EV" in html  # トピック表示名（改行除去済み）


def test_html_marks_negative():
    articles = [{
        "title": "減益で下方修正",
        "url": "",
        "date": "2026-06-09",
        "source": "x",
        "categories": {"negative": True},
    }]
    _, html = digest.build_html(articles, datetime(2026, 6, 7), datetime(2026, 6, 13))

    assert "Negative" in html
    assert "減益で下方修正" in html  # URLなしでもタイトルは出る
```

- [ ] **Step 2: テスト実行して失敗を確認**

Run: `py -m pytest tests/test_digest.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'src.digest'`）

- [ ] **Step 3: src/digest.py を作成**

`src/digest.py`:
```python
"""分類済み記事リストから週刊ダイジェストのHTML本文を組み立てるモジュール。"""
from datetime import datetime

from config import CATEGORIES


def build_html(articles: list[dict], start: datetime, end: datetime) -> tuple[str, str]:
    """(件名, HTML本文) を返す。純粋関数（I/Oなし）。"""
    period = f"{start.strftime('%Y/%m/%d')}〜{end.strftime('%m/%d')}"
    subject = f"半導体ニュース週報 {period}（{len(articles)}件）"

    items = "\n".join(_render_article(a) for a in articles)
    html = (
        "<html><body style=\"font-family:'Yu Gothic',sans-serif;color:#222;\">"
        "<h2>半導体ニュース週報</h2>"
        f"<p>{period} / 全{len(articles)}件</p>"
        "<ul style=\"list-style:none;padding:0;\">"
        f"{items}"
        "</ul>"
        "</body></html>"
    )
    return subject, html


def _badge(article: dict) -> str:
    cats = article.get("categories", {})
    if cats.get("negative"):
        return ('<span style="background:#FFE0E0;padding:2px 6px;'
                'border-radius:3px;font-size:0.85em;">Negative</span>')
    return ('<span style="background:#E2EFDA;padding:2px 6px;'
            'border-radius:3px;font-size:0.85em;">Positive</span>')


def _topic_labels(article: dict) -> str:
    cats = article.get("categories", {})
    names = [
        disp.replace("\n", "")
        for key, (_, disp, _) in CATEGORIES.items()
        if key not in ("negative", "positive", "other") and cats.get(key)
    ]
    return " / ".join(names)


def _render_article(article: dict) -> str:
    title = article.get("title", "")
    url = article.get("url", "")
    date = article.get("date", "")
    source = article.get("source", "")

    link = f'<a href="{url}">{title}</a>' if url else title
    topics = _topic_labels(article)
    topics_html = (
        f' <span style="color:#888;font-size:0.85em;">[{topics}]</span>'
        if topics else ""
    )
    return (
        '<li style="margin-bottom:10px;">'
        f"{_badge(article)} {link}{topics_html}"
        f'<br><span style="color:#888;font-size:0.85em;">{date} / {source}</span>'
        "</li>"
    )
```

- [ ] **Step 4: テスト実行して通ることを確認**

Run: `py -m pytest tests/test_digest.py -v`
Expected: PASS（3 passed）

- [ ] **Step 5: Commit**

```bash
git add src/digest.py tests/test_digest.py
git commit -m "feat: 週刊ダイジェストのHTML生成 digest.build_html を追加"
```

---

### Task 4: mailer.py（汎用SMTP送信）

**Files:**
- Create: `src/mailer.py`
- Test: `tests/test_mailer.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_mailer.py`:
```python
import pytest

from src import mailer

_REQUIRED_ENV = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER",
                 "SMTP_PASS", "SMTP_FROM", "MAIL_TO")


def _set_full_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.test")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "u")
    monkeypatch.setenv("SMTP_PASS", "p")
    monkeypatch.setenv("SMTP_FROM", "from@test")
    monkeypatch.setenv("MAIL_TO", "to@test")
    monkeypatch.setenv("SMTP_TLS", "starttls")


def test_send_raises_when_config_missing(monkeypatch):
    for k in _REQUIRED_ENV + ("SMTP_TLS",):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(RuntimeError):
        mailer.send("件名", "<p>本文</p>")


def test_send_builds_and_sends_message(monkeypatch):
    _set_full_env(monkeypatch)
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port):
            sent["host"] = host
            sent["port"] = port

        def starttls(self):
            sent["starttls"] = True

        def login(self, user, password):
            sent["login"] = (user, password)

        def send_message(self, msg):
            sent["msg"] = msg

        def quit(self):
            sent["quit"] = True

    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)

    mailer.send("件名", "<p>本文</p>")

    assert sent["host"] == "smtp.test"
    assert sent["port"] == 587
    assert sent["starttls"] is True
    assert sent["login"] == ("u", "p")
    assert sent["quit"] is True

    msg = sent["msg"]
    assert msg["Subject"] == "件名"
    assert msg["From"] == "from@test"
    assert msg["To"] == "to@test"
    assert msg.get_content_type() == "text/html"
```

- [ ] **Step 2: テスト実行して失敗を確認**

Run: `py -m pytest tests/test_mailer.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'src.mailer'`）

- [ ] **Step 3: src/mailer.py を作成**

`src/mailer.py`:
```python
"""HTML本文を汎用SMTPで送信するモジュール（標準ライブラリのみ）。"""
import logging
import smtplib
from email.mime.text import MIMEText

from config import load_mail_config

logger = logging.getLogger(__name__)

_REQUIRED = ("host", "port", "user", "password", "sender", "to")


def send(subject: str, html_body: str) -> None:
    """件名とHTML本文をSMTPで送信する。設定不足や送信失敗は例外を送出。"""
    cfg = load_mail_config()
    missing = [k for k in _REQUIRED if not cfg.get(k)]
    if missing:
        raise RuntimeError(f"SMTP設定が不足しています: {', '.join(missing)}")

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = cfg["sender"]
    msg["To"] = ", ".join(cfg["to"])

    _send_smtp(cfg, msg)
    logger.info(f"メール送信完了: 宛先{len(cfg['to'])}件 / 件名「{subject}」")


def _send_smtp(cfg: dict, msg: MIMEText) -> None:
    if cfg["tls"] == "ssl":
        server = smtplib.SMTP_SSL(cfg["host"], cfg["port"])
    else:
        server = smtplib.SMTP(cfg["host"], cfg["port"])
    try:
        if cfg["tls"] == "starttls":
            server.starttls()
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
    finally:
        server.quit()
```

- [ ] **Step 4: テスト実行して通ることを確認**

Run: `py -m pytest tests/test_mailer.py -v`
Expected: PASS（2 passed）

- [ ] **Step 5: Commit**

```bash
git add src/mailer.py tests/test_mailer.py
git commit -m "feat: 汎用SMTP送信 mailer.send を追加"
```

---

### Task 5: weekly.py（週次の起点）

**Files:**
- Create: `weekly.py`
- Test: `tests/test_weekly.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_weekly.py`:
```python
import weekly


def test_weekly_skips_send_when_no_articles(monkeypatch):
    monkeypatch.setattr("src.collector.collect_articles_between", lambda s, e: [])
    sent = []
    monkeypatch.setattr("src.mailer.send", lambda subject, html: sent.append(subject))

    weekly.main()

    assert sent == []  # 0件なら送信しない


def test_weekly_sends_when_articles_exist(monkeypatch):
    articles = [{
        "title": "テスト記事",
        "url": "http://example.com/1",
        "date": "2026-06-10",
        "source": "test",
    }]
    monkeypatch.setattr("src.collector.collect_articles_between", lambda s, e: articles)
    sent = []
    monkeypatch.setattr("src.mailer.send", lambda subject, html: sent.append((subject, html)))

    weekly.main()

    assert len(sent) == 1
    subject, html = sent[0]
    assert "1件" in subject
    assert "テスト記事" in html
```

- [ ] **Step 2: テスト実行して失敗を確認**

Run: `py -m pytest tests/test_weekly.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'weekly'`）

- [ ] **Step 3: weekly.py を作成**

プロジェクトルートに `weekly.py`:
```python
"""週刊ニュースダイジェストをメール送信するスクリプト。

使い方:
  py weekly.py        # 直近7日分のダイジェストを生成して送信
"""
import logging
from datetime import datetime, timedelta, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("run.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    logger.info(f"=== 週刊ダイジェスト: {start.date()} 〜 {end.date()} ===")

    from src.collector import collect_articles_between
    articles = collect_articles_between(start, end)
    logger.info(f"収集: {len(articles)}件")

    if not articles:
        logger.info("対象記事が0件のため送信をスキップします。")
        return

    from src.classifier import classify_articles
    classified = classify_articles(articles)

    from src.digest import build_html
    subject, html = build_html(classified, start, end)

    from src.mailer import send
    send(subject, html)
    logger.info(f"=== 送信完了: {subject} ===")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: テスト実行して通ることを確認**

Run: `py -m pytest tests/test_weekly.py -v`
Expected: PASS（2 passed）

- [ ] **Step 5: 全テストを実行して回帰がないことを確認**

Run: `py -m pytest -v`
Expected: 全テスト PASS（Task 0〜5 の全件）

- [ ] **Step 6: Commit**

```bash
git add weekly.py tests/test_weekly.py
git commit -m "feat: 週刊メールの起点 weekly.py を追加"
```

---

### Task 6: ドキュメント・設定サンプルの追記

**Files:**
- Modify: `.env.example`（SMTP系サンプルを追記）
- Modify: `TASK.md`（週次セクションを追記）

- [ ] **Step 1: .env.example に SMTP サンプルを追記**

`.env.example` の末尾に追加（既存のGEMINI行は残す）:
```
# 週刊メール (SMTP) 設定
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-user
SMTP_PASS=your-password
SMTP_FROM=from@example.com
SMTP_TLS=starttls
MAIL_TO=recipient1@example.com,recipient2@example.com
```

- [ ] **Step 2: TASK.md に週次セクションを追記**

`TASK.md` の末尾（Excel仕様の後）に新セクションを追加:
```markdown

---

## 週刊メール発行（月次とは独立）

### 実行環境

クラウドのリモートエージェントが週次で `py weekly.py`（ローカルでは `python weekly.py`）を実行する。
SMTP認証情報と宛先は **環境変数** で渡す（`.env` はクラウドに届かないため）。

| 環境変数 | 説明 |
|---|---|
| SMTP_HOST | SMTPサーバホスト |
| SMTP_PORT | ポート（既定587） |
| SMTP_USER | 認証ユーザ |
| SMTP_PASS | 認証パスワード |
| SMTP_FROM | 送信元アドレス |
| SMTP_TLS | starttls(既定)/ssl/none |
| MAIL_TO | 宛先（カンマ区切りで複数可） |

### 処理手順

```bash
python weekly.py
```

スクリプトが以下を自動実行する:
1. **RSS収集**: 直近7日間の記事を収集（`collect_articles_between`）
2. **ルールベース分類**: 既存の23カテゴリ分類を再利用
3. **HTML生成**: ダイジェスト本文を組み立て
4. **メール送信**: 汎用SMTPでHTMLメールを配信

対象記事が0件の週は送信をスキップして正常終了する。
```

- [ ] **Step 3: 全テストを実行（ドキュメント変更で壊れていないこと）**

Run: `py -m pytest -v`
Expected: 全テスト PASS

- [ ] **Step 4: Commit**

```bash
git add .env.example TASK.md
git commit -m "docs: 週刊メール機能の手順とSMTP設定サンプルを追記"
```

---

## 完了条件

- `py -m pytest -v` が全件PASS
- `py weekly.py` が（SMTP環境変数を設定すれば）直近7日のダイジェストを送信し、0件の週はスキップする
- 既存の `py main.py` / 月次Excel生成の挙動が変わっていない（collector回帰テストで担保）
- `classifier.py` / `generator.py` / `main.py` は未変更
