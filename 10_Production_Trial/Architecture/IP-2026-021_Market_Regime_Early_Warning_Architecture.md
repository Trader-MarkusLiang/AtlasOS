# IP-2026-021 Architecture — Market Regime Early Warning v0.1

## Status

Proposed Architecture.

Not implemented.

Requires user discussion, Architecture Review, Acceptance Test definition, and explicit approval
before implementation.

## Core Definition

Market Regime Early Warning v0.1 is a lightweight, explainable, non-trading risk-context layer.

It does not predict index points.

It does not produce trade commands.

It does not authorize deployment.

It observes whether public attention, narrative crowding, leadership behavior, market
participation, and price confirmation suggest that the market has moved from healthy attention
momentum into fragile crowding, distribution warning, risk-off, or crash stress.

The module adjusts only:

- market-regime context
- CDE precision status
- Rebalance Authority cap

CDE authorization and user confirmation remain mandatory.

## Why Not Pure Technical Indicators

MA20, MA60, 20D change, and 60D change are useful confirmation tools, but they are often lagging.

They can confirm that a market is already extended or broken, but they may not warn early enough
when attention, media saturation, and narrative crowding are already shifting the risk profile.

Therefore, v0.1 prioritizes leading or semi-leading observations:

- search momentum
- media saturation
- social discussion intensity
- narrative crowding
- evidence-to-narrative deterioration
- leadership fragility
- market participation deterioration

Price structure remains a confirmation layer, not the primary warning source.

## Key Concepts

### Attention Momentum

Attention Momentum describes the phase where rising public attention, search intensity, media
coverage, and social discussion attract incremental capital and reinforce price trends.

Typical signs:

- search heat rises
- media coverage increases
- social discussion expands
- price and volume confirm
- new participants begin to follow the theme

Atlas interpretation:

Attention Momentum can be positive during early and middle stages, but it requires monitoring for
crowding.

### Narrative Crowding

Narrative Crowding describes the later phase where attention remains high but incremental evidence
weakens.

Typical signs:

- "ten-bagger", "faith", "never sell", "all in", "cannot miss", "strongest theme" language increases
- discussion shifts from evidence to slogan
- price is already elevated
- more new participants ask whether they can still get in
- media coverage becomes repetitive or promotional
- broker reports and influencer posts cluster around the same theme

Atlas interpretation:

Narrative Crowding limits CDE precision and may cap Rebalance Authority.

### Attention Exhaustion

Attention Exhaustion describes the danger phase where public attention remains elevated but price
leadership weakens or stops responding.

Typical signs:

- search and social discussion remain high
- media coverage remains intense
- price stalls or fails to make new highs
- volume rises but price no longer advances
- leaders show long upper shadows, failed breakouts, or sharp intraday reversals
- followers begin to underperform

Atlas interpretation:

Attention Exhaustion may trigger Distribution Warning or Risk-Off depending on leadership and
participation confirmation.

### Attention-Price Divergence

Attention-Price Divergence is the key early-warning relationship.

| Attention | Price / Leadership | Interpretation |
|---|---|---|
| Rising | Rising with volume | Attention Momentum |
| Rising fast | Price stalls | Attention Exhaustion |
| Extreme | Leaders break | Distribution Warning |
| Falling | Price remains strong | Possible institutional trend / lower-noise advance |
| Low | Price starts rising | Early discovery candidate |

### Evidence-to-Narrative Ratio

Evidence-to-Narrative Ratio compares factual information quality with narrative intensity.

Evidence includes:

- orders
- revenue
- customer confirmation
- capacity utilization
- margin improvement
- financial results
- backlog
- delivery cycle
- capex confirmation
- industry pricing data

Narrative includes:

- ten-bagger claims
- faith language
- all-in language
- "strongest theme"
- "this time is different"
- "huge space"
- "cannot miss"
- price-target fantasy without evidence

If discussion volume rises but evidence density falls, Atlas should raise a Narrative Crowding
Warning.

## Signal Stack

Market Regime Early Warning v0.1 uses six layers:

1. Narrative / Attention Crowding
2. Market Participation / Breadth
3. Leadership Fragility
4. Portfolio / Candidate Stress
5. Price / Volume Confirmation
6. Data Quality

### 1. Narrative / Attention Crowding

Purpose:

Detect whether a theme is moving from discovery to crowding.

Possible inputs:

- search-index breakout
- search-index percentile
- media article count
- repeated media headlines
- social discussion volume
- influencer concentration
- broker report clustering
- theme keyword frequency
- late-cycle retail language

Key observations:

- `search_heat`: Low / Medium / High / Extreme
- `media_saturation`: Low / Medium / High / Extreme
- `social_crowding`: Low / Medium / High / Extreme
- `evidence_to_narrative_ratio`: Improving / Stable / Deteriorating / Very Weak
- `attention_phase`: Discovery / Attention Momentum / Narrative Crowding / Attention Exhaustion

Important rule:

Attention is not automatically bearish.

Rising attention can attract incremental capital during Attention Momentum.

The warning comes when attention is extreme, evidence quality deteriorates, and price / leadership
stops responding.

### 2. Market Participation / Breadth

Purpose:

Detect whether the theme has broad participation or narrowing leadership.

Possible inputs:

- advancing / declining names
- limit-up / limit-down count
- 20-day new highs / new lows
- number of rising theme names
- sector participation
- turnover concentration

Key observations:

- `breadth_status`: Healthy / Narrowing / Deteriorating / Washout / Data Missing
- `theme_participation`: Broad / Narrowing / Single-leader / Broken

### 3. Leadership Fragility

Purpose:

Detect whether core leaders are still confirming the theme.

Possible inputs:

- leader breakout success / failure
- long upper shadows
- intraday reversal
- failed limit-up / board break
- leader-follower divergence
- strong-stock next-day premium
- high-position stock failure rate

Key observations:

- `leadership_status`: Healthy / Narrowing / Fragile / Breaking / Broken
- `leader_price_action`: Confirming / Stalling / Reversing / Breaking

### 4. Portfolio / Candidate Stress

Purpose:

Personalize market regime risk to the user's portfolio and Atlas candidate pool.

Possible inputs:

- current holdings 5D / 10D stress
- current holdings anomaly status
- candidate-pool severe ratio
- candidate-pool warning ratio
- candidate-pool sharp-pullback ratio
- candidate-pool overextended ratio
- current holding breakdown ratio

Key observations:

- `holding_stress`: Low / Medium / High / Severe
- `candidate_pool_stress`: Low / Medium / High / Severe
- `candidate_pool_overheat_ratio`
- `candidate_pool_warning_ratio`
- `candidate_pool_severe_ratio`

### 5. Price / Volume Confirmation

Purpose:

Confirm whether attention and leadership warnings are visible in price and volume.

This layer is confirmation only.

Possible inputs:

- 5D / 10D price change
- intraday reversal
- volume expansion without price progress
- high-volume stalling
- MA5 / MA10 / MA20
- distance from recent high
- breakdown from recent range

Key observations:

- `price_confirmation`: Confirming / Stalling / Pullback / Breakdown / Data Missing
- `volume_confirmation`: Healthy / Exhaustion / Distribution / Data Missing

### 6. Data Quality

Purpose:

Prevent false confidence when data is incomplete.

Possible inputs:

- missing search data
- missing media counts
- missing breadth data
- missing leadership data
- stale market data
- partial candidate snapshot
- user-observation-only data

Key observations:

- `data_quality`: High / Medium / Low
- `confidence`: High / Medium / Low
- `missing_data`: []

## Data Availability Principle

Atlas must not depend only on hard-to-obtain market microstructure data.

When high-precision market data is unavailable, Atlas may accept structured qualitative observations
from the user and public information channels.

Examples:

- "搜索指数爆发"
- "媒体铺天盖地报道"
- "X / 雪球 / 股吧讨论明显增加"
- "很多人开始喊十倍 / 满仓 / 信仰"
- "券商研报突然密集"
- "但没有看到新的订单 / 财报 / 客户证据"
- "龙头冲高回落"
- "板块里只有少数股票还在涨"

Atlas should convert such observations into explicit, confidence-limited regime signals.

Example output:

```text
search_heat: High
media_saturation: Extreme
social_crowding: Extreme
evidence_to_narrative_ratio: Deteriorating
leadership_fragility: Warning
price_confirmation: Stalling
confidence: Medium
data_source: User Observation + Public Search
```

Structured user observation is valid input, but it must lower or limit confidence when not
independently verified.

## Proposed v0.1 Weighting

| Layer | Weight | Role |
|---|---:|---|
| Narrative / Attention Crowding | 25 | Leading |
| Market Participation / Breadth | 20 | Leading |
| Leadership Fragility | 20 | Semi-leading |
| Portfolio / Candidate Stress | 20 | User-specific risk |
| Price / Volume Confirmation | 10 | Confirmation |
| Data Quality | 5 | Confidence control |

This weighting intentionally reduces dependence on lagging technical indicators.

## Regime Labels

| Regime | Description |
|---|---|
| Early Discovery | Low attention, improving evidence, early price response |
| Attention Momentum | Attention rising, price / volume confirming, participation broadening |
| Extended Risk-On | Attention high, price strong, crowding rising |
| Narrative Crowding | Attention extreme, evidence-to-narrative ratio deteriorating |
| Attention Exhaustion | Attention high but price / leadership stops responding |
| Distribution Warning | Leadership fragile, participation deteriorating, crowding high |
| Risk-Off | Broad weakness, leaders breaking, portfolio / candidate stress high |
| Crash Stress | Liquidity / breadth / leadership all deteriorate sharply |
| Data Insufficient | Not enough reliable data for precise regime |

## Hard Rules

### Hard Rule 1 — Attention Momentum

If search, media, and social attention are rising and price / volume confirms with healthy
participation:

- regime should be at least `Attention Momentum`
- decision impact may remain `Normal`
- do not treat rising attention as automatically bearish

### Hard Rule 2 — Narrative Crowding

If attention is High or Extreme, evidence-to-narrative ratio is deteriorating, and late-cycle retail
language is increasing:

- regime should be at least `Narrative Crowding`
- decision impact should be at least `CDE Precision Limited`

### Hard Rule 3 — Attention Exhaustion

If attention remains High or Extreme but price stalls, volume expands without progress, or
leadership weakens:

- regime should be at least `Attention Exhaustion`
- rebalance authority should be capped

### Hard Rule 4 — Attention-Price Divergence

If search / media / social heat breaks out but price no longer advances or leaders fail:

- regime should be at least `Distribution Warning`

### Hard Rule 5 — Leadership Break

If core theme leaders break while social and media heat remains high:

- regime should be at least `Distribution Warning`
- if breadth also deteriorates, regime may escalate to `Risk-Off`

### Hard Rule 6 — Evidence Deterioration

If discussion volume rises but new evidence quality declines:

- raise `Narrative Crowding Warning`
- do not upgrade CDE authority based on attention alone

### Hard Rule 7 — Data Quality

If most attention and sentiment inputs are user-observed only and not independently verified:

- confidence must not be High

### Hard Rule 8 — No Trade Command

Market Regime Early Warning must never produce Buy / Sell instructions.

It can only affect:

- market-regime context
- CDE precision status
- Rebalance Authority cap
- review requirements

## Proposed Output Schema

```python
{
    "market_regime": "Early Discovery / Attention Momentum / Extended Risk-On / Narrative Crowding / Attention Exhaustion / Distribution Warning / Risk-Off / Crash Stress / Data Insufficient",
    "early_warning_score": 0,
    "signal_stack": {
        "search_heat": "Low / Medium / High / Extreme / Data Missing",
        "media_saturation": "Low / Medium / High / Extreme / Data Missing",
        "social_crowding": "Low / Medium / High / Extreme / Data Missing",
        "evidence_to_narrative_ratio": "Improving / Stable / Deteriorating / Very Weak / Data Missing",
        "breadth_status": "Healthy / Narrowing / Deteriorating / Washout / Data Missing",
        "leadership_status": "Healthy / Narrowing / Fragile / Breaking / Broken / Data Missing",
        "holding_stress": "Low / Medium / High / Severe / Data Missing",
        "candidate_pool_stress": "Low / Medium / High / Severe / Data Missing",
        "price_confirmation": "Confirming / Stalling / Pullback / Breakdown / Data Missing",
        "data_quality": "High / Medium / Low"
    },
    "leading_flags": [],
    "confirming_flags": [],
    "main_drivers": [],
    "missing_data": [],
    "confidence": "High / Medium / Low",
    "decision_impact": "Normal / CDE Precision Limited / Rebalance Capped / Execution Blocked",
    "rebalance_authority_cap": "No Cap / 20-40% / 10-20% / 5-10% / 0-5%",
    "review_required": True
}
```

## Decision Impact Mapping

| Regime | Decision Impact | Rebalance Authority Cap |
|---|---|---|
| Early Discovery | Normal | No extra cap |
| Attention Momentum | Normal / Watch | No extra cap or 20-40%, subject to CDE |
| Extended Risk-On | CDE Precision Limited | 10-20% |
| Narrative Crowding | CDE Precision Limited | 5-10% / 10-20% |
| Attention Exhaustion | Rebalance Capped | 0-5% / 5-10% |
| Distribution Warning | Rebalance Capped | 0-5% / 5-10% |
| Risk-Off | Execution Blocked | 0-5% |
| Crash Stress | Execution Blocked | 0-5% |
| Data Insufficient | CDE Precision Limited | 0-5% / 5-10% |

This mapping is an authority cap, not an action recommendation.

CDE authorization and user confirmation remain mandatory.
