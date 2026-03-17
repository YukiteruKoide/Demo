/* 
  顧客履歴テーブル(customers_history)から
  各顧客IDごとにaddress, email, firstname, lastnameの件数を集計し
  集計結果をマテリアライズドビュー(customers_history_agg)として作成する
*/
CREATE OR REPLACE MATERIALIZED VIEW customers_history_agg_sql AS
SELECT
  id,
  count("address") as address_count,
  count("email") AS email_count,
  count("firstname") AS firstname_count,
  count("lastname") AS lastname_count
FROM customers_history_sql
GROUP BY id