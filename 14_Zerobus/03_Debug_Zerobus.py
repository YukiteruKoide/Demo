# Databricks notebook source
# MAGIC %md
# MAGIC # Debug: Zerobus接続テスト

# COMMAND ----------

import requests, json
from datetime import datetime, timezone

WORKSPACE_ID = "1444828305810485"
REGION = "us-west-2"
ZEROBUS_ENDPOINT = f"https://{WORKSPACE_ID}.zerobus.{REGION}.cloud.databricks.com"
TABLE_FULL_NAME = "users.yukiteru_koide.zerobus_pos_transactions"
INGEST_URL = f"{ZEROBUS_ENDPOINT}/zerobus/v1/tables/{TABLE_FULL_NAME}/insert"

TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

print(f"Endpoint: {INGEST_URL}")
print(f"Token (first 20 chars): {TOKEN[:20]}...")

# COMMAND ----------

# テスト送信（エラー詳細を表示）
test_data = [{
    "transaction_id": "test-001",
    "store_id": "store-test",
    "store_name": "テスト店",
    "register_id": "reg-01",
    "event_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    "items": [{"sku": "TEST-001", "product_name": "テスト商品", "category": "食品", "quantity": 1, "unit_price": 100.0}],
    "total_amount": 100.0,
    "payment_method": "cash",
    "customer_id": None
}]

print("=== Request ===")
print(f"URL: {INGEST_URL}")
print(f"Body: {json.dumps(test_data, ensure_ascii=False)[:200]}")

response = requests.post(INGEST_URL, headers=HEADERS, json=test_data)

print(f"\n=== Response ===")
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body: {response.text}")
