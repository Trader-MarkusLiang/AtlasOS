# Atlas Audit Methodology

Git construction success does not equal Atlas migration success. The audit verifies Knowledge
Consistency.

## Level 1: Structure

Check:

- Git repository exists.
- Required directories exist.
- `VERSION.md` exists and records the target version.
- `CHANGELOG.md` exists and records the release.
- Git tag exists for the release.

## Level 2: Knowledge

Required modules:

| Module | Required File |
|---|---|
| Atlas Principles | `00_Core/Atlas_Principles.md` |
| Seven Layer Reasoning | `00_Core/Seven_Layer_Reasoning.md` |
| AI Bottleneck Index | `01_Framework/AI_Bottleneck_Index.md` |
| Capital Relay | `01_Framework/Capital_Relay.md` |
| ROI Engine | `01_Framework/ROI_Engine.md` |
| Efficiency Multiplier | `01_Framework/Efficiency_Multiplier.md` |
| Trading OS | `03_Trading_OS/Daily_Dashboard_Template.md` |
| AI Shovel 100 | `02_Databases/AI_Shovel_100.md` |

Output:

- Knowledge Coverage %
- Missing Modules

Coverage formula:

```text
existing required knowledge modules / total required knowledge modules * 100
```

## Level 3: Reasoning

Re-run reasoning audit for:

- Apple CXMT
- DeepSeek Spark
- Google Gemini
- Corning
- Nomura FCF
- Korea Memory CapEx
- HBM Supercycle
- DRAM Supercycle

Audit fails if outputs clearly diverge from the stored Atlas consensus.

## Level 4: Trading

Verify Trading OS can still output:

- Current Bottleneck ranking
- Current Capital Relay
- Current position suggestion
- Current risk level
- Current waiting conditions

## Regression Rule

Every release must at least run:

- Apple CXMT
- DeepSeek Spark
- Nomura
- Corning
- Google Gemini
- Korea Memory CapEx

Any FAIL blocks release.
