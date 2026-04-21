"""
市場ニュースレポート自動生成スクリプト

使い方:
  python main.py              # 今月分を生成
  python main.py 2025 10      # 指定月 (年 月) を生成
"""
import sys
import logging
from datetime import datetime

from config import GEMINI_API_KEY

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
    # 対象年月の決定
    if len(sys.argv) == 3:
        year, month = int(sys.argv[1]), int(sys.argv[2])
    else:
        now = datetime.now()
        year, month = now.year, now.month

    logger.info(f"=== 処理開始: {year}年{month:02d}月 ===")

    # APIキーチェック
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY が設定されていません。.env ファイルを確認してください。")
        sys.exit(1)

    # Step 1: 記事収集
    logger.info("--- Step 1: RSS収集 ---")
    from src.collector import collect_articles
    articles = collect_articles(year, month)

    if not articles:
        logger.warning("記事が0件です。RSSフィードを確認してください。")
        sys.exit(0)

    logger.info(f"収集完了: {len(articles)}件")

    # Step 2: AI分類
    logger.info("--- Step 2: Claude API分類 ---")
    from src.classifier import classify_articles
    classified = classify_articles(articles)
    logger.info(f"分類完了: {len(classified)}件")

    # Step 3: Excel生成
    logger.info("--- Step 3: Excel生成 ---")
    from src.generator import generate_excel
    path = generate_excel(classified, year, month)

    logger.info(f"=== 完了: {path} ===")
    print(f"\n✓ 出力ファイル: {path}")
    print(f"  記事数: {len(classified)}件")


if __name__ == "__main__":
    main()
