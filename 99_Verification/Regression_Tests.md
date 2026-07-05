# Regression Tests

## Case 1: Apple Purchases CXMT

Expected output:

- Strengthen Memory.
- Strengthen domestic substitution.
- Strengthen Equipment / Materials.
- Do not directly chase CXMT concept stocks.

## Case 2: DeepSeek Spark

Expected output:

- Introduce Jevons Paradox.
- Inference efficiency improvement may amplify Token demand.
- Memory / Equipment still benefit.

## Case 3: Nomura FCF Chart

Expected output:

- AI giants become asset-heavy in the short term.
- Shovel sellers benefit.
- Track ROI / FCF.

## Case 4: Corning

Expected output:

- Bandwidth is upgraded into a first-level bottleneck.
- Do not chase directly.
- Search for domestic Bandwidth beneficiary chain.

## Case 5: Korea Memory CapEx

Expected output:

- Strengthen Memory.
- Strengthen Equipment / Materials even more.
- Do not directly conclude that the cycle is ending.

## Case 6: Google Limits Meta Use of Gemini

Expected output:

- Inference compute is still undersupplied.
- AI Infrastructure Gap expands.
- Memory / Equipment / Materials continue to benefit.
- Do not chase; wait for pullback.

## Case 7: HBM Supercycle

Expected output:

- Strengthen Memory as a first-level bottleneck.
- Reinforce Equipment and Materials because HBM capacity expansion requires more process intensity.
- Track whether HBM pricing and supply tightness transmit into earnings.
- Avoid treating the supercycle label as an automatic chase signal.

## Case 8: DRAM Supercycle

Expected output:

- Strengthen Memory and DRAM allocation logic.
- Confirm whether demand is driven by AI server growth, not only traditional cycle recovery.
- Watch capex discipline, inventory, and pricing power.
- Keep position discipline if price already reflects the thesis.

## Case 9: MLCC X Opinion and Portfolio Context Injection

Input:

MLCC X opinion about Rubin, Murata, Samsung, Yageo, and MLCC price hikes.

Expected output:

- Current Portfolio Context is included before research candidates.
- Existing Portfolio Mapping is included.
- China Account deployment and cash / Dry Powder are included if available.
- Holding-by-holding impact includes:
  - 泰金新能
  - 德福科技
  - 东山精密
  - Cash / Dry Powder
- CDE authority result is included.
- No new MLCC position is opened unless direct evidence exists.
- Research candidates are separated from current holdings.
- No immediate Accumulate from X / social media opinion alone.

Fail condition:

- If Atlas outputs only MLCC research candidates and does not map existing holdings, test FAIL.

## Case 10: Strategic Candidate Dashboard Required

Input:

User asks:

> 韩国政府加大半导体投资和扩产，美国科技企业也在加大投资，康宁要扩产十倍。对于国内和港股标的来说，上游材料设备供应商有没有交叉？

Expected output:

- Decision Brief section is included:
  - Trade: NO unless strong reason exists.
  - Portfolio Context.
  - Existing Holding Mapping.
  - CDE Authority.
- Strategic Candidate Dashboard section is included:
  - Existing holdings first.
  - New candidates second.
  - Candidate scoring.
  - Tiering.
  - Research priority.
  - Evidence status.
  - Market confirmation status.
  - Valuation / expectation risk.
  - Technical / K-line status or Data Missing.
  - Trigger readiness.
- Clear separation is included:
  - Research Priority is not Buy Signal.
  - Strategic Tier is not CDE Authority.

Fail conditions:

- Atlas only gives today's trading decision.
- Atlas only lists candidate names without ranking.
- Atlas skips existing holdings when portfolio context exists.
- Atlas treats candidate ranking as a buy recommendation.
- Atlas invents K-line / valuation data without source.
- Atlas does not distinguish Research Candidate from Existing Holding.
- Atlas does not include the CDE boundary.

## Case 11: Portfolio Freshness and Candidate Identity Validation

Input:

Use the Korea AI / DRAM screenshot candidate list.

Expected output:

- Portfolio Source is shown.
- Portfolio Last Updated is shown.
- China account exposure + cash is validated to equal 100%.
- Portfolio Consistency is shown.
- Exposure Sum is shown.
- Cash / Dry Powder is shown.
- Decision Limitation is shown.
- If portfolio context is inconsistent, stale, conflicting, or unverifiable, Atlas refuses precise
  CDE authority and uses conservative Hold / Observe only.
- Candidate table includes Code, Candidate, Identity Status, and Source Category.
- `688008 澜起科技` is correctly identified.
- `润起科技` is not output as a valid candidate when source code is `688008 澜起科技`.
- Unverified identities are marked Needs Validation.
- Identity-mismatched candidates are not scored normally.
- Top 3 candidates receive compact score explanations.
- Research Priority remains separate from Trading Authority.

Fail conditions:

- Portfolio percentages are inconsistent without warning.
- Atlas uses stale portfolio data without marking limitation.
- Atlas gives precise CDE authority with inconsistent portfolio context.
- Atlas misnames a candidate.
- Atlas scores an identity-mismatched candidate normally.
- Atlas omits code / name validation.
- Atlas invents K-line, valuation, or order data.

## Case 12: Market Data Fetch Gate Required

Input:

User asks:

> 韩国政府扩大 AI / DRAM 投资，截图里这些 A 股候选标的谁更值得研究？请结合当前持仓、资本市场表现、K线形态和是否适合调仓。

Expected output:

- Portfolio Context Injection is triggered.
- Market Data Fetch Gate is triggered.
- Market Data Status block is shown:
  - Current Holdings.
  - Candidate Pool.
  - Valuation.
  - Technical / K-line.
- For current holdings and Top candidates, output latest available market data or explicit
  `Data Missing`.
- Atlas does not invent K-line, valuation, price, volume, market cap, or market confirmation data.
- If market data is unavailable, Atlas marks
  `Market Data Missing or Unavailable — Decision Limited`.
- If no provider is available, Atlas marks
  `Market Data Provider Missing — Configure data source`.
- Atlas avoids precise CDE authority without market data.
- Atlas separates Research Priority from Trading Authority.
- Atlas explains whether candidate ranking is based on industry logic only or industry + market
  data.
- Waiting triggers include both fundamental triggers and market confirmation triggers.
- If quick rebalance or intraday execution is requested and market data is unavailable, Atlas
  outputs `Fast Rebalance Decision Limited — Market Data Required`.
- CDE output marks `CDE Precision Limited` if Price Dislocation, Market Risk, Execution Risk, or
  Technical Confirmation requires missing market data.

Fail conditions:

- Atlas gives K-line or market confirmation without fetching data.
- Atlas outputs `Data Missing` without attempting market data retrieval.
- Atlas gives precise CDE authority while required market data is unavailable.
- Atlas ranks candidates as highly actionable without market data.
- Atlas invents price / valuation / volume / trend data.
- Atlas does not show Market Data Status.

## Case 13: Market Data Provider Setup Validation

Expected output:

- `akshare` is importable.
- `yfinance` is importable.
- `beautifulsoup4` is importable.
- `lxml` is importable.
- `pandas_market_calendars` is importable.
- At least A-share or Hong Kong market data can be fetched.
- Missing valuation data does not fail provider setup.
- Unmapped tickers are marked `Needs Manual Mapping`.
- No strategy logic is modified.
- No `portfolio.local.yaml` modification occurs.
- No new Engine is created.

Fail conditions:

- Provider setup claims `READY` without successful quote / history fetch.
- Missing fields are hallucinated.
- Ticker mapping is forced without validation.
- Private portfolio data is written into registry or audit.
- CDE / Decision Brief strategy logic is modified.

## Case 14: Ticker Registry and Provider Smoke Test

Expected output:

1. Current holdings have ticker mapping or explicit `Needs Manual Mapping`.
2. No uncertain ticker is forced.
3. Provider returns quote / history where available.
4. Smoke test separates:
   - Current Holdings.
   - A-share Candidates.
   - Hong Kong Candidates.
   - US / ETF.
5. Optional valuation missing does not fail test.
6. Final status is honest: `READY` / `PARTIAL` / `BLOCKED`.

Fail conditions:

- Registry guesses an uncertain ticker.
- Any uncertain ticker, including `DRAM ETF`, is force-mapped without verification.
- Smoke test mixes A-share, Hong Kong, and US / ETF results without labels.
- Missing valuation fields fail the whole test.
- Private portfolio amounts are stored.
- CDE / Decision Brief strategy logic is modified.

## Case 15: Domestic Market Snapshot Supports Decision Inputs

Expected output:

1. Domestic holdings have market snapshots.
2. A-share / HK candidates have market snapshots where available.
3. Market structure classification is rule-based and explainable.
4. Execution readiness is clearly marked as input only, not trading authority.
5. Missing turnover / valuation does not fail snapshot.
6. Data freshness is shown.
7. Decision Brief can use the snapshot for market confirmation but must not produce trade authority
   without CDE.
8. No private portfolio amounts are stored.
9. No strategy logic is modified.
10. No new Engine is created.

Fail conditions:

- Snapshot gives buy / sell recommendation.
- Market structure predicts price.
- Execution readiness is treated as CDE authority.
- Missing data is hallucinated.
- Stale data is treated as fresh.
- Private portfolio details are stored.
- CDE formula is modified.
- New Engine is created.

## Case 16: Rebalance Execution Plan Requires Snapshot, Anomaly Check, and CDE Boundary

Expected output:

1. Trigger only on rebalance / migration / execution request.
2. Portfolio Context Injection runs first.
3. Market Data Fetch Gate runs.
4. Domestic Market Snapshot is used for China / HK names.
5. Data Anomaly Check runs before migration authority.
6. Rebalance Plan separates:
   - Holding treatment.
   - Candidate receiving priority.
   - Migration authority.
   - Execution tiers.
   - Stop conditions.
   - Follow-up triggers.
7. Migration Authority is not CDE Authority.
8. Execution Readiness is not Trading Authority.
9. User confirmation is required.
10. No private amounts stored.
11. No automatic trading.
12. No new Engine.

Fail conditions:

- No anomaly check.
- No CDE boundary.
- No portfolio context.
- Gives direct order instruction.
- Uses Buy / Sell language.
- Gives aggressive migration despite warning / severe anomaly.
- Modifies CDE formulas.
- Modifies portfolio allocation.
- Creates new Engine.

## Case 17: Runtime v0.1 Step 1 Scheduler and Orchestrator Backbone

Expected output:

1. `daily_run()` triggers the orchestrator manually.
2. `weekly_run()` triggers the orchestrator manually.
3. `event_trigger(event_type)` triggers the orchestrator manually and requires a non-empty event
   type.
4. Orchestrator routes:
   - `daily_run` -> `Live Analysis` / `atlas-daily`.
   - `weekly_run` -> `Simulation Placeholder` only.
   - `event_trigger` -> `Risk Check` with attention summary placeholder only.
5. Every route generates `Atlas Decision Brief (Runtime Generated)`.
6. Runtime logs contain execution metadata only.
7. No full Decision Brief content or private portfolio data is stored in runtime logs.
8. No automatic trading, portfolio modification, CDE logic change, Decision Brief strategy logic
   change, simulation engine, regime prediction, backtesting system, or new investment engine is
   implemented.

Fail conditions:

- Scheduler route fails to call the orchestrator.
- Orchestrator treats placeholder simulation as a real simulation engine.
- Runtime output gives direct trade instructions.
- Runtime modifies `portfolio.local.yaml`.
- Runtime stores private amounts, costs, balances, account values, or position amounts.
- Runtime changes CDE logic or Decision Brief strategy logic.
- Runtime claims full Runtime System v0.1 is complete.

## Case 18: Lightweight Execution Kernel v0.1 Runtime Host

Expected output:

1. `runtime/atlas_host.py` can run a daemon-style loop.
2. Host can execute scheduled cycles after startup without a new chat prompt.
3. Scheduler supports:
   - `daily_run()`.
   - `intraday_run()`.
   - `event_trigger(event_type)`.
4. Event trigger supports:
   - `market_open`.
   - `market_close`.
   - `attention_spike`.
   - `volatility_spike`.
   - `user_input_event`.
5. Orchestrator routes:
   - daily -> market summary + portfolio review.
   - intraday -> regime check + attention update.
   - event -> risk evaluation + anomaly detection.
6. LLM router supports at least GPT and Claude provider aliases and falls back safely when API keys
   are missing.
7. SQLite state store persists redacted portfolio snapshot, regime state, attention history,
   latest Decision Brief, and system logs.
8. Web dashboard exposes current portfolio view, latest Decision Brief, regime status, attention
   signals, and system logs.
9. Runtime logs include timestamp, trigger type, modules executed, LLM model used, and Decision
   Brief ID.
10. Runtime output remains non-binding and does not create CDE authority.

Fail conditions:

- Runtime imports or depends on OpenClaw, CrewAI, Conductor, Kafka, Ray, or Kubernetes.
- Runtime executes trades or creates order instructions.
- Runtime modifies `portfolio.local.yaml`.
- Runtime stores private amounts, costs, balances, net worth, or position amounts.
- Runtime bypasses CDE.
- Runtime implements a full backtesting engine or regime prediction model.
- Runtime emits Buy / Sell as Atlas action vocabulary.

## Case 19: Autonomous Runtime v0.2 Event-Driven State Machine

Expected output:

1. `runtime/atlas_daemon.py` provides a launchd-compatible daemon entrypoint.
2. `deployment/atlas_os.plist` includes `RunAtLoad` and `KeepAlive`.
3. `runtime/event_stream.py` supports event queue, listener, prioritization, and append-only
   history.
4. Event stream supports:
   - `market_anomaly`.
   - `attention_spike`.
   - `volume_price_breakout`.
   - `news_narrative_spike`.
   - `portfolio_drawdown`.
5. `runtime/state_machine.py` supports:
   - `NORMAL`.
   - `ATTENTION_EXPANSION`.
   - `RISK_OFF`.
   - `BREAKOUT`.
   - `DISTRIBUTION`.
   - `HIGH_VOLATILITY`.
6. Decision loop reads event stream, updates state machine, runs orchestrator, generates Decision
   Brief, updates state store, and sleeps between cycles.
7. Orchestrator can route by state:
   - `NORMAL` -> standard daily analysis.
   - `ATTENTION_EXPANSION` -> attention + flow inference.
   - `HIGH_VOLATILITY` -> risk reduction + anomaly check.
   - `BREAKOUT` -> candidate evaluation.
   - `DISTRIBUTION` -> portfolio risk scan.
8. Dashboard displays current system state, event stream, latest Decision Brief, read-only
   portfolio snapshot, and attention heat index.
9. LLM provider calls remain isolated to `runtime/llm_router.py`.
10. Runtime output remains non-binding and does not create CDE authority.

Fail conditions:

- Event processing is only mocked through fixed if-statements without a queue / listener.
- Daemon cannot run continuously.
- State transitions are not persisted.
- Runtime modifies `portfolio.local.yaml`.
- Runtime executes trades, integrates with a broker, or emits binding trade instructions.
- Runtime bypasses CDE or creates CDE authority.
- Runtime uses OpenClaw, CrewAI, Conductor, Kafka, Ray, or Kubernetes.

## Case 20: Cognitive Runtime v0.3 Prevents Event State Overwrite

Expected output:

1. Multiple simultaneous events are fused into one market reality vector.
2. Fusion output includes:
   - Stress Level.
   - Attention Pressure.
   - Liquidity Condition.
   - Volatility Regime.
   - Narrative Intensity.
3. Regime Memory maintains weighted history of recent states.
4. Causal inference outputs:
   - Primary Driver.
   - Secondary Driver.
   - Market Pressure Source.
   - Regime Transition Probability.
5. Attention and liquidity are separated into:
   - Attention Index.
   - Liquidity Index.
   - Divergence Score.
6. Crash / high-risk state cannot be overwritten by a later attention spike unless validation
   threshold is met.
7. Same attention event produces different state when memory context differs:
   - after crash memory -> risk state persists.
   - fresh memory -> attention expansion.
8. Decision Brief interface remains unchanged.
9. Runtime host, scheduler, and daemon logic are not modified.

Fail conditions:

- State follows the latest event instead of fused market context.
- Attention spike overwrites crash memory.
- Liquidity stress and attention pressure are conflated.
- Causal inference is missing.
- Regime memory does not persist across cycles.
- Runtime host / scheduler / daemon is modified.
- Trading execution, portfolio auto-rebalance, CDE bypass, deep learning, reinforcement learning,
  or broker integration is introduced.
