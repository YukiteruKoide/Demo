# Databricks notebook source
# MAGIC %md 
# MAGIC # セットアップ方法
# MAGIC ハンズオンの前にこちらのノートブックを実行しておきます。

# COMMAND ----------

# MAGIC %md
# MAGIC ## スキーマの作成 

# COMMAND ----------

# デモで利用するスキーマ情報を定義します
# 下記の「yukiteru」を適切な名前に変更してください
# schema = 'Koide'

# # Schemaの作成
# spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}_handson")



# COMMAND ----------

spark.sql("USE users.yukiteru_koide")

# COMMAND ----------

# MAGIC %md 
# MAGIC ## テーブルの作成

# COMMAND ----------

import seaborn as sns
pandas_df = sns.load_dataset('titanic')
spark_df = spark.createDataFrame(pandas_df)

(spark_df
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable(f"titanic")
)


# COMMAND ----------

# MAGIC %md
# MAGIC # schemaの削除

# COMMAND ----------

# MAGIC %sql
# MAGIC -- DROP SCHEMA IF EXISTS Koide_handson

# COMMAND ----------


