# Atlas OS User Decision Home Baseline

Date: 2026-07-10

Scope: audit the actual latest Home before the user-decision rebuild. This is a UI information
architecture audit only. It does not change cognition semantics, Event Fusion, CIL, LMSE, MPCE,
MLE, UMIS, Decision Contract, CDE authority, forecast semantics, candidate semantics, portfolio
mutation, or trading execution.

## Runtime Sample

Observed through the normal `/state` path during audit:

- Tick counter: approximately `1000+`.
- Regime state: runtime state changing between `RISK_OFF` and `ATTENTION_EXPANSION`.
- Latest DecisionPacket: low-confidence fallback/neutral or observe posture depending on tick.
- Candidate pool: `27` records from `02_Databases/AI_Shovel_100.md`.
- Forecast ledger: `25` records, all `OPEN`; no evaluated miss available yet.
- Portfolio context: configured, percentage-only, no private account amount stored in Home.
- Market channels: price/volume and portfolio relevance available; several breadth/news/macro
  channels explicitly unconfigured or simulated.

## Baseline Block Classification

| Visible Home block | Classification | User question answered | Decision value | Required change |
|---|---|---|---|---|
| Current State | `ESSENTIAL` + `TOO_DETAILED` | What is happening now? | Useful, but regime label and driver chips were not enough to tell the user what to do next. | Merge into one Core Judgment that starts with "What changed?" and shows one judgment, confidence, evidence quality, and update time. |
| Market Outlook / Forward Outlook | `ESSENTIAL` + `DUPLICATED` | What might happen next? | Useful, but equal-weight Base/Upside/Downside cards diluted conviction. | Replace with one strongest Forward View plus horizon, confidence, evidence quality, and falsification condition. Move scenario detail out of Home. |
| Portfolio Impact | `ESSENTIAL` + `SUPPORTING` | Why does this matter to my holdings? | Necessary for Atlas to be user-relevant. | Compress into Portfolio Relevance: overall impact, shared risk, most sensitive holding, strongest buffer. |
| Candidate Pool / Research Candidates | `SUPPORTING` + `MOVE_OFF_HOME` | What deserves deeper research? | Useful, but showing five rows, filters, and changes made Home feel like a database page. | Show only Top 3 research priorities on Home; keep full pool behind `/candidates`. |
| Candidate filters | `MOVE_OFF_HOME` | How can I inspect the full pool? | Not needed for first decision. | Keep only on `/candidates`; remove from Home. |
| Candidate table | `MOVE_OFF_HOME` | What are all current candidates? | Too much for Home. | Remove from Home; preserve full candidate page. |
| Forecast Accountability | `ESSENTIAL` + `TOO_DETAILED` | Does Atlas deserve trust? | Required, but five status counts and timeline competed with the primary decision path. | Compact to open/verified/invalidated/inconclusive, recent miss, and what changed afterward. |
| Forecast timeline | `TOO_DETAILED` | What are latest ledger rows? | Better suited to Predictions page. | Remove from Home; keep link to `/predictions`. |
| Expert Analysis | `EXPERT_ONLY` | Why did the system reason this way? | Valuable for audit and expert use, but not first-screen decision material. | Keep collapsed and secondary after the decision journey. |
| Raw Evidence | `EXPERT_ONLY` | What state values support the view? | Necessary for traceability, harmful as default Home content. | Keep nested inside collapsed Expert Analysis. |
| Proactive Update card | `SUPPORTING` + `DUPLICATED` | What will Atlas refresh? | Useful operational context, but not part of the six-question Home journey. | Fold its effect into Core Judgment, Decision Agenda, and triggers rather than adding a separate module. |

## Candidate Priority Truth

Source inspected: `02_Databases/AI_Shovel_100.md`.

Current candidate priority is:

- `static source order`: yes.
- `manually ranked`: yes, via Priority S/A/B repository tables.
- `dynamic runtime relevance`: not proven.
- `portfolio-aware ranking`: only as a UI presentation overlay when current portfolio context is
  matched to static records.
- `evidence-aware ranking`: not proven unless a specific evidence change is displayed.

Decision for rebuild:

- Home may show current-portfolio-relevant Top 3 research priorities.
- Home must label this as static repository pool plus presentation-only portfolio relevance.
- Home must not present the static pool as a live dynamic ranking.
- Full pool remains available on `/candidates`.

## User-Centered Defects Found

1. Home presented six intelligence modules with similar visual weight.
2. The first viewport did not enforce the mandatory sequence:
   what changed -> strongest judgment -> portfolio relevance -> decision agenda.
3. Market Outlook showed multiple scenarios before one strongest view.
4. Candidate Pool occupied too much Home space and exposed database mechanics.
5. Forecast Accountability was too broad for first decision comprehension.
6. Expert Analysis competed with the decision path.
7. Candidate priority truth was not explicit enough on Home.
8. Low-confidence or fallback states were not transformed into a clear user judgment.

## Target Reduction

Required new structure:

1. First viewport: exactly four primary blocks.
   - Today's Core Judgment.
   - Strongest Forward View.
   - Portfolio Relevance.
   - Decision Agenda.
2. Supporting section:
   - What Would Change the View.
   - Today's Top 3 Research Priorities.
3. Accountability:
   - Compact Forecast Accountability.
4. Expert:
   - Collapsed Expert Analysis.

Acceptance depends on actual rendered Home and validator/browser evidence, not this audit alone.
