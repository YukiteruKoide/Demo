# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Bricks レシピ例
# MAGIC 
# MAGIC Unity Catalog Volume に移動した Markdown ファイルを使用して  
# MAGIC Agent Bricks の RAG エージェントを作成する例を示します。

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. 簡易インジェスト方式（推奨：検証・デモ用）

# COMMAND ----------

# Agent Bricks レシピ（YAML形式の例）
agent_recipe_yaml = """
agent:
  name: "Yukiteru Mart Assistant"
  description: "Yukiteru Mart の店舗運営、商品、技術に関する質問に回答するアシスタント"
  
  # システムプロンプト
  instructions: |
    あなたは Yukiteru Mart の専門アシスタントです。
    以下の観点で親切丁寧に回答してください：
    - 店舗運営に関する質問：店舗ガイドを参照
    - 商品に関する質問：商品カタログを参照  
    - 技術的な質問：アーキテクチャガイドを参照
    - よくある質問：FAQを参照
    
    回答は日本語で行い、情報源を明記してください。
    分からない場合は正直に「分かりません」と答えてください。

# データソース（簡易インジェスト）
datasets:
  - path: "/Volumes/yukiteru_rag/knowledge_base/documents/business_docs/*.md"
    description: "店舗ガイドと商品カタログ"
  - path: "/Volumes/yukiteru_rag/knowledge_base/documents/faq/*.md"  
    description: "よくある質問"
  - path: "/Volumes/yukiteru_rag/knowledge_base/documents/technical_docs/*.md"
    description: "技術ドキュメント"

# モデル設定
llm:
  model: "databricks-dbrx-instruct"  # または "databricks-meta-llama-3-1-405b-instruct"
  temperature: 0.1
  max_tokens: 2000

# 検索設定
retrieval:
  chunk_size: 400        # トークン数
  chunk_overlap: 50      # オーバーラップ
  top_k: 5              # 検索結果数
  similarity_threshold: 0.7
"""

print("=== Agent Bricks レシピ (YAML) ===")
print(agent_recipe_yaml)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Python API 方式

# COMMAND ----------

# Python での Agent 作成例
from databricks.agents import create_agent

# エージェント作成
agent = create_agent(
    name="yukiteru_mart_assistant",
    description="Yukiteru Mart の専門アシスタント",
    
    # システムプロンプト
    instructions="""
    あなたは Yukiteru Mart の専門アシスタントです。
    店舗運営、商品、技術に関する質問に正確に回答してください。
    回答は日本語で行い、情報源を明記してください。
    """,
    
    # データソース
    datasets=[
        {
            "path": "/Volumes/yukiteru_rag/knowledge_base/documents/business_docs/*.md",
            "description": "店舗ガイドと商品カタログ"
        },
        {
            "path": "/Volumes/yukiteru_rag/knowledge_base/documents/faq/*.md",
            "description": "よくある質問"
        },
        {
            "path": "/Volumes/yukiteru_rag/knowledge_base/documents/technical_docs/*.md",
            "description": "技術ドキュメント"
        }
    ],
    
    # モデル設定
    llm_config={
        "model": "databricks-dbrx-instruct",
        "temperature": 0.1,
        "max_tokens": 2000
    }
)

print("✅ Agent作成完了！")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. エージェントのテスト

# COMMAND ----------

# テスト質問
test_questions = [
    "Yukiteru Mart の営業時間は何時から何時までですか？",
    "商品の返品ポリシーについて教えてください",
    "Databricks の Unity Catalog とは何ですか？",
    "レジでエラーが発生した時の対処法は？"
]

print("=== エージェントテスト ===")
for i, question in enumerate(test_questions, 1):
    print(f"\n【質問 {i}】{question}")
    
    # エージェントに質問（実際の実行時）
    try:
        # response = agent.ask(question)
        # print(f"【回答】{response.answer}")
        # print(f"【情報源】{response.sources}")
        print("【回答】（実際の実行時にエージェントが回答します）")
    except Exception as e:
        print(f"エラー: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. カスタムパイプライン方式（本番運用向け）

# COMMAND ----------

# より高度な制御が必要な場合のパイプライン例
custom_pipeline_code = """
# 1. Delta テーブル作成
CREATE TABLE IF NOT EXISTS yukiteru_rag.knowledge_base.document_chunks (
  id STRING,
  text STRING,
  embedding ARRAY<FLOAT>,
  source STRING,
  category STRING,
  metadata MAP<STRING, STRING>
) USING DELTA
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

# 2. Vector Search Index 作成
CREATE VECTOR INDEX IF NOT EXISTS yukiteru_rag.knowledge_base.idx_document_chunks
ON TABLE yukiteru_rag.knowledge_base.document_chunks
TEXT COLUMN text
VECTOR COLUMN embedding
METADATA COLUMNS (source, category);

# 3. Agent レシピでインデックス指定
datasets:
  vector_index: "yukiteru_rag.knowledge_base.idx_document_chunks"
"""

print("=== カスタムパイプライン例 ===")
print(custom_pipeline_code)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. 次のステップ
# MAGIC 
# MAGIC ### ✅ 完了事項
# MAGIC - ナレッジベースファイルを Volume に移動
# MAGIC - Agent Bricks レシピの作成方法を確認
# MAGIC 
# MAGIC ### 🚀 次に実行すべき作業
# MAGIC 
# MAGIC **A. 簡易インジェスト（すぐに試したい場合）**
# MAGIC 1. Databricks Agent Builder UI を開く
# MAGIC 2. 上記の YAML レシピをコピー&ペースト
# MAGIC 3. エージェントをデプロイしてテスト
# MAGIC 
# MAGIC **B. カスタムパイプライン（本番運用の場合）**
# MAGIC 1. `03_Custom_RAG_Pipeline.py` ノートブックを実行
# MAGIC 2. チャンク化→埋め込み→Delta テーブル作成
# MAGIC 3. Vector Search Index 作成
# MAGIC 4. Agent レシピでインデックスを指定
# MAGIC 
# MAGIC **C. 検証・改善**
# MAGIC 1. 各種質問でエージェントをテスト
# MAGIC 2. チャンクサイズや検索パラメータを調整
# MAGIC 3. システムプロンプトを最適化

# COMMAND ----------

print("🎉 Agent Bricks レシピ準備完了！")
print("\n📁 利用可能なファイル:")
print("- /Volumes/yukiteru_rag/knowledge_base/documents/business_docs/")
print("- /Volumes/yukiteru_rag/knowledge_base/documents/faq/")  
print("- /Volumes/yukiteru_rag/knowledge_base/documents/technical_docs/")
print("\n🚀 Databricks Agent Builder で上記レシピを使用してエージェントを作成してください！") 