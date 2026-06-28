---
name: atlas-repository
description: Use for Atlas OS Git work, Markdown maintenance, audit reports, commits, tags, changelog, version updates, release hygiene, and repository structure. Do not make investment judgments.
---

# Atlas Repository

## when_to_use

Use this skill when the task involves:

- Git status, diff, commit, tag, branch, or release work.
- Markdown file creation or maintenance.
- Version, changelog, audit report, release gate, or verification package updates.
- Repository structure, `.gitignore`, or session logs.

## required_reads

- `README.md`
- `VERSION.md`
- `CHANGELOG.md`
- `99_Verification/Audit_Methodology.md`
- `99_Verification/Release_Gate.md`
- Relevant target files named by the user.

## output_format

Return:

1. Files changed.
2. Verification performed.
3. Audit or release result, if relevant.
4. Commit hash, if committed.
5. Tag, if created.
6. Remaining risks or uncommitted changes.

## forbidden_actions

- Do not make independent investment judgments.
- Do not alter Atlas core principles or frameworks unless explicitly requested.
- Do not commit private portfolio files.
- Do not create software architecture, dashboards, crawlers, APIs, or automation unless requested.
- Do not run destructive Git commands without explicit user instruction.
