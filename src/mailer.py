"""HTML本文を汎用SMTPで送信するモジュール（標準ライブラリのみ）。"""
import logging
import smtplib
from email.mime.text import MIMEText

from config import load_mail_config

logger = logging.getLogger(__name__)

_REQUIRED = ("host", "port", "user", "password", "sender", "to")
_SMTP_TIMEOUT = 30  # 秒。応答のないサーバで無限待機しないため


def send(subject: str, html_body: str) -> None:
    """件名とHTML本文をSMTPで送信する。設定不足や送信失敗は例外を送出。"""
    cfg = load_mail_config()
    missing = [k for k in _REQUIRED if not cfg.get(k)]
    if missing:
        raise RuntimeError(f"SMTP設定が不足しています: {', '.join(missing)}")

    if cfg["tls"] not in ("starttls", "ssl", "none"):
        raise ValueError(f"SMTP_TLS の値が不正です: {cfg['tls']!r}（starttls/ssl/none）")

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = cfg["sender"]
    msg["To"] = ", ".join(cfg["to"])

    _send_smtp(cfg, msg)
    logger.info(f"メール送信完了: 宛先{len(cfg['to'])}件 / 件名「{subject}」")


def _send_smtp(cfg: dict, msg: MIMEText) -> None:
    if cfg["tls"] == "ssl":
        server = smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=_SMTP_TIMEOUT)
    else:
        server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=_SMTP_TIMEOUT)
    try:
        if cfg["tls"] == "starttls":
            server.starttls()
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
    finally:
        server.quit()
