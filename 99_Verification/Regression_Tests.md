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
- `泰金新能` or `DRAM ETF` is force-mapped without verification.
- Smoke test mixes A-share, Hong Kong, and US / ETF results without labels.
- Missing valuation fields fail the whole test.
- Private portfolio amounts are stored.
- CDE / Decision Brief strategy logic is modified.
