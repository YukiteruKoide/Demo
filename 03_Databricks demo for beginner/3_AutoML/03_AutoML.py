# Databricks notebook source
# MAGIC %md # AutoMLによるモデル作成
# MAGIC
# MAGIC このノートブックでは、01で作ったFeature Store上のデータを使ってベストなモデルを作成します。
# MAGIC

# COMMAND ----------

# MAGIC %md-sandbox ### DatabricksのAuto MLとChurnデータセットの使用
# MAGIC
# MAGIC Auto MLは、「Machine Learning(機械学習)」メニュースペースで利用できます。<br>
# MAGIC (Machine Learning メニューを選択し、ホーム画面で AutoMLを選択してください)
# MAGIC
# MAGIC 新規にAuto-ML実験を開始し、先ほど作成した特徴量テーブル(`churn_features`)を選択するだけで良いのです。
# MAGIC
# MAGIC ML Problem typeは、今回は`classification`です。
# MAGIC 予測対象は`churn`カラムです。
# MAGIC
# MAGIC AutoMLのMetricや実行時間とトライアル回数については、Advance Menuで選択できます。
# MAGIC
# MAGIC Demo時には時間短縮のため、5分にセットしてください。
# MAGIC
# MAGIC Startをクリックすると、あとはDatabricksがやってくれます。
# MAGIC
# MAGIC この作業はUIで行いますが[python API](https://docs.databricks.com/applications/machine-learning/automl.html#automl-python-api-1)による操作も可能です。

# COMMAND ----------

# MAGIC %md ## 実験の経過や結果については、MLflow のExperiment画面で確認可能です。
# MAGIC
# MAGIC

# COMMAND ----------


