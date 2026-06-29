# Decision State Machine

Decision Engine is the Atlas operating mechanism that moves a market item from signal intake to
archive.

It does not replace Atlas Principles, Seven Layer Reasoning, Trading Discipline, Trading OS,
Living Database, or Portfolio Rules. It only defines the state flow between them.

## State Flow

```text
Market Signal
 ↓
Signal Classification
 ↓
Evidence Collection
 ↓
Seven Layer Reasoning
 ↓
Confidence Scoring
 ↓
Research Conclusion
 ↓
Trading Decision
 ↓
Portfolio Action
 ↓
Execution Review
 ↓
Knowledge Update
 ↓
Archive
```

## States

| State | Purpose | Input | Output | Entry Condition | Exit Condition | Owner |
|---|---|---|---|---|---|---|
| Market Signal | Capture a market item before interpretation. | News, filing, earnings, chart, opinion, channel check, price action, or user note. | Raw signal record. | A new item may affect Atlas facts, bottlenecks, ROI, capital flow, risk, or trading. | Source, date, affected company/theme, and initial uncertainty are recorded. | Research |
| Signal Classification | Decide what kind of item entered Atlas. | Raw signal record. | Classification: Fact / Signal / Evidence / Risk / Price Action / Noise. | Market Signal exists. | Classification and affected module are identified, or item is rejected as Noise. | Research |
| Evidence Collection | Separate supported evidence from unsupported claims. | Classified signal. | Evidence packet with source, confidence, missing fields, and `Unknown` / `Unverified` marks. | Signal is not rejected as Noise. | Evidence quality is Low / Medium / High and missing data is explicit. | Research |
| Seven Layer Reasoning | Run the existing Atlas reasoning chain. | Evidence packet. | Layer-by-layer read from Fact to Trading. | Evidence packet has enough information to reason, or missing evidence is marked. | Changed layer, unchanged layer, or insufficient evidence is stated. | Research |
| Confidence Scoring | Convert reasoning strength into decision confidence. | Seven-layer read, evidence quality, counter argument, and risk context. | Confidence: Low / Medium / High / Very High, with reason. | Seven Layer Reasoning completed. | Confidence score and confidence blocker are recorded. | Research |
| Research Conclusion | Decide the research result before trading. | Confidence score and reasoning output. | Research conclusion: Reject / Observe / Research more / Candidate action. | Confidence score exists. | Conclusion includes trigger, counter argument, and required confirmation. | Research |
| Trading Decision | Translate research conclusion into Trading OS decision fields. | Research conclusion. | Trading Decision Table entry or Observe / Watch default. | Research conclusion suggests a possible action or continued observation. | Action, Confidence, Logic Chain, Evidence, Risk / Reward, Trigger, Counter Argument, and Review Plan are complete. | Trading OS |
| Portfolio Action | Translate a valid trading decision into capital behavior. | Completed Trading Decision Table entry. | Portfolio action: Research / Observe / Build / Accumulate / Hold / Reduce / Exit. | Trading Decision passes all gates. | Position state, source of funds, size implication, and portfolio risk are reviewed. | Portfolio |
| Execution Review | Review the action or non-action after outcome evidence appears. | Portfolio action, execution record, or deliberate no-action decision. | Review record with thesis, reality, right/wrong, unexpected, and lessons. | Action was executed, rejected, or held through a review trigger. | Lessons and database update needs are recorded. | Portfolio |
| Knowledge Update | Feed validated learning back into Atlas knowledge assets. | Execution Review and updated evidence. | Suggested or completed updates to database, cases, current state, or verification notes. | Review identifies durable learning or changed facts. | Update target is recorded, or no update is needed. | Repository |
| Archive | Close the decision loop while preserving traceability. | Completed decision packet. | Archived decision record or session note. | Knowledge update is complete or explicitly unnecessary. | Resume path and review date are clear. | Repository |

## State Rule

A state can only move forward when its exit condition is met. If the exit condition is not met,
the decision remains in the current state or falls back to Observe / Research more.

## Presentation Layer

Decision Engine internals remain unchanged.

Internally, Atlas still runs:

```text
Signal
 ↓
Evidence
 ↓
Reasoning
 ↓
Knowledge
 ↓
Repository
```

Externally, the Presentation Layer converts the current result into Decision Brief by default.

Do not expose internal state, Seven Layer Reasoning, knowledge proposals, repository workflow, audit,
or Git workflow unless the user asks for the corresponding expanded view.
