from pyspark import pipelines as dp
from pyspark.sql.functions import *

path = "/Volumes/users/yukiteru_koide/raw_data/customers"

# カタログとスキーマを明示する場合
dp.create_streaming_table(
    name="customers_cdc_bronze_Python",
    comment="クラウドオブジェクトストレージのランディングゾーンから増分取り込まれる新規顧客データ"
)

@dp.append_flow(
    target="customers_cdc_bronze_Python",
    name="customers_bronze_ingest_flow"
)
def customers_bronze_ingest_flow():
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.inferColumnTypes", "true")
            .load(path)
    )