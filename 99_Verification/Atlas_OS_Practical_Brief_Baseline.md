# Atlas OS Practical Brief Baseline

Date: 2026-07-10

## Baseline Finding

Before this rebuild, Home used the previous user-decision journey:

```text
what changed -> strongest judgment -> portfolio relevance -> decision agenda
-> view-change triggers -> research priorities
```

That structure was useful but failed the Practical Decision Brief goal because it did not begin with
whether action was needed today and did not restore the historical operating chain.

## Current Defects Found

| Requirement | Baseline Status | Defect |
|---|---|---|
| Home begins with Action Today | FAIL | First section was current/core judgment, not YES / NO / CONDITIONAL. |
| One total judgment | PARTIAL | A core judgment existed but competed with other equal-weight cards. |
| Strongest predictions | PARTIAL | Forward view existed, but not a max-3 prediction list with required fields. |
| AI Bottleneck Index | FAIL | Not shown on Home. |
| Capital Relay | FAIL | Not shown as first-class Home section. |
| Actual configured holdings | PARTIAL | Portfolio relevance existed, but not per-holding posture / trigger board. |
| Capital Allocation Board | FAIL | No source -> destination planning surface. |
| Waiting Triggers with status | FAIL | Positive/negative trigger ideas existed but lacked MET / PARTIAL / NOT MET / UNKNOWN status. |
| Top 3 research tasks | PARTIAL | Top priorities existed but were closer to candidate items than tasks. |
| Candidate source truth | PARTIAL | Truth label existed but needed clearer static/manual/runtime distinction. |
| Intelligence & Alerts | FAIL | No compact intelligence brief section. |
| Counter Argument | FAIL | Expert analysis contained depth, but Home did not always surface the strongest objection. |
| Review Plan | FAIL | No explicit next review plan. |
| Forecast Accountability | PASS | Compact support block existed. |
| Expert Analysis secondary | PASS | Expert layer was collapsed by default. |

## Rebuild Decision

The previous Home information architecture conflicts with the Practical Decision Brief goal and must
not be preserved as the default Home. It is replaced with the exact operating chain:

```text
今日是否行动 -> 今日总判断 -> 最强预测 -> AI 瓶颈指数 -> 资本迁移 -> 当前持仓
-> 资金调度 -> 等待触发条件 -> 今日研究任务 -> 情报与预警 -> 反方观点 -> 复盘计划
```

## Baseline Status

FAIL before rebuild. The Home route required structural replacement, not more cards.
