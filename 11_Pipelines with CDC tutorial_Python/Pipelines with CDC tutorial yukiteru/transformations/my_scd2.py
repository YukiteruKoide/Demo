from pyspark import pipelines as dp
from pyspark.sql.functions import *

# テーブルを作成（顧客のSCD2履歴用）
dp.create_streaming_table(
    name="customers_history_Python", comment="顧客のスローリー・チェンジング・ディメンションタイプ2"
)

# すべての変更をSCD2として保存
dp.create_auto_cdc_flow(
    target="customers_history_Python",
    source="customers_cdc_clean_Python",
    keys=["id"],
    sequence_by=col("operation_date"),
    ignore_null_updates=False,
    apply_as_deletes=expr("operation = 'DELETE'"),
    except_column_list=["operation", "operation_date", "_rescued_data"],
    stored_as_scd_type="2",
)  # SCD2を有効化し、個別の更新を保存
