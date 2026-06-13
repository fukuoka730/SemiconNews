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


def test_html_escapes_special_chars_in_title():
    from src import digest as _d
    from datetime import datetime
    articles = [{
        "title": 'A & B <script> "x"',
        "url": "http://example.com/q?a=1&b=2",
        "date": "2026-06-10",
        "source": "S & P",
        "categories": {"positive": True},
    }]
    _, html = _d.build_html(articles, datetime(2026, 6, 7), datetime(2026, 6, 13))

    # raw special chars must NOT appear unescaped in the title text
    assert "<script>" not in html
    assert "A &amp; B" in html
    assert "&lt;script&gt;" in html
    # url ampersand escaped inside the href attribute
    assert "a=1&amp;b=2" in html
    assert 'href="http://example.com/q?a=1&b=2"' not in html  # unescaped form absent
