-- customers_cdc_cleanテーブルの変更履歴をSCD Type 2でcustomers_historyテーブルに格納する処理
CREATE OR REFRESH STREAMING TABLE customers_history_sql;

-- customers_cdc_cleanテーブルの変更データキャプチャ（CDC）をcustomers_historyテーブルに適用するフロー
CREATE FLOW customers_history_cdc_sql
AS AUTO CDC INTO
  customers_history_sql
FROM stream(customers_cdc_clean_sql)
KEYS (id)
APPLY AS DELETE WHEN
operation = "DELETE"
SEQUENCE BY operation_date
COLUMNS * EXCEPT (operation, operation_date, _rescued_data)
STORED AS SCD TYPE 2;