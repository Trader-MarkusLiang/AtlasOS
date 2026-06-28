# Daily Update Workflow

Daily Update Workflow defines the standard daily operating sequence.

## Steps

### Step 1: Receive User Information

Accept market, industry, company, portfolio, risk, trading, or repository information in rough form.

### Step 2: Classify Input

Classify each item as one of:

- Signal
- Portfolio
- Risk
- Question
- Repository

If classification is unclear, mark `Unknown` and route to Research.

### Step 3: Enter Decision Engine State

Assign each item to a Decision Engine state:

- Market Signal
- Signal Classification
- Evidence Collection
- Seven Layer Reasoning
- Confidence Scoring
- Research Conclusion
- Trading Decision
- Portfolio Action
- Execution Review
- Knowledge Update
- Archive

### Step 4: Update Research Judgment

If the item has research value, suggest or perform updates only when requested:

| Evidence Type | Target |
|---|---|
| New signal | `02_Databases/Alpha_Radar.md` |
| Order, capacity, backlog, shipment, utilization, qualification | `02_Databases/Order_Book.md` |
| Risk or invalidation | `02_Databases/Risk_Radar.md` |
| Revenue, margin, ASP, FCF, capex transmission | `02_Databases/Price_Transmission.md` |
| Company thesis, priority, confidence, trigger | `02_Databases/AI_Shovel_100.md` |

Missing evidence remains `Unknown` or `Unverified`.

### Step 5: Update Portfolio Action Suggestion

If the item affects portfolio behavior:

1. Check Decision Gates.
2. Check Trading Decision Table fields.
3. Check Portfolio Rules.
4. Produce one Atlas action only:
   Research / Observe / Build / Accumulate / Hold / Reduce / Exit.

### Step 6: Output Atlas Daily Report

Use `08_Daily_Operating_Cycle/Daily_Report_Template.md`.

Daily output should summarize:

- What changed.
- What did not change.
- What is blocked by missing evidence.
- What action, if any, is allowed today.

### Step 7: Repository Sync Instruction

If the user confirms repository sync, generate a repository update plan:

```text
Target files:
Reason:
Evidence:
Privacy check:
Commit needed: YES / NO
```

Do not commit unless the user explicitly asks for commit.

## Daily Stop Rule

If evidence is insufficient, stop at Observe / Research and list waiting triggers.
