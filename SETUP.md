# Setup (Free Edition, Git folder + workspace UI, ~15 min)

1. Create a **new private GitHub repo** (e.g. `shopnest-mock`) → Add file → Upload files → drag the **contents** of this folder (`databricks.yml` must be at the root) → Commit. If GitHub's uploader refuses the folders, upload `data/` in a second commit.
2. Databricks → Workspace → your home folder → **Create → Git folder** → paste the repo URL. (The Databricks GitHub App needs access to the new repo: GitHub → Settings → Applications → Databricks → Configure.)
3. Open `databricks.yml` → **Deployments** (rocket icon) → target `dev` → **Deploy**.
4. Run `[dev <you>] shopnest_00_setup` (Deployments panel or Jobs & Pipelines). ~5–10 minutes.

## Check
```sql
SELECT count(*) FROM workspace.sim_system.billing_usage;        -- 17,401
SELECT count(*) FROM workspace.sim_system.job_run_timeline;     -- 11,708
SELECT count(*) FROM workspace.shopnest.gold_daily_revenue;     -- > 0
```

## Notes
- `mode: development` prefixes job names with `[dev <you>]` and pauses every schedule. Leave them paused.
- `clickstream_sessions_daily` **fails** when you run it on its own. That's the production behaviour, not a setup problem.
- Free Edition: one active pipeline at a time, small serverless warehouse, everything serverless. That's fine here.
- Your catalog isn't `workspace`? Change the `catalog` variable default in `databricks.yml`.
