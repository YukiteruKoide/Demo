# Databricks notebook source
# MAGIC %md
# MAGIC # 01. Zerobus POS Demo - テーブルセットアップ
# MAGIC
# MAGIC このノートブックでは、POSデモに必要なDelta tableを作成・初期化します。

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. テーブル作成

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS users.yukiteru_koide.zerobus_pos_transactions (
# MAGIC   transaction_id STRING,
# MAGIC   store_id STRING,
# MAGIC   store_name STRING,
# MAGIC   register_id STRING,
# MAGIC   event_time TIMESTAMP,
# MAGIC   items ARRAY<STRUCT<
# MAGIC     sku: STRING,
# MAGIC     product_name: STRING,
# MAGIC     category: STRING,
# MAGIC     quantity: INT,
# MAGIC     unit_price: DOUBLE
# MAGIC   >>,
# MAGIC   total_amount DOUBLE,
# MAGIC   payment_method STRING,
# MAGIC   customer_id STRING
# MAGIC )
# MAGIC USING DELTA
# MAGIC COMMENT 'POSトランザクションデータ - Zerobus Ingestでリアルタイム投入'
# MAGIC TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. テーブル確認

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE EXTENDED users.yukiteru_koide.zerobus_pos_transactions

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. データクリア（再デモ時に使用）

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 必要に応じてコメントを外して実行
# MAGIC -- TRUNCATE TABLE users.yukiteru_koide.zerobus_pos_transactions
