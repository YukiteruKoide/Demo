# Databricks notebook source
# MAGIC %run ../0_userenv

# COMMAND ----------

import pandas as pd
import mlflow

# Unity Catalogにモデルを登録する場合
mlflow.set_registry_uri("databricks-uc")

# mlflowからモデルを取得
model_name =f"{catalog}.{user}.churn_model"
churn_model = mlflow.pyfunc.load_model(f"models:/{model_name}/1")

# 以下のようにエイリアス指定でも可能です
#churn_model = mlflow.pyfunc.load_model(f"models:/{model_name}@prod")

# 予測データ読み込み。　今回はPandasを利用しております。Spark DataFrameも可能です。
#　　注意：本来は訓練データではなく、別のデータを使用すべきですが、今回はMLFlowの使い方を見るためシンプルにしております。
customers_df = spark.read.table(f"{catalog}.{user}.customers_table").toPandas()

# 解約予測
predict = churn_model.predict(customers_df)
print(predict)

# 元のデータに結合
predict_df = pd.DataFrame(predict, columns=["predict"])
result = pd.concat([customers_df,predict_df],axis=1)

display(result)

# COMMAND ----------

# DBTITLE 1,Delta Tableに保存
result_df = spark.createDataFrame(result)
result_df.write.mode("overwrite").saveAsTable("final_table")
