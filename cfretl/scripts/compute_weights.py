"""### Set a project
We need to provide a GCP project to BigQuery connector, it will be used to execute your queries. Set `project_id` below to the project provided to you during your access request e.g. `moz-fx-data-bq-<team-name>`
"""


from google.cloud import bigquery
from pyspark.sql.functions import col, udf, when
from pyspark.sql.types import BooleanType
from sklearn.metrics import classification_report, precision_recall_fscore_support
from IPython.display import display
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, CategoricalNB
from sklearn.preprocessing import OrdinalEncoder
from sklearn_porter import Porter
from sklearn.utils.fixes import logsumexp
import numpy as np
import json
import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt


# TODO: this might need to be imported as an enviroment variable?
project_id = "cfr-personalization-experiment"

"""
consider block, dismiss, manage, only impressions as a failure to convert
Everything else considered "success"
Potentially update in future experiments
"""

# Obtain a spark session
spark = SparkSession.builder.master("yarn").appName("spark-bigquery-demo").getOrCreate()


def get_success_bool(lst):
    if "CLICK_DOORHANGER" in lst:
        return True
    elif "RATIONALE" in lst:
        return True
    elif "ENABLE" in lst:
        return True
    elif "INSTALL" in lst:
        return True
    elif "CLICK" in lst:
        return True
    elif "PIN" in lst:
        return True
    elif "LEARN_MORE" in lst:
        return True

    return False


get_success_bool_udf = udf(lambda lst: get_success_bool(lst), BooleanType())


client = bigquery.Client(project=project_id)

cfr_ext = client.query(
    """
select * from `moz-fx-data-shar-nonprod-efed`.analysis.cfr_extended
where places_bookmarks_count_mean is not null
"""
).to_dataframe()


df_cfr_ext = spark.createDataFrame(cfr_ext)  # convert to spark df
df_cfr_ext = df_cfr_ext.drop("fxa_configured")  # this field contains garbage

df_cfr_ext.take(10)


successes = (
    df_cfr_ext.groupBy("client_id", "message_id")
    .agg(F.collect_list("event").alias("event_list"))
    .withColumn("success", get_success_bool_udf(col("event_list")))
    .select("client_id", "success")
)
df = successes.join(df_cfr_ext, "client_id").drop("event").drop_duplicates()

counts = df.groupBy("message_id").count().select("message_id", col("count").alias("n"))
acceptance = (
    df.where(col("success") == True).groupBy("message_id").count()
)  # noqa: E712
acceptance_rates = (
    counts.join(acceptance, "message_id", how="full")
    .fillna(0)
    .withColumn("acceptance_rate", col("count") / col("n"))
    .select("message_id", "acceptance_rate", "n")
    .orderBy(col("acceptance_rate"))
)

df_cfr_ext.select("client_id").distinct().count()


def display_spark_df(df_spark):
    # display(HTML(df_spark.toPandas().to_html())) #WTF. There must be a better way
    # There is, Colab outputs HTML by default for Pandas: acceptance_rates.toPandas(), and we can tweak the output through options:
    with pd.option_context(
        "display.max_rows",
        None,
        "display.max_columns",
        None,
        "display.max_colwidth",
        -1,
    ):  # more options can be specified also
        display(df_spark.toPandas())


display_spark_df(acceptance_rates)
# .where(col("n") > 2)


fig, ax = plt.subplots(3, 1, figsize=(5, 10))

df.where(col("active_hours_sum") < 100).toPandas().hist(
    ax=ax[0], column="active_hours_sum", bins=30, log=True
)

df.where(col("active_addons_count_mean") < 100).toPandas().hist(
    ax=ax[1], column="active_addons_count_mean", bins=30, log=True
)

df.where(col("places_bookmarks_count_mean") < 1000).toPandas().hist(
    ax=ax[2], column="places_bookmarks_count_mean", bins=30, log=True
)

plt.tight_layout()
ax[0].set_yscale("log")
ax[1].set_yscale("log")
ax[2].set_yscale("log")


# 5 is std number of addons installed (and bobokmarks by default?). for hours, 5 coincidentally works as heuristic
df = (
    df.withColumn(
        "installed_addons",
        when(col("active_addons_count_mean") > 5, True).otherwise(False),
    )
    .withColumn("is_active", when(col("active_hours_sum") > 5, True).otherwise(False))
    .withColumn(
        "has_bookmarks",
        when(col("places_bookmarks_count_mean") > 5, True).otherwise(False),
    )
)


bnb = BernoulliNB(
    fit_prior=True, binarize=None
)  # @ilana: I added binarize=None here to make sure there is less magic /motin


def export_model_data(classifier):
    porter = Porter(classifier, language="java")
    porter.export(export_data=True)
    with open("data.json", "r") as f:
        model = json.load(f)
    return model


features = [
    "message_id",
    "is_default_browser",
    "installed_addons",
    "is_active",
    "has_bookmarks",
]
df_p = df[features + ["success"]].toPandas()
df_p


cnb = CategoricalNB(fit_prior=True)


enc = OrdinalEncoder()

enc.fit(df_p)
df_trans = enc.transform(df_p)
df_trans


saved_cols = df_p.columns
df_trans = pd.DataFrame(df_trans, columns=saved_cols)


df_trans

df_train, df_test = train_test_split(df_trans, test_size=0.5, random_state=1)

enc.categories_


cnb.fit(df_train[features], df_train["success"])


pred_cat = cnb.predict(df_test[features])


print(
    "Number of mislabeled points out of a total {} points : {}, performance {:05.2f}%".format(
        df_test.shape[0],
        (df_test["success"] != pred_cat).sum(),
        100 * (1 - (df_test["success"] != pred_cat).sum() / df_test.shape[0]),
    )
)

unique, counts = np.unique(pred_cat, return_counts=True)
print("classification counts: ", dict(zip(unique, counts)))

print("dataset class count: ", cnb.class_count_)
print("log prob of features | class: ", cnb.feature_log_prob_)


y_true = df_test["success"]
y_pred = pred_cat
target_names = ["Rejected CFR", "Accepted CFR"]
print(classification_report(y_true, y_pred, target_names=target_names))


features = [
    "message_id",
    "is_default_browser",
    "installed_addons",
    "is_active",
    "has_bookmarks",
]
df_p = df[features + ["success"]].toPandas()

df_encoded = pd.get_dummies(df_p)
features_encoded = list(df_encoded.drop("success", axis=1))


df_encoded


features_encoded


bnb = BernoulliNB(
    fit_prior=True, binarize=None
)  # @ilana: I added binarize=None here to make sure there is less magic /motin

df_train, df_test = train_test_split(df_encoded, test_size=0.5, random_state=1)

bnb.fit(df_train[features_encoded], df_train["success"])
pred_bern = bnb.predict(df_test[features_encoded])


print(
    "Number of mislabeled points out of a total {} points : {}, performance {:05.2f}%".format(
        df_test.shape[0],
        (df_test["success"] != pred_bern).sum(),
        100 * (1 - (df_test["success"] != pred_bern).sum() / df_test.shape[0]),
    )
)

unique, counts = np.unique(pred_bern, return_counts=True)
print("classification counts: ", dict(zip(unique, counts)))

print("dataset class count: ", bnb.class_count_)
print("log prob of features | class: ", bnb.feature_log_prob_)


y_true = df_test["success"]
y_pred = pred_bern
target_names = ["Rejected CFR", "Accepted CFR"]
print(classification_report(y_true, y_pred, target_names=target_names))


precision, recall, fscore, support = precision_recall_fscore_support(
    y_true, y_pred, average=None, labels=[False, True]
)
precision, recall, fscore, support


model = export_model_data(bnb)
print(model)


df_test[features_encoded]


# jll is what is available in JS (from the sklearn-porter
# implementation), anything else had to be ported to JS
jll = bnb._joint_log_likelihood(df_test[features_encoded])
display(jll)


jll_exp = np.exp(jll.astype(float))
jll_exp


jll_exp.describe()


# very simple mapping-function
jll_exp_diff_times_5k_plus_5k = (jll_exp[1] - jll_exp[0]) * 5000 + 5000
jll_exp_diff_times_5k_plus_5k.astype(int)


display(bnb.predict_log_proba(df_test[features_encoded]))


# normalize by P(x) = P(f_1, ..., f_n)
print(jll.astype(float))
log_prob_x = logsumexp(jll.astype(float), axis=1)
print(log_prob_x)
normalizing_constants = np.atleast_2d(log_prob_x).T
print(normalizing_constants.shape)
normalizing_constants
normalized_jll = jll - normalizing_constants
normalized_jll


np.exp(normalized_jll.astype(float))


display(bnb.predict_proba(df_test[features_encoded]))


unique_message_ids = np.unique(df_p[["message_id"]])

training_results = []

for message_id in unique_message_ids:
    print(message_id)
    message_specific_df_p = df_p[df_p["message_id"] == message_id].drop(
        "message_id", axis=1
    )
    print(len(message_specific_df_p))
    if len(message_specific_df_p) < 100:
        print("Skipping model training since there are less than 100 samples")
        continue
    message_specific_df_encoded = pd.get_dummies(message_specific_df_p)
    message_specific_features_encoded = list(
        message_specific_df_encoded.drop("success", axis=1)
    )
    message_specific_bnb = BernoulliNB(fit_prior=True, binarize=None)
    message_specific_df_train, message_specific_df_test = train_test_split(
        message_specific_df_encoded, test_size=0.5, random_state=1
    )
    message_specific_bnb.fit(
        message_specific_df_train[message_specific_features_encoded],
        message_specific_df_train["success"],
    )
    message_specific_pred_bern = message_specific_bnb.predict(
        message_specific_df_test[message_specific_features_encoded]
    )
    y_true = message_specific_df_test["success"]
    y_pred = message_specific_pred_bern
    target_names = ["Rejected CFR", "Accepted CFR"]
    report = classification_report(y_true, y_pred, target_names=target_names)
    # print(report)
    precision, recall, fscore, support = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=[False, True]
    )
    precision, recall, fscore, support
    training_result = {
        "message_id": message_id,
        "accepted_cfr_precision": precision[1],
        "accepted_cfr_recall": recall[1],
        "accepted_cfr_fscore": fscore[1],
        "accepted_cfr_support": support[1],
        "rejected_cfr_precision": precision[0],
        "rejected_cfr_recall": recall[0],
        "rejected_cfr_fscore": fscore[0],
        "rejected_cfr_support": support[0],
        "classifier": message_specific_bnb,
    }
    training_results.append(training_result)


training_results_df = pd.DataFrame(training_results)
with pd.option_context(
    "display.max_rows", None, "display.max_columns", None, "display.max_colwidth", -1
):
    display(training_results_df.drop(["classifier"], axis=1))


def export_models_by_cfr_id(training_results):
    models_by_cfr_id = {}
    for training_result in training_results:
        message_id = training_result["message_id"]
        # print(message_id)
        bnb = training_result["classifier"]
        model = export_model_data(bnb)
        # print(model)
        models_by_cfr_id[message_id] = model
        # print("")
    return (
        models_by_cfr_id
    )  # vng: i outdented this one level as the loop was terminating early


models_by_cfr_id = export_models_by_cfr_id(training_results)
print(json.dumps(models_by_cfr_id, indent=2))
