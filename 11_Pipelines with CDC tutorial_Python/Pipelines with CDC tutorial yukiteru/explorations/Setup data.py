# Databricks notebook source
# MAGIC %md
# MAGIC ### サンプル探索ノートブック
# MAGIC
# MAGIC このノートブックを使用して、パイプラインで生成されたデータをお好みのプログラミング言語で探索できます。
# MAGIC
# MAGIC **注意**: このノートブックはパイプラインの一部として実行されません。

# COMMAND ----------

# MAGIC %pip install faker
# MAGIC # パイプラインのステップ1で使用したカタログとスキーマに合わせて更新してください
# MAGIC catalog = "users"
# MAGIC schema = dbName = db = "yukiteru_koide"
# MAGIC
# MAGIC spark.sql(f'USE CATALOG `{catalog}`')
# MAGIC spark.sql(f'USE SCHEMA `{schema}`')
# MAGIC spark.sql(f'CREATE VOLUME IF NOT EXISTS `{catalog}`.`{db}`.`raw_data`')
# MAGIC volume_folder =  f"/Volumes/{catalog}/{db}/raw_data"
# MAGIC
# MAGIC try:
# MAGIC   dbutils.fs.ls(volume_folder+"/customers")
# MAGIC except:
# MAGIC   print(f"フォルダが存在しないため、{volume_folder} にデータを生成します...")
# MAGIC   from pyspark.sql import functions as F
# MAGIC   from faker import Faker
# MAGIC   from collections import OrderedDict
# MAGIC   import uuid
# MAGIC   fake = Faker()
# MAGIC   import random
# MAGIC
# MAGIC   # ダミーデータ生成用UDF
# MAGIC   fake_firstname = F.udf(fake.first_name)
# MAGIC   fake_lastname = F.udf(fake.last_name)
# MAGIC   fake_email = F.udf(fake.ascii_company_email)
# MAGIC   fake_date = F.udf(lambda:fake.date_time_this_month().strftime("%m-%d-%Y %H:%M:%S"))
# MAGIC   fake_address = F.udf(fake.address)
# MAGIC   operations = OrderedDict([("APPEND", 0.5),("DELETE", 0.1),("UPDATE", 0.3),(None, 0.01)])
# MAGIC   fake_operation = F.udf(lambda:fake.random_elements(elements=operations, length=1)[0])
# MAGIC   fake_id = F.udf(lambda: str(uuid.uuid4()) if random.uniform(0, 1) < 0.98 else None)
# MAGIC
# MAGIC   # 10万件のダミーデータを生成
# MAGIC   df = spark.range(0, 100000).repartition(100)
# MAGIC   df = df.withColumn("id", fake_id())
# MAGIC   df = df.withColumn("firstname", fake_firstname())
# MAGIC   df = df.withColumn("lastname", fake_lastname())
# MAGIC   df = df.withColumn("email", fake_email())
# MAGIC   df = df.withColumn("address", fake_address())
# MAGIC   df = df.withColumn("operation", fake_operation())
# MAGIC   df_customers = df.withColumn("operation_date", fake_date())
# MAGIC   # JSON形式で保存
# MAGIC   df_customers.repartition(100).write.format("json").mode("overwrite").save(volume_folder+"/customers")
# MAGIC
