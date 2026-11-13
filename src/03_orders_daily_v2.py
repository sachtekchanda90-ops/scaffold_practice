# Databricks notebook source
# MAGIC %md
# MAGIC # orders_daily_v2
# MAGIC rahul.verma, 2026-10-03: "faster version for the web team, skips the MERGE. TODO: retire orders_daily once this is stable"
# MAGIC Scheduled 03:30 daily on shared-etl-1, right after orders_daily.

# COMMAND ----------

from datetime import date, timedelta
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "shopnest")
dbutils.widgets.text("since", "")          # setup replays history from 2026-10-03; daily runs use yesterday
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
T = lambda name: f"{CATALOG}.{SCHEMA}.{name}"
since = dbutils.widgets.get("since") or (date.today() - timedelta(days=1)).isoformat()

# COMMAND ----------

web = (spark.table(T("orders_raw"))
       .where((F.col("channel") == "web") & (F.to_date("order_ts") >= F.lit(since)))
       .withColumn("_loaded_by", F.lit("orders_daily_v2")))

web.write.mode("append").saveAsTable(T("silver_orders"))   # fast: no MERGE
print("appended", web.count(), "rows since", since)
