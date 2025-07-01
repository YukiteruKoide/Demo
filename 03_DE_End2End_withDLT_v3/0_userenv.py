# Databricks notebook source
# DBTITLE 1,ハンズオン用の初期設定
#個人用の環境を分けるため固有の名前を指定してください。（この後ハンズオン用のデータベース名として利用します。）         

user = "Koide"

# COMMAND ----------

# DBTITLE 1,***.  ここより以下は修正不要です  ***


# COMMAND ----------

# Handsonで利用するCatalog
catalog = "databricks_handson"

# 利用するDatabase（Schema)を作成
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{user}")
spark.sql(f"USE {catalog}.{user}")

print(f"今回利用されるデータはここに保存されます: 　{catalog}.{user}")
