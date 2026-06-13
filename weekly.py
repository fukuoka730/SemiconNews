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
