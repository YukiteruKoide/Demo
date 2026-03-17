-- ============================================================================
-- Bronze Layer: 生データの取り込み
-- ============================================================================
-- VolumeからJSONファイルを増分的に読み込み、生データとして保存

CREATE OR REFRESH STREAMING TABLE bronze_raw_data
COMMENT "VolumeからのCSV/JSON生データ - 変換なし"
AS SELECT 
  id,
  firstname,
  lastname,
  email,
  address,
  operation,
  operation_date,
  _rescued_data,
  current_timestamp() AS ingestion_timestamp
FROM STREAM(read_files(
  '/Volumes/users/yukiteru_koide/raw_data/',
  format => 'json',
  multiLine => true
));
