CREATE OR REFRESH STREAMING TABLE customers_cdc_bronze_sql
COMMENT "クラウドオブジェクトストレージのランディングゾーンから増分で取り込まれる新規顧客データ";

CREATE FLOW customers_bronze_ingest_flow AS
INSERT INTO customers_cdc_bronze_sql BY NAME
  SELECT *
  FROM STREAM read_files(
    -- 使用しているカタログ/スキーマに置き換えてください:
    "/Volumes/users/yukiteru_koide/raw_data/customers",
    format => "json",
    inferColumnTypes => "true"
  )