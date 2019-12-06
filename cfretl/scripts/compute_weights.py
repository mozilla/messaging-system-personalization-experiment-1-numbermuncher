#!/usr/bin/python

from pyspark.sql import SparkSession
from sklearn import metrics

# Import numerical computation libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, CategoricalNB
from sklearn.preprocessing import OrdinalEncoder
import numpy as np
import pandas as pd  # noqa


def check_sklearn_dev():
    '''
    This just verifies that sklearn 0.23-dev is installed properly
    by checking CategoricalNB results
    '''
    rng = np.random.RandomState(1)
    X = rng.randint(5, size=(6, 100))
    y = np.array([1, 2, 3, 4, 5, 6])

    clf = CategoricalNB()
    clf.fit(X, y)
    assert [3] == clf.predict(X[2:3])

def spark_query_bq():
    spark = (
        SparkSession.builder.master("yarn").appName("spark-bigquery-demo").getOrCreate()
    )

    # Use the Cloud Storage bucket for temporary BigQuery export data used
    # by the connector. This assumes the Cloud Storage connector for
    # Hadoop is configured.
    bucket = spark.sparkContext._jsc.hadoopConfiguration().get("fs.gs.system.bucket")
    spark.conf.set("temporaryGcsBucket", bucket)

    str_ts = "2019-11-24 00:00:00.000000 UTC"
    end_ts = "2019-11-25 00:00:00.000000 UTC"

    # Load data from BigQuery.
    df = (
        spark.read.format("bigquery")
        .option("table", "moz-fx-data-shar-nonprod-efed:messaging_system_live.cfr_v1")
        .option("filter", "submission_timestamp >= '{str_ts:s}'".format(str_ts=str_ts))
        .option("filter", "submission_timestamp >= '{end_ts:s}'".format(end_ts=end_ts))
        .load()
    )

    df.createOrReplaceTempView("cfr_v1")

    sql_template = """select * from cfr_v1"""

    # Demonstrate we can hook a pyspark dataframe here
    sql = sql_template.format(str_ts=str_ts, end_ts=end_ts)
    row_df = spark.sql(sql)

    print("Fetched {:d} rows from bq via spark".format(row_df.count()))

    # Create a bunch of dummy CFR_IDs with weights
    row_df = spark.createDataFrame(
        [("CFR_1", 1), ("CFR_2", 5), ("CFR_3", 9), ("CFR_4", 21), ("CFR_5", 551)]
    )
    return row_df


check_sklearn_dev()
row_df = spark_query_bq()
# Stuff the results into a versioned table
row_df.write.format("bigquery").mode("overwrite").option(
    "table", "cfr_etl.cfr_weights_v010"
).save()
