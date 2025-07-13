# Databricks notebook source
# MAGIC %run ../0_userenv

# COMMAND ----------

# DBTITLE 1,Rawデータ取り込み
df = (
  spark.read.format('csv')
  .option('Header', True)
  .option('inferSchema', True)
  .load(f'/Volumes/{catalog}/handson_db/handson_volume/customer.csv') 
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
