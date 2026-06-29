# Atlas World Model

Atlas does not collect news.

Atlas continuously updates its understanding of the world.

Atlas 不收集新闻。

Atlas 持续更新自己对世界的理解。

## Role

World Model is Atlas's highest active knowledge structure.

Database, Pattern, Case, Evidence, and Signal are components of the World Model. Markdown is only
persistent storage. World Model is the actual knowledge object.

## Knowledge Hierarchy

```text
Theory
 ↓
World Model
 ↓
Pattern
 ↓
Case
 ↓
Evidence
 ↓
Signal
```

Theory can only emerge through long-term operation.

Theory cannot be manually created.

## World Model Rule

World Model does not record news.

World Model records Atlas's current understanding of the AI world.

Every node must answer:

- What does Atlas believe this domain means?
- How important is it in the AI world?
- How confident is Atlas?
- Is the domain strengthening, weakening, stable, developing, or early?
- Which Patterns support the node?
- Which Cases validate or challenge the node?
- Which counter evidence could change the model?
- Which waiting triggers matter next?

## AI World

```text
AI World
├── Compute
├── Memory
├── Networking
├── Optical Interconnect
├── Power
├── Manufacturing
├── Materials
├── Robotics
└── Industry AI
```

## Node Template

```text
Node:
Definition:
Current Weight:
Confidence:
Trend:
Supporting Pattern:
Supporting Case:
Counter Evidence:
Waiting Trigger:
Last Updated:
```

## Current Nodes

### Compute

Node: Compute

Definition: Accelerators, processors, and compute platforms that convert capital and energy into AI
training or inference capacity.

Current Weight: Unknown

Confidence: Unknown

Trend: Developing

Supporting Pattern:

- Infrastructure Before Application

Supporting Case:

- Unknown

Counter Evidence:

- Compute supply grows faster than monetizable demand.

Waiting Trigger:

- Cloud CapEx guidance.
- Accelerator backlog.
- Inference utilization.

Last Updated: 2026-06-29

### Memory

Node: Memory

Definition: DRAM, HBM, NAND, legacy memory, and memory-adjacent constraints that determine AI
system throughput, pricing power, and supply bottlenecks.

Current Weight: 70%

Confidence: High

Trend: Stable

Supporting Pattern:

- Memory Constraint
- HBM Supercycle
- Pricing Power

Supporting Case:

- Unknown

Counter Evidence:

- DRAM ASP declines.
- HBM lead time shortens.
- Cloud CapEx declines.

Waiting Trigger:

- DRAM ASP two-week decline.
- HBM lead time compression.
- Memory supplier guidance cut.

Last Updated: 2026-06-29

### Networking

Node: Networking

Definition: Switching, routing, and high-speed data movement infrastructure that determines whether
compute clusters can scale efficiently.

Current Weight: Unknown

Confidence: Medium

Trend: Developing

Supporting Pattern:

- Bandwidth Constraint

Supporting Case:

- Unknown

Counter Evidence:

- Network upgrade cycle slows before cluster demand slows.

Waiting Trigger:

- Switch ASIC roadmap.
- AI cluster networking spend.
- Ethernet / InfiniBand demand split.

Last Updated: 2026-06-29

### Optical Interconnect

Node: Optical Interconnect

Definition: Optical data movement, CPO, PIC, modulators, WDM, and optical engine integration that
may become the next bandwidth-density constraint.

Current Weight: 23%

Confidence: 82%

Trend: Strengthening

Supporting Pattern:

- PIC Ownership
- Bandwidth Constraint
- Component Ownership Beats Substrate Narrative

Supporting Case:

- Broadcom CPO architecture: Partial

Counter Evidence:

- Glass substrate becomes the dominant CPO bottleneck.
- PIC integration fails to scale commercially.

Waiting Trigger:

- Broadcom CPO roadmap.
- Chinese PIC orders.
- TFLN modulator capacity and ASP.
- CPO customer adoption.

Last Updated: 2026-06-29

### Power

Node: Power

Definition: Electricity generation, grid, thermal, and power delivery constraints that limit AI
infrastructure deployment.

Current Weight: Unknown

Confidence: Medium

Trend: Developing

Supporting Pattern:

- Power Bottleneck
- Infrastructure Before Application

Supporting Case:

- Unknown

Counter Evidence:

- Grid and generation capacity expands faster than data center load.

Waiting Trigger:

- Data center power contract backlog.
- Utility capex.
- Power price inflation.

Last Updated: 2026-06-29

### Manufacturing

Node: Manufacturing

Definition: Semiconductor equipment, packaging, foundry, and advanced manufacturing capacity that
turns demand into supply.

Current Weight: Unknown

Confidence: Medium

Trend: Developing

Supporting Pattern:

- Capacity Constraint
- Supply Chain Verification

Supporting Case:

- Unknown

Counter Evidence:

- Capacity additions exceed demand.

Waiting Trigger:

- Tool order backlog.
- Advanced packaging capacity.
- Utilization and lead time.

Last Updated: 2026-06-29

### Materials

Node: Materials

Definition: Advanced materials, substrates, chemicals, optical materials, and critical inputs that
enable AI hardware scaling.

Current Weight: Unknown

Confidence: Medium

Trend: Developing

Supporting Pattern:

- Materials Constraint
- Supply Chain Verification

Supporting Case:

- Unknown

Counter Evidence:

- Materials supply proves abundant or substitutable.

Waiting Trigger:

- Material ASP.
- Qualification cycle.
- Customer certification.

Last Updated: 2026-06-29

### Robotics

Node: Robotics

Definition: Embodied AI, robot hardware, motion, sensing, actuation, and industrial deployment
chains.

Current Weight: Unknown

Confidence: Low / Medium

Trend: Early Stage

Supporting Pattern:

- Efficiency Multiplier

Supporting Case:

- Unknown

Counter Evidence:

- Unit economics fail to improve.
- Deployment remains demonstration-scale.

Waiting Trigger:

- Real order conversion.
- Unit economics.
- Component bottleneck evidence.

Last Updated: 2026-06-29

### Industry AI

Node: Industry AI

Definition: AI adoption in vertical industries where workflow change, ROI, and deployment friction
determine real demand.

Current Weight: Unknown

Confidence: Medium

Trend: Developing

Supporting Pattern:

- Efficiency Multiplier
- Infrastructure Before Application

Supporting Case:

- Unknown

Counter Evidence:

- Enterprise AI ROI remains weak.

Waiting Trigger:

- Paid deployment expansion.
- Workflow productivity evidence.
- Customer retention.

Last Updated: 2026-06-29

## World Model Delta Rule

Knowledge Delta is now World Model Delta.

World Model Delta answers which World Model domains or nodes changed today.

If no model changed, output:

```text
No World Model Change Today
```

## Pattern Rule

Pattern cannot exist independently.

Every Pattern must belong to a World Model Node.

No Node, no new Pattern.

Examples:

- Memory Constraint belongs to Memory.
- PIC Ownership belongs to Optical Interconnect.
- Pricing Power belongs to Economics.
- Power Bottleneck belongs to Power.

## Case Rule

Case must answer:

- Which Pattern did it validate, refute, or modify?
- Which World Model Node did that Pattern affect?

If a Case cannot answer both questions, it cannot merge.

## Signal Rule

Signal does not change World Model by default.

Only Evidence + Reasoning + Review can change World Model.

## Portfolio Rule

Portfolio tracks World Model, not news.

Portfolio Action must be driven by World Model changes, not headlines or single Patterns.
