# FAQ

**Are the system tables real?** No. `sim_system.*` is ShopNest's production telemetry, simulated, with the same table and column names as `system.*` (one difference: `query_history.warehouse_id` is a top-level column). Write your queries as you would against `system.*`, then swap the schema.

**Why don't I see the analysts' SQL in `query_history`?** It only covers SQL warehouses. Analysts run SQL in notebooks on an all-purpose cluster.

**Do the prices match my contract?** They're list prices (`list_prices`). Treat cost as an estimate at list price.

**Can I change the production notebooks?** Yes. Extend whatever supports your recommendation. You don't have to fix everything.

**The bundle only has a dev target. Is that intentional?** Yes. That's how the customer works today.

**What does “production” mean here?** The jobs in `docs/prod_job_configs/jobs_inventory.json`. Only four are in this bundle.

**How much does it matter that it all runs?** The steering review is the main assessment; the build supports it. A clear before/after on one thing beats many half-finished changes.
