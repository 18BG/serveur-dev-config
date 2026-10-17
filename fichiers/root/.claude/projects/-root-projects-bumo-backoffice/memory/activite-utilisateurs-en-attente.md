---
name: activite-utilisateurs-en-attente
description: "Most active users" + activity charts on user/business pages — prototype built 2026-10-17 on branches feat/activite-utilisateurs (front + bumo-hooks), thresholds still to calibrate
metadata:
  type: project
---

The user could not settle what "active" means. On 2026-10-17 they asked for a concrete prototype "pour voir" instead of more explanation, so keep explanations short and show results.

Prototype, uncommitted at the time, on branch `feat/activite-utilisateurs` in both repos:
- bumo-hooks: `backoffice_activity_service.py`, routes `GET /bumo/backoffice/activity?business=|user=&grain=day|week|month` and `/activity/top?days=7|30|90`.
- front: the "Activité dans l'app" panel on business and user pages, plus the `/activity` page "Les plus actifs".

Definition chosen: an operation is a deliberate action with an author (sale, purchase, expense, quotation, entered order, product, customer, cash session opened). The level counts days with at least one operation among the last 28 calendar days: regular ≥ 12, occasional 1–11, asleep 0 with history, never, new < 14 days.

**Why:** the user wanted something "vrai et parlant", not just a chart.
**How to apply:** the thresholds (12/28, 14 days) are guesses; calibrate them on production data before relying on them. Front branch is stacked on fix/navigation-et-devises. See [[git-pull-github-indisponible]].
