-- ============================================================================
-- Gold Layer: 月別サマリー
-- ============================================================================
-- 月別の操作サマリーを集計（顧客登録・更新・削除の統計）

CREATE OR REFRESH MATERIALIZED VIEW gold_monthly_summary
COMMENT "月別操作サマリー - 顧客の登録・更新・削除の月次統計"
AS
SELECT 
  DATE_TRUNC('MONTH', operation_timestamp) AS month,
  YEAR(operation_timestamp) AS year,
  MONTH(operation_timestamp) AS month_number,
  
  -- 操作タイプ別の件数
  COUNT(*) AS total_operations,
  COUNT(CASE WHEN operation = 'APPEND' THEN 1 END) AS append_count,
  COUNT(CASE WHEN operation = 'UPDATE' THEN 1 END) AS update_count,
  COUNT(CASE WHEN operation = 'DELETE' THEN 1 END) AS delete_count,
  
  -- ユニーク顧客数
  COUNT(DISTINCT id) AS unique_customers,
  
  -- 最初と最後の操作日時
  MIN(operation_timestamp) AS first_operation,
  MAX(operation_timestamp) AS last_operation
  
FROM silver_cleaned_data
GROUP BY ALL
ORDER BY month DESC;
