# Execution Log

All Atlas trades should be recorded here after execution. This file is a template and process log;
real sensitive portfolio data may belong in local-only files if it should not enter Git.

| Date | Company | Action | Reason | Evidence | Result | Review | Lessons Learned |
|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | Company name | Research / Observe / Build / Accumulate / Hold / Reduce / Exit | Link to Trading OS reason | Living Database / signal / order / risk / price transmission | Pending / Profit / Loss / No action | Review date or event | Learning to feed back into Research |

## Execution Rule

Execution records the trade. It does not create the research thesis.

If execution depends on current price, intraday timing, K-line / technical status, volume, price
dislocation, market confirmation, or quick rebalance conditions, Market Data Fetch Gate must run
before the execution rationale is treated as valid.

If market data is unavailable, record:

```text
Fast Rebalance Decision Limited — Market Data Required
```

Do not record precise execution authority, intraday timing, or technical confirmation as valid
without current market data.

Before any execution entry is treated as valid, it must have:

1. Reason.
2. Evidence.
3. Capital action.
4. Review plan.

## Log

| Date | Company | Action | Reason | Evidence | Result | Review | Lessons Learned |
|---|---|---|---|---|---|---|---|
| 2026-07-19 | 东山精密 002384.SZ | Exit | User confirmed full exit of previous positions | User-confirmed portfolio refresh 2026-07-19 | Pending | 2026-07-26 weekly review | Thesis evidence was never refreshed; concept exposure alone did not justify holding |
| 2026-07-19 | 中船特气 688146.SH | Build (29.0%) | Electronic specialty gases / semiconductor materials exposure | User-confirmed holding 2026-07-19; demand and qualification evidence Unverified | Pending | 2026-07-26 weekly review | Largest single position; concentration risk to monitor |
| 2026-07-19 | 风华高科 000636.SZ | Build (12.5%) | MLCC / AI server BOM component exposure | User-confirmed holding 2026-07-19; AI demand linkage Unverified | Pending | 2026-07-26 weekly review | Indirect thematic exposure; needs order/price evidence |
| 2026-07-19 | 国际复材 301526.SZ | Build (7.2%) | Electronic glass fiber cloth upstream of PCB / CCL | User-confirmed holding 2026-07-19; AI PCB transmission Unverified | Pending | 2026-07-26 weekly review | Smallest position; thesis-sensitive |
| 2026-07-19 | 建滔集团 00148.HK | Hold (26.0% -> 18.4%) | Position resized within full portfolio refresh | User-confirmed holding and cost basis 2026-07-19 | Pending | 2026-07-26 weekly review | Deep drawdown; thesis re-verification required before any action |
| 2026-07-19 | 安集科技 688019.SH | Hold (34.0% -> 12.2%) | Position resized within full portfolio refresh | User-confirmed holding and cost basis 2026-07-19 | Pending | 2026-07-26 weekly review | Deep drawdown; thesis re-verification required before any action |
