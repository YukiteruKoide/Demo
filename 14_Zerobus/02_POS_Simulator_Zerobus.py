# Databricks notebook source
# MAGIC %md
# MAGIC # 02. POS シミュレーター（Zerobus Ingest SDK）
# MAGIC
# MAGIC 複数店舗のPOSレジデータをシミュレートし、Zerobus Ingest SDKで直接Delta tableにプッシュします。
# MAGIC
# MAGIC **アーキテクチャ:**
# MAGIC ```
# MAGIC POS Simulator (このノートブック)
# MAGIC     ↓ Zerobus Ingest SDK (gRPC)
# MAGIC Delta Table (users.yukiteru_koide.zerobus_pos_transactions)
# MAGIC     ↓
# MAGIC Lakeview Dashboard（リアルタイム可視化）
# MAGIC ```
# MAGIC
# MAGIC **ポイント:** Kafka/Event Hubs不要。Databricksだけで完結。

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. SDK インストール

# COMMAND ----------

# MAGIC %pip install databricks-zerobus-ingest-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 設定

# COMMAND ----------

import json
import time
import random
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from zerobus.sdk.sync import ZerobusSdk
from zerobus.sdk.shared import RecordType, StreamConfigurationOptions, TableProperties

# Zerobus設定
WORKSPACE_ID = "1444828305810485"
REGION = "us-west-2"
SERVER_ENDPOINT = f"https://{WORKSPACE_ID}.zerobus.{REGION}.cloud.databricks.com"
WORKSPACE_URL = "https://e2-demo-field-eng.cloud.databricks.com"
TABLE_FULL_NAME = "users.yukiteru_koide.zerobus_pos_transactions"

# サービスプリンシパル認証（OAuth M2M）
# 本番ではdbutils.secrets等で管理してください
CLIENT_ID = "2bd76b1a-21b5-41a9-a4f4-ca2a21215dc8"
CLIENT_SECRET = "dosed9763d8b350a6b7a57fa50f3d6ffdeaa"

print(f"Zerobus Endpoint: {SERVER_ENDPOINT}")
print(f"Target Table: {TABLE_FULL_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. 商品マスタ＆店舗マスタ

# COMMAND ----------

# 店舗マスタ
STORES = [
    {"store_id": "store-tokyo-shibuya",    "store_name": "渋谷店"},
    {"store_id": "store-tokyo-shinjuku",   "store_name": "新宿店"},
    {"store_id": "store-osaka-umeda",      "store_name": "梅田店"},
    {"store_id": "store-osaka-namba",      "store_name": "なんば店"},
    {"store_id": "store-nagoya-sakae",     "store_name": "栄店"},
    {"store_id": "store-fukuoka-tenjin",   "store_name": "天神店"},
    {"store_id": "store-sapporo-tanuki",   "store_name": "狸小路店"},
    {"store_id": "store-sendai-ichibancho","store_name": "一番町店"},
]

# 商品マスタ（小売）
PRODUCTS = [
    # 食品・飲料
    {"sku": "FD-001", "product_name": "おにぎり（鮭）",       "category": "食品",   "unit_price": 150},
    {"sku": "FD-002", "product_name": "サンドイッチ",         "category": "食品",   "unit_price": 380},
    {"sku": "FD-003", "product_name": "カップ麺",             "category": "食品",   "unit_price": 220},
    {"sku": "FD-004", "product_name": "弁当（幕の内）",       "category": "食品",   "unit_price": 550},
    {"sku": "FD-005", "product_name": "パン（メロンパン）",   "category": "食品",   "unit_price": 160},
    {"sku": "BV-001", "product_name": "ペットボトル水",       "category": "飲料",   "unit_price": 110},
    {"sku": "BV-002", "product_name": "コーヒー（缶）",       "category": "飲料",   "unit_price": 140},
    {"sku": "BV-003", "product_name": "緑茶（500ml）",        "category": "飲料",   "unit_price": 160},
    {"sku": "BV-004", "product_name": "エナジードリンク",     "category": "飲料",   "unit_price": 220},
    {"sku": "BV-005", "product_name": "牛乳（1L）",           "category": "飲料",   "unit_price": 240},
    # 日用品
    {"sku": "HG-001", "product_name": "ティッシュペーパー",   "category": "日用品", "unit_price": 280},
    {"sku": "HG-002", "product_name": "洗剤",                 "category": "日用品", "unit_price": 350},
    {"sku": "HG-003", "product_name": "歯ブラシ",             "category": "日用品", "unit_price": 200},
    {"sku": "HG-004", "product_name": "シャンプー",           "category": "日用品", "unit_price": 480},
    {"sku": "HG-005", "product_name": "除菌シート",           "category": "日用品", "unit_price": 320},
    # スナック・菓子
    {"sku": "SN-001", "product_name": "ポテトチップス",       "category": "菓子",   "unit_price": 180},
    {"sku": "SN-002", "product_name": "チョコレート",         "category": "菓子",   "unit_price": 250},
    {"sku": "SN-003", "product_name": "グミ",                 "category": "菓子",   "unit_price": 130},
    {"sku": "SN-004", "product_name": "アイスクリーム",       "category": "菓子",   "unit_price": 300},
    {"sku": "SN-005", "product_name": "せんべい",             "category": "菓子",   "unit_price": 200},
]

PAYMENT_METHODS = ["credit_card", "cash", "ic_card", "qr_pay", "e_money"]
# 決済方法の重み（キャッシュレスが多め）
PAYMENT_WEIGHTS = [30, 15, 25, 20, 10]

print(f"店舗数: {len(STORES)}")
print(f"商品数: {len(PRODUCTS)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. POSトランザクション生成

# COMMAND ----------

def generate_transaction(store: dict) -> dict:
    """1件のPOSトランザクションを生成"""
    # 1〜5品をランダムに選択
    num_items = random.choices([1, 2, 3, 4, 5], weights=[25, 35, 25, 10, 5])[0]
    selected_products = random.sample(PRODUCTS, num_items)

    items = []
    total = 0.0
    for product in selected_products:
        qty = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
        item = {
            "sku": product["sku"],
            "product_name": product["product_name"],
            "category": product["category"],
            "quantity": qty,
            "unit_price": float(product["unit_price"])
        }
        items.append(item)
        total += product["unit_price"] * qty

    # 顧客ID（ポイントカード利用率60%）
    customer_id = f"cust-{random.randint(10000, 99999)}" if random.random() < 0.6 else None

    transaction = {
        "transaction_id": f"txn-{int(time.time()*1000)}-{random.randint(1000,9999)}",
        "store_id": store["store_id"],
        "store_name": store["store_name"],
        "register_id": f"reg-{random.randint(1, 6):02d}",
        "event_time": int(datetime.now(timezone.utc).timestamp() * 1_000_000),  # エポックマイクロ秒
        "items": items,
        "total_amount": round(total, 0),
        "payment_method": random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0],
        "customer_id": customer_id if customer_id else ""
    }
    return transaction

# テスト: 1件生成して確認
sample = generate_transaction(STORES[0])
print(json.dumps(sample, ensure_ascii=False, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Zerobus Ingest 接続テスト

# COMMAND ----------

# Zerobus SDKでストリーム作成 & 1件送信テスト
sdk = ZerobusSdk(SERVER_ENDPOINT, WORKSPACE_URL)
table_props = TableProperties(TABLE_FULL_NAME)
options = StreamConfigurationOptions(record_type=RecordType.JSON)

stream = sdk.create_stream(CLIENT_ID, CLIENT_SECRET, table_props, options)

test_txn = generate_transaction(STORES[0])
offset = stream.ingest_record_offset(test_txn)
stream.wait_for_offset(offset)

print("✅ Zerobus Ingest 接続成功！1件送信完了")
print(f"   Table: {TABLE_FULL_NAME}")
print(f"   Transaction: {test_txn['transaction_id']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. リアルタイムPOSデータ送信
# MAGIC
# MAGIC 複数店舗から同時にPOSデータを送信します。
# MAGIC **デモ時はこのセルを実行して、ダッシュボードと並べて見せてください。**

# COMMAND ----------

def create_store_stream():
    """店舗ごとにZerobusストリームを作成"""
    sdk = ZerobusSdk(SERVER_ENDPOINT, WORKSPACE_URL)
    table_props = TableProperties(TABLE_FULL_NAME)
    options = StreamConfigurationOptions(record_type=RecordType.JSON)
    return sdk.create_stream(CLIENT_ID, CLIENT_SECRET, table_props, options)


def send_batch(stream, store: dict, batch_size: int = 5) -> dict:
    """1店舗分のバッチを生成して送信"""
    try:
        for _ in range(batch_size):
            txn = generate_transaction(store)
            stream.ingest_record(txn)  # fire-and-forget（高速）
        return {"store": store["store_name"], "count": batch_size, "success": True}
    except Exception as e:
        return {"store": store["store_name"], "count": 0, "success": False, "error": str(e)}


def run_simulation(duration_seconds: int = 60, interval_seconds: float = 2.0, stores_per_batch: int = 4):
    """
    POSシミュレーションを実行

    Args:
        duration_seconds: シミュレーション実行時間（秒）
        interval_seconds: バッチ送信間隔（秒）
        stores_per_batch: 1回のバッチで送信する店舗数
    """
    # 各店舗用のストリームを事前作成
    print("ストリーム作成中...")
    store_streams = {}
    for store in STORES:
        store_streams[store["store_id"]] = create_store_stream()
    print(f"✅ {len(store_streams)}店舗分のストリーム作成完了")

    start_time = time.time()
    total_sent = 0
    total_errors = 0
    batch_num = 0

    print(f"\n🚀 POSシミュレーション開始")
    print(f"   実行時間: {duration_seconds}秒 | 送信間隔: {interval_seconds}秒")
    print(f"   店舗数: {stores_per_batch}/{len(STORES)}店舗/バッチ")
    print("-" * 60)

    try:
        while time.time() - start_time < duration_seconds:
            batch_num += 1
            # ランダムに店舗を選択
            active_stores = random.sample(STORES, min(stores_per_batch, len(STORES)))

            for store in active_stores:
                s = store_streams[store["store_id"]]
                batch_size = random.randint(3, 8)
                result = send_batch(s, store, batch_size)
                if result["success"]:
                    total_sent += result["count"]
                else:
                    total_errors += result["count"]

            elapsed = time.time() - start_time
            print(f"  Batch #{batch_num:03d} | {elapsed:.0f}s | 累計: {total_sent}件送信 | エラー: {total_errors}件")

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n⏹ シミュレーション停止（手動）")
    finally:
        # ストリームをクローズ
        for s in store_streams.values():
            try:
                s.close()
            except Exception:
                pass

    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"✅ シミュレーション完了")
    print(f"   実行時間: {elapsed:.1f}秒")
    print(f"   送信件数: {total_sent}件")
    print(f"   スループット: {total_sent/elapsed:.1f} 件/秒")
    print(f"   エラー: {total_errors}件")

# COMMAND ----------

# MAGIC %md
# MAGIC ### ▶ シミュレーション実行
# MAGIC
# MAGIC パラメータを調整して実行してください：
# MAGIC - `duration_seconds`: デモの長さ（デフォルト60秒）
# MAGIC - `interval_seconds`: 送信間隔（短いほど高頻度）
# MAGIC - `stores_per_batch`: 同時送信する店舗数

# COMMAND ----------

# === シミュレーション実行 ===
# 60秒間、2秒間隔で4店舗ずつ同時送信します。
# デモ時はダッシュボードと並べてリアルタイムにデータが流れる様子を確認できます。
run_simulation(duration_seconds=60, interval_seconds=2.0, stores_per_batch=4)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. 送信データ確認

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   transaction_id,
# MAGIC   store_name,
# MAGIC   register_id,
# MAGIC   event_time,
# MAGIC   total_amount,
# MAGIC   payment_method,
# MAGIC   size(items) as item_count
# MAGIC FROM users.yukiteru_koide.zerobus_pos_transactions
# MAGIC ORDER BY event_time DESC
# MAGIC LIMIT 20

# COMMAND ----------

# MAGIC %sql
# MAGIC -- サマリー
# MAGIC SELECT
# MAGIC   COUNT(*) as total_transactions,
# MAGIC   COUNT(DISTINCT store_id) as active_stores,
# MAGIC   ROUND(SUM(total_amount)) as total_sales,
# MAGIC   ROUND(AVG(total_amount)) as avg_transaction,
# MAGIC   MIN(event_time) as first_event,
# MAGIC   MAX(event_time) as last_event
# MAGIC FROM users.yukiteru_koide.zerobus_pos_transactions
