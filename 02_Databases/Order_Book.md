# Order Book

Order Book tracks confirmed order, capacity, and backlog evidence.

| Date | Company / Chain | Evidence | Bottleneck | Read-through | Source |
|---|---|---|---|---|---|
| 2026-06-28 | Memory chain | Repository-level thesis: Memory ranked S+ | Memory | Order evidence should be collected before changing position size | `04_Current_State/Bottleneck_Map_v1.md` |
| 2026-06-28 | Equipment chain | Repository-level thesis: Equipment ranked S+ and taking relay | Equipment | Confirmed orders/backlog should validate relay strength | `01_Framework/Capital_Relay.md` |
| 2026-06-28 | Bandwidth chain | Repository-level thesis: Bandwidth ranked S | Bandwidth | Confirm customer demand before treating as first-level trade | `05_Cases/Corning_Bandwidth.md` |

## Real Evidence Record Template

Use this table for actual order, capacity, delivery, backlog, shipment, utilization, or customer
qualification records. Do not mix thesis-only notes with confirmed evidence.

| Date | Company | Customer | Evidence | Order | Capacity | Shipment | Utilization | Qualification | Revenue Impact | Source | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | Company name | Customer, supplier, or chain | Order / Capacity / Delivery / Backlog / Shipment / Utilization / Qualification | Confirmed order value/volume or Unknown | Capacity value or Unknown | Shipment status or Unknown | Utilization/backlog or Unknown | Qualification status or Unknown | Revenue, margin, capex, FCF, or Unknown | Source link or internal note | Low / Medium / High |

## Living Evidence Seed

These are watch records, not confirmed order records. Missing public evidence is marked `Unknown`.

| Date | Company | Customer | Evidence | Order | Capacity | Shipment | Utilization | Qualification | Revenue Impact | Source | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-29 | Micron（MU） | Unknown | Priority S Memory holding; order evidence not yet recorded | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | SK Hynix | Unknown | Priority A Memory research record; order evidence not yet recorded | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | LRCX | Unknown | Priority A Equipment research record; order/backlog evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | AMAT | Unknown | Priority A Equipment research record; order/backlog evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | 拓荆科技 | Unknown | Domestic Equipment research record; customer/order evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | 北方华创 | Unknown | Domestic Equipment research record; customer/order evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | 中微公司 | Unknown | Domestic Equipment research record; customer/order evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | 盛美上海 | Unknown | Domestic Equipment research record; customer/order evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `02_Databases/AI_Shovel_100.md` | Low |
| 2026-06-29 | Corning | Unknown | Priority A Bandwidth research record; customer adoption evidence required | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | `05_Cases/Corning_Bandwidth.md` | Low |

## Evidence Standard

Order evidence should be recorded only when it can identify:

1. Customer, supplier, or chain.
2. Order, capacity, backlog, shipment, or utilization signal.
3. Affected bottleneck.
4. Read-through into revenue, margin, capex, or capital flow.
5. Source or internal case file.
