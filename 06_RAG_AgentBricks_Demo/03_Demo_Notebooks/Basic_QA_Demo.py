# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Bricks RAG 質問応答デモ
# MAGIC
# MAGIC このノートブックでは、作成したRAGシステムを使用して、自然言語での質問応答を実演します。
# MAGIC
# MAGIC ## デモ内容
# MAGIC 1. 技術系質問（Databricks機能）
# MAGIC 2. ビジネス系質問（Yukiteru Mart情報）
# MAGIC 3. インタラクティブな質問応答

# COMMAND ----------

# MAGIC %md ## 1. セットアップとライブラリのインポート

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient
from databricks.agent import AgentClient
import pandas as pd

# 設定（前回のセットアップと同じ）
CATALOG_NAME = "users"
SCHEMA_NAME = "yukiteru_koide"
VECTOR_SEARCH_ENDPOINT = "rag_vector_search_endpoint"
INDEX_NAME = "knowledge_base_vector_index"

# Unity Catalogの設定
spark.sql(f"USE CATALOG {CATALOG_NAME}")
spark.sql(f"USE SCHEMA {SCHEMA_NAME}")

print("✅ 環境設定完了")

# COMMAND ----------

# MAGIC %md ## 2. RAG検索機能のテスト
# MAGIC
# MAGIC まず、ベクトル検索が正常に動作することを確認します。

# COMMAND ----------

# Vector Search Clientの初期化
vsc = VectorSearchClient()

def search_knowledge_base(query_text, num_results=3):
    """知識ベースから関連文書を検索する関数"""
    try:
        index = vsc.get_index(endpoint_name=VECTOR_SEARCH_ENDPOINT, index_name=INDEX_NAME)
        results = index.similarity_search(
            query_text=query_text,
            columns=["doc_id", "title", "content", "category"],
            num_results=num_results
        )
        
        search_results = []
        for result in results.get("result", {}).get("data_array", []):
            search_results.append({
                "doc_id": result[0],
                "title": result[1], 
                "content": result[2],
                "category": result[3],
                "score": result[4] if len(result) > 4 else "N/A"
            })
        
        return search_results
    except Exception as e:
        print(f"検索エラー: {str(e)}")
        return []

# テスト検索
test_query = "メダリオンアーキテクチャについて教えて"
print(f"🔍 検索クエリ: {test_query}")
results = search_knowledge_base(test_query)

print(f"\n📚 検索結果 ({len(results)}件):")
for i, result in enumerate(results, 1):
    print(f"{i}. [{result['category']}] {result['title']}")
    print(f"   内容: {result['content'][:100]}...")
    print()

# COMMAND ----------

# MAGIC %md ## 3. 技術系質問のデモ

# COMMAND ----------

# 技術系質問の例
technical_questions = [
    "メダリオンアーキテクチャのメリットは何ですか？",
    "Auto Loaderの使い方を教えてください",
    "Delta Lakeでタイムトラベルする方法は？",
    "Bronze層とSilver層の違いを説明してください"
]

print("🔧 技術系質問のベクトル検索結果:")
print("=" * 60)

for question in technical_questions:
    print(f"\n❓ 質問: {question}")
    results = search_knowledge_base(question, num_results=2)
    
    if results:
        print(f"📖 最も関連性の高い文書: {results[0]['title']}")
        print(f"📝 内容抜粋: {results[0]['content'][:150]}...")
    else:
        print("❌ 関連文書が見つかりませんでした")
    
    print("-" * 40)

# COMMAND ----------

# MAGIC %md ## 4. ビジネス系質問のデモ

# COMMAND ----------

# ビジネス系質問の例
business_questions = [
    "新宿店の特徴を教えてください",
    "Yukiteru Martの商品カテゴリは何がありますか？",
    "どんな商品を扱っていますか？",
    "店舗の営業時間は？"
]

print("🏪 ビジネス系質問のベクトル検索結果:")
print("=" * 60)

for question in business_questions:
    print(f"\n❓ 質問: {question}")
    results = search_knowledge_base(question, num_results=2)
    
    if results:
        print(f"📖 最も関連性の高い文書: {results[0]['title']}")
        print(f"📝 内容抜粋: {results[0]['content'][:150]}...")
    else:
        print("❌ 関連文書が見つかりませんでした")
    
    print("-" * 40)

# COMMAND ----------

# MAGIC %md ## 5. RAG応答生成のシミュレーション
# MAGIC
# MAGIC 実際のAgent Bricksの代わりに、検索結果を使った回答生成をシミュレートします。

# COMMAND ----------

def generate_rag_response(question, search_results):
    """検索結果を基にRAG風の回答を生成する関数（シミュレーション）"""
    
    if not search_results:
        return "申し訳ありません。関連する情報が見つかりませんでした。"
    
    # 最も関連性の高い文書を使用
    relevant_doc = search_results[0]
    
    # 簡単な回答生成（実際のRAGでは大規模言語モデルが使用される）
    response = f"""
【{relevant_doc['title']}】に基づいてお答えします。

{relevant_doc['content'].strip()}

この情報は{relevant_doc['category']}カテゴリの知識ベースから取得しました。
詳細な情報が必要でしたら、具体的な項目についてさらにお尋ねください。
"""
    
    return response

# デモ質問での回答生成
demo_questions = [
    "メダリオンアーキテクチャとは何ですか？",
    "新宿店について教えてください"
]

print("🤖 RAG応答生成デモ:")
print("=" * 60)

for question in demo_questions:
    print(f"\n❓ 質問: {question}")
    search_results = search_knowledge_base(question, num_results=1)
    response = generate_rag_response(question, search_results)
    
    print("🤖 AI回答:")
    print(response)
    print("-" * 40)

# COMMAND ----------

# MAGIC %md ## 6. インタラクティブ質問応答
# MAGIC
# MAGIC 以下のセルでは、自由に質問を変更してRAGシステムをテストできます。

# COMMAND ----------

# カスタム質問（ここを変更して様々な質問をテストしてください）
custom_question = "Delta Lakeの特徴について教えて"

print(f"❓ カスタム質問: {custom_question}")
print("=" * 60)

# ベクトル検索実行
search_results = search_knowledge_base(custom_question, num_results=3)

print("🔍 検索結果:")
for i, result in enumerate(search_results, 1):
    print(f"{i}. [{result['category']}] {result['title']}")
    print(f"   スコア: {result['score']}")
    print(f"   内容: {result['content'][:100]}...")
    print()

# RAG応答生成
response = generate_rag_response(custom_question, search_results)
print("🤖 AI回答:")
print(response)

# COMMAND ----------

# MAGIC %md ## 7. 知識ベース分析

# COMMAND ----------

# 知識ベースの統計情報
knowledge_stats = spark.table("knowledge_base_documents").groupBy("category").count().collect()

print("📊 知識ベース統計:")
print("=" * 30)
for row in knowledge_stats:
    print(f"{row['category']}: {row['count']}件")

print("\n📚 全文書リスト:")
docs_df = spark.table("knowledge_base_documents").select("doc_id", "title", "category")
display(docs_df)

# COMMAND ----------

# MAGIC %md ## 8. パフォーマンス測定

# COMMAND ----------

import time

def measure_search_performance(queries, num_trials=3):
    """検索パフォーマンスを測定する関数"""
    results = []
    
    for query in queries:
        times = []
        for trial in range(num_trials):
            start_time = time.time()
            search_knowledge_base(query, num_results=3)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        results.append({
            "query": query,
            "avg_response_time": avg_time,
            "trials": num_trials
        })
    
    return results

# パフォーマンステスト用クエリ
test_queries = [
    "メダリオンアーキテクチャ",
    "新宿店の情報",
    "商品カテゴリ"
]

print("⚡ パフォーマンス測定:")
print("=" * 40)

performance_results = measure_search_performance(test_queries)

for result in performance_results:
    print(f"クエリ: {result['query']}")
    print(f"平均応答時間: {result['avg_response_time']:.3f}秒")
    print("-" * 20)

# COMMAND ----------

# MAGIC %md ## 9. デモ総括

# COMMAND ----------

print("🎉 Agent Bricks RAG デモ完了!")
print("=" * 50)

print("\n✅ 実装した機能:")
print("  📚 知識ベース構築 (5文書)")
print("  🔍 ベクトル検索システム")
print("  🤖 RAG応答生成（シミュレーション）")
print("  📊 パフォーマンス測定")

print("\n🎯 デモで確認できたこと:")
print("  • 技術文書の検索・回答")
print("  • ビジネス情報の検索・回答") 
print("  • 自然言語での柔軟な質問対応")
print("  • 検索精度と応答時間")

print("\n🚀 次のステップ:")
print("  1. より多くの文書を知識ベースに追加")
print("  2. Agent Bricksの本格的な導入")
print("  3. 既存のDatabricksプロジェクトとの統合")
print("  4. ユーザーフィードバックによる改善")

print("\n💡 活用アイデア:")
print("  • 新入社員の研修支援")
print("  • 技術サポートの自動化")
print("  • ビジネス分析の効率化")
print("  • ドキュメント検索の高速化")

print("\n✨ Agent Bricks RAGシステムの構築が完了しました！")

# COMMAND ----------

# MAGIC %md ## 補足: 実際のAgent Bricks実装
# MAGIC
# MAGIC 実際の本番環境では、以下のように Agent Bricks を使用します：
# MAGIC
# MAGIC ```python
# MAGIC # Agent Bricks実装例
# MAGIC from databricks.agent import AgentClient
# MAGIC
# MAGIC agent_client = AgentClient()
# MAGIC
# MAGIC # エージェント作成
# MAGIC agent = agent_client.create_agent(
# MAGIC     name="yukiteru_mart_assistant",
# MAGIC     description="Yukiteru Mart & Databricks expert assistant",
# MAGIC     model="databricks-dbrx-instruct",
# MAGIC     vector_search_endpoint=VECTOR_SEARCH_ENDPOINT,
# MAGIC     vector_search_index=INDEX_NAME,
# MAGIC     system_prompt="Yukiteru MartとDatabricks技術の専門家として回答してください..."
# MAGIC )
# MAGIC
# MAGIC # 質問応答
# MAGIC response = agent.query("メダリオンアーキテクチャについて教えてください")
# MAGIC print(response)
# MAGIC ```
# MAGIC
# MAGIC このデモで作成した基盤を使って、実際のAgent Bricksを簡単に導入できます！ 