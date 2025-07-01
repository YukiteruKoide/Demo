-- Databricks notebook source
-- MAGIC %md-sandbox # Delta Live Tables quickstart (SQL)
-- MAGIC
-- MAGIC [Delta Live Tables](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-sql-ref.html)のパイプラインの例を提供するノートブックです。
-- MAGIC
-- MAGIC ## Delta Live Table とは？
-- MAGIC
-- MAGIC <img style="float:right" src="https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/DLT-pipe-2.png" width="800">
-- MAGIC
-- MAGIC **ETL 開発の加速** <br/>
-- MAGIC シンプルなパイプラインの開発とメンテナンスにより、アナリストとデータ・エンジニアの迅速なイノベーションを可能にします。
-- MAGIC
-- MAGIC **運用の複雑さを解消** <br/>
-- MAGIC 複雑な管理タスクを自動化し、パイプラインの運用をより広範に可視化します。
-- MAGIC
-- MAGIC **データの信頼性** <br/>
-- MAGIC 組み込みの品質管理と品質モニタリングにより、正確で有用な BI、データサイエンス、ML を実現します。
-- MAGIC
-- MAGIC **バッチとストリーミングの簡素化** <br/>
-- MAGIC バッチまたはストリーミング処理のための自己最適化と自動スケーリングデータパイプラインを搭載 
-- MAGIC
-- MAGIC ## 今回実施する内容
-- MAGIC 1. ストレージ上にある（今回はDBFS上）JSONクリックストリームデータを新規ファイルのみ読み込みます。
-- MAGIC 1. rawデータテーブルからレコードを読み込み、Delta Live Tablesクエリーと[制約(Constraint)](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-expectations.html)を使用して、クリーニングされ準備されたデータで新しいテーブルを作成します。
-- MAGIC 1. Delta Live Tablesクエリを使用して、準備されたデータに対して分析を実行します。
-- MAGIC
-- MAGIC #### データロード
-- MAGIC 静的なデータやストリーミングデータ、インクリメンタルな取り込みなどに対応しております。
-- MAGIC 詳細は[ドキュメント](https://docs.databricks.com/delta-live-tables/load.html#)をご覧ください。

-- COMMAND ----------

-- DBTITLE 1,インクリメンタルにデータを取り込む
CREATE OR REFRESH STREAMING TABLE clickstream_stream
COMMENT "インクリメンタルにデータを取り込む"
AS SELECT * FROM cloud_files(
  "dbfs:/databricks-datasets/wikipedia-datasets/data-001/clickstream/raw-uncompressed-json/", "json"
)

-- COMMAND ----------

-- DBTITLE 1,データのクリーニングと準備
CREATE OR REFRESH STREAMING TABLE clickstream_clean(
  CONSTRAINT valid_current_page EXPECT (current_page_title IS NOT NULL),
  CONSTRAINT valid_count EXPECT (click_count > 0) ON VIOLATION FAIL UPDATE
)
COMMENT "ウィキペディアのクリックストリームデータをクリーニングし、分析の準備をする。"
AS SELECT
  curr_title AS current_page_title,
  CAST(n AS INT) AS click_count,
  prev_title AS previous_page_title
FROM stream(live.clickstream_stream)

-- COMMAND ----------

-- DBTITLE 1,制約に引っかかったデータを隔離
CREATE OR REFRESH STREAMING TABLE bad_txs (
  CONSTRAINT invalid_current_page EXPECT (current_page_title IS NULL),
  CONSTRAINT invalid_count EXPECT (click_count < 0) 
)
  COMMENT "人による分析が必要なエラーデータ"
AS SELECT * from STREAM(live.clickstream_clean)

-- COMMAND ----------

-- DBTITLE 1,トップ参照ページ
CREATE OR REFRESH LIVE TABLE top_spark_gold
COMMENT "Apache Sparkページにリンクしているトップページを含む表"
AS SELECT
  previous_page_title as referrer,
  click_count
FROM live.clickstream_clean
WHERE current_page_title = 'Apache_Spark'
ORDER BY click_count DESC
LIMIT 10

-- COMMAND ----------

-- MAGIC %md # DLTパイプラインの設定
-- MAGIC
-- MAGIC 左の **ワークフロー** メニューを開き、** Delta Live Table** タブを開き、**パイプラインを作成** をクリックします。
-- MAGIC
-- MAGIC 以下の図のように、<name> の箇所は各自の名前を入れてください。（他の方と被らないように）
-- MAGIC
-- MAGIC <img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/DLT-config.png' width='800'>
-- MAGIC <!---<img src='https://sajpstorage.blob.core.windows.net/maruyama/handsOn/konicaminolta/DLT_AGC.png' width='800'>--->
-- MAGIC
-- MAGIC 作成したら、右上の **開始** ボタンをクリックします。
