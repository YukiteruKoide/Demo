# Databricks notebook source
# MAGIC %md # Databricks環境の紹介、基本的な使い方

# COMMAND ----------

# MAGIC %md ##クラスターの作成＆アタッチ
# MAGIC <br>
# MAGIC
# MAGIC - 左のメニューの**クラスター** - **クラスターを作成** を選択
# MAGIC - クラスター名：　<お名前>_cluseter 
# MAGIC - クラスターモード：　シングルノード
# MAGIC - Databricks Runtime バージョン: ML -> 13.3 LTS
# MAGIC - Photonチェックボックスを外す (MLライブラリには対応していないため)
# MAGIC - ノートブックの左上のクラスターリストから、作成したクラスターをアタッチする。

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC
# MAGIC <table>
# MAGIC <tr>
# MAGIC 　　<td>
# MAGIC     
# MAGIC ##Databricks Notebook の概要
# MAGIC     
# MAGIC     特徴
# MAGIC - SQL/Python/R/Scala 言語をサポート
# MAGIC - Markdownや、HTML, Shell Command 等もサポート
# MAGIC - コラボレーション機能
# MAGIC - アクセス権限の付与
# MAGIC - 可視化機能 (display)
# MAGIC - ヒストリー機能
# MAGIC - スケジュール実行
# MAGIC - Git base コラボレーション (CI/CD)
# MAGIC - MLflow インテグレーション
# MAGIC   

# COMMAND ----------

# MAGIC %md ## 既存Deltaテーブルからの呼び出し
# MAGIC
# MAGIC 左のメニューの**カタログ**を開くと保存済みのデータが確認できます。<br>

# COMMAND ----------

# MAGIC %md
# MAGIC ## データの内容
# MAGIC |データ項目|説明|
# MAGIC |-|-|
# MAGIC |survived|生存フラグ|
# MAGIC |pclass|チケットクラス|
# MAGIC |sex|性別|
# MAGIC |age|年齢|
# MAGIC |sibsp|兄弟・配偶者の数|
# MAGIC |parch|親・子の数|
# MAGIC |fare|料金|
# MAGIC |embarked|出港地|
# MAGIC |class|チケットクラス|
# MAGIC |who|性別|
# MAGIC |adult_male|成人男性かどうか|
# MAGIC |deck|乗船していたデッキ|
# MAGIC |embark_town|出港地名|
# MAGIC |alive|生存|
# MAGIC |alone|一人か？|

# COMMAND ----------

# DBTITLE 1,既存データの呼び出し
# MAGIC %sql
# MAGIC -- schemaはご自身のお名前に変更して実行してください
# MAGIC SELECT * FROM users.yukiteru_koide.titanic
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## テーブルの作成

# COMMAND ----------

# DBTITLE 1,Survived Passengers Table
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS users.yukiteru_koide.passengers_alive
# MAGIC AS
# MAGIC SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS id, survived
# MAGIC FROM users.yukiteru_koide.titanic

# COMMAND ----------

# DBTITLE 1,create passenger details table
# MAGIC %sql
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

# MAGIC %md
# MAGIC ## テーブルの結合

# COMMAND ----------

# DBTITLE 1,Passenger Details Join
# MAGIC %sql
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
# MAGIC     users.yukiteru_koide.passengers_details AS d ON a.id = d.id;
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## NULLの除外

# COMMAND ----------

# DBTITLE 1,Feature Engineering
# MAGIC %sql
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

# COMMAND ----------

# MAGIC %md
# MAGIC ## テーブルの保存
# MAGIC

# COMMAND ----------

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

# COMMAND ----------

# MAGIC %md
# MAGIC # Pythonの操作

# COMMAND ----------

# MAGIC %md
# MAGIC ## ライブラリのインストール

# COMMAND ----------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns

# COMMAND ----------

# MAGIC %md
# MAGIC ## データのロード
# MAGIC

# COMMAND ----------

# SQLクエリを実行してpassengers_aliveテーブルを取得
spark_df_alive = spark.sql("SELECT * FROM users.yukiteru_koide.passengers_alive")
pandas_df_alive = spark_df_alive.toPandas()

# id列をインデックスに設定
pandas_df_alive.set_index('id', inplace=True)


# SQLクエリを実行してpassengers_detailsテーブルを取得
spark_df_detail = spark.sql("SELECT * FROM users.yukiteru_koide.passengers_details")
pandas_df_detail = spark_df_detail.toPandas()

# id列をインデックスに設定
pandas_df_detail.set_index('id', inplace=True)


# COMMAND ----------

# pandas_df_aliveの確認
# head()を用いることでTOP5を見ることができる
pandas_df_alive.head()

# COMMAND ----------

# pandas_df_detailの確認
pandas_df_detail.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ## データの結合

# COMMAND ----------

pandas_df = pandas_df_alive.join(pandas_df_detail)
pandas_df.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ## EDA
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### データの内容（再掲）
# MAGIC |データ項目|説明|
# MAGIC |-|-|
# MAGIC |survived|生存フラグ|
# MAGIC |pclass|チケットクラス|
# MAGIC |sex|性別|
# MAGIC |age|年齢|
# MAGIC |sibsp|兄弟・配偶者の数|
# MAGIC |parch|親・子の数|
# MAGIC |fare|料金|
# MAGIC |embarked|出港地|
# MAGIC |class|チケットクラス|
# MAGIC |who|性別|
# MAGIC |adult_male|成人男性かどうか|
# MAGIC |deck|乗船していたデッキ|
# MAGIC |embark_town|出港地名|
# MAGIC |alive|生存|
# MAGIC |alone|一人か？|

# COMMAND ----------

# MAGIC %md
# MAGIC ### データの内容確認

# COMMAND ----------

# TOP5の表示
pandas_df.head()

# COMMAND ----------

# DFのNULL値、型の確認
pandas_df.info()

# COMMAND ----------

# 基本統計量の確認
pandas_df.describe()

# COMMAND ----------

# 行数の確認
print(len(pandas_df))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Databricksおすすめの機能！display関数

# COMMAND ----------

display(pandas_df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### その他のPythonコード

# COMMAND ----------

# MAGIC %md
# MAGIC #### 分布の確認1

# COMMAND ----------

numeric_df = pandas_df.select_dtypes(include='number')
sns.pairplot(numeric_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### 分布の確認2

# COMMAND ----------

sns.pairplot(numeric_df, hue='survived')

# COMMAND ----------

# MAGIC %md
# MAGIC #### 相関関係

# COMMAND ----------

# 相関行列の計算
corr_matrix = numeric_df.corr()

# ヒートマップの描画
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Heatmap')
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 機械学習

# COMMAND ----------

# MAGIC %md
# MAGIC ### 前処理

# COMMAND ----------

# データの分割
df_survived = pandas_df[['survived']]
# pandas DataFrameから'survived'列と'alive'列を削除
df_feature = pandas_df.drop(['survived', 'alive'], axis=1)

# COMMAND ----------

# データの目視
display(df_survived)

# COMMAND ----------

# データの目視
display(df_feature)

# COMMAND ----------

# DFのNULL値、型の確認
df_feature.info()

# COMMAND ----------

# 数値データの欠損値補完（平均値で補完）
for column in df_feature.select_dtypes(include=['float', 'int']).columns:
    mean_value = df_feature[column].mean()
    df_feature[column].fillna(mean_value, inplace=True)

# COMMAND ----------

# データの目視
display(df_feature)

# COMMAND ----------

# 行数の確認
print(len(df_feature))

# COMMAND ----------

# オブジェクトデータの欠損値補完（最頻値で補完）
for column in df_feature.select_dtypes(include=['object']).columns:
    mode_value = df_feature[column].mode()[0]
    df_feature[column].fillna(mode_value, inplace=True)

# COMMAND ----------

display(df_feature)

# COMMAND ----------

# 行数の確認
print(len(df_feature))

# COMMAND ----------

# DFのNULL値、型の確認
df_feature.info()

# COMMAND ----------

# 参考
# 0で保管も追加する
# for column in pandas_df.select_dtypes(include=['float', 'int']).columns:
#     pandas_df[column].fillna(0, inplace=True)

# # 欠損値削除
# pandas_df = pandas_df.dropna()



# COMMAND ----------

# bool 型の列を int 型に変換
df_feature['adult_male'] = df_feature['adult_male'].astype(int)
df_feature['alone'] = df_feature['alone'].astype(int)

# エンコーディング
df_feature = pd.get_dummies(df_feature, drop_first=True)

# COMMAND ----------

display(df_feature)

# COMMAND ----------

# 目的変数、説明変数の作成
X = df_feature
y = df_survived['survived']

# COMMAND ----------

display(X)

# COMMAND ----------

display(y)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 前処理のテーブルを保存

# COMMAND ----------

# Convert pandas DataFrame to Spark DataFrame
spark_df_feature = spark.createDataFrame(df_feature)

# Save Spark DataFrame as Delta table
spark_df_feature.write.format("delta").saveAsTable("users.yukiteru_koide.feature_gold")

# COMMAND ----------

# MAGIC %md
# MAGIC ### モデル学習・推論

# COMMAND ----------

# Hold-out
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Logistic Regression model
model = LogisticRegression()

# Train the model
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# COMMAND ----------

# MAGIC %md
# MAGIC ### モデルの評価

# COMMAND ----------

# Evaluate
print(accuracy_score(y_test, y_pred))
print(f1_score(y_test, y_pred))

# COMMAND ----------

# MAGIC %md
# MAGIC # 参考：Pysparkの操作

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sparkデータフレームの分割

# COMMAND ----------

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# データの読み込み（pandasからSpark DataFrameへ）
pandas_df = sns.load_dataset('titanic')
spark_df = spark.createDataFrame(pandas_df)

# カテゴリカル変数の処理
categoricalColumns = ['sex', 'embarked', 'class', 'deck']
stages = []  # ステージを保存するリスト

for categoricalCol in categoricalColumns:
    # カテゴリのインデックス作成
    stringIndexer = StringIndexer(inputCol=categoricalCol, outputCol=categoricalCol + 'Index')
    # ワンホットエンコーダー
    encoder = OneHotEncoder(inputCols=[stringIndexer.getOutputCol()], outputCols=[categoricalCol + "classVec"])
    stages += [stringIndexer, encoder]

# 数値変数の選択
numericCols = ['age', 'fare', 'parch', 'sibsp']
assemblerInputs = [c + "classVec" for c in categoricalColumns] + numericCols

# VectorAssemblerを使用して特徴量を一つのベクトルに統合
assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="features")
stages += [assembler]

# ロジスティック回帰モデルの設定
lr = LogisticRegression(featuresCol='features', labelCol='survived', maxIter=10)
stages += [lr]

# パイプラインの構築
pipeline = Pipeline(stages=stages)

# データの欠損値を削除
spark_df = spark_df.dropna(subset=["age", "sex", "embarked", "fare", "class", "deck"])

# データを訓練用とテスト用に分割
train, test = spark_df.randomSplit([0.7, 0.3], seed=2018)

# モデルの訓練
model = pipeline.fit(train)

# テストデータに対する予測
predictions = model.transform(test)

# 評価（AUCスコア）
evaluator = BinaryClassificationEvaluator(labelCol="survived", rawPredictionCol="rawPrediction")
auc = evaluator.evaluate(predictions)
print("Test AUC = %g" % auc)


# COMMAND ----------


