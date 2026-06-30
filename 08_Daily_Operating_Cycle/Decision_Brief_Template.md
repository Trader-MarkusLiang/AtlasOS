# Decision Brief Template

```text
==================================================
Atlas Decision Brief
Date: YYYY-MM-DD
==================================================

【Executive Conclusion】
一句话告诉用户今天最大的结论。

Example:
Memory Thesis 持续强化。暂无调仓必要。

==================================================
【Today's Action】
Trade: YES / NO
Portfolio Action: Build / Hold / Reduce / Exit

If No Action:
一句话说明原因。

==================================================
【World Model Status】
Atlas World:
Memory: █████████░ Stable
Optical Interconnect: ███████░░░ Strengthening
Power: ██████░░░░ Developing
Robotics: █████░░░░░ Early Stage

This is World Model health, not a stock score or price forecast.

==================================================
【Current Portfolio Context】
If portfolio context exists, include:
Portfolio Source:
Portfolio Last Updated:
Account:
Deployment:
Cash / Dry Powder:
Existing Thesis Exposure:
Portfolio Consistency:
Exposure Sum:
Decision Limitation:

Validate for each account:
Total Exposure + Cash = 100%

If portfolio context is missing or stale:
Portfolio Context Missing or Stale — Decision Limited

If portfolio context is stale, inconsistent, conflicting, or cannot be verified:
Portfolio Context Stale / Inconsistent — Decision Limited

If multiple portfolio versions exist and the latest valid source cannot be determined:
Portfolio Context Conflict — Decision Limited

When limited:
• Do not give strong portfolio action.
• Do not calculate precise CDE authority.
• Use conservative Hold / Observe only.
• Ask user to confirm portfolio if needed.

==================================================
【Existing Portfolio Mapping】
For each relevant current holding:

Holding:
• Exposure: Direct / Indirect / None / Unknown
• Impact:
• Action: Research / Observe / Build / Accumulate / Hold / Reduce / Exit
• Evidence Status: Verified / Unverified / Unknown

Cash / Dry Powder:
• Deployment implication:
• CDE authority impact:

Research candidates must be separated from current holdings.

==================================================
【Market Data Status】
Include when the output depends on current price, daily change, K-line / technical status, volume /
turnover, market confirmation, valuation / expectation risk, price dislocation, rebalance timing,
intraday execution, candidate ranking with market confirmation, or CDE authority affected by price
or market movement.

Before filling market-sensitive fields, attempt to retrieve latest available market data from the
local environment or web-search fallback.

If market data cannot be retrieved:
Market Data Missing or Unavailable — Decision Limited

If no provider is available:
Market Data Provider Missing — Configure data source

If quick rebalance or intraday execution is requested and market data is unavailable:
Fast Rebalance Decision Limited — Market Data Required

| Scope | Status | Source | Timestamp | Limitation |
|---|---|---|---|---|
| Current Holdings | Available / Partial / Unavailable | source name | time | limitation |
| Candidate Pool | Available / Partial / Unavailable | source name | time | limitation |
| Valuation | Available / Partial / Unavailable | source name | time | limitation |
| Technical / K-line | Available / Partial / Unavailable | source name | time | limitation |

For each current holding and each Top candidate when material, attempt to collect:
• Code / ticker
• Latest price
• Price timestamp
• Daily change %
• Volume / turnover if available
• 5-day change %
• 20-day change %
• 60-day change %
• Distance from 20-day moving average if available
• Distance from 60-day moving average if available
• Market cap if available
• PE / PB if available
• Data source
• Data freshness

If some fields are unavailable, mark them individually as Data Missing.

Do not make strong claims about K-line structure, market confirmation, valuation level, price
dislocation, intraday execution window, or precise deployment authority without market data.

==================================================
【Strategic Candidate Dashboard v0.1】
Optional. Include only when the user asks about candidate stocks, beneficiaries, industry-chain
opportunities, supplier overlap, rankings, watchlists, strategic opportunities, upstream /
downstream mapping, capital market confirmation, K-line / technical position, industry cycle
position, waiting for entry points, or which names deserve deeper research.

Strategic Summary:
3-5 concise sentences:
• What opportunity is being evaluated.
• Which industry-chain layer matters most.
• Whether this is early-cycle, mid-cycle, late-cycle, or crowded.
• Whether current portfolio already has exposure.
• Whether this is research-only or potentially actionable later.

Current holdings must be included first when portfolio context exists.
If portfolio context is missing or stale:
Portfolio Context Missing or Stale — Candidate Dashboard Limited

Research Priority Is Not Trading Authority.
Strategic Candidate Score answers research priority.
CDE Deployment Score answers whether capital deployment is allowed today.
S Tier does not mean Buy. Candidate ranking is not a trading action.

Candidate Identity Validation:
For every candidate extracted from image, screenshot, OCR, social media post, or unstructured text,
validate:
• Ticker / Code
• Chinese Name
• Category
• Source Mention
• Identity Status: Validated / Needs Validation / Mismatch / Data Missing

If code and name do not match:
Candidate Identity Mismatch — Needs Validation

Candidate Table:
| Code | Candidate | Identity Status | Source Category | Type | Exposure | Thesis Fit | Cycle | Evidence | Market Confirmation | Valuation Risk | Technical Status | Portfolio Fit | Trigger | Score | Tier | Atlas Stance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|
| ... | ... | Validated / Needs Validation / Mismatch / Data Missing | ... | Existing Holding / New Candidate / Sector / Chain / Invalid | Direct / Indirect / None / Unknown | ... | Early / Mid / Late / Top Risk / Re-acceleration / Structural / Pure Cyclical | Known / Partially Verified / Unverified / Data Missing | Confirmed / Partially Confirmed / Not Confirmed / Overcrowded / Broken / Data Missing | Underpriced / Reasonably priced / Fully priced / Overpriced / Bubble risk / Data Missing | Breakout / Pullback to Support / Uptrend Continuation / Overextended / Distribution Risk / Breakdown / Data Missing | Complements / Duplicates / Concentration risk / Replacement / Irrelevant | ... | __ / N/A | S / A / B / C / Reject / N/A | Hold / Verify / Research / Watch / Wait for Pullback / Avoid / Replace Candidate / Needs Validation / Data Missing |

Strategic Candidate Score:
Thesis Fit: __/20
Industry Cycle Position: __/15
Evidence Quality: __/15
Capital Market Confirmation: __/15
Valuation / Expectation Risk: __/10
Technical / K-line Structure: __/10
Portfolio Fit: __/10
Trigger Readiness: __/5

Tiering:
85-100: S — Strategic priority research candidate.
75-84: A — Strong research candidate; wait for trigger.
65-74: B — Valid watchlist candidate.
50-64: C — Low priority / needs more proof.
<50: Reject / Ignore — Not enough strategic value.

Data Discipline:
Do not invent stock price, PE / PB, market cap, K-line status, volume breakout, valuation level,
customer order, or margin change. If unavailable, write Data Missing or Needs Verification.

Market Data Discipline:
If Market Confirmation, Valuation Risk, Technical Status, or Price Dislocation is included, Market
Data Fetch Gate must run first.
When market data is available, fill Market Confirmation, Valuation Risk, and Technical Status from
the retrieved data.
When unavailable, output Data Missing / Needs Market Data, and mark Decision Limited if material.
Do not rank candidates as S Tier solely from industry logic if market data is missing. The maximum
tier should usually be A unless evidence quality is exceptionally high.

Top Candidate Score Explanation:
Explain only Top 3 candidates or candidates directly related to current holdings.

Format:
Candidate — Score / Tier
• Thesis Fit:
• Evidence Quality:
• Portfolio Fit:
• Data Missing:
• Main Trigger:

==================================================
【Capital Deployment Dashboard】
Deployment Lifecycle:
Observe / Pilot Deployment / Initial Deployment / Scaling / Maximum Opportunity / Capital Preservation

Deployment Score:
__/100

Score Composition:
World Model Stability: __/25
Evidence Quality: __/20
Price Dislocation: __/20 or CDE Precision Limited
Portfolio Exposure: __/15
Dry Powder: __/10
Market Risk: __/10 or CDE Precision Limited

Score Reason:
• ...

Today’s Authority:
__%

Derived From:
Deployment Score: __
Deployment Lifecycle: ...
Dry Powder: __%
Execution Risk: Low / Medium / High

Authority Reason:
一句话说明今日权限为什么是这个比例。

If market data is missing:
CDE Precision Limited
Do not calculate precise authority.
Do not include precise Price Dislocation, Market Risk, Execution Risk, or Technical Confirmation.

Executed Today:
Remaining Dry Powder:
Next Lifecycle Stage:
Unlock Conditions:
□ World Model unchanged or strengthening
□ No fundamental deterioration
□ Portfolio exposure below threshold
□ Dry Powder remains above required reserve

Authority is the maximum additional capital allowed today.
It is not a mandatory action.

==================================================
【Portfolio Impact】
Tiger:
• Thesis 是否变化:
• 是否需要调整:

China:
• Thesis 是否变化:
• 是否需要调整:

Do not repeat allocation percentages in the default brief.

==================================================
【Today's New Risks】
No New Risk Today

or:
• 新增风险:
• 为什么今天新增:

Do not repeat historical risks.

==================================================
【Waiting Triggers】
□ Observable trigger
□ Observable trigger
□ Observable trigger

Triggers must be observable.

Examples:
□ DRAM ASP 连续两周下跌
□ HBM Lead Time 缩短
□ Cloud CapEx 下修
□ 三星 Guidance 下调

Do not use vague triggers.

==================================================
【World Model Delta】
No World Model Change Today

or:
• Domain:
• Changed Node:
• Weight:
• Confidence:
• Reason:
• Evidence:
• Counter Evidence:

World Model Delta describes how Atlas's understanding of the AI world changed.
It must not show Repository, Pattern Merge, or news repetition.

==================================================
【Bias Warning】
Today's Biggest Mistake:
...

Examples:
不要因为价格下跌，误判 Thesis 已结束。
不要因为一条 X 消息，改变长期仓位。

==================================================
【Decision Confidence】
Decision Confidence: High / Medium / Low

Confidence means evidence completeness.
It is not a probability forecast of price direction.
==================================================
```

Keep the brief within one screen when possible.

Default Decision Brief must answer:

1. Do I need to act?
2. Has my thesis changed?
3. What should I watch next?

If these are answered, stop. Do not continue into internal workflow.
