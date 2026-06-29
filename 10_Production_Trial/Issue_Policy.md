# Issue Policy

## Core Rule

No Issue, No Iteration.

没有 Issue，就不进入迭代。

## Rules

1. Any new idea must first be recorded as an Issue.
2. An Issue is not an Improvement Proposal.
3. An Issue only becomes an Improvement Proposal after discussion and prioritization.
4. Repeated issues gain priority.
5. High-impact issues may be escalated immediately.
6. Low-frequency ideas remain Watching.
7. No new Engine may be implemented directly from an idea.
8. Production Trial allows bug fixes and usability polish only.
9. Architecture changes require multiple Issues or one Critical Issue.
10. Every future iteration must reference at least one Issue.

## Priority

| Priority | Meaning |
|---|---|
| P0 | Critical. Blocks investment decision or causes wrong portfolio action. |
| P1 | High. Repeated issue affecting decision quality, capital discipline, or trust. |
| P2 | Medium. Usability, clarity, explainability, or workflow friction. |
| P3 | Low. Nice-to-have, style preference, or one-time improvement idea. |

## Lifecycle

```text
Observed
 ↓
Recorded
 ↓
Watching
 ↓
Discussed
 ↓
Accepted / Rejected
 ↓
Converted to IP
 ↓
Implemented
 ↓
Validated
```

## Production Trial Boundary

Issue System is not AES.

Issue System is not a new Engine.

Issue System is not a feature upgrade.

It is a lightweight Production Trial tracking layer.
