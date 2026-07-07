# Atlas OS Market Data Reality Report

Date: 2026-07-08

| Channel | Reality Classification | Evidence |
|---|---|---|
| Price | ACTIVE_WITH_FALLBACK | Normalized `price_breakout` routes to `volume_price_breakout`; live provider not proven in morning pass. |
| Volume | ACTIVE_WITH_FALLBACK | Same price/volume backbone; depends on provider availability. |
| Breadth | NOT_CONFIGURED | Explicitly reported missing. |
| Volatility | PARTIAL | Derived from price/history when available; not a full source. |
| Liquidity proxy | PARTIAL | Derived from volume/market context when available. |
| News | NOT_CONFIGURED | No live adapter. |
| Announcement | NOT_CONFIGURED | No live adapter. |
| Macro | NOT_CONFIGURED | No live adapter. |
| Narrative | NOT_CONFIGURED | No live adapter. |
| Attention | SIMULATED_OR_EVENT_DRIVEN | EventStream supports attention events; no live attention feed proven. |
| Social | NOT_CONFIGURED | Router supports social type; no live feed. |
| Portfolio-relevant events | ACTIVE_FOR_CONFIGURED_ASSETS | Read-only context exists; live event generation depends on market provider. |

## Verdict

Market-awareness is PARTIAL. Labeling is honest; full live market intelligence is not proven.
