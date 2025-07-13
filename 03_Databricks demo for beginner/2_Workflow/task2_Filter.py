# Databricks notebook source
# DBTITLE 1,Create SilverTable from Passengers Data
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS users.yukiteru_koide.SilverTable AS
# MAGIC SELECT
# MAGIC     a.id,
# MAGIC     a.survived,
# MAGIC     d.pclass,
# MAGIC     d.sex,
# MAGIC     d.age,
# MAGIC     d.sibsp,
# MAGIC     d.parch,
# MAGIC     d.fare,
# MAGIC     d.embarked,
# MAGIC     d.class,
# MAGIC     d.who,
# MAGIC     d.adult_male,
# MAGIC     d.deck,
# MAGIC     d.embark_town,
# MAGIC     d.alive,
# MAGIC     d.alone
# MAGIC FROM
# MAGIC     users.yukiteru_koide.passengers_alive AS a
# MAGIC JOIN
# MAGIC     users.yukiteru_koide.passengers_details AS d ON a.id = d.id
# MAGIC WHERE
# MAGIC     d.age IS NOT NULL AND
# MAGIC     d.embarked IS NOT NULL AND
# MAGIC     d.deck IS NOT NULL AND
# MAGIC     d.embark_town IS NOT NULL;
# MAGIC
# MAGIC
