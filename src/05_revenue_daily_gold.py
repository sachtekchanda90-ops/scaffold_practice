# Databricks notebook source
# MAGIC %md
# MAGIC # revenue_daily_gold
# MAGIC Owner: tom.reed · Finance's daily revenue table (Tableau "Daily Revenue" workbook reads this).

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "shopnest")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
T = lambda name: f"{CATALOG}.{SCHEMA}.{name}"

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {T('gold_daily_revenue')} AS
SELECT to_date(o.order_ts) AS order_date, o.channel, c.region,
       count(*) AS orders, sum(o.amount) AS revenue
FROM {T('silver_orders')} o
JOIN {T('customers')} c ON o.customer_id = c.customer_id
GROUP BY ALL
""")
print(spark.table(T("gold_daily_revenue")).count())
