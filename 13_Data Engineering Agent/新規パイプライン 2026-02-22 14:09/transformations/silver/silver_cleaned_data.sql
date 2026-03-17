-- ============================================================================
-- Silver Layer: データクレンジング
-- ============================================================================
-- 重複除去、表記ゆれ統一、異常値除外、NULL処理を実施

CREATE OR REFRESH STREAMING TABLE silver_cleaned_data
COMMENT "クレンジング済みデータ - 重複除去・正規化・異常値除外・NULL処理済み"
AS
WITH cleaned AS (
  SELECT 
    -- ID: NULLまたは空文字を除外
    TRIM(id) AS id,
    
    -- 名前: 表記ゆれ統一（先頭大文字、残り小文字）、空白除去
    INITCAP(TRIM(firstname)) AS firstname,
    INITCAP(TRIM(lastname)) AS lastname,
    
    -- メール: 小文字統一、空白除去、形式チェック
    LOWER(TRIM(email)) AS email,
    
    -- 住所: 空白の正規化
    REGEXP_REPLACE(TRIM(address), '\\s+', ' ') AS address,
    
    -- 操作: 大文字統一
    UPPER(TRIM(operation)) AS operation,
    
    -- 日付: タイムスタンプ型に変換
    TO_TIMESTAMP(operation_date, 'MM-dd-yyyy HH:mm:ss') AS operation_timestamp,
    
    ingestion_timestamp,
    
    -- 重複除去用: 最新レコードを特定
    ROW_NUMBER() OVER (
      PARTITION BY TRIM(id) 
      ORDER BY TO_TIMESTAMP(operation_date, 'MM-dd-yyyy HH:mm:ss') DESC
    ) AS row_num
    
  FROM STREAM(bronze_raw_data)
  WHERE 
    -- NULL除外
    id IS NOT NULL 
    AND TRIM(id) != ''
    AND email IS NOT NULL
    AND TRIM(email) != ''
    -- メールアドレス形式チェック（基本的な検証）
    AND email RLIKE '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
)
SELECT 
  id,
  firstname,
  lastname,
  email,
  address,
  operation,
  operation_timestamp,
  ingestion_timestamp
FROM cleaned
WHERE row_num = 1;  -- 重複除去: 最新レコードのみ保持
