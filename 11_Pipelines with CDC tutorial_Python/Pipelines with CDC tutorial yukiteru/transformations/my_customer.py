from pyspark import pipelines as dp
from pyspark.sql.functions import *

dp.create_streaming_table(name="customers_sdp_Python", comment="クリーンでマテリアライズされた顧客テーブル")

dp.create_auto_cdc_flow(
  target="customers_sdp_Python",  # 顧客テーブル（マテリアライズ対象）
  source="customers_cdc_clean_Python",  # 入力されるCDCデータ
  keys=["id"],  # 行のアップサートに使用するキー
  sequence_by=col("operation_date"),  # operation_dateで重複排除し、最新値を取得
  ignore_null_updates=False,
  apply_as_deletes=expr("operation = 'DELETE'"),  # DELETE条件
  except_column_list=["operation", "operation_date", "_rescued_data"],  # 除外するカラム
)
