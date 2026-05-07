"""
ルールベースで記事タイトルをカテゴリ分類するモジュール (API不要)
キーワードマッチングによる分類。negative/positive は必ずどちらか一方を付与する。
"""
import logging
from typing import Any

from config import CATEGORIES

logger = logging.getLogger(__name__)

# ---- センチメント判定キーワード ----
_NEG_WORDS = [
    "減益", "減収", "赤字", "下落", "縮小", "悪化", "下方修正", "損失",
    "低迷", "不振", "落ち込み", "停止命令", "出荷停止", "禁止", "制裁",
    "禁輸", "撤退", "中断", "遅延", "難航", "リストラ", "人員削減", "倒産",
    "苦戦", "失速", "鈍化", "余剰在庫", "市況悪化", "暴落", "急落",
]

_POS_WORDS = [
    "増益", "増収", "最高益", "過去最高", "好調", "急増", "急伸", "拡大",
    "成長", "上方修正", "黒字転換", "黒字", "回復", "改善", "強化", "増産",
    "受注", "躍進", "復調", "牽引", "新設", "進出", "突破", "達成", "量産",
    "参入", "採択", "選定", "落札", "急騰", "大幅増",
]

# ---- トピック判定キーワード ----
_TOPIC_RULES: dict[str, list[str]] = {
    "economic_index": [
        "PMI", "GDP", "鉱工業生産", "生産指数", "経済指標", "CPI", "景況感",
    ],
    "regional_economy": [
        "熊本", "広島", "北海道", "千歳", "九州", "東北", "地方経済", "地域産業",
    ],
    "gov_project": [
        "NEDO", "JST", "経産省", "経済産業省", "補助金", "国家プロジェクト", "国プロ",
        "政府支援", "公的資金", "助成金", "文科省", "内閣府", "LSTC",
        "次世代半導体等小委員会", "次世代半導体",
    ],
    "tariff": [
        "関税", "輸出規制", "輸出管理", "CHIPS法", "制裁", "禁輸", "EAR",
        "Entity List", "安全保障", "経済安保", "BIS", "出荷停止命令",
        "出荷停止", "対中規制", "米中規制", "対中", "輸出禁止",
    ],
    "pwr_ic_ev": [
        "パワー半導体", "SiC", "GaN", "電気自動車", "インバーター", "IGBT",
        "車載半導体", "xEV", "BEV", "HEV", "パワーデバイス",
    ],
    "ai": [
        "AI", "人工知能", "LLM", "GPU", "生成AI", "機械学習", "深層学習",
        "NVIDIA", "ChatGPT", "推論チップ", "HPC", "データセンター",
        "Blackwell", "Hopper",
    ],
    "qt_optical": [
        "量子コンピュータ", "量子技術", "光電融合", "シリコンフォトニクス",
        "フォトニクス", "量子通信", "量子暗号",
    ],
    "memory": [
        "DRAM", "NAND", "HBM", "フラッシュメモリ", "メモリ半導体",
        "SKハイニックス", "SK Hynix", "マイクロン", "Micron", "メモリ市況",
        "DDR", "LPDDR", "GDDR", "3D NAND", "NORフラッシュ","MRAM","ReRAM", "次世代メモリ", 
        "不揮発性メモリ","サンディスク","SanDisk","KIOXIA","キオクシア","FeRAM",
    ],
    "sensor": [
        "イメージセンサー", "CMOSセンサー", "LiDAR", "ToFセンサー",
        "ソニーセミコン", "ソニーセミコンダクタ", "Sony Semiconductor", "CIS",
        "センサー半導体", "車載センサー", 
    ],
    "3dic_chiplet": [
        "チップレット", "3D IC", "CoWoS", "先端パッケージ", "インターポーザ",
        "SoIC", "ウェーハボンディング", "ファンアウト", "FOPLP", "2.5D", "3Dスタック",
        "EMIB", "InFO", "InFO_oS", "InFO_SoW", "InFO_WLP",
    ],
    "fpd_solar": [
        "液晶", "有機EL", "OLED", "太陽電池", "ペロブスカイト", "ディスプレイ",
        "FPD", "マイクロLED","次世代ディスプレイ","LCD","AMOLED","QLED",
        "LTPS", "IGZO", "JDI", "Japan Display", "ジャパンディスプレイ",
        "シャープディスプレイ","太陽光", "ソーラーパネル", "HTPS", "HMD", "ヘッドマウントディスプレイ",
        "フレキシブル", "ポリシリコン"
    ],
    "material": [
        "フォトレジスト", "レジスト", "特殊ガス", "CMP材料", "絶縁膜",
        "半導体材料", "シリコンウェーハ", "フォトマスク", "研磨材",
    ],
    "eco_sgds": [
        "カーボンニュートラル", "SDGs", "省エネ", "ESG", "脱炭素",
        "再生可能エネルギー", "CO2削減", "グリーン半導体",
    ],
    "production_consumer": [
        "スマートフォン", "スマホ", "PC需要", "家電", "タブレット",
        "需要回復", "在庫調整", "民生向け",
    ],
    "production_equipment": [
        "製造装置", "半導体装置", "露光装置", "ASML", "東京エレクトロン", "アドバンテスト",
        "Advantest", "ラムリサーチ", "Lam Research", "KLA", "CVD装置",
        "エッチング", "検査装置", "設備投資", "TEL",
        "Photo electron Soul",
    ],
    "infrastructure": [
        "工場建設", "新工場", "新拠点", "電力インフラ", "電力供給",
        "ファブ建設", "クリーンルーム", "新棟建設", "液冷データセンター",
    ],
    "consortium": [
        "M&A", "買収", "合併", "アライアンス", "資本提携", "合弁設立",
        "企業統合", "共同出資", "出資合意",
    ],
    "education": [
        "大学", "産学連携", "人材育成プログラム", "共同研究", "論文発表",
        "研究開発拠点", "寄附講座", "奨学金",
    ],
    "human_resource": [
        "採用強化", "採用計画", "中途採用", "雇用創出", "人員削減",
        "リストラ", "希望退職", "人材確保",
    ],
    "stock_earnings": [
        "株価", "時価総額", "決算", "業績", "営業利益", "純利益", "売上高",
        "四半期", "業績予想", "配当", "EPS", "増益", "減益",
    ],
}


def _contains(text: str, keyword: str) -> bool:
    return keyword.lower() in text.lower()


def _classify_one(title: str) -> dict[str, Any]:
    category_keys = list(CATEGORIES.keys())
    assigned: set[str] = set()

    # トピック判定
    for cat, keywords in _TOPIC_RULES.items():
        if any(_contains(title, kw) for kw in keywords):
            assigned.add(cat)

    # センチメント判定（negative / positive は必須）
    neg_score = sum(1 for w in _NEG_WORDS if _contains(title, w))
    pos_score = sum(1 for w in _POS_WORDS if _contains(title, w))

    if neg_score > pos_score:
        assigned.add("negative")
    else:
        assigned.add("positive")  # 同点・0-0 は positive デフォルト

    # トピックが何も当たらなければ other
    if not (assigned - {"positive", "negative"}):
        assigned.add("other")

    return {key: (key in assigned) for key in category_keys}


def classify_articles(articles: list[dict]) -> list[dict]:
    """記事リストを分類し、各記事にcategoriesフィールドを追加して返す。"""
    results = []
    for i, article in enumerate(articles):
        logger.info(f"分類中 [{i+1}/{len(articles)}]: {article['title'][:40]}...")
        categories = _classify_one(article["title"])
        results.append({**article, "categories": categories})
    return results
