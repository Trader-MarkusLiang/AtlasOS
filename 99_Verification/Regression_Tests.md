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

## Case 21: DSA Adapter v0.4 Preserves Atlas Cognitive Layer

Expected output:

1. `runtime/adapter/dsa_bridge.py` defines and validates the Atlas unified event schema:
   - `type`
   - `timestamp`
   - `source`
   - `intensity`
   - `metadata`
2. DSA-style search / social / sentiment signals map into Atlas runtime events such as
   `attention_spike` or `news_narrative_spike`.
3. DSA-style liquidity / volatility / anomaly signals map into Atlas runtime events such as
   `liquidity_shock`, `volatility_spike`, or `market_anomaly`.
4. EventStream inbox ingestion accepts native Atlas events and DSA-style unified events.
5. Native and DSA-adapted versions of the same event produce consistent Atlas cognitive state.
6. Adapter strips and neutralizes trading / business logic fields such as buy, sell, action,
   strategy, weight, recommendation, target price, and position size.
7. Event Fusion, Regime Memory, Causal Inference, State Controller, and Attention vs Liquidity
   model remain unchanged.
8. DSA data fetch is optional and fails safely when not configured.
9. LiteLLM backend selection is optional and does not replace the default native router.
10. Dashboard exposes infrastructure status without turning Atlas into a DSA dashboard.

Fail conditions:

- Atlas imports DSA stock-picking logic, MA strategy, scoring systems, or single-stock pipeline.
- Adapter accepts buy / sell rules or portfolio action fields.
- Cognitive core files are modified.
- DSA unavailable state causes runtime failure.
- Event schema is not stable.
- Trading execution, CDE bypass, portfolio auto-modification, broker integration, or stock-analysis
  bot behavior is introduced.

## Case 22: Input Abstraction Layer v0.4.1 Decouples EventStream From DSA

Expected output:

1. `runtime/event_stream.py` imports `runtime.adapter.input_router`, not
   `runtime.adapter.dsa_bridge`.
2. `runtime/adapter/input_router.py` is the source-neutral external input entry point.
3. Input Router emits:
   - `type`
   - `timestamp`
   - `source`
   - `intensity`
   - `payload`
4. Illegal fields are stripped recursively:
   - `buy_signal`
   - `sell_signal`
   - `strategy`
   - `alpha_score`
   - `target_weight`
   - `recommendation`
   - MA decision-signal fields.
5. Any input containing illegal fields is downgraded to neutral `market_event` with no regime
   signal intensity.
6. Removing `dsa_bridge.py` does not break DecisionLoop / EventStream cognition for native events.
7. Native and DSA-style versions of the same non-poisoned event produce identical state, memory,
   and causal primary driver.
8. Cognitive modules do not import `runtime.adapter`.
9. Event Fusion, Regime Memory, Causal Inference, State Controller, and Attention vs Liquidity
   model remain unchanged.

Fail conditions:

- EventStream imports `dsa_bridge`.
- Cognitive modules import infrastructure adapters.
- Poisoned fields survive into runtime payload.
- Poisoned fields influence regime state.
- DSA removal breaks native runtime cognition.
- Trading logic, strategy logic, stock picking, CDE bypass, or portfolio automation is introduced.

## Case 23: Causal Intelligence Layer v0.5 Explains Regime Formation

Expected output:

1. `runtime/cognition/causal_intelligence_layer.py` defines a symbolic causal graph with:
   - Attention.
   - Liquidity.
   - Price Momentum.
   - Volatility.
   - Narrative Pressure.
   - Institutional Flow.
   - Retail Flow.
2. Attention is resolved as causal symptom, not direct signal:
   - high-liquidity context -> `liquidity-driven attention`.
   - low-liquidity / stress context -> `panic-driven attention`.
   - narrative-heavy context -> `retail narrative attention`.
   - volume / lower-narrative context -> `institutional repositioning attention`.
3. Flow propagation outputs:
   - Retail Flow Strength.
   - Institutional Flow Strength.
   - Latency from attention to flow.
   - Conversion Efficiency from attention to capital.
   - Volatility Expansion Pressure.
4. Regime emergence output includes formation process, dominant causal drivers, structural tension
   map, regime formation probability, and `not_final_label: true`.
5. Counterfactual removal of Attention reduces retail flow and attention-to-capital conversion.
6. Contradictory signals such as price up, liquidity down, and attention high do not collapse into
   one directional label.
7. DecisionLoop persists CIL fields under `cognition_state.causal`.
8. Event Fusion Engine, Regime Memory implementation, Input Router, and DSA adapter layer are not
   modified.

Fail conditions:

- Attention is treated as Buy / Sell signal.
- Regime output is only a final label without formation reasoning.
- The layer introduces machine learning / deep learning, stochastic simulation, trading execution,
  portfolio automation, CDE bypass, or broker integration.
- CDE formulas or Decision Brief strategy logic are modified.
- `portfolio.local.yaml` is modified.

## Case 36: LLM Provider Runtime UI i18n v1.4 Keeps Cognition Isolated

Expected output:

1. `runtime/llm/provider_registry.py` supports configurable provider entries for:
   - OpenAI.
   - Claude.
   - Ollama.
   - MoreCode / cc switch.
   - ARK Coding.
   - Volcano Coding.
   - Custom proxy.
2. Provider API keys are stored only in local ignored config and masked in UI/API output.
3. `runtime/llm/provider_router.py` selects the active provider, falls back on failure, and returns
   a unified response envelope.
4. `runtime/llm_router.py` delegates native runtime routing to the provider router while preserving
   raw text output for Decision Contract parsing.
5. `/settings` supports multi-provider add/remove, API key input, base URL, model, fallback chain,
   and provider test connection.
6. `/state` exposes provider status metadata for the UI without exposing secrets.
7. Dashboard uses a single central focus card and a reduced right-side intelligence panel.
8. Top bar includes a persistent EN/CN language toggle using `ui/i18n/i18n.py`.
9. Event Fusion, CIL, LMSE, MPCE, MLE, Decision Contract semantics, and runtime cognition
   algorithms remain unchanged.

Fail conditions:

- Any cognitive-core layer is modified for provider/UI behavior.
- Provider key values appear in rendered HTML, state API output, or committed config.
- LLM provider failure crashes runtime routing instead of returning failsafe output.
- UI returns to dense debug-style panels or equal-weight layout.
- EN/CN toggle is missing or not persisted.
- ML / RL, trading logic, prediction behavior, broker integration, portfolio automation, or CDE
  bypass is introduced.
- `portfolio.local.yaml` is modified.

## Case 24: Market World Model v0.6 Simulates Structural Evolution

Expected output:

1. `runtime/cognition/world_model_engine.py` defines `MarketState(t)` with:
   - Attention Field.
   - Liquidity Field.
   - Volatility Field.
   - Narrative Field.
   - Institutional Flow Field.
   - Retail Flow Field.
2. A 3-step simulation produces an evolving trajectory:
   - `t0 -> t1 -> t2 -> t3`.
   - state fields change across time.
   - output is not repeated classification.
3. `attention_to_liquidity()` shows attention does not directly equal flow and depends on:
   - market regime context.
   - liquidity availability.
   - narrative credibility.
   - institutional participation.
4. Same attention spike under high liquidity and low liquidity produces different evolution paths.
5. `simulate_regime_emergence()` outputs:
   - regime pressure map.
   - instability gradients.
   - phase transition likelihood.
   - structural imbalance fields.
   - `regime_is_emergent: true`.
6. `simulate_counterfactual_market()` removes attention spike and produces a different trajectory,
   divergence score, and regime sensitivity index.
7. DecisionLoop persists World Model output under `cognition_state.world_model`.
8. The module remains interpretable and explicitly marks:
   - `simulation_mode: interpretable_deterministic_scenario`.
   - `not_forecast: true`.
   - `no_trade_action: true`.
9. Event Fusion Engine, Regime Memory system, and Causal Intelligence Layer are not modified.

Fail conditions:

- World Model output becomes a price forecast, target, or trading signal.
- State output is only a final regime label.
- Attention is treated as direct capital flow.
- Counterfactual simulation produces the same trajectory.
- ML / deep learning / reinforcement learning, trading execution, portfolio automation, CDE bypass,
  broker integration, or Buy / Sell recommendation is introduced.
- CDE formulas or Decision Brief strategy logic are modified.
- `portfolio.local.yaml` is modified.

## Case 25: Latent Market Structure Engine v0.7 Models Hidden Structure

Expected output:

1. `runtime/cognition/latent_market_structure_engine.py` defines latent regime space:
   - observed variables: attention, liquidity, volatility, narrative, flows.
   - latent variables: structural liquidity pressure, attention persistence field, narrative
     propagation inertia, hidden risk compression, capital rotation tension.
2. Observed variables are treated as projections of latent market structure.
3. `compute_regime_attractors()` outputs multiple attractor basins with:
   - attractor strength.
   - basin depth.
   - transition barrier.
   - structural stability index.
4. Regimes are attractor basins, not labels.
5. Small attention persistence changes do not immediately flip the dominant attractor basin.
6. `map_market_phase_space()` outputs:
   - phase curvature.
   - trajectory drift vector.
   - volatility manifold shape.
   - liquidity gradient field.
7. `attention_field_dynamics()` treats attention as a persistent field with:
   - attention persistence.
   - decay rate.
   - reinforcement loops.
   - cross-asset diffusion.
8. `simulate_structural_evolution()` evolves structure slower than observed variables.
9. `simulate_structural_counterfactual()` modifies hidden risk compression and produces structural
   divergence plus phase-space deformation.
10. DecisionLoop persists LMSE output under `cognition_state.latent_structure`.
11. The module remains interpretable and explicitly marks:
   - `model_mode: interpretable_latent_structure_non_ml`.
   - `not_prediction_engine: true`.
   - `no_trade_action: true`.

Fail conditions:

- Observed spikes directly define regime.
- Regime output is only a label.
- Attention is treated as one-off event signal.
- Small attention changes instantly flip structure.
- Structural counterfactual produces no trajectory divergence.
- ML / deep learning / reinforcement learning, trading execution, portfolio automation, CDE bypass,
  broker integration, prediction engine behavior, or Buy / Sell recommendation is introduced.
- Event Fusion Engine, Regime Memory implementation, or Causal Intelligence Layer is modified.
- CDE formulas or Decision Brief strategy logic are modified.
- `portfolio.local.yaml` is modified.

## Case 26: Market Physics Constraint Engine v0.8 Constrains Market Evolution

Expected output:

1. `runtime/cognition/market_physics_constraint_engine.py` defines:
   - liquidity conservation law.
   - attention conservation soft form.
   - flow continuity law.
2. Liquidity spike without origin trace violates conservation.
3. Liquidity spike with origin trace passes conservation.
4. `compute_market_entropy()` outputs:
   - narrative entropy.
   - volatility entropy.
   - liquidity entropy.
   - total system entropy.
5. High entropy reduces stability score and increases regime fragility index.
6. `check_structural_invariants()` checks:
   - regime stability bounds.
   - liquidity redistribution bounds.
   - attention persistence limits.
   - flow conservation consistency.
7. Invariant violations mark unstable regime transition zone and do not force a regime label.
8. `formulate_dynamic_system()` represents:
   - `dS/dt = F(S, constraints, latent_structure)`.
   - constrained and unconstrained evolution diverge structurally.
   - constraints modify trajectory but do not override state directly.
9. Constraint-driven regime emergence outputs:
   - constraint tension map.
   - stability boundary proximity.
   - phase transition likelihood.
   - structural collapse risk index.
10. DecisionLoop persists MPCE output under `cognition_state.physics_constraints`.
11. The module remains interpretable and explicitly marks:
   - `model_mode: interpretable_constraint_system_non_ml`.
   - `not_forecasting_engine: true`.
   - `no_trade_action: true`.

Fail conditions:

- Liquidity appears without source attribution.
- Attention expands without bound over short horizon.
- Flow jumps without intermediate structural state.
- Invariant violation forces a regime label.
- Regime emergence is based on event threshold classification.
- MPCE becomes forecasting engine or trading signal.
- ML / deep learning / reinforcement learning, trading execution, portfolio automation, CDE bypass,
  broker integration, or Buy / Sell recommendation is introduced.
- Event Fusion Engine, Regime Memory, CIL, or LMSE is modified.
- CDE formulas or Decision Brief strategy logic are modified.
- `portfolio.local.yaml` is modified.

## Case 27: Market Law Emergence Engine v0.9 Evolves Constraints Interpretably

Expected output:

1. `runtime/cognition/market_law_emergence_engine.py` defines `discover_market_laws()`.
2. Repeated structural patterns generate emergent law candidates with:
   - law type.
   - stability score.
   - recurrence frequency.
   - violation rate.
   - regime dependency.
3. At least one emergent law candidate has stability above threshold.
4. `evolve_constraints()` outputs:
   - updated constraint graph.
   - constraint stability weights.
   - evolutionary drift map.
5. Constraint weights change over time and at least one constraint evolves.
6. Stable constraints can strengthen, unstable constraints can decay, and contradictory constraints
   can split into sub-laws.
7. `regime_conditioned_laws()` shows the same law behaves differently across regimes.
8. `simulate_meta_dynamics()` outputs:
   - law birth.
   - law decay.
   - law mutation.
   - law drift velocity.
   - structural mutation rate.
   - self-organization index.
9. `check_law_consistency()` preserves contradictions as multi-law coexistence zones and does not
   force resolution.
10. DecisionLoop persists MLE output under `cognition_state.market_laws`.
11. The module remains interpretable and explicitly marks:
   - `model_mode: interpretable_market_law_emergence_non_ml`.
   - `not_prediction_engine: true`.
   - `no_trade_action: true`.

Fail conditions:

- Constraints remain static.
- Repeated structure fails to generate law candidates.
- Contradictory laws collapse into one forced rule.
- Regime-dependent variants are identical.
- MLE becomes prediction engine or trading signal.
- ML / deep learning / reinforcement learning, black-box optimization, trading execution,
  portfolio automation, CDE bypass, broker integration, or Buy / Sell recommendation is introduced.
- Event Fusion Engine or Regime Memory is modified.
- CDE formulas or Decision Brief strategy logic are modified.
- `portfolio.local.yaml` is modified.

## Case 28: Unified Market Intelligence Core v1.0 Closes the Cognition Loop

Expected output:

1. `runtime/cognition/unified_market_intelligence_core.py` defines `build_unified_market_state()`.
2. UnifiedMarketState includes:
   - event state.
   - causal state.
   - latent structure state.
   - physics constraint state.
   - emergent law state.
3. The unified state marks:
   - `unified_state_space: true`.
   - `isolated_interpretation_layers: false`.
4. `market_system_feedback_loop()` shows:
   - market to Atlas observation.
   - Atlas observation to interpretation.
   - interpretation to state update.
   - state update to next market feedback probe.
5. The feedback loop is closed and not a one-way pipeline.
6. `self_referential_causality()` shows prior Atlas interpretation can affect current reasoning
   and increases recursion depth across cycles.
7. `co_evolution_dynamics()` outputs:
   - co-evolution trajectory.
   - system adaptation rate.
   - market sensitivity to system state.
   - mutual influence loop.
8. `interpret_unified_state()` outputs:
   - dominant regime structure.
   - causal-latent alignment.
   - physics constraint pressure.
   - emergent law consistency.
9. `system_self_adaptation()` adapts only internal interpretation weights and explicitly does not
   adapt trading or portfolio weights.
10. DecisionLoop persists UMIS output under `cognition_state.unified_intelligence`.
11. The module remains interpretable and explicitly marks:
   - `model_mode: interpretable_unified_market_intelligence_non_ml`.
   - `not_prediction_engine: true`.
   - `no_trade_action: true`.
   - `no_signal_generator: true`.

Fail conditions:

- Unified state is missing one of the required layer projections.
- Interpretation is generated from isolated modules rather than unified state.
- Previous system state has no effect on the next reasoning cycle.
- The loop remains a one-way pipeline.
- UMIS becomes a prediction engine, trading signal, or CDE authority layer.
- ML / deep learning / reinforcement learning, black-box prediction, trading execution, portfolio
  automation, CDE bypass, broker integration, or Buy / Sell recommendation is introduced.
- Event Fusion Engine logic or Regime Memory architecture is modified.
- CDE formulas or Decision Brief strategy logic are modified.
- `portfolio.local.yaml` is modified.

## Case 29: Bidirectional Perception Loop v1.2 Deforms Input Representation

Expected output:

1. `runtime/cognition/bidirectional_perception_engine.py` defines:
   - `compute_perception_weight_field()`.
   - `deform_input_distribution()`.
   - `perception_feedback_loop()`.
   - `attention_influenced_observation()`.
   - `generate_biased_market_view()`.
   - `measure_system_market_coupling()`.
2. Perception weight field outputs:
   - attention bias map.
   - volatility sensitivity modifier.
   - narrative amplification factor.
   - liquidity perception shift.
3. EventStream applies BMPL before appending events to the queue.
4. The same raw event receives different internal priority under high-attention vs low-attention
   system state.
5. The same raw event produces different Fusion attention representation after BMPL.
6. Attention-influenced observation changes:
   - detection probability.
   - observation granularity.
   - anomaly sensitivity.
7. Coupling metrics are non-zero:
   - perception influence strength.
   - input deformation ratio.
   - feedback loop intensity.
8. Stability guardrails remain active:
   - event type is preserved.
   - priority delta is bounded.
   - heartbeat is not deformed.
   - interpretability is preserved.

Fail conditions:

- Same event has identical priority under high-attention and low-attention system states.
- BMPL requires Event Fusion core logic changes.
- BMPL mutates trading, portfolio, CDE, Buy / Sell, or broker behavior.
- BMPL becomes a prediction engine or signal generator.
- CIL, LMSE, MPCE, or MLE logic is modified.
- ML / deep learning / reinforcement learning is introduced.
- `portfolio.local.yaml` is modified.

## Case 30: Explanation Self-Correction v0.6 Uses Explanation Error As Bounded Feedback

Expected output:

1. `runtime/cognition/explanation_error_engine.py` defines `compute_explanation_error()`.
2. `runtime/cognition/causal_self_correction_engine.py` defines
   `apply_causal_self_correction()`.
3. `runtime/cognition/regime_explanation_alignment.py` defines
   `align_regime_explanation()`.
4. A wrong or incomplete explanation produces:
   - non-zero `explanation_error_score`.
   - missing causal links.
   - overestimated factors.
   - underestimated factors.
5. High-trust explanation mismatch produces bounded causal edge correction.
6. Low trust freezes causal self-correction and produces no edge updates.
7. Corrections use known causal edges only:
   - no node creation.
   - no graph topology rewrite.
   - no full causal graph replacement.
8. Structural drift can persist explanation feedback as bounded reversible edge drift.
9. Structural evolution can accept explanation feedback only through existing trust-field gating.
10. DecisionLoop persists:
   - `cognition_state.explanation_error`.
   - `cognition_state.causal_self_correction`.
   - `cognition_state.regime_explanation_alignment`.
   - `structural_coevolution_state.explanation_feedback`.

Fail conditions:

- Explanation feedback modifies Event Fusion core logic.
- LMSE, MPCE, or MLE definitions are changed.
- Decision Contract structure is changed.
- Correction creates new graph nodes or rewrites topology.
- Low-trust correction changes structural state.
- The layer introduces ML / RL training, trading logic, prediction logic, broker integration,
  portfolio automation, CDE bypass, or Buy / Sell recommendations.
- `portfolio.local.yaml` is modified.

## Case 31: Causal Self-Discovery v0.7 Treats Explanations As Hypotheses

Expected output:

1. `runtime/cognition/causal_hypothesis_engine.py` defines `generate_causal_hypotheses()`.
2. Each event window generates at least three causal hypotheses.
3. Hypotheses are structurally different, not just different edge weights.
4. Hypotheses are marked as competing explanations and not truth claims.
5. `runtime/cognition/hypothesis_scoring_engine.py` defines `score_causal_hypotheses()`.
6. Hypothesis scoring emits:
   - best hypothesis id.
   - ranked hypotheses.
   - score distribution.
7. `runtime/cognition/causal_structure_selector.py` defines
   `select_active_causal_structure()`.
8. The selector chooses one active causal structure and retains shadow hypotheses.
9. Selection is non-permanent and can switch under regime shift, new evidence, or trust drift.
10. Low trust reduces switching frequency.
11. One-tick oscillation is blocked by stability rules.
12. `runtime/cognition/hypothesis_memory.py` persists:
   - past hypotheses.
   - why selected.
   - why rejected.
   - regime context at selection time.
13. `runtime/cognition/explanation_error_engine.py` supports multi-explanation competition metrics:
   - explanation divergence index.
   - causal conflict score.
   - model instability pressure.
14. DecisionLoop persists:
   - `cognition_state.causal_hypotheses`.
   - `cognition_state.hypothesis_scoring`.
   - `cognition_state.active_causal_structure`.
   - `cognition_state.multi_explanation_competition`.
   - `causal_hypothesis_memory`.

Fail conditions:

- The system collapses competing explanations into one truth model.
- Hypotheses differ only by numeric weights and not structure.
- Active causal structure switches every tick without stability gating.
- Low trust increases or forces switching.
- Event Fusion core logic is modified.
- LMSE, MPCE, MLE definitions are changed.
- Decision Contract schema is changed.
- The layer introduces ML / DL / RL training, trading logic, prediction logic, broker integration,
  portfolio automation, CDE bypass, or Buy / Sell recommendations.
- `portfolio.local.yaml` is modified.

## Case 32: Roadmap Dev Registry UI Tracks Lifecycle Without Runtime Mutation

Expected output:

1. `docs/atlas_roadmap.json` exists and is valid machine-readable JSON.
2. Roadmap JSON includes:
   - `version`.
   - `layers`.
   - `current_stage`.
   - `next_stage`.
3. Roadmap layers include:
   - v0.1 Runtime Daemon as completed.
   - v0.7 Causal Self-Discovery as completed.
   - v0.8 Causal Interaction Layer as planned.
4. `GET /roadmap` returns:
   - current version.
   - completed layers.
   - active stage.
   - next planned stage.
5. `ui/pages/dev_registry.py` renders:
   - version timeline.
   - module evolution log.
   - validation results panel.
   - current system state.
   - architecture evolution graph.
6. Dashboard navigation shows:
   - System.
   - Chat.
   - Inspector.
   - Graph.
   - Roadmap.
   - Dev Registry.
7. Dev Registry and Roadmap are read-only and do not mutate cognition or runtime state.

Fail conditions:

- Roadmap is not machine-readable.
- `/roadmap` returns HTML instead of JSON.
- Dev Registry fails to render v0.1 through v0.8 history.
- UI imports cognitive modules directly.
- Cognitive core, decision logic, trust system, or runtime daemon execution semantics are changed.
- ML / RL, trading logic, prediction behavior, broker integration, portfolio automation, or CDE
  bypass is introduced.
- `portfolio.local.yaml` is modified.

## Case 33: UI Cognitive Onboarding v1.2 Explains Runtime State

Expected output:

1. `ui/components/onboarding_overlay.py` renders first-load onboarding.
2. Onboarding modal includes:
   - `Welcome to Atlas OS Runtime Cognitive System`.
   - Start System Tour button.
   - View Roadmap button.
   - Enter Dashboard button.
3. Onboarding explains:
   - real-time cognitive loop.
   - tick-based event processing.
   - probabilistic outputs.
   - `UNKNOWN` means insufficient signal.
   - `NEUTRAL` means no strong regime signal.
4. First-load boot sequence shows:
   - Booting Atlas OS Cognitive Runtime.
   - Initializing Event Stream.
   - Loading Cognitive Layers.
   - System Ready.
5. `ui/components/top_bar.py` includes persistent help links:
   - Roadmap.
   - Dev Registry.
   - System State Guide.
6. `ui/pages/system_guide.py` renders:
   - What is Atlas OS.
   - State Meaning.
   - Decision Flow.
   - What user should look at.
7. Dashboard contains a visible System Navigation card above the main panels.
8. Raw `UNKNOWN` UI values are replaced with:
   - `Waiting for sufficient cognitive signal...`
   - tooltip: `System has not yet converged on this metric.`
9. The change is UI-only and does not import cognitive modules directly.

Fail conditions:

- Onboarding does not appear on first load / refresh.
- Roadmap or Dev Registry is more than one click away.
- System Guide route is missing.
- Raw `UNKNOWN` appears without explanation.
- Runtime, cognition, event processing, decision, trust, or backend execution semantics are changed.
- ML / RL, trading logic, prediction behavior, broker integration, portfolio automation, or CDE
  bypass is introduced.
- `portfolio.local.yaml` is modified.

## Case 34: UI Control Plane v1.3 Uses Production-Grade Control Layout

Expected output:

1. `ui/components/sidebar.py` renders left sidebar sections:
   - System Status.
   - Model Configuration.
   - API Keys.
   - Runtime Settings.
   - Asset Configuration.
   - LLM Providers.
   - Logs.
   - Roadmap.
2. Dashboard uses four control-plane zones:
   - left sidebar,
   - center workspace,
   - right inspector,
   - bottom execution timeline.
3. Center workspace includes mode switcher:
   - Chat Mode.
   - System Mode.
   - Workflow Mode.
   - Architecture Mode.
4. Right inspector remains visible and cleaner than raw debug output.
5. Bottom timeline reads:
   - Event -> Cognition -> Decision -> Explanation -> Feedback.
6. `ui/pages/settings.py` exposes:
   - LLM provider, API key, base URL, model.
   - tick interval, runtime mode, trust threshold, hypothesis switching sensitivity.
   - portfolio JSON, asset list editor, optional weights.
7. Settings save writes local UI-only config to `runtime/config/user_config.json`.
8. `ui/components/workflow_graph.py` renders clickable nodes:
   - Event Stream.
   - Cognitive Pipeline.
   - Causal Layer.
   - World Model.
   - Hypothesis Engine.
   - Decision Contract.
   - LLM Router.
   - Feedback Loop.
9. Routes exist:
   - `/dashboard`.
   - `/settings`.
   - `/workflow`.
   - `/system-guide`.
10. Runtime, cognition, event stream, decision, trust, and causal engine semantics remain unchanged.

Fail conditions:

- UI remains a raw debug panel.
- Settings page cannot save local config.
- API key is echoed unmasked in save response.
- Asset config implies trading or execution.
- Workflow graph is missing or static text only.
- Navigation is not sidebar-based.
- Runtime / cognition / event processing / decision / trust / backend execution semantics are
  changed.
- Heavy frontend framework is introduced.
- ML / RL, trading logic, prediction behavior, broker integration, portfolio automation, or CDE
  bypass is introduced.
- `portfolio.local.yaml` is modified.

## Case 36: Workflow and Roadmap Pages Are Product-Grade UI Surfaces

Expected output:

1. `/workflow` renders a polished Atlas Workflow page, not a generic HTML shell.
2. Workflow page includes:
   - Guided Execution Path.
   - active stage detail.
   - stage cards.
   - boundary / output / guardrail facts.
   - read-only UI / structured output / bounded feedback principles.
3. `/roadmap` renders a polished Atlas Roadmap page by default in a browser.
4. Roadmap page includes:
   - Current Stage hero.
   - Release Progress summary.
   - Version Timeline cards.
   - Architecture Evolution section.
5. Roadmap JSON remains available through:
   - `/roadmap?format=json`.
   - `/roadmap.json`.
6. Workflow and Roadmap pages follow the Atlas OS v2.0 visual system.
7. UI pages do not import cognitive modules.

Fail conditions:

- `/roadmap` displays raw JSON by default in the browser.
- `/workflow` displays plain links or an unstyled block.
- Roadmap machine-readable access is removed.
- Runtime / cognition / event processing / decision / trust / backend execution semantics are
  changed.
- Heavy frontend framework is introduced.
- ML / RL, trading logic, prediction behavior, broker integration, portfolio automation, or CDE
  bypass is introduced.
- `portfolio.local.yaml` is modified.

## Case 35: UI Cognitive Control Center v2.0 Uses Single-Focus Product Layout

Expected output:

1. `ui/components/control_panel.py` renders the left control/config panel with:
   - System Control.
   - Start / Stop.
   - Tick interval.
   - Simulation mode.
   - Model Config.
   - LLM provider, API key, base URL, model.
   - Asset Config JSON editor.
2. Dashboard uses the v2.0 three-zone cognitive-control layout:
   - left control panel,
   - center primary focus workspace,
   - right intelligence panel,
   - minimal bottom flow timeline.
3. Center default System Mode shows only:
   - Current Regime.
   - Trust Score.
   - Active Decision.
   - minimal System Status.
4. Center mode switch includes only:
   - Chat Mode.
   - System Mode.
   - Workflow Mode.
5. Top navigation is simplified to:
   - Dashboard.
   - Workflow.
   - Roadmap.
   - Settings.
6. `ui/components/intelligence_panel.py` shows:
   - Reasoning Summary.
   - top causal factors.
   - Hypothesis State.
   - System Health.
7. `ui/components/execution_timeline.py` shows a compressed Event -> Decision -> Feedback chain.
8. Empty states use:
   - `Waiting for cognitive signal`.
   - `Insufficient system context`.
   - `System initializing reasoning layer`.
9. `ui/components/workflow_graph.py` renders a minimalist active path with faded inactive nodes and
   a node explanation panel.
10. Runtime, cognition, event stream, decision, trust, and causal engine semantics remain unchanged.

Fail conditions:

- UI still presents multiple equal-weight debug panels.
- Center workspace is not the dominant visual focus.
- Redundant navigation or mode toggles remain.
- Settings page removes LLM / asset / runtime config fields.
- Workflow graph is non-clickable or lacks explanation context.
- Runtime / cognition / event processing / decision / trust / backend execution semantics are
  changed.
- Heavy frontend framework is introduced.
- ML / RL, trading logic, prediction behavior, broker integration, portfolio automation, or CDE
  bypass is introduced.
- `portfolio.local.yaml` is modified.
