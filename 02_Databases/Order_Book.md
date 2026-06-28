# Order Book

Order Book tracks confirmed order, capacity, and backlog evidence.

| Date | Company / Chain | Evidence | Bottleneck | Read-through | Source |
|---|---|---|---|---|---|
| 2026-06-28 | Memory chain | Repository-level thesis: Memory ranked S+ | Memory | Order evidence should be collected before changing position size | `04_Current_State/Bottleneck_Map_v1.md` |
| 2026-06-28 | Equipment chain | Repository-level thesis: Equipment ranked S+ and taking relay | Equipment | Confirmed orders/backlog should validate relay strength | `01_Framework/Capital_Relay.md` |
| 2026-06-28 | Bandwidth chain | Repository-level thesis: Bandwidth ranked S | Bandwidth | Confirm customer demand before treating as first-level trade | `05_Cases/Corning_Bandwidth.md` |

## Evidence Standard

Order evidence should be recorded only when it can identify:

1. Customer, supplier, or chain.
2. Order, capacity, backlog, shipment, or utilization signal.
3. Affected bottleneck.
4. Read-through into revenue, margin, capex, or capital flow.
5. Source or internal case file.
