# Databricks Demo Collection 🚀

## 概要
このリポジトリは、Databricksプラットフォームを活用したデータエンジニアリングおよびデータ分析のデモプロジェクト集です。初心者向けチュートリアルから実践的なETLパイプライン、エンドツーエンドのデータソリューションまで、段階的に学習できる構成になっています。

## 🏗️ プロジェクト構成

### 📊 [01_yukiteru_mart](./01_yukiteru_mart/) - データ分析基礎
**レベル**: 初級〜中級 | **所要時間**: 2-3時間

Yukiteru Martの売上データを使った基本的なデータ分析プロジェクト

**学習内容:**
- データベース制約の設定（主キー・外部キー）
- 分析用マートテーブルの作成
- Auto Loaderによるデータ取り込み
- 基本的なダッシュボード作成

**技術スタック:**
- Databricks SQL
- Delta Lake
- Auto Loader
- Databricks ダッシュボード

**主要コンポーネント:**
- **01_事前作業.ipynb**: データベース制約設定とスキーマ設計
- **02_マート作成.ipynb**: 顧客・店舗・商品別の分析用マートテーブル構築
- **パイプライン/**: Auto Loaderによる新規データ自動取り込み
- **ダッシュボード**: KPI監視とビジネス分析の可視化

**実現できる分析:**
- 📊 顧客セグメンテーションとライフタイムバリュー分析
- 🏪 店舗別パフォーマンス比較と運営効率性評価
- 📦 商品・在庫分析とABC分類
- ⏰ 時間帯別売上パターンと季節性分析

### 🔄 [02_yukiterumart_ETL](./02_yukiterumart_ETL/) - メダリオンアーキテクチャETL
**レベル**: 中級〜上級 | **所要時間**: 4-6時間

本格的なETLパイプラインをメダリオンアーキテクチャで構築

**学習内容:**
- Bronze/Silver/Goldレイヤーの設計・実装
- 増分データ処理とMERGE INTO
- データ品質管理
- ビジネスインテリジェンス向け集計テーブル

**技術スタック:**
- Databricks Runtime
- Delta Lake (ACID, Time Travel)
- Auto Loader
- PySpark
- Databricks Workflows

**アーキテクチャ概要:**
- **🥉 Bronze Layer**: CSVデータの生取り込み（最小限の変換）
- **🥈 Silver Layer**: データクレンジング・標準化・結合処理
- **🥇 Gold Layer**: ビジネス分析用集計テーブル

**主要コンポーネント:**

**📁 01_テーブル作成/**
- **01_csv_to_bronze.ipynb**: CSVファイルからDelta Tableへの変換
- **02_bronz_to_sliver.ipynb**: データ品質向上と正規化
- **03_bronze_to_gold_*.ipynb**: 月次売上・顧客セグメント・商品分析マート作成

**📁 02_データ追加/**
- **01_Bronze**: Auto Loaderによる新規CSVの自動取り込み
- **02_Silver**: 新着データの変換・結合処理
- **03_Gold**: 全体データからの再集計

**実現できる分析:**
- 📈 月次・店舗・カテゴリ別売上分析
- 👥 RFM分析による顧客セグメンテーション
- 🏪 店舗パフォーマンス比較分析
- ⭐ 商品売上とレビュー評価の相関分析
- 📊 増分データ処理による リアルタイム更新

### 🎓 [03_Databricks demo for beginner](./03_Databricks%20demo%20for%20beginner/) - 初心者向けチュートリアル
**レベル**: 初級 | **所要時間**: 1-2時間

Databricks初心者向けの基本操作習得プロジェクト

**学習内容:**
- Databricksクラスターの作成・管理
- ノートブックの基本操作
- SQLとPythonの基本的な使い方
- 機械学習（AutoML）の基礎

**技術スタック:**
- Databricks Community Edition対応
- Spark SQL
- Pandas
- Scikit-learn
- AutoML

### ☁️ [04_ykoide_AWS_EndToEnd_withUC_v2](./04_ykoide_AWS_EndToEnd_withUC_v2/) - AWS統合エンドツーエンド
**レベル**: 上級 | **所要時間**: 6-8時間

AWSサービスとの統合によるエンタープライズ級データソリューション

**学習内容:**
- Unity Catalogによるデータガバナンス
- AWSサービス（S3, IAM等）との連携
- エンドツーエンドのデータパイプライン
- MLOpsとモデル管理

**技術スタック:**
- Databricks on AWS
- Unity Catalog
- MLflow
- AWS S3/IAM
- Databricks Asset Bundles

### 🌊 [05_DE_End2End_withDLT_v3](./05_DE_End2End_withDLT_v3/) - Delta Live Tables
**レベル**: 上級 | **所要時間**: 4-6時間

Delta Live Tablesを活用した宣言的データパイプライン

**学習内容:**
- Delta Live Tables (DLT)による宣言的パイプライン
- データ品質チェックとExpectations
- 継続的データ配信
- パイプライン監視と運用

**技術スタック:**
- Delta Live Tables
- Databricks Workflows
- Data Quality Monitoring
- Unity Catalog

## 🎯 学習パス

### 📚 推奨学習順序

1. **データ分析入門**
   ```
   03_Databricks demo for beginner → 01_yukiteru_mart
   ```

2. **データエンジニアリング習得**
   ```
   02_yukiterumart_ETL → 05_DE_End2End_withDLT_v3
   ```

3. **エンタープライズ実装**
   ```
   04_ykoide_AWS_EndToEnd_withUC_v2
   ```

### 🛠️ 習得技術マップ

| プロジェクト | SQL | Python | Spark | Delta | AutoML | DLT | Unity Catalog | AWS |
|-------------|-----|--------|-------|-------|--------|-----|---------------|-----|
| 01_yukiteru_mart | ✅ | ⭐ | ⭐ | ✅ | ❌ | ❌ | ⭐ | ❌ |
| 02_yukiterumart_ETL | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ⭐ | ❌ |
| 03_beginner | ✅ | ✅ | ⭐ | ⭐ | ✅ | ❌ | ❌ | ❌ |
| 04_AWS_EndToEnd | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| 05_DLT | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ✅ | ⭐ |

**凡例**: ✅ 重点習得 | ⭐ 軽く使用 | ❌ 使用しない

## 🚀 クイックスタート

### 前提条件
- Databricksアカウント（Community Editionでも可）
- 基本的なSQL知識
- Pythonの基本的な知識（推奨）

### 環境セットアップ
1. **Databricksワークスペースの作成**
   - [Databricks Community Edition](https://community.cloud.databricks.com/) でアカウント作成
   - または企業版Databricksへのアクセス権取得

2. **クラスターの作成**
   ```
   - クラスター名: learning-cluster
   - Runtime: LTS (最新版推奨)
   - ノードタイプ: 小〜中規模 (学習用)
   ```

3. **ノートブックのインポート**
   - 各プロジェクトフォルダからノートブックをDatabricksにインポート
   - READMEファイルの手順に従って実行

## 📖 各プロジェクトの詳細

### ビジネスシナリオ
全プロジェクトは「Yukiteru Mart」という架空の小売チェーンを題材にしており、以下のデータを扱います：

- **顧客データ**: 年齢、性別、メンバーシップレベル
- **商品データ**: カテゴリ、価格、在庫情報
- **店舗データ**: 立地、管理者、営業時間
- **売上データ**: 取引履歴、購入数量、日時
- **レビューデータ**: 商品評価、顧客フィードバック

### 実現できる分析
- 📊 **売上分析**: 店舗別・商品別・時系列パフォーマンス
- 👥 **顧客分析**: セグメンテーション、LTV、チャーン予測
- 🏪 **店舗分析**: 立地効果、運営効率、比較分析
- ⭐ **商品分析**: 売上vs評価、在庫最適化

## 🔧 技術詳細

### Databricksコア機能
- **Unity Catalog**: データガバナンスとメタデータ管理
- **Delta Lake**: ACID準拠のデータレイク
- **Auto Loader**: ストリーミングデータ取り込み
- **MLflow**: 機械学習ライフサイクル管理
- **Workflows**: ジョブスケジューリングと自動化

### アーキテクチャパターン
- **メダリオンアーキテクチャ**: Bronze → Silver → Gold
- **Lambda Architecture**: バッチ + ストリーミング処理
- **データメッシュ**: 分散データ所有権
- **レイクハウス**: データレイク + データウェアハウス

## 🎓 学習成果

### 初級レベル完了後
- Databricksの基本操作をマスター
- SQLとPythonでのデータ操作
- 基本的なデータ可視化
- 簡単な機械学習モデル作成

### 中級レベル完了後
- ETLパイプラインの設計・実装
- Delta Lakeによるデータ管理
- メダリオンアーキテクチャの理解
- データ品質管理の実装

### 上級レベル完了後
- エンタープライズ級データソリューション設計
- Unity Catalogによるガバナンス実装
- AWSクラウドサービスとの統合
- Delta Live Tablesによる宣言的パイプライン
- MLOpsとモデル運用

## 🤝 貢献とフィードバック

### 改善提案
- Issue作成によるバグ報告・機能要望
- Pull Requestによるコード改善
- ドキュメント更新

### 質問・サポート
- 各プロジェクトのREADMEを確認
- GitHub Discussionsでの質問
- コミュニティフォーラムの活用

## 📚 関連リソース

### 公式ドキュメント
- [Databricks Documentation](https://docs.databricks.com/)
- [Delta Lake Documentation](https://docs.delta.io/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)

### 学習リソース
- [Databricks Academy](https://academy.databricks.com/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Unity Catalog Best Practices](https://docs.databricks.com/data-governance/unity-catalog/index.html)

### コミュニティ
- [Databricks Community Forum](https://community.databricks.com/)
- [Stack Overflow - Databricks](https://stackoverflow.com/questions/tagged/databricks)

---

## 📄 ライセンス

このプロジェクトは教育目的で作成されています。コードとドキュメントは自由に使用・改変できますが、商用利用時は適切な帰属表示をお願いします。

## 🏷️ タグ

`#Databricks` `#DataEngineering` `#DataAnalytics` `#ETL` `#DeltaLake` `#MachineLearning` `#BigData` `#CloudComputing` `#Tutorial` `#HandsOn` 