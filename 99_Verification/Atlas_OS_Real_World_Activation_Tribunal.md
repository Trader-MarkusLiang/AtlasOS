# Atlas OS Real-World Activation Tribunal

Date: 2026-07-08

| Capability | Classification | Evidence |
|---|---|---|
| Real daemon path | `REAL_RUNTIME_PROVEN` | daemon CLI ticks created briefs, transitions, forecasts |
| Real scheduler path | `REAL_RUNTIME_PROVEN` | real sleep soak used interval 10, no `--no-sleep` |
| Real UI-to-runtime path | `REAL_RUNTIME_PROVEN` | `/settings` portfolio A/B and `/chat/send` inbox path |
| Real provider inference | `LIVE_PROVEN` | local ARK cc-switch inference through provider router |
| Real provider fallback | `LIVE_PROVEN` | MoreCode 401 -> ARK |
| Real market observation | `PARTIAL` | direct provider succeeded once; daemon path degraded |
| Real market freshness | `EXTERNAL_BLOCKER` | Eastmoney proxy/yfinance rate limit in daemon |
| Real portfolio context | `REAL_RUNTIME_PROVEN` | A/B relevance/sensitivity changed |
| Real forecast lifecycle | `REAL_RUNTIME_PROVEN` | daemon-created forecast plus UI mature/evaluate endpoints |
| Real prediction error | `REAL_RUNTIME_PROVEN` | INVALIDATED forecast produced error 1.0 |
| Real trust update | `REAL_RUNTIME_PROVEN` | later tick applied `-0.12` forecast calibration |
| Real hypothesis reranking | `REAL_RUNTIME_PROVEN` | treatment score distribution changed |
| Real structural adaptation | `REAL_RUNTIME_PROVEN` | treatment structural shift differed |
| Real self-iteration | `LIVE_PROVEN` | normal path treatment/control produced behavioral delta |
| Real daily cycle | `REAL_RUNTIME_PROVEN` | all four phases via daemon `--daily-cycle-now` |
| Real recovery | `REAL_RUNTIME_PROVEN` | malformed inbox, telemetry, stale PID, degraded market |
| Real-duration stability | `PARTIAL` | 6 cycles over about 3m46s, 0 tick errors |
| Browser usability | `PARTIAL` | browser routes rendered after stale server restart |
| Bilingual parity | `PARTIAL` | zh/en endpoint works; mixed page labels remain |
| Security | `LIVE_PROVEN` | tracked secret-shape scans clean after excluding command self-references; runtime config/log/sqlite paths ignored |

## Tribunal Verdict

Atlas OS is upgraded from controlled-fixture internal alpha to **partially real-runtime-proven
internal alpha**. It is not Release Candidate, not production, not 2-hour stable, and not live
market proven.
