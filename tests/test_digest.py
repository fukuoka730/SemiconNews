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
