# Home Position Cost And PnL Goal Prompt

- Date: 2026-07-14 09:17 CST
- Session id: 019f0ead-cd83-7f81-8bef-ded7fb3d4659
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Design an executable Goal prompt for Home position cost, price, and PnL visualization
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

Prepare a Goal prompt for upgrading the investor Home brief with average cost, latest market price,
profit/loss visualization, privacy-safe local portfolio data, and evidence-based implementation.

## Work Done

- Audited the current local portfolio fields and confirmed that average cost and quantity are absent.
- Confirmed that market observations already expose latest price but Home holdings do not present it.
- Defined privacy modes, mixed-currency/FX handling, missing-data behavior, calculations, UI hierarchy,
  security boundaries, browser validation, and Production Trial gating.
- Produced an execution prompt only; no feature implementation was started.

## Decisions

- Cost is risk and execution context, not thesis evidence.
- Exact cost, quantity, market value, and PnL amount remain local-only and must never enter Git,
  telemetry, snapshots, or LLM prompts.
- PnL percentage can be computed from average cost and latest price; amount and dynamic current
  weight require quantity plus trustworthy FX for mixed currencies.
- Missing or stale data must remain explicit and must never be converted to zero.

## Current State

- Goal prompt delivered in the conversation.
- Implementation remains pending a future Goal execution.

## Resume Instructions

1. Use the delivered Goal prompt as the execution objective.
2. Record a new Production Trial Issue before implementation.
3. Preserve private portfolio data outside Git.

## Open Questions

- Real average cost and quantity values still need user input before personalized PnL can be shown.
