# Databricks notebook source
# MAGIC %run ../0_userenv

# COMMAND ----------

# DBTITLE 1,２つのテーブル読み込み
from pyspark.sql.types import DoubleType, FloatType

# task1で保存したデータを読み込み
contract_df = spark.table("customer_contract")

# 既存の顧客テーブルを読み込み
info_df = spark.read.table(f"{catalog}.handson_db.customer_info")

# COMMAND ----------

# DBTITLE 1,結合しテーブルを保存
# contract_df(顧客契約情報)とinfo_df(顧客情報)を結合
customers_df = contract_df.join(info_df, on='customerID')

# データ保存
customers_df.write.mode("overwrite").saveAsTable("customers_table")
