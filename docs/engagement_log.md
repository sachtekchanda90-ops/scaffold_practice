# ShopNest × Databricks: engagement log (account team notes)

Internal notes from the Databricks account team. Shared with the DSA joining mid-engagement.

## People
| Name | Role | Notes |
|---|---|---|
| Elena Brooks | Head of Data / Platform Owner | Exec sponsor. Promised the CMO a Black Friday conversion dashboard by **Mon Nov 23**. |
| Victor Hale | Budget Owner, FP&A | Approved **$40k/month** for the data platform this fiscal year. |
| Sam Okafor | Platform Engineering Lead | Runs the workspace, clusters and the 40-person data engineering group. |
| Rahul Verma, Jake Lin, Priya Nair, Maria Gomez, Tom Reed, Omar Haddad | Data engineers | Own the orders, clickstream, marketing, finance and ML jobs. |

## Timeline
- **Jun 2026:** ShopNest moves its analytics off a legacy warehouse onto Databricks. One workspace, used for development and production. Notebooks live under `/Users/<name>/`. No Git, no bundles.
- **Jul 2026:** 34 scheduled jobs live. Most run on job clusters; ten share an all-purpose cluster (`shared-etl-1`).
- **Aug 25:** Sam: “Job clusters take 6–7 minutes to start and the hourly jobs were missing their windows.” He creates `shared-etl-2` and moves 14 more jobs onto shared all-purpose clusters. Auto-termination is set to 0 on both “so they're always warm”. No change request.
- **Sep 1:** Three engineers set auto-termination to 0 on their personal dev clusters (“tired of waiting for them to start every morning”).
- **Sep 22:** Priya upgrades pandas to 2.2.3 on `shared-etl-2` for a new feature-engineering job. Nobody else is told.
- **Late Sep:** “Random” failures start on several jobs. Engineers hotfix notebooks in production at night; some fixes are lost when someone else edits the same notebook.
- **Oct 3:** Rahul creates `orders_daily_v2` (“faster, skips the MERGE”) and schedules it after `orders_daily`. The plan was to retire `orders_daily` once v2 was stable. Both are still running.
- **Oct 20:** Victor emails Elena: “The platform bill has gone from about $38k in August to more than $65k. That's well over the $40k we approved. Explain or I freeze new spend.”
- **Oct 28:** Tom (finance data) notices October web revenue in the Tableau “Daily Revenue” workbook is higher than the payouts Finance receives. Marked “investigate after month-end”.
- **Nov 2:** Marketing asks again for the Black Friday conversion dashboard. Jake: “clickstream_sessions_daily keeps failing, I re-run it by hand most mornings.”
- **Nov 9:** Elena asks Databricks for help: “I need to show Victor a plan, show the CMO we'll make Nov 23, and stop my team editing production by hand. Sam wants to keep the shared clusters.”

## What the customer has asked for
1. Why is the bill up, and what will it be after fixes?
2. Why do jobs fail, and how do we stop it?
3. A way of working: Git, dev → prod, no hand edits in production. Their app team already uses GitHub Actions.
4. The Black Friday conversion dashboard by Nov 23, and a cost view Victor can open himself.

## Constraints
- 40 engineers, mostly notebook users; few have used Git.
- Change freeze for Black Friday week: **Nov 23 – Dec 1**.
- Finance closes November on Dec 3; the revenue numbers must be right by then.
