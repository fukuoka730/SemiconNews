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
