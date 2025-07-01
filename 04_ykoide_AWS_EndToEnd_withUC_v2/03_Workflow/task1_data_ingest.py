# Databricks notebook source
# DBTITLE 1,初期設定
#個人用の環境を分けるため固有の名前を指定してください。（この後ハンズオン用のデータベース名として利用します。）
user = "ykoide"

### -------------ここより以下は変更不要です ------------------------------
# 利用するDatabase（Schema)を作成
spark.sql(f"CREATE SCHEMA IF NOT EXISTS handson.{user}")
spark.sql(f"USE handson.{user}")

# COMMAND ----------

# DBTITLE 1,Rawデータ取り込み
df = (
  spark.read.format('csv')
  .option('Header', True)
  .option('inferSchema', True)
  .load('/Volumes/handson/handson_db/handson_volume/customer.csv')
)

# COMMAND ----------

# DBTITLE 1,データクレンジング
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType, FloatType

df = (df.withColumn("totalCharges", col("totalCharges").cast(DoubleType()))
          .withColumnRenamed("churnString", "churn")
          .na.drop(subset=["totalCharges"]))

# COMMAND ----------

# DBTITLE 1,データ保存
df.write.mode("overwrite").saveAsTable("customer_contract")
