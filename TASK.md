# 半導体市場ニュースレポート 月次自動生成タスク

## 処理手順

### Step 1: 対象月を決定
前月の年月を計算する（このタスクは毎月1日に実行されるため、前月が対象）。

例: 5月1日実行 → 2025年4月分を生成

### Step 2: RSS収集
以下を実行して記事を収集する:
```bash
python src/collector.py {YEAR} {MONTH}
```
結果は `data/articles_{YEAR}{MONTH:02d}.json` に保存される。

### Step 3: 記事分類
`data/articles_{YEAR}{MONTH:02d}.json` を読み込み、各記事タイトルを以下のカテゴリに分類する。

**カテゴリ定義:**

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
| pl45_customer | TSMCの先端ノード顧客（Apple/NVIDIA/AMD/Qualcomm等） |
| other | 上記に明確に該当しないニュース |

**分類ルール:**
- 1記事に複数カテゴリを付与可能（通常2〜5個）
- `negative` と `positive` は必ずどちらか一方を選択
- `other` は他カテゴリが全く当てはまらない場合のみ

分類結果を以下の形式で `data/classified_{YEAR}{MONTH:02d}.json` に保存する:
```json
[
  {
    "title": "記事タイトル",
    "date": "2025-10-31",
    "source": "Google News - 半導体市場",
    "categories": {
      "negative": false,
      "positive": true,
      "ai": true,
      "stock_earnings": true,
      ...
    }
  }
]
```

### Step 4: Excel生成
以下を実行してExcelを生成する:
```bash
python src/generator.py {YEAR} {MONTH}
```

### Step 5: 完了確認
`output/` ディレクトリにExcelファイルが生成されたことを確認し、件数を報告する。
