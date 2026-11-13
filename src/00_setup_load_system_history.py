# Databricks notebook source
# MAGIC %md
# MAGIC # 00 · Load system-table history (setup)
# MAGIC Free Edition workspaces are new, so their real `system.*` tables have little history.
# MAGIC This notebook loads **104 days (Aug 1 – Nov 12, 2026) of ShopNest's production telemetry**
# MAGIC into `<catalog>.sim_system`, using the same table and column names as the real system tables:
# MAGIC
# MAGIC | sim table | mirrors |
# MAGIC |---|---|
# MAGIC | `billing_usage` | `system.billing.usage` |
# MAGIC | `list_prices` | `system.billing.list_prices` |
# MAGIC | `jobs` | `system.lakeflow.jobs` |
# MAGIC | `job_run_timeline` | `system.lakeflow.job_run_timeline` |
# MAGIC | `clusters` | `system.compute.clusters` |
# MAGIC | `warehouses` | `system.compute.warehouses` |
# MAGIC | `query_history` | `system.query.history` (warehouse_id flattened) |
# MAGIC | `access_audit` | `system.access.audit` |

# COMMAND ----------

import os
import pandas as pd
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("sim_schema", "sim_system")
dbutils.widgets.text("bundle_root", "")
CATALOG = dbutils.widgets.get("catalog")
SIM = dbutils.widgets.get("sim_schema")
ROOT = dbutils.widgets.get("bundle_root") or os.path.abspath(os.path.join(os.getcwd(), ".."))
DATA = os.path.join(ROOT, "data", "system_history")
print("Reading CSVs from", DATA)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SIM}")


def load(name):
    pdf = pd.read_csv(os.path.join(DATA, name), dtype=str, keep_default_na=False)
    return spark.createDataFrame(pdf)


def save(df, table):
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table)
    print(f"{table}: {spark.table(table).count():,} rows")


def ts_or_null(c):
    return F.to_timestamp(F.when(F.col(c) != "", F.col(c)))

# COMMAND ----------

USAGE_META = "struct<cluster_id:string,job_id:string,job_run_id:string,warehouse_id:string>"
usage = (load("billing_usage.csv")
    .withColumn("usage_start_time", F.to_timestamp("usage_start_time"))
    .withColumn("usage_end_time", F.to_timestamp("usage_end_time"))
    .withColumn("usage_date", F.to_date("usage_date"))
    .withColumn("usage_quantity", F.col("usage_quantity").cast("decimal(38,18)"))
    .withColumn("custom_tags", F.from_json("custom_tags", "map<string,string>"))
    .withColumn("usage_metadata", F.from_json("usage_metadata", USAGE_META))
    .withColumn("identity_metadata", F.from_json("identity_metadata", "struct<run_as:string>"))
    .withColumn("product_features", F.from_json("product_features", "struct<is_serverless:boolean>")))
save(usage, f"{CATALOG}.{SIM}.billing_usage")

prices = (load("list_prices.csv")
    .withColumn("price_start_time", F.to_timestamp("price_start_time"))
    .withColumn("price_end_time", ts_or_null("price_end_time"))
    .withColumn("pricing", F.from_json("pricing", "struct<default:decimal(30,18)>")))
save(prices, f"{CATALOG}.{SIM}.list_prices")

jobs = (load("jobs.csv")
    .withColumn("tags", F.from_json("tags", "map<string,string>"))
    .withColumn("change_time", F.to_timestamp("change_time"))
    .withColumn("delete_time", ts_or_null("delete_time")))
save(jobs, f"{CATALOG}.{SIM}.jobs")

timeline = (load("job_run_timeline.csv")
    .withColumn("period_start_time", F.to_timestamp("period_start_time"))
    .withColumn("period_end_time", F.to_timestamp("period_end_time"))
    .withColumn("compute_ids", F.from_json("compute_ids", "array<string>")))
save(timeline, f"{CATALOG}.{SIM}.job_run_timeline")

clusters = (load("clusters.csv")
    .withColumn("worker_count", F.col("worker_count").cast("int"))
    .withColumn("auto_termination_minutes", F.col("auto_termination_minutes").cast("int"))
    .withColumn("tags", F.from_json("tags", "map<string,string>"))
    .withColumn("change_time", F.to_timestamp("change_time"))
    .withColumn("delete_time", ts_or_null("delete_time")))
save(clusters, f"{CATALOG}.{SIM}.clusters")

warehouses = (load("warehouses.csv")
    .withColumn("min_clusters", F.col("min_clusters").cast("int"))
    .withColumn("max_clusters", F.col("max_clusters").cast("int"))
    .withColumn("auto_stop_minutes", F.col("auto_stop_minutes").cast("int"))
    .withColumn("tags", F.from_json("tags", "map<string,string>"))
    .withColumn("change_time", F.to_timestamp("change_time")))
save(warehouses, f"{CATALOG}.{SIM}.warehouses")

queries = (load("query_history.csv")
    .withColumn("start_time", F.to_timestamp("start_time"))
    .withColumn("total_duration_ms", F.col("total_duration_ms").cast("bigint"))
    .withColumn("read_rows", F.col("read_rows").cast("bigint")))
save(queries, f"{CATALOG}.{SIM}.query_history")

audit = (load("access_audit.csv")
    .withColumn("event_time", F.to_timestamp("event_time"))
    .withColumn("event_date", F.to_date("event_date"))
    .withColumn("user_identity", F.from_json("user_identity", "struct<email:string>"))
    .withColumn("request_params", F.from_json("request_params", "map<string,string>")))
save(audit, f"{CATALOG}.{SIM}.access_audit")
