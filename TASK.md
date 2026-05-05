# 半導体市場ニュースレポート 月次自動生成タスク

## 実行環境

クラウド上のリモートエージェント（Claude Code Remote）が毎月1日に自動実行する。
ローカルでの手動実行も可能。

## 処理手順

### Step 1: 対象月を決定

```python
from datetime import date
from dateutil.relativedelta import relativedelta
target = date.today().replace(day=1) - relativedelta(months=1)
print(target.year, target.month)
```

### Step 2: 依存ライブラリのインストール

```bash
pip install openpyxl python-dateutil -q
```

### Step 3: 記事収集（WebSearch使用）

WebSearchで以下3クエリを検索し、各クエリから10件ずつ、計30件を収集する。

1. `半導体 市場 {year}年{month}月`
2. `AI 半導体 投資 {year}年{month}月`
3. `半導体 業績 決算 {year}年{month}月`

**日付フィルタ**: 対象月（`{year}-{month:02d}`）に公開された記事のみを含める。対象月外・日付不明は除外する。

### Step 4: 記事分類とJSON保存

全記事を一括で分類し、`data/classified_{year}{month:02d}.json` に保存する。

**カテゴリ定義（23種）:**

| キー | 説明 |
|---|---|
| negative | 業績悪化・市場縮小・損益悪化・価格下落など否定的内容 |
| positive | 業績好調・市場拡大・増収増益・設備投資増加など肯定的内容 |
| economic_index | 鉱工業生産指数・PMI・GDP等のマクロ経済指標 |
| regional_economy | 地方の経済動向（熊本・広島・北海道等の地域ニュース） |
| gov_project | NEDO・JST・経産省補助金・国家プロジェクト・公的資金 |
| tariff | 米中貿易規制・輸出管理・関税・CHIPS法 |
| pwr_ic_ev | パワー半導体・SiC・GaN・EV・自動車向け半導体 |
| ai | AI・LLM・データセンター・GPU・HPC・推論チップ |
| qt_optical | 量子コンピュータ・光電融合・シリコンフォトニクス |
| memory | DRAM・NAND・HBM・メモリ半導体 |
| sensor | CMOSイメージセンサー・LiDAR・各種センサー |
| 3dic_chiplet | 3D IC・チップレット・CoWoS・先端パッケージング |
| fpd_solar | 液晶・有機EL・OLED・太陽電池・ディスプレイ |
| material | フォトレジスト・特殊ガス・CMP材料・半導体材料 |
| eco_sgds | 環境・カーボンニュートラル・SDGs・省エネ・ESG |
| production_consumer | スマホ・PC・家電の生産動向・在庫・出荷 |
| production_equipment | 半導体製造装置・露光装置・CVD・設備投資 |
| infrastructure | データセンター・電力インフラ・通信・工場建設 |
| consortium | M&A・アライアンス・合弁・資本提携・企業統合 |
| education | 大学・研究機関・産学連携・人材育成プログラム |
| human_resource | 採用・雇用・人員削減・経営人事・人材確保 |
| stock_earnings | 株価・時価総額・決算発表・業績予想・増減益 |
| other | 上記に明確に該当しないニュース |

**分類ルール:**
- `negative` と `positive` は必ずどちらか一方を選択
- 他は該当するものをすべて選択
- `other` は他カテゴリが全く当てはまらない場合のみ

**JSON形式**（トークン節約のため `true` のカテゴリのみ記載）:
```json
[
  {
    "title": "記事タイトル",
    "date": "2026-04-15",
    "url": "https://...",
    "source": "WebSearch",
    "categories": {
      "positive": true,
      "ai": true,
      "stock_earnings": true
    }
  }
]
```

### Step 5: Excel生成

```bash
mkdir -p data
python src/generator.py {year} {month}
```

出力ファイル: `output/MarketNews-{year}{month:02d}.xlsx`

**Excel仕様:**
- フォント: 游ゴシック
- グリッド線: OFF
- Title列: 記事URLへのハイパーリンク
- ウィンドウ枠の固定: C3

### Step 6: GitHubにpush

```bash
git config user.email "claude-agent@anthropic.com"
git config user.name "Claude Agent"
git remote set-url origin https://fukuoka730:{PAT}@github.com/fukuoka730/SemiconNews.git
git add output/
git commit -m "[Auto] {year}/{month:02d} 半導体市場ニュースレポート"
git push origin main
```

### Step 7: 完了確認

記事数、生成ファイル名、push成否を報告する。
