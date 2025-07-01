# Databricks notebook source
# DBTITLE 1,初期設定
#個人用の環境を分けるため固有の名前を指定してください。（この後ハンズオン用のデータベース名として利用します。）
user = "ykoide"

### -------------ここより以下は変更不要です ------------------------------
# 利用するDatabase（Schema)を作成
spark.sql(f"CREATE SCHEMA IF NOT EXISTS handson.{user}")
spark.sql(f"USE handson.{user}")

# COMMAND ----------

# DBTITLE 1,２つのテーブル読み込み
from pyspark.sql.types import DoubleType, FloatType

# task1で保存したデータを読み込み
contract_df = spark.table("customer_contract")

# 既存の顧客テーブルを読み込み
info_df = spark.read.table("handson.handson_db.customer_info")

# COMMAND ----------

# DBTITLE 1,結合しテーブルを保存
# contract_df(顧客契約情報)とinfo_df(顧客情報)を結合
customers_df = contract_df.join(info_df, on='customerID')

# データ保存
customers_df.write.mode("overwrite").saveAsTable("customers_table")
