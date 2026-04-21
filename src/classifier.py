"""
Google Gemini APIを使って記事タイトルをカテゴリ分類するモジュール
無料枠: 1,500リクエスト/日、15回/分 (gemini-1.5-flash)
"""
import json
import logging
import time
from typing import Any

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, CATEGORIES

logger = logging.getLogger(__name__)

# カテゴリ説明テキスト
_CATEGORY_DESCRIPTIONS = "\n".join(
    f'- "{key}": {desc}' for key, (_, _, desc) in CATEGORIES.items()
)

_SYSTEM_PROMPT = f"""あなたは半導体・電子部品業界の市場ニュースを分類する専門アナリストです。

以下のカテゴリ定義に従い、記事タイトルを分類してください。

【カテゴリ一覧】
{_CATEGORY_DESCRIPTIONS}

【ルール】
1. 1つの記事に複数カテゴリを付与可能（通常2〜5個）
2. "negative"と"positive"は必ずどちらか一方を選択（センチメント）
3. "other"は他のカテゴリが全く当てはまらない場合のみ使用
4. "pl45_customer"はApple、NVIDIA、AMD、Qualcomm、Broadcom、Intelなど
   TSMCの先端ノード顧客に関するニュースのみ付与
5. 半導体・電子部品業界に無関係なニュースでも分類を行う

必ずJSON形式のみで回答してください（説明文不要）:
{{"categories": ["category_key1", "category_key2"]}}"""

# 無料枠レート: 15回/分 → 1回あたり4秒待機
_INTERVAL_SEC = 4


def classify_articles(articles: list[dict]) -> list[dict]:
    """
    記事リストを分類し、各記事にcategoriesフィールドを追加して返す。
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    results = []

    for i, article in enumerate(articles):
        logger.info(f"分類中 [{i+1}/{len(articles)}]: {article['title'][:40]}...")
        categories = _classify_one(client, article["title"])
        results.append({**article, "categories": categories})
        time.sleep(_INTERVAL_SEC)

    return results


def _classify_one(client: genai.Client, title: str) -> dict[str, Any]:
    category_keys = list(CATEGORIES.keys())

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=f"記事タイトル: {title}",
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                temperature=0.1,
                max_output_tokens=256,
            ),
        )
        raw = response.text.strip()

        # コードブロック除去
        if "```" in raw:
            raw = raw.split("```")[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

        parsed = json.loads(raw)
        assigned = set(parsed.get("categories", []))

    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"分類失敗 '{title[:40]}': {e}")
        assigned = {"other"}

    return {key: (key in assigned) for key in category_keys}
