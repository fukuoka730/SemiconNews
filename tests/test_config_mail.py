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
