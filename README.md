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

**プロジェクト詳細構成:**

#### 📋 データアーキテクチャ設計
**エンティティ関係**:
- **Customers**: 顧客マスタテーブル（主キー: customer_id）
- **Products**: 商品マスタテーブル（主キー: product_id）
- **Stores**: 店舗マスタテーブル（主キー: store_id）
- **Inventory**: 在庫管理テーブル（複合キー: store_id + product_id）
- **Transactions**: 取引トランザクションテーブル（主キー: transaction_id）

#### 📝 [01_事前作業.ipynb] - データベース制約とスキーマ設計
**目的**: データ整合性確保のための基盤構築
**実装内容**:

**1. 主キー制約の設定**:
```sql
-- 顧客テーブルの主キー設定
ALTER TABLE customers 
ADD CONSTRAINT pk_customers PRIMARY KEY (customer_id);

-- 商品テーブルの主キー設定
ALTER TABLE products 
ADD CONSTRAINT pk_products PRIMARY KEY (product_id);

-- 店舗テーブルの主キー設定
ALTER TABLE stores 
ADD CONSTRAINT pk_stores PRIMARY KEY (store_id);
```

**2. 外部キー制約の実装**:
```sql
-- 取引テーブルの外部キー制約
ALTER TABLE transactions 
ADD CONSTRAINT fk_transactions_customer 
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE transactions 
ADD CONSTRAINT fk_transactions_product 
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE transactions 
ADD CONSTRAINT fk_transactions_store 
FOREIGN KEY (store_id) REFERENCES stores(store_id);

-- 在庫テーブルの外部キー制約
ALTER TABLE inventory 
ADD CONSTRAINT fk_inventory_product 
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE inventory 
ADD CONSTRAINT fk_inventory_store 
FOREIGN KEY (store_id) REFERENCES stores(store_id);
```

**3. データ整合性チェック**:
```sql
-- 孤立レコードの検出
SELECT COUNT(*) as orphaned_transactions
FROM transactions t
LEFT JOIN customers c ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 参照整合性の検証
SELECT 
  'transactions->customers' as reference_check,
  COUNT(DISTINCT t.customer_id) as referenced_customers,
  COUNT(DISTINCT c.customer_id) as available_customers
FROM transactions t
LEFT JOIN customers c ON t.customer_id = c.customer_id;
```

#### 🏪 [02_マート作成.ipynb] - 分析用マートテーブル構築
**目的**: ビジネス分析に最適化された集計テーブルの作成

**1. 顧客分析マート (customer_summary_mart)**:
```sql
CREATE OR REPLACE TABLE customer_summary_mart AS
SELECT 
  c.customer_id,
  c.customer_name,
  c.age,
  c.gender,
  c.membership_level,
  -- 購買行動指標
  COUNT(DISTINCT t.transaction_id) as total_transactions,
  COUNT(DISTINCT DATE(t.transaction_date)) as visit_days,
  SUM(t.quantity * p.unit_price) as total_spent,
  AVG(t.quantity * p.unit_price) as avg_transaction_value,
  MAX(t.transaction_date) as last_purchase_date,
  MIN(t.transaction_date) as first_purchase_date,
  DATEDIFF(MAX(t.transaction_date), MIN(t.transaction_date)) as customer_lifetime_days,
  
  -- 商品嗜好分析
  MODE(p.category) as favorite_category,
  COUNT(DISTINCT p.product_id) as unique_products_purchased,
  
  -- 店舗利用パターン
  MODE(s.store_name) as most_visited_store,
  COUNT(DISTINCT s.store_id) as stores_visited,
  
  -- 顧客セグメント分類
  CASE 
    WHEN SUM(t.quantity * p.unit_price) >= 50000 THEN 'VIP'
    WHEN SUM(t.quantity * p.unit_price) >= 20000 THEN '優良'
    WHEN SUM(t.quantity * p.unit_price) >= 5000 THEN '一般'
    ELSE '新規・低頻度'
  END as customer_segment,
  
  -- 購買頻度評価
  ROUND(COUNT(DISTINCT t.transaction_id) * 1.0 / 
        NULLIF(DATEDIFF(MAX(t.transaction_date), MIN(t.transaction_date)), 0) * 30, 2) 
        as monthly_purchase_frequency
        
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
LEFT JOIN products p ON t.product_id = p.product_id
LEFT JOIN stores s ON t.store_id = s.store_id
GROUP BY c.customer_id, c.customer_name, c.age, c.gender, c.membership_level
```

**2. 店舗売上分析マート (store_sales_summary_mart)**:
```sql
CREATE OR REPLACE TABLE store_sales_summary_mart AS
SELECT 
  s.store_id,
  s.store_name,
  s.location,
  s.manager_name,
  s.opening_hours,
  
  -- 売上実績指標
  COUNT(DISTINCT t.transaction_id) as total_transactions,
  COUNT(DISTINCT t.customer_id) as unique_customers,
  COUNT(DISTINCT DATE(t.transaction_date)) as operating_days,
  SUM(t.quantity * p.unit_price) as total_revenue,
  AVG(t.quantity * p.unit_price) as avg_transaction_value,
  SUM(t.quantity) as total_items_sold,
  
  -- 効率性指標
  ROUND(SUM(t.quantity * p.unit_price) / COUNT(DISTINCT DATE(t.transaction_date)), 2) 
    as daily_average_revenue,
  ROUND(COUNT(DISTINCT t.customer_id) * 1.0 / COUNT(DISTINCT DATE(t.transaction_date)), 2) 
    as daily_customer_traffic,
  ROUND(SUM(t.quantity * p.unit_price) / COUNT(DISTINCT t.customer_id), 2) 
    as revenue_per_customer,
    
  -- 商品構成分析
  COUNT(DISTINCT p.product_id) as products_sold,
  MODE(p.category) as top_selling_category,
  
  -- 時間帯分析
  MODE(HOUR(t.transaction_date)) as peak_hour,
  COUNT(CASE WHEN HOUR(t.transaction_date) BETWEEN 9 AND 12 THEN 1 END) as morning_transactions,
  COUNT(CASE WHEN HOUR(t.transaction_date) BETWEEN 12 AND 17 THEN 1 END) as afternoon_transactions,
  COUNT(CASE WHEN HOUR(t.transaction_date) BETWEEN 17 AND 21 THEN 1 END) as evening_transactions,
  
  -- パフォーマンス評価
  CASE 
    WHEN SUM(t.quantity * p.unit_price) >= 100000 THEN '高収益店舗'
    WHEN SUM(t.quantity * p.unit_price) >= 50000 THEN '標準店舗'
    ELSE '改善必要店舗'
  END as performance_category

FROM stores s
LEFT JOIN transactions t ON s.store_id = t.store_id
LEFT JOIN products p ON t.product_id = p.product_id
GROUP BY s.store_id, s.store_name, s.location, s.manager_name, s.opening_hours
```

**3. 商品分析マート (product_analysis_mart)**:
```sql
CREATE OR REPLACE TABLE product_analysis_mart AS
SELECT 
  p.product_id,
  p.product_name,
  p.category,
  p.unit_price,
  
  -- 売上パフォーマンス
  COUNT(DISTINCT t.transaction_id) as times_sold,
  SUM(t.quantity) as total_quantity_sold,
  SUM(t.quantity * p.unit_price) as total_revenue,
  AVG(i.quantity_on_hand) as avg_inventory_level,
  
  -- 在庫効率性
  ROUND(SUM(t.quantity) * 1.0 / NULLIF(AVG(i.quantity_on_hand), 0), 2) as inventory_turnover_ratio,
  
  -- 店舗間パフォーマンス
  COUNT(DISTINCT t.store_id) as sold_in_stores,
  MODE(s.store_name) as best_performing_store,
  
  -- 顧客嗜好
  COUNT(DISTINCT t.customer_id) as unique_buyers,
  ROUND(SUM(t.quantity) * 1.0 / COUNT(DISTINCT t.customer_id), 2) as avg_quantity_per_customer
  
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
LEFT JOIN inventory i ON p.product_id = i.product_id
LEFT JOIN stores s ON t.store_id = s.store_id
GROUP BY p.product_id, p.product_name, p.category, p.unit_price
```

#### 🔄 Auto Loader パイプライン実装
**実装ディレクトリ**: `パイプライン/`

**1. [BeforeAfter.ipynb] - データ整合性検証**:
```python
# データ処理前後の件数チェック
def validate_data_integrity():
    # 処理前データ件数
    before_counts = {
        'customers': spark.table('customers').count(),
        'products': spark.table('products').count(),
        'transactions': spark.table('transactions').count()
    }
    
    # マート作成後の整合性チェック
    after_counts = {
        'customer_mart': spark.table('customer_summary_mart').count(),
        'store_mart': spark.table('store_sales_summary_mart').count(),
        'product_mart': spark.table('product_analysis_mart').count()
    }
    
    # データ品質レポート生成
    quality_report = spark.sql("""
        SELECT 
          'データ整合性チェック' as check_type,
          CASE 
            WHEN customer_count = customer_mart_count THEN 'OK'
            ELSE 'ERROR'
          END as customer_data_integrity,
          CASE 
            WHEN total_transactions = sum_mart_transactions THEN 'OK'
            ELSE 'ERROR'
          END as transaction_data_integrity
        FROM (
          SELECT 
            (SELECT COUNT(*) FROM customers) as customer_count,
            (SELECT COUNT(*) FROM customer_summary_mart) as customer_mart_count,
            (SELECT SUM(total_transactions) FROM customer_summary_mart) as sum_mart_transactions,
            (SELECT COUNT(*) FROM transactions) as total_transactions
        )
    """)
    
    return quality_report
```

**2. [Volume をトリガーにした Auto Loader.ipynb] - 自動データ取り込み**:
```python
# Auto Loader設定
def setup_auto_loader():
    # 新着トランザクションファイルの監視設定
    auto_loader_stream = (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", "/databricks/schemas/new_transactions")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.rescuedDataColumn", "_rescued_data")
        .load("/databricks/datasets/yukiteru_mart/new_data/")
    )
    
    # リアルタイム処理とマート更新
    def process_new_transactions(batch_df, batch_id):
        # 新規データの前処理
        cleaned_df = batch_df.filter(col("_rescued_data").isNull())
        
        # 既存トランザクションテーブルに追加
        cleaned_df.write.format("delta").mode("append").saveAsTable("transactions")
        
        # マートテーブルの増分更新
        update_customer_mart(batch_df)
        update_store_mart(batch_df)
        
        print(f"Batch {batch_id}: {batch_df.count()} records processed")
    
    # ストリーミング処理開始
    query = (auto_loader_stream.writeStream
        .foreachBatch(process_new_transactions)
        .option("checkpointLocation", "/databricks/checkpoints/auto_loader")
        .trigger(availableNow=True)
        .start()
    )
    
    return query

# マート増分更新関数
def update_customer_mart(new_transactions_df):
    # 影響を受ける顧客のみ再計算
    affected_customers = new_transactions_df.select("customer_id").distinct()
    
    # 部分更新クエリ実行
    spark.sql("""
        MERGE INTO customer_summary_mart target
        USING (
            SELECT customer_id, ... -- 再計算ロジック
            FROM customers c
            JOIN transactions t ON c.customer_id = t.customer_id
            WHERE c.customer_id IN (SELECT customer_id FROM affected_customers_temp)
            GROUP BY c.customer_id, ...
        ) source
        ON target.customer_id = source.customer_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
```

#### 📊 [yukiteru_martダッシュボード.lvdash.json] - ビジネスインテリジェンス
**実装されているダッシュボード機能**:

**1. エグゼクティブサマリー**:
- 総売上・顧客数・取引数のKPI表示
- 前月比成長率とトレンド分析
- 店舗別パフォーマンスランキング

**2. 顧客分析ダッシュボード**:
- 顧客セグメント分布円グラフ
- 年齢層別購買パターン分析
- メンバーシップレベル別売上貢献度
- 顧客ライフタイムバリュー分布

**3. 店舗運営ダッシュボード**:
- 店舗別売上比較棒グラフ
- 地域別パフォーマンスマップ
- 時間帯別売上パターン分析
- 店舗効率性指標（客単価、客数等）

**4. 商品・在庫分析**:
- 商品カテゴリ別売上構成
- 在庫回転率ヒートマップ
- 季節性商品の需要変動
- ABC分析による商品分類

#### 🎯 ビジネス価値とユースケース

**1. データドリブン意思決定支援**:
- リアルタイム売上監視による迅速な経営判断
- 店舗間ベンチマーキングによる改善機会特定
- 顧客セグメント別マーケティング戦略立案

**2. 運営効率化**:
- 在庫最適化による機会損失削減
- 店舗スタッフ配置最適化
- 商品陳列・プロモーション効果測定

**3. 顧客体験向上**:
- 個人化推奨システムの基盤データ
- 顧客満足度向上施策の効果測定
- チャーン予測による顧客維持施策

**4. データガバナンス**:
- データ品質管理とエラー検出
- 参照整合性による信頼性確保
- 監査証跡とコンプライアンス対応

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

**プロジェクト詳細構成:**

#### 📋 データ構造
- **customers.csv**: 顧客マスタ（ID、名前、年齢、性別、メンバーシップ等）
- **products.csv**: 商品マスタ（ID、名前、カテゴリ、価格、在庫等）
- **stores.csv**: 店舗マスタ（ID、名前、立地、管理者、営業時間等）
- **transactions.csv**: 取引データ（取引ID、顧客・商品・店舗ID、数量、日時等）
- **reviews.csv**: レビューデータ（商品ID、評価、コメント等）
- **new_transactions_july2025.csv**: 増分データ（新着取引）

#### 🥉 Bronze Layer - 生データ格納層
**目的**: 元のCSVファイルを最小限の変換でDelta形式に保存
**実装ファイル**: `01_csv_to_bronze.ipynb`
**主要機能**:
- CSVからDelta Tableへの一括変換
- スキーマ自動推論とデータ型最適化
- インデックス追加、監査カラム追加（作成日時等）
- データリネージの確立

**技術的特徴**:
```python
# Auto Loader設定例
.option("cloudFiles.format", "csv")
.option("cloudFiles.schemaLocation", schema_path)
.option("cloudFiles.inferColumnTypes", "true")
```

#### 🥈 Silver Layer - 洗浄・統合層
**目的**: データ品質向上とテーブル間結合の準備
**実装ファイル**: `02_bronz_to_sliver.ipynb`
**主要機能**:
- データクレンジング（NULL値処理、重複除去、異常値検出）
- データ型変換と標準化
- ビジネスルールの適用
- 参照整合性チェック
- テーブル間の正規化・非正規化

**データ変換例**:
```sql
-- 顧客年齢グループ化
CASE 
  WHEN age < 25 THEN '若年層'
  WHEN age < 45 THEN '中年層'
  WHEN age < 65 THEN '壮年層'
  ELSE 'シニア層'
END as age_group

-- 取引金額計算
quantity * unit_price as total_amount
```

#### 🥇 Gold Layer - ビジネス分析層
**目的**: ビジネス要件に特化した分析用テーブル
**実装ファイル**: `03_bronze_to_gold_1.ipynb`, `03_bronze_to_gold_2.ipynb`, `03_bronze_to_gold_3.ipynb`

**Gold 1 - 月次売上サマリー**:
```sql
-- 月次・店舗・商品カテゴリ別売上集計
CREATE OR REPLACE TABLE gold.monthly_sales_summary AS
SELECT 
  year_month,
  store_name,
  product_category,
  COUNT(DISTINCT transaction_id) as transaction_count,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_transaction_value,
  COUNT(DISTINCT customer_id) as unique_customers
FROM silver.transactions_detailed
GROUP BY year_month, store_name, product_category
```

**Gold 2 - 顧客セグメント分析**:
```sql
-- RFM分析による顧客セグメンテーション
CREATE OR REPLACE TABLE gold.customer_segments AS
SELECT 
  customer_id,
  recency_score, frequency_score, monetary_score,
  CASE 
    WHEN rfm_score >= 9 THEN 'VIP顧客'
    WHEN rfm_score >= 7 THEN '優良顧客'
    WHEN rfm_score >= 5 THEN '一般顧客'
    ELSE '休眠顧客'
  END as customer_segment
FROM (
  SELECT *,
    recency_score + frequency_score + monetary_score as rfm_score
  FROM silver.customer_rfm_base
)
```

**Gold 3 - 商品パフォーマンス分析**:
```sql
-- 商品売上 vs レビュー評価分析
CREATE OR REPLACE TABLE gold.product_performance AS
SELECT 
  p.product_name,
  p.category,
  SUM(t.total_amount) as total_sales,
  COUNT(t.transaction_id) as sales_count,
  AVG(r.rating) as avg_rating,
  COUNT(r.review_id) as review_count,
  -- 売上レーティング比率
  ROUND(SUM(t.total_amount) / NULLIF(AVG(r.rating), 0), 2) as sales_per_rating
FROM silver.products p
LEFT JOIN silver.transactions t ON p.product_id = t.product_id
LEFT JOIN silver.reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name, p.category
```

#### 🔄 増分データ処理システム
**目的**: 新着データの効率的な処理とマート更新
**実装ディレクトリ**: `02_データ追加/`

**Auto Loader による新規データ取り込み** (`01_Bronze: Auto Loader による新規CSV自動取り込み.ipynb`):
```python
# ストリーミング取り込み設定
bronze_stream = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .option("cloudFiles.useStrictMode", "true")
  .load(source_path)
)

# Bronze テーブルへの書き込み
bronze_query = (bronze_stream.writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .table("bronze.new_transactions")
)
```

**Silver Layer 増分変換** (`02_Silver: 新着トランザクションを変換・結合.ipynb`):
```sql
-- MERGE INTO による効率的な更新
MERGE INTO silver.transactions_detailed as target
USING (
  SELECT 
    t.*, c.customer_name, p.product_name, s.store_name,
    t.quantity * p.unit_price as total_amount
  FROM bronze.new_transactions t
  JOIN silver.customers c ON t.customer_id = c.customer_id
  JOIN silver.products p ON t.product_id = p.product_id
  JOIN silver.stores s ON t.store_id = s.store_id
  WHERE t.processed_flag = 0
) as source
ON target.transaction_id = source.transaction_id
WHEN NOT MATCHED THEN INSERT *
```

**Gold Layer 再集計** (`03_Gold: Silver全体から再集計.ipynb`):
- 月次売上サマリーの差分更新
- 顧客セグメントの再計算
- 商品パフォーマンス指標の更新
- データ品質メトリクスの生成

#### 📊 実装されている分析機能

**1. 売上分析ダッシュボード**:
- 時系列売上推移（日次・月次・四半期）
- 店舗間パフォーマンス比較
- 商品カテゴリ別売上構成
- 季節性・トレンド分析

**2. 顧客分析**:
- RFM分析による顧客セグメンテーション
- 顧客ライフタイムバリュー（CLV）算出
- チャーン予測モデル用特徴量
- 購買行動パターン分析

**3. 商品・在庫分析**:
- 商品回転率と在庫最適化
- 売上 vs レビュー評価の相関分析
- ABC分析による商品分類
- 季節性商品の需要予測

**4. 店舗運営分析**:
- 店舗立地効果の測定
- スタッフパフォーマンス評価
- 営業時間別売上パターン
- 地域別市場特性分析

#### 🎯 データ品質管理
**実装機能**:
- スキーマ進化の自動検出と対応
- データプロファイリングと異常検出
- 参照整合性チェック
- ビジネスルール違反の検出とアラート
- データリネージの可視化

**品質チェック例**:
```sql
-- データ品質チェッククエリ例
CREATE OR REPLACE VIEW data_quality.transaction_checks AS
SELECT 
  'transactions' as table_name,
  COUNT(*) as total_records,
  COUNT(*) - COUNT(customer_id) as null_customer_ids,
  COUNT(*) - COUNT(product_id) as null_product_ids,
  SUM(CASE WHEN quantity <= 0 THEN 1 ELSE 0 END) as invalid_quantities,
  SUM(CASE WHEN total_amount <= 0 THEN 1 ELSE 0 END) as invalid_amounts
FROM silver.transactions_detailed
```

#### 🔧 技術的最適化
**パフォーマンス向上手法**:
- Z-Order最適化によるクエリ高速化
- パーティショニング戦略（年月別）
- Delta Lake Time Travelによる変更履歴管理
- Auto Compactionによる小ファイル統合
- Bloom Filterによる検索最適化

**監視・運用**:
- Delta Lake メトリクス監視
- ジョブ実行ステータスの追跡
- エラーログ分析とアラート
- リソース使用量最適化

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