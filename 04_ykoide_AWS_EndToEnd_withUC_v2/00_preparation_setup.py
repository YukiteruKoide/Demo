# Databricks notebook source
# MAGIC %md 
# MAGIC
# MAGIC ##  環境条件
# MAGIC
# MAGIC Unity Catalogがセットアップされており、このノートブックを実行する管理者はカタログ作成権限を持っていること
# MAGIC
# MAGIC ##  セットアップ方法
# MAGIC 1. 以下のカタログ名を入力してください。
# MAGIC 1. 管理者はハンズオンやデモの前にこちらのノートブックを実行しておきます。

# COMMAND ----------

# デモで利用するカタログやスキーマ情報を定義します
catalog = 'handson'

# COMMAND ----------

spark.sql(f'CREATE CATALOG IF NOT EXISTS {catalog}')
spark.sql(f'GRANT CREATE, USAGE ON CATALOG {catalog} TO `account users`')
spark.sql(f'USE CATALOG {catalog}')

# COMMAND ----------

# DBTITLE 1,Schema作成
spark.sql('Create schema if not exists handson_db')
spark.sql('GRANT ALL PRIVILEGES ON SCHEMA handson_db TO `account users`')
spark.sql('USE SCHEMA handson_db')

# COMMAND ----------

# DBTITLE 1,Volume作成
spark.sql('CREATE VOLUME IF NOT EXISTS handson_volume;')
spark.sql('GRANT ALL PRIVILEGES ON VOLUME handson_volume TO `account users`')

# COMMAND ----------

# DBTITLE 1,Customer_info Tableの作成
df_info = spark.read.format('csv').option('inferSchema',True).option('header',True).load('wasbs://public-data@sajpstorage.blob.core.windows.net/customerInfo.csv')
df_info.write.mode('overwrite').saveAsTable('customer_info')

# COMMAND ----------

# DBTITLE 1,Customer_contract tableの作成
df_contract = spark.read.format('csv').option('inferSchema',True).option('header',True).load('wasbs://public-data@sajpstorage.blob.core.windows.net/training_data.csv')
df_contract.write.mode('overwrite').saveAsTable('customer_contract')

# COMMAND ----------

# DBTITLE 1,Customers_table の作成
customers_df = df_info.join(df_contract, on='customerID')
customers_df.write.mode("overwrite").saveAsTable("customers_table")

# COMMAND ----------

# MAGIC %md ## マニュアル upload するサンプルデータ
# MAGIC
# MAGIC こちらからダウンロード。（右クリックしてローカルに保存）<br>
# MAGIC https://sajpstorage.blob.core.windows.net/public-data/customer_contract.csv
