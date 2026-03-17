CREATE OR REFRESH STREAMING TABLE customers_cdc_clean_sql (
  -- _rescued_data列がNULLであることを確認し、不正なデータ行は削除します
  CONSTRAINT no_rescued_data EXPECT (_rescued_data IS NULL) ON VIOLATION DROP ROW,
  -- id列がNULLでないことを確認し、NULLの場合は行を削除します
  CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW,
  -- operation列が'APPEND', 'DELETE', 'UPDATE'のいずれかであることを確認し、該当しない場合は行を削除します
  CONSTRAINT valid_operation EXPECT (operation IN ('APPEND', 'DELETE', 'UPDATE')) ON VIOLATION DROP ROW
)
COMMENT "クラウドオブジェクトストレージのランディングゾーンから増分で取り込まれた新規顧客データ";

-- customers_cdc_bronze_sqlテーブルからデータを取り込み、customers_cdc_clean_sqlストリーミングテーブルにレコードを挿入するフローを定義します
CREATE FLOW customers_cdc_clean_flow_sql AS
INSERT INTO customers_cdc_clean_sql BY NAME
SELECT * FROM STREAM customers_cdc_bronze_sql;