# ShopNest workspace modernization (practice scaffold)

**Fictional company, practice material.** ShopNest is a US home-goods e-commerce retailer. Its data team runs 34 scheduled jobs (clickstream, orders, marketing, finance, ML) in a single Databricks workspace that is used for both development and production.

You are the Databricks Delivery Solutions Architect, mid-engagement. In the steering review you'll meet the Head of Data (Elena Brooks), the Budget Owner (Victor Hale, FP&A) and the Platform Engineering Lead (Sam Okafor).

## What's in this bundle
| Path | What |
|---|---|
| `databricks.yml` | The bundle. One `dev` target only. |
| `resources/jobs.yml` | Setup job + 4 of the 34 production jobs, re-pointed at serverless. |
| `src/00_setup_load_system_history.py` | Loads 104 days of production telemetry into `sim_system` (same shape as `system.*`). |
| `src/01_load_source_data.py` | Loads orders, customers, Finance payouts; generates clickstream. |
| `src/02_orders_daily.py` … `05_revenue_daily_gold.py` | Production notebooks, as the team wrote them. |
| `docs/engagement_log.md` | Account-team notes: people, timeline, asks, constraints. |
| `docs/prod_job_configs/` | Exports from the production workspace: jobs, clusters + libraries, policies, warehouses, the app team's CI. |

## Tables after setup
- `workspace.sim_system.*`: billing_usage, list_prices, jobs, job_run_timeline, clusters, warehouses, query_history, access_audit.
- `workspace.shopnest.*`: orders_raw, customers, finance_payouts, clickstream_events, silver_orders, gold_sessions, gold_daily_revenue.

## Your four tasks
1. **Diagnose** what's driving cost and delivery risk, grounded in system tables and workspace artifacts.
2. **Build:** extend the artifacts that best support your recommendation.
3. **Guard:** implement guardrails to prevent recurrence.
4. **Prepare:** a short deck (3 slides max) with a prioritized remediation plan.

There's more here than 4 hours allows. What you choose not to do is part of the exercise.
