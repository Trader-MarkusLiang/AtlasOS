# Home Position Valuation Security and Privacy Report

Date: 2026-07-14

Linked Issue: `ISSUE-2026-061`

Linked IP: `IP-2026-061`

## Result

`PASS`

No real average cost, quantity, total cost, market value, PnL amount, account value, execution price,
broker data, or API secret is recorded in this report or its machine-readable evidence.

## Boundary

| Surface | Exact private fields allowed | Evidence |
|---|---:|---|
| ignored local `user_config.json` | yes | Git ignore check PASS |
| ephemeral server-side Home projection | yes, visibility-gated | synthetic browser test PASS |
| Settings save response | no, values replaced by stored-local status | round-trip test PASS |
| general `/state` | no | live recursive key scan PASS |
| `build_portfolio_context()` | no | synthetic recursive key scan PASS |
| EventStream / DecisionLoop / cognition | no | import and protected-path audit PASS |
| external LLM context | no | orchestrator import/context audit PASS |
| telemetry / snapshot / replay / logs | no | no integration or persistence path added |
| Git and verification reports | no real private values | repository and evidence review PASS |

## Controls

- Cost and PnL percentages follow local display preferences.
- Quantity, current market value, total cost, and PnL amounts are hidden by default.
- Invalid cost, quantity, currency, and timestamp values are rejected before writing config.
- Settings responses do not echo submitted private numbers.
- Home values are produced during local server rendering; the safe state passed to the App Shell
  remains the ordinary percentage-only state.
- No dedicated public valuation API was added because server-side Home rendering satisfies the UI
  need with a smaller exposure surface.

## Privacy Verification

`99_Verification/validate_home_position_valuation.py` proved:

- private keys do not survive in cognition-facing portfolio context;
- private values are masked in Settings responses;
- privacy toggles remove unauthorized fields from the Home projection;
- the valuation module is not imported by the runtime orchestrator;
- malformed private input does not crash Home or daemon-adjacent code;
- `runtime/config/user_config.json` remains ignored and untracked.

## Residual Risks

- Any user with local machine/browser access can see values that the user explicitly enables on
  localhost. Atlas does not provide multi-user authentication.
- Screenshots of an enabled private Home page are themselves private user artifacts. Committed
  screenshots for this Goal use synthetic positions only.
- The current implementation does not import broker records or reconstruct corporate-action cost;
  adjusted average cost remains user supplied.
