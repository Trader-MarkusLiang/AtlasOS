# Atlas Production Trial

Atlas Production Trial is the operating period after RC and before Final.

Architecture is frozen during Production Trial.

Allowed:

- Daily real usage.
- Bug fixes.
- Usability polish.
- Issue recording.
- Weekly review.
- Improvement candidate discussion.

Forbidden:

- New Engine.
- AES implementation.
- Workflow redesign.
- Architecture expansion.
- Direct implementation from a new idea.

Core rule:

```text
No Issue, No Iteration.
```

没有 Issue，就不进入迭代。

## Directory Map

| Directory | Purpose |
|---|---|
| `Issues/` | Raw Production Trial issues observed from real usage. |
| `Weekly_Reviews/` | Weekly operating reviews of repeated and critical issues. |
| `Improvement_Candidates/` | Repeated issue patterns being considered for IP conversion. |
| `Accepted_Issues/` | Issues accepted for discussion or IP conversion. |
| `Rejected_Issues/` | Issues rejected, deferred, or recorded for traceability. |

## Operating Rule

Every future Atlas iteration must reference at least one Issue.

An Issue is not an Improvement Proposal. An Issue becomes an IP only after discussion,
prioritization, and user approval.
