import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 出力先ディレクトリ
OUTPUT_DIR = "output"

# RSSフィード定義
# Google News RSSはキーワード検索で日本語ニュースを取得
RSS_FEEDS = [
    {
        "url": "https://eetimes.itmedia.co.jp/rss/eetimes.xml",
        "name": "EE Times Japan",
    },
    {
        "url": "https://ednjapan.com/edn/rss/",
        "name": "EDN Japan",
    },
    {
        "url": "https://www.semiconductorportal.com/archive/rss.xml",
        "name": "Semiconductor Portal",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E5%8D%8A%E5%B0%8E%E4%BD%93+%E5%B8%82%E5%A0%B4&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - 半導体市場",
    },
    {
        "url": "https://news.google.com/rss/search?q=AI%E5%8D%8A%E5%B0%8E%E4%BD%93+%E6%8A%95%E8%B3%87&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - AI半導体",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E5%8D%8A%E5%B0%8E%E4%BD%93+%E6%B1%BA%E7%AE%97+%E6%A5%AD%E7%B8%BE&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - 半導体決算",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E9%9B%BB%E5%AD%90%E9%83%A8%E5%93%81+%E5%B8%82%E5%A0%B4+%E7%94%9F%E7%94%A3&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - 電子部品市場",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E5%8D%8A%E5%B0%8E%E4%BD%93%E8%A3%BD%E9%80%A0%E8%A3%85%E7%BD%AE+%E5%A4%A7%E6%89%8B&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - 半導体製造装置",
    },
    {
        "url": "https://news.google.com/rss/search?q=%E5%8D%8A%E5%B0%8E%E4%BD%93+%E8%A8%AD%E5%82%99%E6%8A%95%E8%B3%87+%E5%B7%A5%E5%A0%B4&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - 半導体設備投資",
    },
    {
        "url": "https://news.google.com/rss/search?q=TSMC+%E7%86%8A%E6%9C%AC+%E5%8D%8A%E5%B0%8E%E4%BD%93&hl=ja&gl=JP&ceid=JP:ja",
        "name": "Google News - TSMC熊本",
    },
]

# カテゴリ定義: key → (列インデックス1始まり, 表示名, 分類説明)
CATEGORIES = {
    "negative": (3, "Negative", "景気後退・業績悪化・市場縮小・損益悪化・価格下落・需要減退など否定的内容"),
    "positive": (4, "Positive", "業績好調・市場拡大・増収増益・新技術・設備投資・需要増加など肯定的内容"),
    "economic_index": (5, "経済\n指標", "鉱工業生産指数・PMI・GDP・経済統計・マクロ経済指標"),
    "regional_economy": (6, "地方\n経済", "地方の経済動向・地域産業・熊本/北海道/広島等の地域ニュース"),
    "gov_project": (7, "国プロ/ \n公金補助", "NEDO・JST・経産省補助金・国家プロジェクト・政府支援・公的資金"),
    "tariff": (8, "対中/ US関税", "米中貿易規制・輸出管理・関税・EAR・Entity List・CHIPS法"),
    "pwr_ic_ev": (9, "Pwr IC/EV", "パワー半導体・SiC・GaN・EV・電気自動車・自動車向け半導体・インバーター"),
    "ai": (10, "AI", "AI・機械学習・LLM・データセンター・GPU・HPC・推論チップ"),
    "qt_optical": (11, "QT／光電", "量子コンピュータ・量子技術・光電融合・シリコンフォトニクス"),
    "memory": (12, "Memory", "DRAM・NAND・HBM・メモリ半導体・ストレージ"),
    "sensor": (13, "Sensor", "CMOSイメージセンサー・LiDAR・各種センサーデバイス"),
    "3dic_chiplet": (14, "3DIC/\nChiplet", "3D IC・チップレット・CoWoS・先端パッケージング・ウェーハー接合"),
    "fpd_solar": (15, "FPD\n太陽電池", "液晶・有機EL・OLED・太陽電池・ペロブスカイト・ディスプレイ"),
    "material": (16, "材料", "フォトレジスト・特殊ガス・CMP材料・絶縁膜・半導体材料全般"),
    "eco_sgds": (17, "Eco/\nSGDs", "環境・カーボンニュートラル・SDGs・省エネ・リサイクル・ESG"),
    "production_consumer": (18, "生産\n消費財", "スマートフォン・PC・家電・消費財の生産動向・在庫・出荷"),
    "production_equipment": (19, "生産\n設備材", "半導体製造装置・露光装置・CVD・エッチング・検査装置・設備投資"),
    "infrastructure": (20, "インフラ", "データセンター・電力インフラ・交通インフラ・通信インフラ・工場建設"),
    "consortium": (21, "企業\n連合", "M&A・アライアンス・合弁・資本提携・企業統合・コンソーシアム"),
    "education": (22, "教育", "大学・研究機関・人材育成プログラム・産学連携・論文・研究開発"),
    "human_resource": (23, "人材", "採用・雇用・人員削減・経営人事・転職・人材確保"),
    "stock_earnings": (24, "株価\n／業績", "株価・時価総額・決算発表・業績予想・営業利益・純利益・増益・減益"),
    "pl45_customer": (25, "PL45顧客", "TSMC PL45顧客: Apple・NVIDIA・AMD・Qualcomm・Broadcom・Intel等"),
    "other": (26, "その他", "上記カテゴリに明確に該当しないニュース"),
}

# ヘッダーグループ定義 (グループ名, 開始列, 終了列)
HEADER_GROUPS = [
    ("Title",               1,  1),
    ("景気動向",             3,  6),
    ("政策／規制",            7,  8),
    ("技術動向",             9, 17),
    ("投資/景気動向",        18, 20),
    ("企業連合・教育・人材",  21, 23),
    ("企業動向",            24, 26),
]
