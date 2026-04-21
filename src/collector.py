"""
RSSフィードから指定月のニュース記事を収集し、JSONファイルに保存するモジュール
"""
import json
import logging
import sys
from datetime import datetime, timezone
from calendar import monthrange

import feedparser

from config import RSS_FEEDS

logger = logging.getLogger(__name__)


def collect_articles(year: int, month: int) -> list[dict]:
    """指定した年月のニュース記事をRSSから収集する。"""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    articles = []
    seen: set[str] = set()

    for feed_config in RSS_FEEDS:
        fetched = _fetch_feed(feed_config, start, end, seen)
        articles.extend(fetched)
        logger.info(f"{feed_config['name']}: {len(fetched)}件")

    articles.sort(key=lambda a: a["date"], reverse=True)
    logger.info(f"合計: {len(articles)}件収集")
    return articles


def _fetch_feed(feed_config, start, end, seen):
    articles = []
    try:
        feed = feedparser.parse(feed_config["url"])
    except Exception as e:
        logger.warning(f"フィード取得失敗 {feed_config['name']}: {e}")
        return articles

    for entry in feed.entries:
        pub_date = _parse_date(entry)
        if pub_date is None or not (start <= pub_date <= end):
            continue

        title = _clean_title(getattr(entry, "title", ""))
        if not title:
            continue

        key = title.strip().lower()
        if key in seen:
            continue
        seen.add(key)

        articles.append({
            "title": title,
            "date": pub_date.strftime("%Y-%m-%d"),
            "url": getattr(entry, "link", ""),
            "source": feed_config["name"],
        })

    return articles


def _parse_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def _clean_title(title: str) -> str:
    title = title.strip()
    if " - " in title:
        title = title.rsplit(" - ", 1)[0].strip()
    return title


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if len(sys.argv) == 3:
        year, month = int(sys.argv[1]), int(sys.argv[2])
    else:
        now = datetime.now()
        year, month = now.year, now.month

    articles = collect_articles(year, month)

    os.makedirs("data", exist_ok=True)
    out_path = f"data/articles_{year}{month:02d}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"収集完了: {len(articles)}件 → {out_path}")
