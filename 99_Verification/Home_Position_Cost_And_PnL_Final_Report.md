# Home Position Cost and PnL Final Verification Report

Date: 2026-07-14

Classification: `PROVEN_COMPLETE`

Linked Issue: `ISSUE-2026-061`

Linked IP: `IP-2026-061`

## Implemented Path

```text
Settings position editor
-> ignored local user config
-> private-field validation
-> public market observation and identity match
-> deterministic Decimal valuation
-> local visibility filter
-> portfolio-first Home holdings board
```

The existing percentage-only cognition path remains separate.

## Calculations

- Return: `((latest price - average cost) / average cost) * 100`.
- Total cost: `average cost * quantity` only when quantity exists.
- Market value: `latest price * quantity` only when quantity and usable real price exist.
- PnL amount: `(latest price - average cost) * quantity` only when all inputs and currency identity
  are valid.
- All user financial calculations use Python `Decimal` and explicit rounding.
- Configured allocation is never presented as estimated current live weight.

## Market And FX Evidence

The canonical runtime on port 8765 reported three configured positions. A fresh public-source
refresh produced the following safe evidence:

| Asset | Provider | Observed | Freshness | Quality | Price available | Currency |
|---|---|---|---|---|---:|---|
| `00148.HK` | `tencent_kline` | `2026-07-14T00:00:00` | DELAYED | Available | yes | HKD |
| `002384.SZ` | `tencent_kline` | `2026-07-14T00:00:00` | DELAYED | Available | yes | CNY |
| `688019.SH` | `tencent_kline` | `2026-07-14T00:00:00` | DELAYED | Available | yes | CNY |

No current real price, cost, quantity, market value, or PnL number is recorded here. Delayed market
data remains usable with a visible verify-before-acting warning. FX is not configured, so mixed-
currency aggregate valuation remains explicitly limited. Per-position native-currency returns are
available when the user supplies same-currency cost.

## Missing And Degraded Behavior

| Condition | Behavior |
|---|---|
| missing cost | return and PnL unavailable, never zero |
| missing quantity | return may remain available; amounts and current weight unavailable |
| missing/failed price | valuation blocked |
| simulated price | real PnL blocked |
| delayed/cached price | status and timestamp shown with verification warning |
| ticker identity mismatch | valuation blocked |
| cost/price currency mismatch | return and PnL blocked |
| missing FX | aggregate cross-currency valuation limited |
| malformed private config | save rejected or Home degrades without crashing |

## Browser Evidence

All committed screenshots use synthetic positions only:

- `99_Verification/artifacts/home_position_valuation/home_synthetic_en_holdings_desktop.png`
- `99_Verification/artifacts/home_position_valuation/home_synthetic_en_holdings_mobile.png`
- `99_Verification/artifacts/home_position_valuation/settings_synthetic_en_portfolio_desktop.png`

Desktop results: 1440 x 1000, three cards, three cost charts, three PnL charts, no page overflow,
no cost-label overlap, and no amount overflow.

Mobile results: 390 x 844, three cards, no page/card/chart/amount overflow.

Browser Settings save returned `Saved`; all four privacy controls were visible. Disabling amount
visibility removed market-value and PnL-amount labels while retaining cost and return charts.

## Test Results

`99_Verification/artifacts/home_position_valuation/validation_result.json` records PASS for all 14
required groups plus Settings response masking, safe state, and price-currency metadata.

Additional current validators:

- Goal 03 market intelligence: PASS
- Goal 04 portfolio cognition: PASS
- Home intelligence: PASS
- Home localization v2: PASS
- Investor Home Goal: PASS
- task-aware multi-LLM routing v1.5: PASS
- productization backbone: PASS

The legacy `validate_practical_brief_home.py` still encodes the pre-portfolio-first chain order and
also treats the `sk-o` substring in `risk-off` as a key-like token. Its failures predate and do not
exercise this Goal's current authoritative Home contract; the script was not weakened to manufacture
a green result.

## Acceptance Matrix

| Requirement | Result |
|---|---|
| cost entry without JSON | PASS |
| quantity optional | PASS |
| private data outside Git | PASS |
| cost and latest price on Home | PASS |
| deterministic return | PASS |
| amount/value only with quantity | PASS |
| honest mixed-currency handling | PASS |
| configured vs current weight distinction | PASS |
| missing/stale/failed never becomes zero | PASS |
| no exact private LLM/telemetry context | PASS |
| cost does not override thesis/CDE/evidence | PASS |
| zh/en parity | PASS |
| desktop/mobile browser validation | PASS |
| cognition/task-routing regression | PASS |
| canonical UI on 8765 | PASS |
| no real private values in evidence | PASS |
| commits reference Issue | PASS |

## Implementation Commits

- `27499bb` - Production Trial Issue, IP, and privacy boundary.
- `b52a559` - local valuation, Settings, Home, market currency, and privacy integration.
- `67743d9` - synthetic verification, browser evidence, reports, and presentation version update.

## Personalized PnL Status

`NOT_CONFIGURED`

The current ignored local portfolio has valid allocation and public market observations but does not
contain average cost or quantity. Atlas therefore shows an honest missing-cost state. No value was
inferred from prior account-size or allocation discussion.

## Remaining Limitations

- No broker import or corporate-action cost reconstruction.
- No FX provider is configured for account-level mixed-currency totals.
- Estimated current portfolio weight remains unavailable until quantity, complete normalized prices,
  FX where needed, and an explicit cash-value treatment are all available.
- Market observations are delayed, not live intraday data.
