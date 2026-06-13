# 半導体市場ニュースレポート 月次自動生成タスク

## 実行環境

クラウド上のリモートエージェント（Claude Code Remote）が毎月1日に自動実行する。
ローカルでの手動実行も可能。

## 処理手順

### Step 1: 依存ライブラリのインストール

```bash
pip install openpyxl python-dateutil feedparser -q
```

### Step 2: レポート生成

前月分を自動生成（毎月1日実行時）:

```bash
python main.py
```

特定月を指定する場合:

```bash
python main.py {year} {month}
```

例: `python main.py 2026 4`

スクリプトが以下を自動実行する:
1. **RSS収集**: 10件のRSSフィードから対象月の記事を収集
2. **ルールベース分類**: キーワードマッチングで23カテゴリに分類（API不要）
3. **Excel生成**: `output/MarketNews-{year}{month:02d}.xlsx` を出力

### Step 3: GitHubにpush

```bash
git config user.email "claude-agent@anthropic.com"
git config user.name "Claude Agent"
git remote set-url origin https://fukuoka730:{PAT}@github.com/fukuoka730/SemiconNews.git
git add output/
git commit -m "[Auto] {year}/{month:02d} 半導体市場ニュースレポート ({件数}件)"
git push origin main
```

### Step 4: 完了確認

記事数、生成ファイル名、push成否を報告する。

---

## カテゴリ定義（23種）

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

---

## Excel仕様

- フォント: 游ゴシック
- グリッド線: OFF
- Title列: 記事URLへのハイパーリンク
- ウィンドウ枠の固定: C3
- 出力先: `output/MarketNews-{year}{month:02d}.xlsx`

---

## 週刊メール発行（月次とは独立）

### 実行環境

ローカルのWindowsタスクスケジューラで毎週月曜 8:00 に `weekly.py` を実行する。
登録は `setup_weekly_scheduler.ps1`、実行ラッパーは `run_weekly.bat`（ログは `run_weekly.log`）。
SMTP認証情報と宛先は ローカルの `.env` に記載する（`load_dotenv()` が環境変数へ読み込む）。

| 環境変数 | 説明 |
|---|---|
| SMTP_HOST | SMTPサーバホスト |
| SMTP_PORT | ポート（既定587） |
| SMTP_USER | 認証ユーザ |
| SMTP_PASS | 認証パスワード（Gmailの場合はアプリパスワード） |
| SMTP_FROM | 送信元アドレス |
| SMTP_TLS | starttls(既定)/ssl/none |
| MAIL_TO | 宛先（カンマ区切りで複数可） |

### 処理手順

手動実行:

```bash
python weekly.py
```

スケジューラ登録（毎週月曜 8:00）:

```powershell
.\setup_weekly_scheduler.ps1
```

スクリプトが以下を自動実行する:
1. **RSS収集**: 直近7日間の記事を収集（`collect_articles_between`）
2. **ルールベース分類**: 既存の23カテゴリ分類を再利用
3. **HTML生成**: ダイジェスト本文を組み立て
4. **メール送信**: 汎用SMTPでHTMLメールを配信

対象記事が0件の週は送信をスキップして正常終了する。
