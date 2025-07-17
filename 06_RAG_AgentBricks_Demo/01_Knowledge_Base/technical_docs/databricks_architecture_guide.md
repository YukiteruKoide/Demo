# Databricks アーキテクチャガイド

## 概要
Databricksは統合分析プラットフォームで、データエンジニアリング、データサイエンス、機械学習を一つのプラットフォームで実現できます。

## メダリオンアーキテクチャ

### 基本概念
メダリオンアーキテクチャは、データレイクハウスの標準的な設計パターンです。データ品質を段階的に向上させながら、Bronze → Silver → Gold の3層で構成されます。

### Bronze層（青銅層）
**目的**: 生データの保存
- **特徴**: オリジナルデータをそのまま保持
- **データ形式**: 通常はParquetまたはDelta Lake
- **用途**: データの永続化、監査証跡、履歴保持
- **処理**: 最小限の変換のみ（スキーマ推論、基本的なデータ型変換）

```python
# Bronze層の例
df_bronze = (
    spark.read.format("csv")
    .option("header", True)
    .option("inferSchema", True)
    .load("/path/to/raw/data.csv")
)
df_bronze.write.format("delta").saveAsTable("bronze.raw_transactions")
```

### Silver層（銀層）
**目的**: データのクリーニングと統合
- **特徴**: ビジネスルールの適用、データ品質の向上
- **処理**: 重複除去、データ型の統一、欠損値の処理、外れ値の検出
- **用途**: 分析の基礎となるクリーンなデータセット
- **最適化**: パーティショニング、Z-Order最適化

```python
# Silver層の例
df_silver = (
    spark.table("bronze.raw_transactions")
    .filter(col("amount") > 0)  # データ品質チェック
    .withColumn("transaction_date", to_date(col("date_string")))
    .dropDuplicates(["transaction_id"])
)
df_silver.write.format("delta").mode("overwrite").saveAsTable("silver.clean_transactions")
```

### Gold層（金層）
**目的**: ビジネス要件に特化した集計・分析
- **特徴**: 高度に集約されたビジネス指標
- **処理**: 複雑な集計、KPI計算、ダッシュボード用データ
- **用途**: レポート、ダッシュボード、BI、機械学習特徴量
- **性能**: 高速クエリに最適化

```python
# Gold層の例
df_gold = (
    spark.table("silver.clean_transactions")
    .groupBy("store_id", "product_category", "month")
    .agg(
        sum("amount").alias("total_sales"),
        count("transaction_id").alias("transaction_count"),
        avg("amount").alias("avg_transaction_value")
    )
)
df_gold.write.format("delta").saveAsTable("gold.monthly_sales_summary")
```

## Unity Catalog

### 概要
Unity Catalogは、Databricksの統合データガバナンスソリューションです。データ資産の発見、アクセス制御、データ系譜の管理を一元化します。

### 3層アーキテクチャ
1. **Catalog（カタログ）**: 最上位の名前空間
2. **Schema（スキーマ）**: テーブルの論理的なグループ化
3. **Table/Volume（テーブル/ボリューム）**: 実際のデータ資産

```sql
-- Unity Catalogの階層構造
catalog_name.schema_name.table_name
-- 例: production.sales.transactions
```

### Volume機能
Volumeは、Unity Catalog管理下でファイルを格納する機能です。
- **管理対象Volume**: Unity Catalogで完全管理
- **外部Volume**: 既存のストレージを参照

```python
# Volume使用例
file_path = "/Volumes/catalog/schema/volume/data.csv"
df = spark.read.csv(file_path, header=True)
```

## Delta Lake

### 主要機能

#### 1. ACID準拠
トランザクションの原子性、一貫性、分離性、永続性を保証します。

#### 2. Time Travel
データの履歴バージョンにアクセス可能です。
```sql
-- 特定の時点のデータを参照
SELECT * FROM table_name TIMESTAMP AS OF '2024-01-15'

-- 特定のバージョンを参照  
SELECT * FROM table_name VERSION AS OF 10
```

#### 3. スキーマ進化
既存のテーブルに新しい列を安全に追加できます。
```python
# スキーマ進化を有効化
df.write.format("delta").option("mergeSchema", "true").mode("append").saveAsTable("table_name")
```

#### 4. 最適化機能

**OPTIMIZE**: ファイルの最適化
```sql
OPTIMIZE table_name
ZORDER BY column_name  -- Z-Order最適化
```

**VACUUM**: 不要ファイルのクリーンアップ
```sql
VACUUM table_name RETAIN 168 HOURS  -- 7日以上古いファイルを削除
```

## Auto Loader

### 概要
Auto Loaderは、クラウドストレージから新しいファイルを自動的に検出・処理するストリーミング機能です。

### 主要機能
- **自動ファイル検出**: 新しいファイルの自動発見
- **スキーマ推論**: データ型の自動判定
- **スキーマ進化**: 新しい列の自動追加
- **再処理防止**: 処理済みファイルのスキップ

### 実装例
```python
# Auto Loader設定
(spark.readStream
 .format("cloudFiles")
 .option("cloudFiles.format", "csv")
 .option("cloudFiles.schemaLocation", "/path/to/schema")
 .option("header", "true")
 .load("/path/to/source/")
 .writeStream
 .format("delta")
 .option("checkpointLocation", "/path/to/checkpoint")
 .table("target_table")
)
```

## クラスター管理

### クラスターの種類
1. **All-Purpose Cluster**: 対話的な分析用
2. **Job Cluster**: バッチ処理専用
3. **SQL Warehouse**: SQLクエリ専用

### スケーリング
- **Auto Scaling**: 負荷に応じた自動スケール
- **Spot Instance**: コスト削減のためのスポットインスタンス利用

### パフォーマンス最適化
- **Photon Engine**: 高速化エンジン
- **Delta Cache**: SSDを活用したキャッシュ
- **Adaptive Query Execution**: クエリ実行時の最適化

## ベストプラクティス

### データ設計
1. **適切なパーティショニング**: クエリパターンに基づく分割
2. **Z-Order最適化**: よく使用される列での最適化
3. **データ型の最適化**: 適切なデータ型の選択

### パフォーマンス
1. **ファイルサイズ**: 128MB-1GB程度が理想
2. **パーティション数**: クラスターのコア数の2-4倍
3. **定期的なOPTIMIZE**: パフォーマンス維持

### セキュリティ
1. **Unity Catalogの活用**: 統合ガバナンス
2. **最小権限の原則**: 必要最小限のアクセス権限
3. **監査ログ**: アクセス状況の監視

---

このアーキテクチャガイドを参考に、効率的なデータパイプラインを構築してください。質問がある場合は、具体的な技術要素について詳しく説明いたします。 