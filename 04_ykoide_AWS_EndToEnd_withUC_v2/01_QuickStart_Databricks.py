# Databricks notebook source
# MAGIC %md # Databricks環境の紹介

# COMMAND ----------

# MAGIC %md ##クラスターの作成＆アタッチ
# MAGIC <br>
# MAGIC
# MAGIC - 左のメニューの**クラスター** - **クラスターを作成** を選択
# MAGIC - クラスター名：　<お名前>_cluseter 
# MAGIC - クラスターモード：　シングルノード
# MAGIC - Databricks Runtime バージョン: ML -> 13.3 LTS
# MAGIC - Photonチェックボックスを外す (MLライブラリには対応していないため)
# MAGIC - ノートブックの左上のクラスターリストから、作成したクラスターをアタッチする。
# MAGIC
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/dataeng_handson/cluster.png' width='600' />
# MAGIC
# MAGIC
# MAGIC [Databricksにおけるクラスター作成](https://qiita.com/taka_yayoi/items/d36a469a1e0c0cebaf1b)

# COMMAND ----------

# DBTITLE 1,ハンズオン用の初期設定
#個人用の環境を分けるため固有の名前を指定してください。（この後ハンズオン用のデータベース名として利用します。）
user = "ykoide"

### -------------ここより以下は変更不要です ------------------------------
# 利用するDatabase（Schema)を作成
spark.sql(f"CREATE SCHEMA IF NOT EXISTS handson.{user}")
spark.sql(f"USE handson.{user}")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC
# MAGIC <table>
# MAGIC <tr>
# MAGIC 　　<td>
# MAGIC     
# MAGIC ##Databricks Notebook の概要
# MAGIC     
# MAGIC     特徴
# MAGIC - SQL/Python/R/Scala 言語をサポート
# MAGIC - Markdownや、HTML, Shell Command 等もサポート
# MAGIC - コラボレーション機能
# MAGIC - アクセス権限の付与
# MAGIC - 可視化機能 (display)
# MAGIC - ヒストリー機能
# MAGIC - スケジュール実行
# MAGIC - Git base コラボレーション (CI/CD)
# MAGIC - MLflow インテグレーション
# MAGIC - <B>AI Assistant</B>
# MAGIC
# MAGIC https://databricks.com/jp/product/collaborative-notebooks
# MAGIC
# MAGIC   </td>
# MAGIC   <td>
# MAGIC <img style="margin-top:25px;" src="https://psajpstorage.blob.core.windows.net/commonfiles/Collaboration001.gif" width="800">
# MAGIC     </td>
# MAGIC   </tr>
# MAGIC   </table>
# MAGIC   

# COMMAND ----------

# MAGIC %md # AI Assistantのご紹介
# MAGIC
# MAGIC https://qiita.com/taka_yayoi/items/855e15def68150bdea55
# MAGIC
# MAGIC AI Assistantに以下のような質問を投げてみよう。 <br>
# MAGIC ```samples.nyctaxi.trips データの平均運賃を計算して```
# MAGIC
# MAGIC 表示されたコードを入力して実行してみよう。
# MAGIC

# COMMAND ----------

# MAGIC %md # データ取り込み
# MAGIC
# MAGIC データの取り込み方法はいくつかありますが、今回は以下の２つの方法をご紹介します。
# MAGIC - UnityCatalog Volumeからの取り込み
# MAGIC - 既存テーブルからの取り込み
# MAGIC
# MAGIC データ追加メニュー <br>
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/dataeng_handson/data_ingest.png' width='800'>

# COMMAND ----------

# MAGIC %md ## 1. Unity Catalog Volumes からデータの取り込み
# MAGIC
# MAGIC #### 1) 「カタログエクスプローラ」　から対象のボリュームを確認
# MAGIC (databricks_handson.handson_db.handson_volume)　<br>
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/dataeng_handson/catalog_volume.png' width='800'>
# MAGIC
# MAGIC (*) こちらのサンプルファイルをあらかじめアップロードしております。<br>
# MAGIC <a href='https://sajpstorage.blob.core.windows.net/public-data/customer.csv' target=_blank>https://sajpstorage.blob.core.windows.net/public-data/customer.csv </a>

# COMMAND ----------

# MAGIC %md ## アップロードしたファイルを確認してみます
# MAGIC
# MAGIC "%sh" マジックコマンドを使うと Shellコマンドが利用出来ます。

# COMMAND ----------

# MAGIC %sh
# MAGIC head /Volumes/handson/handson_db/handson_volume/customer.csv

# COMMAND ----------

# MAGIC %md ## ノートブック上にデータを呼び出してみましょう

# COMMAND ----------

# DBTITLE 1,Pythonで呼び出し
df = (
  spark.read.format('csv')
  .option('Header', True)
  .option('inferSchema', True)
  .load('/Volumes/handson/handson_db/handson_volume/customer.csv') 
)

display(df)

# COMMAND ----------

# DBTITLE 1,注意：dfはPandas dfではなく、Spark df
type(df)

# COMMAND ----------

# DBTITLE 1,SQLで呼び出し
# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMPORARY VIEW CONTRACT
# MAGIC USING CSV
# MAGIC OPTIONS (path "/Volumes/handson/handson_db/handson_volume/customer.csv", header "true", mode "FAILFAST");
# MAGIC SELECT * FROM CONTRACT

# COMMAND ----------

# MAGIC %md
# MAGIC ## データのクレンジング
# MAGIC 1. 元データの型確認
# MAGIC 2. データ型の変更(string → double)　& 欠損値の除去

# COMMAND ----------

# DBTITLE 1,1. 元データの型確認
df.printSchema()

# COMMAND ----------

# DBTITLE 1,2. データ型の変更&欠損値の除去(クレンジング)
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType, FloatType

df = (df.withColumn("totalCharges", col("totalCharges").cast(DoubleType()))
          .withColumnRenamed("churnString", "churn")
          .na.drop(subset=["totalCharges"])
)

display(df)

# COMMAND ----------

# DBTITLE 1,データの保存
df.write.mode("overwrite").saveAsTable("customer_contract")

# COMMAND ----------

# MAGIC %md ## 2. 既存Deltaテーブルからの呼び出し
# MAGIC
# MAGIC 左のメニューの**データ**　を開くと保存済みのデータが確認できます。<br>
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/explore.png' width='800'>
# MAGIC <br>
# MAGIC 左のデータマークからも呼び出せます<br>
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/data_menu.png' width='200'>

# COMMAND ----------

# DBTITLE 1,既存データの呼び出し
from pyspark.sql.types import DoubleType, FloatType

info_df = spark.read.table("handson.handson_db.customer_info")

display(info_df)

# COMMAND ----------

# MAGIC %md # データを結合して新しいデータを作成
# MAGIC
# MAGIC contract_df(顧客契約情報)とinfo_df(顧客情報)を結合して新しいデータを作成し分析してみる

# COMMAND ----------

# 最初に保存したデータを呼び出し
contract_df = spark.table("customer_contract")

contract_df.display()

# COMMAND ----------

# 最初に保存したデータを呼び出し
contract_df = spark.table("customer_contract")
contract_df.display()

# COMMAND ----------

# contract_df(顧客契約情報)とinfo_df(顧客情報)を結合
# Databricksのデフォルトのjoinはinner join
customers_df = contract_df.join(info_df, on='customerID')

# データ保存
customers_df.write.mode("overwrite").saveAsTable("customers_table")

display(customers_df)

# COMMAND ----------

# MAGIC %md ## データエクスプローラで、データリネージュを見てみよう
# MAGIC
# MAGIC 左の「データ」メニューを開き、対象のカタログ・スキーマ内のテーブルから、**customers_table** を開き、依存関係タブにある「リネージュ」ボタンをクリックしてみよう
# MAGIC
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/dataeng_handson/data_lineage.png' width='600'>

# COMMAND ----------

# MAGIC %md # 最後にスケジュール設定をしてみよう
# MAGIC
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/jobs.png' width='800'>　<br>
# MAGIC <br>
# MAGIC ### 左のワークフローメニューからも確認することができます。<br>
# MAGIC
# MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/workflow.png' width='800'>

# COMMAND ----------

test = "Hello, World!"
print(test)

# COMMAND ----------

# PandasのDataFrameを作成する
import pandas as pd

# DataFrameを生成する
df = pd.DataFrame({
       'col1': [1, 2],
       'col2': ['A', 'B']
     })

# 表示
df


# COMMAND ----------


