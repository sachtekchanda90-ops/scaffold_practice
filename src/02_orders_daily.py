# Databricks notebook source
# MAGIC %md
# MAGIC # orders_daily
# MAGIC Owner: rahul.verma · copied from /Users/jake.lin@shopnest.example/orders/orders_daily (Jun 2026)
# MAGIC Builds `silver_orders`: one row per order, latest version wins.

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "shopnest")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
T = lambda name: f"{CATALOG}.{SCHEMA}.{name}"

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {T('silver_orders')} (
  order_id STRING, customer_id STRING, order_ts TIMESTAMP, channel STRING,
  amount DECIMAL(12,2), status STRING, updated_at TIMESTAMP, _loaded_by STRING)
""")

spark.sql(f"""
MERGE INTO {T('silver_orders')} t
USING (
  SELECT * EXCEPT (rn), 'orders_daily' AS _loaded_by FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
    FROM {T('orders_raw')})
  WHERE rn = 1) s
ON t.order_id = s.order_id AND t._loaded_by = 'orders_daily'
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")
print(spark.table(T("silver_orders")).count())
