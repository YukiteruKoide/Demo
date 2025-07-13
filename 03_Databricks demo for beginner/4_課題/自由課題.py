# Databricks notebook source
# MAGIC %md
# MAGIC # ライブラリのインポート

# COMMAND ----------

import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
import seaborn as sns

# COMMAND ----------

# MAGIC %md
# MAGIC # 準備
# MAGIC 注意！パスを自分の名前に変更してください
# MAGIC

# COMMAND ----------

# data import
Pandas_X = pd.DataFrame(dataset['data'], columns=dataset['feature_names'])
Pandas_y = dataset['target']

# Convert Pandas_X to a Spark DataFrame
spark_X = spark.createDataFrame(Pandas_X)
spark_y = spark.createDataFrame(Pandas_y)

# `***_handson`データベースを使用
spark.sql("USE ***_handson")

# `X`をHiveメタストアのテーブルとして保存
spark_X.write.format("delta").mode("overwrite").saveAsTable("fetch_california_housing_feature")
spark_y.write.format("delta").mode("overwrite").saveAsTable("fetch_california_housing_target")



# COMMAND ----------

# MAGIC %md
# MAGIC # データの内容
# MAGIC |データ項目|説明|
# MAGIC |-|-|
# MAGIC |MedInc|ブロックの所得中央値|
# MAGIC |HouseAge|ブロックの家屋年齢の中央値|
# MAGIC |AveRooms|1世帯あたりの平均部屋数|
# MAGIC |AveBedrms|1世帯あたりの平均寝室数|
# MAGIC |Population|ブロックの人口|
# MAGIC |AveOccup|世帯人数の平均値|
# MAGIC |Latitude|緯度|
# MAGIC |Longitude|経度|
# MAGIC |Price|住宅価格|

# COMMAND ----------

# MAGIC %md
# MAGIC # 課題
# MAGIC 1. カタログを確認し、'fetch_california_housing_feature'、'fetch_california_housing_target'が存在するか確認
# MAGIC 2. データの内容をカタログの画面から確認
# MAGIC 3. 「クエリ」を実行し、可視化をする
# MAGIC 4. 「ノートブック」を利用し、'fetch_california_housing_feature'をSQLで取得
# MAGIC 5. 「ノートブック」を利用し、'fetch_california_housing_target'をSQLで取得
# MAGIC 3. 上記2テーブルのEDAを実施してください

# COMMAND ----------

# こちらにコードを記載してください

# COMMAND ----------

# MAGIC %md
# MAGIC # 解答例

# COMMAND ----------

# MAGIC %sql
# MAGIC -- データの取得およびデータのプロファイルの実施
# MAGIC SELECT * FROM koide_handson.fetch_california_housing_feature

# COMMAND ----------

# MAGIC %sql
# MAGIC -- データの取得およびデータのプロファイルの実施
# MAGIC SELECT * FROM koide_handson.fetch_california_housing_target

# COMMAND ----------

# データをデータフレームへ格納
spark_df = spark.sql("SELECT * FROM hive_metastore.koide_handson.fetch_california_housing_feature")
pandas_df = spark_df.toPandas()

# データの表示
display(pandas_df)

# COMMAND ----------

sns.pairplot(pandas_df)

# COMMAND ----------

sns.heatmap(pandas_df.corr(), annot=True)
