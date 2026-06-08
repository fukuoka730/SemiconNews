# 半導体市場ニュースレポート 自動生成システム

## 概要

このプロジェクトは、複数のRSSフィードから半導体業界のニュース記事を自動収集し、ルールベースの分類システムを使用して23のカテゴリに分類し、月次のExcelレポートとして出力するシステムです。

**主な特徴:**
- 🤖 **API不要**: Gemini APIやLLMに依存しない軽量な実装
- 🔄 **自動月次実行**: CloudベースのリモートエージェントにてScheduled実行
- 📊 **23カテゴリ分類**: 経済指標・政策規制・技術動向・企業動向など多面的に分類
- 📁 **Excel出力**: 日本語対応のフォーマット済みExcelファイル生成
- 🔍 **キーワードベース**: 日本語を含めた複雑なキーワードマッチングルール

---

## システム構成

### アーキテクチャ

```
RSS Feed 収集 → ルールベース分類 → Excel 生成 → GitHub Push
```

### データフロー

1. **RSS収集** (`src/collector.py`): 10個のRSSフィードから対象月の記事を取得
2. **分類** (`src/classifier.py`): キーワードマッチングで23カテゴリに分類
3. **出力** (`src/generator.py`): フォーマット済みExcelファイルを生成
4. **GitHub Push**: 自動的に`output/`ディレクトリをコミット・プッシュ

---

## 実行方法

### 環境セットアップ

```bash
# 依存ライブラリのインストール
pip install openpyxl python-dateutil feedparser -q
```

### スクリプト実行

#### 前月分を自動生成（毎月1日実行）
```bash
python main.py
```

#### 特定月を指定する場合
```bash
python main.py {year} {month}
```

例: `python main.py 2026 4` → 2026年4月分を生成

### 出力

スクリプト実行後、以下が出力されます:
- **Excelファイル**: `output/MarketNews-{year}{month:02d}.xlsx`
- **ログファイル**: `run.log`
- **コンソール出力**: 処理ステップと記事件数

---

## カテゴリ定義（23種）

| カテゴリ | 説明 |
|---------|------|
| **Negative** | 景気後退・業績悪化・市場縮小・損益悪化など否定的内容 |
| **Positive** | 業績好調・市場拡大・増収増益・設備投資増加など肯定的内容 |
| **経済指標** | 鉱工業生産指数・PMI・GDP等のマクロ経済指標 |
| **地方経済** | 地方の経済動向（熊本・広島・北海道等の地域ニュース） |
| **国プロ/公金補助** | NEDO・JST・経産省補助金・国家プロジェクト・公的資金 |
| **対中/US関税** | 米中貿易規制・輸出管理・関税・CHIPS法 |
| **Pwr IC/EV** | パワー半導体・SiC・GaN・EV・自動車向け半導体 |
| **AI** | AI・LLM・データセンター・GPU・HPC・推論チップ |
| **QT/光電** | 量子コンピュータ・光電融合・シリコンフォトニクス |
| **Memory** | DRAM・NAND・HBM・メモリ半導体 |
| **Sensor** | CMOSイメージセンサー・LiDAR・各種センサー |
| **3DIC/Chiplet** | 3D IC・チップレット・CoWoS・先端パッケージング |
| **FPD/太陽電池** | 液晶・有機EL・OLED・太陽電池・ディスプレイ |
| **材料** | フォトレジスト・特殊ガス・CMP材料・半導体材料 |
| **Eco/SGDs** | 環境・カーボンニュートラル・SDGs・省エネ・ESG |
| **生産/消費財** | スマホ・PC・家電の生産動向・在庫・出荷 |
| **生産/設備材** | 半導体製造装置・露光装置・CVD・設備投資 |
| **インフラ** | データセンター・電力インフラ・通信・工場建設 |
| **企業連合** | M&A・アライアンス・合弁・資本提携・企業統合 |
| **教育** | 大学・研究機関・産学連携・人材育成プログラム |
| **人材** | 採用・雇用・人員削減・経営人事・人材確保 |
| **株価/業績** | 株価・時価総額・決算発表・業績予想・増減益 |
| **その他** | 上記に明確に該当しないニュース |

**分類ルール:**
- `Negative` と `Positive` は必ずどちらか一方を選択
- 他は該当するものをすべて選択
- `その他` は他カテゴリが全く当てはまらない場合のみ

---

## RSSフィード一覧

| フィード | ソース |
|---------|--------|
| EE Times Japan | eetimes.itmedia.co.jp |
| EDN Japan | ednjapan.com |
| Semiconductor Portal | semiconductorportal.com |
| Google News - 半導体市場 | news.google.com |
| Google News - AI半導体 | news.google.com |
| Google News - 半導体決算 | news.google.com |
| Google News - 電子部品市場 | news.google.com |
| Google News - 半導体製造装置 | news.google.com |
| Google News - 半導体設備投資 | news.google.com |
| Google News - 半導体検査 | news.google.com |

---

## Excel出力仕様

### フォーマット
- **フォント**: 游ゴシック
- **グリッド線**: OFF
- **Title列**: 記事URLへのハイパーリンク
- **ウィンドウ枠の固定**: C3（最初の列と最初の2行を固定）

### 列構成

**グループ1: Title**
- A: Title（記事URLリンク）

**グループ2: 景気動向**
- C: Negative
- D: Positive
- E: 経済指標
- F: 地方経済

**グループ3: 政策/規制**
- G: 国プロ/公金補助
- H: 対中/US関税

**グループ4: 技術動向**
- I: Pwr IC/EV
- J: AI
- K: QT/光電
- L: Memory
- M: Sensor
- N: 3DIC/Chiplet
- O: FPD/太陽電池
- P: 材料
- Q: Eco/SGDs

**グループ5: 投資/景気動向**
- R: 生産/消費財
- S: 生産/設備材
- T: インフラ

**グループ6: 企業連合・教育・人材**
- U: 企業連合
- V: 教育
- W: 人材

**グループ7: 企業動向**
- X: 株価/業績
- Y: その他

---

## ファイル構成

```
SemiconNews/
├── main.py                    # メインスクリプト
├── config.py                  # 設定ファイル（RSSフィード、カテゴリ定義）
├── requirements.txt           # Python依存パッケージ
├── .env.example              # 環境変数テンプレート
├── TASK.md                   # タスク定義ドキュメント
├── README.md                 # このファイル
├── run_monthly.bat           # Windows月次実行バッチファイル
├── setup_scheduler.ps1       # Windows タスクスケジューラセットアップ
├── src/
│   ├── collector.py          # RSS記事収集モジュール
│   ├── classifier.py         # ルールベース分類モジュール
│   ├── generator.py          # Excel生成モジュール
│   ├── keywords/             # キーワード定義ファイル
│   │   └── *.txt             # カテゴリ別キーワードリスト
│   └── utils.py              # ユーティリティ関数
├── output/                   # 生成されたExcelファイル出力先
│   └── MarketNews-*.xlsx     # 月次レポートファイル
└── .git/                     # Gitリポジトリ
```

---

## 実行環境

### ローカル実行
```bash
python main.py
```

### 自動月次実行（Cloud Remote Agent）
CloudベースのリモートエージェントにてScheduledで毎月1日に自動実行

### Windows定時実行
```powershell
# タスクスケジューラセットアップ
powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1
```

---

## トラブルシューティング

### RSS記事が取得できない場合
- `config.py`のRSSフィードURLを確認
- ネットワーク接続を確認
- フィードの可用性をブラウザで確認

### Excelファイルが生成されない場合
- `openpyxl`がインストールされているか確認：`pip list | grep openpyxl`
- `output/`ディレクトリの書き込み権限を確認
- ログファイル(`run.log`)でエラーメッセージを確認

### 分類がうまくいかない場合
- `src/keywords/`内のキーワード定義ファイルを確認
- キーワードが記事タイトルや説明に含まれているか確認
- キーワードルールを追加・調整する

---

## 開発に関する情報

### 依存パッケージ
- **openpyxl**: Excel ファイル生成
- **feedparser**: RSS フィードパース
- **python-dateutil**: 日付処理

### 拡張方法

#### 新しいカテゴリを追加する
1. `config.py`の`CATEGORIES`辞書に新規追加
2. `src/keywords/`に対応するキーワード定義ファイルを作成
3. `src/classifier.py`の分類ロジックを更新（必要に応じて）

#### RSSフィードを追加する
1. `config.py`の`RSS_FEEDS`リストに新規追加
2. 新しいフィードが有効か確認

#### 出力フォーマットをカスタマイズする
`src/generator.py`の`generate_excel()`関数を編集

---

## ライセンス

（ライセンス情報を追加してください）

---

## 連絡先

問題報告や機能提案は、GitHubのIssuesセクションにお願いします。
