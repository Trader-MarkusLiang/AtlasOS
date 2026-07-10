# Atlas OS Practical Brief Source Audit

Date: 2026-07-10

## Scope

This audit was completed before rebuilding Home. It inspects historical Atlas trading-operating
brief sources, current Home implementation, runtime state inputs, candidate source truth, forecast
ledger access, portfolio projection, and expert analysis boundaries.

## Boundary Decision

The Home route must be a Practical Decision Brief, not a generic system dashboard. The
user-validated operating chain is authoritative:

```text
Action Today -> Core Judgment -> Strongest Predictions -> AI Bottleneck Index -> Capital Relay
-> Current Holdings -> Capital Allocation -> Waiting Triggers -> Research Tasks
-> Intelligence & Alerts -> Counter Argument -> Review Plan
```

No cognition, CDE, Decision Contract, forecast lifecycle, portfolio mutation, runtime scheduling, or
trading execution semantics may change.

## Historical Source Classification

| Source | Classification | Finding | Home Use |
|---|---|---|---|
| `03_Trading_OS/Daily_Dashboard_Template.md` | AUTHORITATIVE_USER_VALIDATED | Defines Trade Today, one-sentence conclusion, AI Bottleneck Index, Capital Relay, actions, risk, and waiting triggers. | Primary Home operating structure. |
| `03_Trading_OS/Trading_Decision_Table.md` | AUTHORITATIVE_USER_VALIDATED | Defines required action object fields: Action, Confidence, Logic Chain, Evidence, Risk/Reward, Trigger, Counter Argument, Review Plan. | Compact Home shows Action / Why / Trigger; expanded evidence remains secondary. |
| `03_Trading_OS/Capital_Allocation_Board.md` | AUTHORITATIVE_USER_VALIDATED | Defines market state, whether to act, source of funds, destination, and ratio concepts. | Home Capital Allocation Board and funding source -> destination logic. |
| `03_Trading_OS/Capital_Rotation_Table.md` | AUTHORITATIVE_USER_VALIDATED | Defines rotation prerequisites and source -> destination chain. | Home capital relay and allocation gating. |
| `01_Framework/AI_Bottleneck_Index.md` | SUPPORTING | Taxonomy authority; current rankings belong elsewhere. | Used to interpret domains only. |
| `04_Current_State/Bottleneck_Map_v1.md` | AUTHORITATIVE_USER_VALIDATED | Current ranking snapshot: Memory S+, Equipment S+, Materials S, Bandwidth S, Power A. | Home AI Bottleneck Index. |
| `01_Framework/Capital_Relay.md` | AUTHORITATIVE_USER_VALIDATED | Framework definition and current v0.1 relay judgment. | Home Capital Relay. |
| `04_Current_State/AI_Capital_Map_v1.md` | AUTHORITATIVE_USER_VALIDATED | Current capital map snapshot. | Home Capital Relay source. |
| `04_Current_State/Current_Holdings_Strategy.md` | SUPPORTING / PARTLY OBSOLETE | Historical holdings include positions no longer matching current runtime config. | Not used as current holdings source. |
| `runtime/config/user_config.json` | ACTIVE_RUNTIME_SOURCE | Local runtime configuration provides actual configured holdings. | Current Holdings only; exact account amount must not be exposed. |
| `02_Databases/AI_Shovel_100.md` | SUPPORTING | Static Markdown candidate pool with manual S/A/B priority. | Home may show only Top 3 research tasks and must link to `/candidates`. |
| `02_Databases/Risk_Radar.md` | SUPPORTING | Contains strongest counter-arguments and high-severity risks. | Home Counter Argument and alerts. |
| `runtime/forecast_ledger.py` / `/predictions` state | ACTIVE_RUNTIME_SOURCE | Forecast accountability ledger exists and is read-only from Home. | Compact Forecast Accountability. |
| `ui/presentation/home_intelligence.py` pre-rebuild | OBSOLETE_FOR_HOME | Built prior six-question user decision journey, not the requested practical chain. | Replaced for Home default view. |
| `ui/pages/product_views.py::home_content` pre-rebuild | OBSOLETE_FOR_HOME | Rendered equal-weight decision cards and supporting modules. | Rebuilt around practical chain. |

## Candidate Pool Truth

`02_Databases/AI_Shovel_100.md` is a static Markdown research pool with manual S/A/B priority. The
Home page must not claim dynamic AI selection, runtime ranking, or trading authority. Current
portfolio relevance can be overlaid for presentation only.

## Portfolio Truth

Actual current holdings must come from runtime configuration and be displayed only as percentages /
relative exposure. Historical holdings in `04_Current_State/Current_Holdings_Strategy.md` are not
authoritative for the current UI if they conflict with configured holdings.

## Source Audit Status

PASS. Historical user-validated practical brief sources are identified, classified, and prioritized
above the recent generic Home information architecture.
