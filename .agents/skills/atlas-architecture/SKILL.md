---
name: atlas-architecture
description: Use for Atlas OS framework review, module boundary checks, audit package design, release gate review, project-stage control, and system architecture decisions. Do not edit files unless explicitly asked.
---

# Atlas Architecture

## when_to_use

Use this skill when the task involves:

- Reviewing Atlas framework boundaries.
- Checking whether a proposed module belongs in Core, Framework, Database, Trading OS, Current State,
  Cases, Portfolio, or Verification.
- Designing audit packages or release gates.
- Evaluating whether a requested change violates project stage.
- Deciding whether Atlas needs a simpler non-code alternative.

## required_reads

- `README.md`
- `00_Core/Atlas_Core.md`
- `00_Core/Atlas_Principles.md`
- `00_Core/Seven_Layer_Reasoning.md`
- `99_Verification/Audit_Methodology.md`
- `99_Verification/Release_Gate.md`
- `VERSION.md`
- `CHANGELOG.md`

## output_format

Return:

1. Scope classification.
2. Module boundary decision.
3. Project-stage risk.
4. Simpler alternative, if available.
5. Required files to change, if the user asked for implementation.
6. Release/audit impact.
7. Recommendation: Accept / Revise / Reject / Needs user decision.

## forbidden_actions

- Do not directly modify files unless the task explicitly asks for implementation.
- Do not create new frameworks when an existing Atlas file can absorb the change.
- Do not add software systems where Markdown process is enough.
- Do not make trade or portfolio recommendations.
- Do not change release gates without explaining the boundary impact.
