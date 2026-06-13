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
