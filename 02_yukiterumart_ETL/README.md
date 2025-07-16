# Yukiteru Mart ETLパイプライン

## 概要
Databricksのメダリオンアーキテクチャを採用したETLパイプラインです。CSV データから Bronze → Silver → Gold の3層に分けてデータを処理し、高品質な分析基盤を構築します。

## 🏗️ メダリオンアーキテクチャ

```
CSV Files → Bronze (生データ) → Silver (整形済み) → Gold (集計済み)
```

### 📁 プロジェクト構成
```
02_yukiterumart_ETL/
├── 00_Data/                       # 元データ（CSV）
├── 01_テーブル作成/
│   ├── 01_csv_to_bronze.ipynb     # Bronze Layer作成
│   ├── 02_bronze_to_silver.ipynb  # Silver Layer作成
│   ├── 03_bronze_to_gold_1.ipynb  # Gold Layer: 月次売上サマリー
│   ├── 03_bronze_to_gold_2.ipynb  # Gold Layer: 顧客セグメント分析
│   └── 03_bronze_to_gold_3.ipynb  # Gold Layer: 商品売上vsレビュー分析
└── 02_データ追加/
    ├── 01_Bronze: Auto Loader による新規CSV自動取り込み.ipynb
    ├── 02_Silver: 新着トランザクションを変換・結合.ipynb
    └── 03_Gold: Silver全体から再集計.ipynb
```

## 🚀 実行フロー

### 初期構築（01_テーブル作成）
1. **Bronze Layer**: CSV → Deltaテーブル（生データ保存）
2. **Silver Layer**: データクレンジング・結合・変換
3. **Gold Layer**: ビジネス要件に特化した集計テーブル作成

### 継続運用（02_データ追加）
1. **新規データ取り込み**: Auto Loaderによる増分処理
2. **Silver更新**: MERGE INTOによる効率的な統合
3. **Gold再集計**: 最新データを反映した分析テーブル更新

## 📊 各レイヤーの役割

### 🥉 Bronze Layer（生データ）
- **目的**: オリジナルデータの完全な保持
- **特徴**: スキーマ推論、監査証跡、データの永続化
- **テーブル**: transactions, customers, products, stores, reviews

### 🥈 Silver Layer（整形済み）
- **目的**: 分析に適した形への変換・統合
- **特徴**: データクレンジング、型変換、テーブル結合
- **テーブル**: transactions_enriched（統合テーブル）

### 🥇 Gold Layer（集計済み）
- **目的**: ビジネス要件に特化した集計・分析テーブル
- **特徴**: 高速クエリ、ダッシュボード対応、KPI計算
- **テーブル**: 
  - monthly_sales_by_store_and_category
  - customer_segment_spending  
  - sales_vs_reviews

## 📈 ビジネス分析テーブル

### 1. 月次売上サマリー
**テーブル**: `monthly_sales_by_store_and_category`

| 分析軸 | 指標 | ビジネス活用 |
|--------|------|-------------|
| 店舗×カテゴリ×月 | 売上金額、販売数量、平均単価 | 店舗パフォーマンス比較、トレンド分析 |

### 2. 顧客セグメント分析
**テーブル**: `customer_segment_spending`

| セグメント軸 | 指標 | ビジネス活用 |
|-------------|------|-------------|
| 年齢層×性別×メンバーシップ | 平均消費額、取引回数 | ターゲットマーケティング、顧客戦略 |

### 3. 商品売上vsレビュー分析
**テーブル**: `sales_vs_reviews`

| 分析軸 | 指標 | ビジネス活用 |
|--------|------|-------------|
| 商品別 | 売上、販売数、平均評価、レビュー数 | 商品戦略、品質改善 |

## 🔧 技術仕様

### Volume設定
- **初期データパス**: `/Volumes/users/yukiteru_koide/yukiterumart_etl`
- **新規データパス**: `/Volumes/users/yukiteru_koide/yukiterumart_etl_newdata`

### Auto Loader設定
- **フォーマット**: CSV（ヘッダー付き）
- **スキーマ管理**: 自動推論＋進化対応
- **チェックポイント**: 処理状態の自動保存
- **冪等性**: 重複処理の防止

### Delta Lake機能
- **ACID準拠**: データの整合性保証
- **タイムトラベル**: 過去バージョンへのアクセス
- **MERGE INTO**: 効率的なUPSERT操作
- **最適化**: 自動ファイル圧縮、Z-Ordering

## 🎯 ビジネス質問と回答

### 📊 売上分析
- Q: どの店舗が最も売上が高いか？
- A: `monthly_sales_by_store_and_category`で店舗別売上ランキング

### 👥 顧客分析  
- Q: どの年齢層が最も消費額が大きいか？
- A: `customer_segment_spending`で年齢層別消費分析

### ⭐ 商品分析
- Q: 高評価商品の売上パフォーマンスは？
- A: `sales_vs_reviews`で評価×売上の4象限分析

## 🔄 データ品質管理

### 検証ポイント
- ✅ **データ型**: 適切な型への変換
- ✅ **NULL値**: 品質フィルタによる除外
- ✅ **重複**: 主キー制約による防止
- ✅ **参照整合性**: 外部キー制約による保証

### 監視メトリクス
- 📊 処理件数の前後比較
- ⏱️ 処理時間のパフォーマンス
- 🚨 エラー率・失敗ジョブの監視
- 📈 データ品質スコアの追跡

## 🚀 運用ベストプラクティス

### 定期実行
- **頻度**: 日次または週次
- **順序**: Bronze → Silver → Gold の順序厳守
- **監視**: 各段階での品質チェック

### スケーラビリティ
- **パーティション**: 日付ベースの効率的な分割
- **圧縮**: Delta Lakeの自動最適化活用
- **並列処理**: Sparkクラスターの適切なサイジング

### エラーハンドリング
- **チェックポイント**: 処理中断からの自動復旧
- **ロールバック**: 問題発生時の安全な戻し
- **アラート**: 失敗時の即座な通知

---

## 🎓 学習ポイント

このプロジェクトで習得できる技術：

### Data Engineering
- **メダリオンアーキテクチャ**: 現代的なデータレイク設計
- **Delta Lake**: 次世代データレイクストレージ
- **Auto Loader**: ストリーミングデータ取り込み
- **MERGE INTO**: 効率的なデータ更新

### Data Analysis
- **顧客セグメンテーション**: RFM分析、行動分析
- **時系列分析**: トレンド、季節性の把握
- **商品分析**: パフォーマンス評価、ポートフォリオ管理

### Databricks Platform
- **ワークスペース管理**: ノートブック、クラスター
- **Unity Catalog**: メタデータ管理、ガバナンス
- **Volume**: ファイルストレージとの統合 