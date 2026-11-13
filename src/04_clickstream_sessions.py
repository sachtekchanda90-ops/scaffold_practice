# Databricks notebook source
# MAGIC %md
# MAGIC # clickstream_sessions_daily
# MAGIC Owner: jake.lin · feeds marketing's conversion analysis (Black Friday campaign)
# MAGIC Rebuilds `gold_sessions` from all clickstream history every night, then writes a small funnel summary.
# MAGIC Prod: runs on shared-etl-2. Libraries on that cluster are installed by hand (see docs/prod_job_configs/clusters.json).

# COMMAND ----------

# %pip install pandas==1.5.3   <- was in Jake's original notebook; removed when we moved to the shared cluster
import pandas as pd
from pyspark.sql import functions as F, Window

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "shopnest")
dbutils.widgets.text("run_summary", "true")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
T = lambda name: f"{CATALOG}.{SCHEMA}.{name}"

# COMMAND ----------

ev = spark.table(T("clickstream_events"))
w = Window.partitionBy("customer_id").orderBy("event_ts")
sessions = (ev
    .withColumn("gap_min", (F.col("event_ts").cast("long") - F.lag("event_ts").over(w).cast("long")) / 60)
    .withColumn("new_session", F.when(F.col("gap_min").isNull() | (F.col("gap_min") > 30), 1).otherwise(0))
    .withColumn("session_no", F.sum("new_session").over(w))
    .groupBy("customer_id", "session_no")
    .agg(F.min("event_ts").alias("session_start"), F.max("event_ts").alias("session_end"),
         F.count("*").alias("events"), F.max(F.when(F.col("page") == "confirm", 1).otherwise(0)).alias("converted")))

# full rebuild every night
sessions.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(T("gold_sessions"))

# COMMAND ----------

if dbutils.widgets.get("run_summary") == "true":
    daily = (spark.table(T("gold_sessions"))
             .groupBy(F.to_date("session_start").alias("day"))
             .agg(F.count("*").alias("sessions"), F.sum("converted").alias("conversions"))
             .orderBy("day").toPandas())
    summary = pd.DataFrame(columns=["day", "sessions", "conversions", "conversion_rate"])
    for _, r in daily.iterrows():
        summary = summary.append({"day": r["day"], "sessions": r["sessions"], "conversions": r["conversions"],
                                  "conversion_rate": r["conversions"] / r["sessions"]}, ignore_index=True)
    spark.createDataFrame(summary).write.mode("overwrite").saveAsTable(T("gold_funnel_daily"))
