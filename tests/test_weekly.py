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
