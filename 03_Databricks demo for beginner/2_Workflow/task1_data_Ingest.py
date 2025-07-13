# Databricks notebook source
# DBTITLE 1,Passenger Survival Data
# MAGIC %sql
# MAGIC
# MAGIC -- 下記パスをご自身のに修正してください
# MAGIC CREATE TABLE IF NOT EXISTS users.yukiteru_koide.passengers_alive
# MAGIC AS
# MAGIC SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS id, survived
# MAGIC FROM users.yukiteru_koide.titanic

# COMMAND ----------

# DBTITLE 1,Passenger Details From Titanic
# MAGIC %sql
# MAGIC
# MAGIC -- 下記パスをご自身のに修正してください
# MAGIC CREATE TABLE IF NOT EXISTS users.yukiteru_koide.passengers_details AS
# MAGIC SELECT 
# MAGIC     ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS id,
# MAGIC     pclass,
# MAGIC     sex,
# MAGIC     age,
# MAGIC     sibsp,
# MAGIC     parch,
# MAGIC     fare,
# MAGIC     embarked,
# MAGIC     class,
# MAGIC     who,
# MAGIC     adult_male,
# MAGIC     deck,
# MAGIC     embark_town,
# MAGIC     alive,
# MAGIC     alone
# MAGIC FROM users.yukiteru_koide.titanic
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------


