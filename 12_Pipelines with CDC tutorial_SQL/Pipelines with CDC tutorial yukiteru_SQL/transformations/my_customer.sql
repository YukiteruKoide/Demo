-- 顧客テーブルのストリーミングターゲットを作成
-- Streaming Table（ストリーミングテーブル）は、変更データキャプチャ（CDC）やストリーミングデータの取り込み先となるDeltaテーブルです。
CREATE OR REFRESH STREAMING TABLE customers_sdp_sql;

-- 顧客CDCフロー: customers_cdc_cleanから変更データをcustomersテーブルへSCD Type 1で反映
-- AUTO CDC（自動変更データキャプチャ）フローを作成します。
-- ・FROM stream(customers_cdc_clean_sql): CDCソーステーブル（ストリーミング）を指定
-- ・KEYS (id): 主キー（id）でレコードを一意に識別
-- ・APPLY AS DELETE WHEN operation = "DELETE": operation列が"DELETE"の場合は削除として処理
-- ・SEQUENCE BY operation_date: CDCイベントの順序付けに使用するカラム
-- ・COLUMNS * EXCEPT (operation, operation_date, _rescued_data): 指定したカラムを除外してターゲットに反映
-- ・STORED AS SCD TYPE 1: SCD Type 1（履歴を保持せず最新値のみ反映）でターゲットを更新
CREATE FLOW customers_cdc_flow_sql
AS AUTO CDC INTO customers_sdp_sql
FROM stream(customers_cdc_clean_sql)
KEYS (id)
APPLY AS DELETE WHEN
operation = "DELETE"
SEQUENCE BY operation_date
COLUMNS * EXCEPT (operation, operation_date, _rescued_data)
STORED AS SCD TYPE 1;