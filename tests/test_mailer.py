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
