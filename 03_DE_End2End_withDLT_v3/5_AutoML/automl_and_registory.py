# Databricks notebook source
# MAGIC %run ../0_userenv

# COMMAND ----------

from databricks import automl

customers_df = spark.table(f"{catalog}.{user}.customers_table")

summary = (automl.classify(customers_df,         # データセット
                           target_col="churn",   # 予測するカラム
                           timeout_minutes=5,    # 学習時間。120分くらいが理想だが、ハンズオンのため最小の５分
                           primary_metric="f1",  # 評価メトリック
                           exclude_cols=['Name','AccountCreation','email','Age']  # 学習対象から外すカラム
                          )
          )

help(summary)

# COMMAND ----------

# DBTITLE 1,best model のロード
from mlflow import MlflowClient
import mlflow

client = MlflowClient()

# get best model uri
model_uri = summary.best_trial.model_path

print(model_uri)

# COMMAND ----------

# DBTITLE 1,Unity Catalogにモデルの保存
# Unity Catalogにモデルを登録する場合
mlflow.set_registry_uri("databricks-uc")

# register model to unity catalog
mlflow.register_model(model_uri, f"{catalog}.{user}.churn_model")

# COMMAND ----------


