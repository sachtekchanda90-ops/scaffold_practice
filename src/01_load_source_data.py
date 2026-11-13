# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Load source data (setup)
# MAGIC Loads ShopNest's order feed, customer table and Finance's payout file, and generates a clickstream sample.
# MAGIC In production, orders land from the storefront every 15 minutes (`orders_raw`, one row per order *version*:
# MAGIC refunds and price fixes arrive as a new row with a later `updated_at`).

# COMMAND ----------

import os
import pandas as pd
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "shopnest")
dbutils.widgets.text("bundle_root", "")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
ROOT = dbutils.widgets.get("bundle_root") or os.path.abspath(os.path.join(os.getcwd(), ".."))
SRC = os.path.join(ROOT, "data", "source")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
T = lambda name: f"{CATALOG}.{SCHEMA}.{name}"


def load(name):
    return spark.createDataFrame(pd.read_csv(os.path.join(SRC, name), dtype=str, keep_default_na=False))

# COMMAND ----------

(load("orders_raw.csv")
    .withColumn("order_ts", F.to_timestamp("order_ts"))
    .withColumn("updated_at", F.to_timestamp("updated_at"))
    .withColumn("amount", F.col("amount").cast("decimal(12,2)"))
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(T("orders_raw")))

(load("customers.csv").withColumn("signup_date", F.to_date("signup_date"))
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(T("customers")))

(load("finance_payouts.csv")
    .withColumn("payout_date", F.to_date("payout_date"))
    .withColumn("payout_amount", F.col("payout_amount").cast("decimal(14,2)"))
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(T("finance_payouts")))

# COMMAND ----------

# Clickstream sample: 400k events across 20k customers, Aug 1 - Nov 12
events = (spark.range(400000)
    .withColumn("customer_id", F.format_string("C%06d", (F.abs(F.hash("id")) % 20000) + 1))
    .withColumn("event_ts", F.from_unixtime(F.lit(1785542400) + (F.abs(F.hash(F.col("id") * 7)) % (104 * 86400))).cast("timestamp"))
    .withColumn("page", F.element_at(F.array(*[F.lit(p) for p in ["home", "search", "product", "cart", "checkout", "confirm"]]),
                                     (F.abs(F.hash(F.col("id") * 13)) % 6 + 1).cast("int")))
    .withColumn("device", F.when(F.abs(F.hash(F.col("id") * 3)) % 10 < 6, "mobile").otherwise("desktop"))
    .drop("id"))
events.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(T("clickstream_events"))

for t in ["orders_raw", "customers", "finance_payouts", "clickstream_events"]:
    print(t, spark.table(T(t)).count())
