# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Bricks RAGシステム セットアップ
# MAGIC
# MAGIC このノートブックでは、Agent Bricksを使用したRAGシステムの初期設定を行います。
# MAGIC
# MAGIC ## 必要な準備
# MAGIC - Unity Catalogの有効化
# MAGIC - Vector Search機能の有効化
# MAGIC - Foundation Modelsへのアクセス

# COMMAND ----------

# MAGIC %md ## 1. 環境設定とライブラリのインポート

# COMMAND ----------

import os
from databricks.vector_search.client import VectorSearchClient
from databricks.agent import AgentClient
import pandas as pd
from pyspark.sql.functions import *

# 設定変数
CATALOG_NAME = "users"
SCHEMA_NAME = "yukiteru_koide"
VECTOR_SEARCH_ENDPOINT = "rag_vector_search_endpoint"

# Unity Catalogの設定
spark.sql(f"USE CATALOG {CATALOG_NAME}")
spark.sql(f"USE SCHEMA {SCHEMA_NAME}")

print(f"✅ カタログ: {CATALOG_NAME}")
print(f"✅ スキーマ: {SCHEMA_NAME}")

# COMMAND ----------

# MAGIC %md ## 2. 知識ベースデータの準備
# MAGIC
# MAGIC RAG用の文書データをテーブル形式で準備します。

# COMMAND ----------

# 知識ベース文書の定義
knowledge_base_docs = [
    {
        "doc_id": "tech_001",
        "title": "メダリオンアーキテクチャガイド",
        "category": "技術",
        "content": """
        メダリオンアーキテクチャは、データレイクハウスの標準的な設計パターンです。
        Bronze層では生データをそのまま保存し、Silver層でデータクリーニングと統合を行い、
        Gold層でビジネス要件に特化した集計・分析を実施します。
        各層で段階的にデータ品質を向上させることで、信頼性の高い分析基盤を構築できます。
        """,
        "keywords": ["メダリオン", "アーキテクチャ", "Bronze", "Silver", "Gold", "データ品質"]
    },
    {
        "doc_id": "tech_002", 
        "title": "Auto Loader使用ガイド",
        "category": "技術",
        "content": """
        Auto Loaderは、クラウドストレージから新しいファイルを自動的に検出・処理するストリーミング機能です。
        cloudFilesフォーマットを使用し、スキーマ推論と進化に対応しています。
        チェックポイント機能により、処理済みファイルのスキップと故障時の復旧が可能です。
        """,
        "keywords": ["Auto Loader", "ストリーミング", "cloudFiles", "スキーマ進化", "チェックポイント"]
    },
    {
        "doc_id": "business_001",
        "title": "Yukiteru Mart 新宿店情報",
        "category": "ビジネス",
        "content": """
        新宿店はYukiteru Martのフラッグシップ店舗です。
        売場面積12,000㎡、地下1階-地上7階の構成で、全7カテゴリの商品を取り扱っています。
        パーソナルショッピングアドバイザー、当日配送サービス、多言語対応スタッフなど、
        充実したサービスを提供しています。営業時間は10:00-22:00（年中無休）です。
        """,
        "keywords": ["新宿店", "フラッグシップ", "12000平米", "多言語対応", "当日配送"]
    },
    {
        "doc_id": "business_002",
        "title": "商品カテゴリ情報",
        "category": "ビジネス",
        "content": """
        Yukiteru Martでは7つの主要カテゴリで商品を展開しています。
        1. 食品・飲料: プレミアム有機野菜、国産黒毛和牛、海外直輸入ワイン
        2. 衣類・ファッション: カジュアルウェア、ビジネススーツ、アクセサリー
        3. 家電・電子機器: スマートホーム機器、キッチン家電、美容・健康家電
        4. ホーム・ガーデン: インテリア家具、寝具、ガーデニング用品
        5. 書籍・文具: ビジネス書籍、高級文具、オフィス用品
        6. スポーツ・アウトドア: フィットネス機器、アウトドア用品
        7. 玩具・ゲーム: 知育玩具、ボードゲーム、模型・ホビー
        """,
        "keywords": ["商品カテゴリ", "食品", "ファッション", "家電", "ホーム", "書籍", "スポーツ", "玩具"]
    },
    {
        "doc_id": "faq_001",
        "title": "Delta Lake Time Travel FAQ",
        "category": "FAQ",
        "content": """
        Q: Delta Lakeでタイムトラベルする方法は？
        A: 以下のSQLコマンドを使用します。
        - 特定の日時: SELECT * FROM table_name TIMESTAMP AS OF '2024-01-15 10:30:00'
        - 特定のバージョン: SELECT * FROM table_name VERSION AS OF 10
        - 履歴確認: DESCRIBE HISTORY table_name
        活用場面：データの誤更新時の復旧、特定時点での分析、A/Bテスト用データセット比較
        """,
        "keywords": ["Delta Lake", "Time Travel", "TIMESTAMP AS OF", "VERSION AS OF", "履歴"]
    }
]

# DataFrameに変換
knowledge_df = spark.createDataFrame(knowledge_base_docs)

# テーブルとして保存
knowledge_df.write.mode("overwrite").saveAsTable("knowledge_base_documents")

print("✅ 知識ベースドキュメントテーブルを作成しました")
display(knowledge_df)

# COMMAND ----------

# MAGIC %md ## 3. Vector Search Endpointの作成
# MAGIC
# MAGIC ベクトル検索のためのエンドポイントを作成します。

# COMMAND ----------

# Vector Search Clientの初期化
vsc = VectorSearchClient()

# エンドポイントの作成（既に存在する場合は使用）
try:
    endpoint = vsc.get_endpoint(VECTOR_SEARCH_ENDPOINT)
    print(f"✅ 既存のエンドポイントを使用: {VECTOR_SEARCH_ENDPOINT}")
except Exception as e:
    print(f"🔄 新しいエンドポイントを作成中: {VECTOR_SEARCH_ENDPOINT}")
    endpoint = vsc.create_endpoint(
        name=VECTOR_SEARCH_ENDPOINT,
        endpoint_type="STANDARD"
    )
    print("✅ Vector Search Endpointを作成しました")

# COMMAND ----------

# MAGIC %md ## 4. Vector Indexの作成
# MAGIC
# MAGIC 知識ベース文書のベクトルインデックスを作成します。

# COMMAND ----------

INDEX_NAME = "knowledge_base_vector_index"

# ベクトルインデックスの設定
vector_index_config = {
    "primary_key": "doc_id",
    "text_column": "content",
    "embedding_model_endpoint_name": "databricks-bge-large-en",  # BGEモデル使用
    "index_name": INDEX_NAME
}

try:
    # 既存のインデックス確認
    index = vsc.get_index(endpoint_name=VECTOR_SEARCH_ENDPOINT, index_name=INDEX_NAME)
    print(f"✅ 既存のインデックスを使用: {INDEX_NAME}")
except Exception as e:
    print(f"🔄 新しいベクトルインデックスを作成中: {INDEX_NAME}")
    
    # ベクトルインデックス作成
    index = vsc.create_delta_sync_index(
        endpoint_name=VECTOR_SEARCH_ENDPOINT,
        source_table_name=f"{CATALOG_NAME}.{SCHEMA_NAME}.knowledge_base_documents",
        index_name=INDEX_NAME,
        primary_key="doc_id",
        text_column="content",
        embedding_model_endpoint_name="databricks-bge-large-en",
        compute_mode="PROVISIONED"
    )
    print("✅ Vector Indexを作成しました")

# COMMAND ----------

# MAGIC %md ## 5. Agent Frameworkの設定
# MAGIC
# MAGIC Agent Bricksを使用したRAGエージェントを設定します。

# COMMAND ----------

# Agent Clientの初期化
agent_client = AgentClient()

# エージェント設定
agent_config = {
    "name": "yukiteru_mart_rag_agent",
    "description": "Yukiteru MartとDatabricksの技術情報に関する質問応答エージェント",
    "model": "databricks-dbrx-instruct",  # DBRXモデル使用
    "vector_search_endpoint": VECTOR_SEARCH_ENDPOINT,
    "vector_search_index": INDEX_NAME,
    "system_prompt": """
    あなたはYukiteru MartとDatabricks技術の専門家です。
    以下の役割で回答してください：
    
    1. Databricks技術（メダリオンアーキテクチャ、Delta Lake、Auto Loader等）に関する質問に正確に回答
    2. Yukiteru Martのビジネス情報（商品、店舗、売上等）について詳しく説明
    3. 操作手順やトラブルシューティングについて具体的なアドバイス提供
    4. 常に日本語で丁寧に回答
    5. 情報が不明な場合は素直に「わからない」と答える
    
    提供された知識ベースの情報を最大限活用し、正確で有用な回答を心がけてください。
    """
}

print("✅ Agent設定を完了しました")
print(f"📝 Agent名: {agent_config['name']}")
print(f"🤖 使用モデル: {agent_config['model']}")

# COMMAND ----------

# MAGIC %md ## 6. セットアップ完了確認
# MAGIC
# MAGIC RAGシステムの基本設定が完了したことを確認します。

# COMMAND ----------

print("🎉 Agent Bricks RAGシステムのセットアップが完了しました！")
print("\n📋 セットアップ内容:")
print(f"  ✅ カタログ・スキーマ: {CATALOG_NAME}.{SCHEMA_NAME}")
print(f"  ✅ 知識ベーステーブル: knowledge_base_documents")
print(f"  ✅ Vector Search Endpoint: {VECTOR_SEARCH_ENDPOINT}")
print(f"  ✅ Vector Index: {INDEX_NAME}")
print(f"  ✅ Agent設定: {agent_config['name']}")

print("\n🚀 次のステップ:")
print("  1. 02_Vector_Index_Creation.py でベクトルインデックスの詳細設定")
print("  2. 03_Demo_Notebooks でRAGシステムのテスト")
print("  3. Basic_QA_Demo.py で質問応答のデモ実行")

# COMMAND ----------

# MAGIC %md ## テスト用クエリ
# MAGIC
# MAGIC セットアップが正常に完了しているか簡単なテストを行います。

# COMMAND ----------

# 知識ベースの内容確認
print("📚 登録された知識ベース文書:")
display(spark.table("knowledge_base_documents").select("doc_id", "title", "category"))

# サンプル検索クエリ（ベクトル検索のテスト）
try:
    # Vector Searchのテスト
    search_results = vsc.get_index(
        endpoint_name=VECTOR_SEARCH_ENDPOINT, 
        index_name=INDEX_NAME
    ).similarity_search(
        query_text="メダリオンアーキテクチャについて教えて",
        columns=["doc_id", "title", "content"],
        num_results=2
    )
    
    print("🔍 ベクトル検索テスト結果:")
    for result in search_results.get("result", {}).get("data_array", []):
        print(f"  - {result[1]}: {result[2][:100]}...")
        
except Exception as e:
    print("⚠️ ベクトル検索のテストは、インデックス作成完了後に実行してください")
    print(f"詳細: {str(e)}")

print("\n✨ セットアップ完了！次のノートブックに進んでください。") 