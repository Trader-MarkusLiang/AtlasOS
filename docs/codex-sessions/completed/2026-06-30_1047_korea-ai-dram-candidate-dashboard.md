# Korea AI DRAM Candidate Dashboard Session

## Metadata

- Date: 2026-06-30
- Session id: 2026-06-30_1047_korea-ai-dram-candidate-dashboard
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Process South Korea AI / DRAM investment signal and screenshot candidate list using latest Atlas OS.
- Status: completed
- Branch: main

## User Request Summary

The user provided a screenshot and summary claiming South Korea will invest at least 30 trillion won
over 15 years in next-generation memory, edge AI, defense chips, and related areas, with DRAM
capacity expected to double within five years and global memory market to grow fourfold. The user
asked Atlas OS to process the information.

## Constraints

- Use current Atlas OS with Portfolio Context Injection and Strategic Candidate Dashboard.
- Treat screenshot candidate names as candidate signals, not verified supplier evidence.
- Do not update repository databases or commit unless explicitly requested.

## Work Done

- Read atlas-research, atlas-portfolio, atlas-daily, AGENTS Strategic Candidate Dashboard rule, and
  local portfolio context.
- Browsed for current verification of the South Korea investment plan.
- Classified the event as a high-quality macro / policy / capex signal and screenshot names as
  low-to-medium quality candidate signals requiring verification.

## Decisions

- Existing portfolio action remains Hold.
- Tiger Memory exposure is directly strengthened but also receives longer-term overcapacity watch.
- China holdings have mostly indirect mapping except materials / gas / equipment-chain overlap.
- Strategic Candidate Dashboard should rank candidates by research priority, not trading action.

## Current State

- Final Decision Brief prepared.
- No database update was made.
- Screenshot candidate names were treated as Strategic Candidate Dashboard inputs, not verified
  supplier evidence.

## Resume Instructions

1. If the user requests persistence, propose candidate database updates separately.
2. Verify each screenshot candidate via official supplier/customer/order evidence before promotion.
3. Do not treat candidate ranking as CDE authority.

## Open Questions

- Whether to add the strongest Korea-linked A-share candidates to local candidate mapping.
