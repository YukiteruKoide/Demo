# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Bricks用データセットをVolumeに移動
# MAGIC 
# MAGIC このノートブックでは、Agent Bricksで使用するナレッジベース（Markdownファイル）を  
# MAGIC Unity Catalog Volumeに移動し、RAGシステムで利用できるように準備します。

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Unity Catalog Volume の作成

# COMMAND ----------

# Note: spark と dbutils は Databricks ランタイムで自動的に利用可能です

# カタログとスキーマの作成
catalog_name = "yukiteru_rag"
schema_name = "knowledge_base"
volume_name = "documents"

# カタログ作成（既に存在する場合はスキップ）
spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
print(f"カタログ '{catalog_name}' を作成しました")

# スキーマ作成
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}")
print(f"スキーマ '{catalog_name}.{schema_name}' を作成しました")

# Volume作成
spark.sql(f"""
CREATE VOLUME IF NOT EXISTS {catalog_name}.{schema_name}.{volume_name}
COMMENT 'Agent Bricks用ナレッジベースドキュメント格納Volume'
""")
print(f"Volume '{catalog_name}.{schema_name}.{volume_name}' を作成しました")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Workspaceファイルの確認

# COMMAND ----------

# Workspaceのナレッジベースファイル一覧を確認
workspace_path = "/Workspace/Repos/yukiteru.koide@databricks.com/Demo/06_RAG_AgentBricks_Demo/01_Knowledge_Base"

print("=== Workspace内のナレッジベースファイル ===")
try:
    files = dbutils.fs.ls(f"file:{workspace_path}")
    for file in files:
        print(f"📁 {file.path}")
        if file.isDir():
            sub_files = dbutils.fs.ls(file.path.replace("file:", "file:"))
            for sub_file in sub_files:
                if sub_file.name.endswith('.md'):
                    print(f"   📄 {sub_file.name} ({sub_file.size} bytes)")
except Exception as e:
    print(f"ファイル一覧取得エラー: {e}")
    print("手動でパスを確認します...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. ファイルをVolumeに移動

# COMMAND ----------

import os

# Volumeのパス
volume_path = f"/Volumes/{catalog_name}/{schema_name}/{volume_name}"

print(f"移動先Volume: {volume_path}")

# 各カテゴリのファイルを移動
categories = ["business_docs", "faq", "technical_docs"]

for category in categories:
    print(f"\n=== {category} カテゴリの処理 ===")
    
    # Volumeにディレクトリ作成
    category_volume_path = f"{volume_path}/{category}"
    dbutils.fs.mkdirs(category_volume_path)
    print(f"ディレクトリ作成: {category_volume_path}")
    
    # ワークスペースからファイルをコピー
    workspace_category_path = f"file:/Workspace/Repos/yukiteru.koide@databricks.com/Demo/06_RAG_AgentBricks_Demo/01_Knowledge_Base/{category}"
    
    try:
        # ディレクトリ内のMarkdownファイルを取得
        if category == "business_docs":
            files_to_copy = ["store_guide.md", "yukiteru_mart_product_catalog.md"]
        elif category == "faq":
            files_to_copy = ["databricks_yukiteru_mart_faq.md"]
        elif category == "technical_docs":
            files_to_copy = ["databricks_architecture_guide.md"]
        
        for file_name in files_to_copy:
            src_path = f"{workspace_category_path}/{file_name}"
            dst_path = f"{category_volume_path}/{file_name}"
            
            try:
                dbutils.fs.cp(src_path, dst_path)
                print(f"✅ コピー完了: {file_name}")
            except Exception as e:
                print(f"❌ コピー失敗: {file_name} - {e}")
                
    except Exception as e:
        print(f"❌ {category} の処理でエラー: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Volume内のファイル確認

# COMMAND ----------

print("=== Volume内のファイル一覧 ===")
try:
    volume_files = dbutils.fs.ls(volume_path)
    for item in volume_files:
        print(f"📁 {item.name}")
        if item.isDir():
            sub_items = dbutils.fs.ls(item.path)
            for sub_item in sub_items:
                if sub_item.name.endswith('.md'):
                    size_kb = sub_item.size / 1024
                    print(f"   📄 {sub_item.name} ({size_kb:.1f} KB)")
except Exception as e:
    print(f"Volume内容確認エラー: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. ファイル内容の確認（サンプル）

# COMMAND ----------

# サンプルファイルの内容を確認
sample_file = f"{volume_path}/business_docs/store_guide.md"

try:
    with open(sample_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=== store_guide.md の内容（最初の500文字） ===")
    print(content[:500] + "..." if len(content) > 500 else content)
    print(f"\n📊 ファイルサイズ: {len(content)} 文字")
    
except Exception as e:
    print(f"ファイル読み込みエラー: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. 次のステップ
# MAGIC 
# MAGIC ✅ **完了**: ナレッジベースファイルがVolumeに移動されました  
# MAGIC 
# MAGIC **次に実行すべき作業:**
# MAGIC 1. **簡易インジェスト**: Agent BricksのYAMLで直接Volumeパスを指定
# MAGIC 2. **カスタムパイプライン**: チャンク化→埋め込み→Deltaテーブル→Vector Index作成
# MAGIC 
# MAGIC **Volume パス:**
# MAGIC ```
# MAGIC /Volumes/yukiteru_rag/knowledge_base/documents/
# MAGIC ├── business_docs/
# MAGIC │   ├── store_guide.md
# MAGIC │   └── yukiteru_mart_product_catalog.md
# MAGIC ├── faq/
# MAGIC │   └── databricks_yukiteru_mart_faq.md
# MAGIC └── technical_docs/
# MAGIC     └── databricks_architecture_guide.md
# MAGIC ```

# COMMAND ----------

print("🎉 Volume移行完了！")
print(f"Volume パス: /Volumes/{catalog_name}/{schema_name}/{volume_name}")
print("Agent Bricks のレシピでこのパスを指定してください。") 