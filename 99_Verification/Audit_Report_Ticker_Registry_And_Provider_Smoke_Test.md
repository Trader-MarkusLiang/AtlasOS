# Audit Report — Ticker Registry and Provider Smoke Test

Date: 2026-06-30

## Executive Summary

Overall provider status:

```text
PARTIAL
```

Current holdings data status:

- Mapped current holdings are fetchable.
- 泰金新能 remains `Needs Manual Mapping`.
- DRAM ETF remains `Needs Manual Mapping`.

Candidate data status:

- A-share candidates tested in this task are fetchable through `yfinance`.
- Hong Kong candidates tested in this task are fetchable through `yfinance`.
- Optional valuation fields remain missing.

Main blockers:

- 泰金新能 executable ticker is not fully verified.
- DRAM ETF executable ticker is not defined.
- Turnover and valuation fields are missing from yfinance-backed snapshots and remain optional.

Final decision:

```text
PARTIAL
```

Next step:

```text
Confirm executable ticker mappings for 泰金新能 and DRAM ETF.
```

## Ticker Registry Status

| Name | Code | Market | Provider Symbol | Identity Status | Notes |
|---|---|---|---|---|---|
| 雅克科技 | 002409 | A-share | 002409 | Validated |  |
| 东山精密 | 002384 | A-share | 002384 | Validated |  |
| 泰金新能 | 688813 | A-share | Needs Manual Mapping | Needs Manual Mapping | Local registry previously mentioned 688813, but mapping requires manual confirmation. |
| 赛腾股份 | 603283 | A-share | 603283 | Validated |  |
| 澜起科技 | 688008 | A-share | 688008 | Validated |  |
| 江丰电子 | 300666 | A-share | 300666 | Validated |  |
| 建滔集团 | 00148 | HK | 00148 | Validated | Registry normalizes to 建滔集团 for HK ticker 00148; 建韬集团 retained as user spelling alias. |
| 长飞光纤光缆 | 06869 | HK | 06869 | Validated |  |
| 中芯国际 | 00981 | HK | 00981 | Validated |  |
| DRAM ETF | Data Missing | US / ETF | Needs Manual Mapping | Needs Manual Mapping | Local portfolio uses descriptive DRAM ETF exposure but no executable ticker mapping. |

## Current Holdings Smoke Test

| Holding | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 雅克科技 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 建滔集团 | HK | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 东山精密 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 泰金新能 | A-share | Data Missing | Data Missing | Data Missing | Data Missing | Optional Data Missing | Needs Manual Mapping | Mapping not forced |
| DRAM ETF | US / ETF | Data Missing | Data Missing | Data Missing | Data Missing | Optional Data Missing | Needs Manual Mapping | Mapping not forced |

## Candidate Smoke Test

### A-share Candidates

| Candidate | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 赛腾股份 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 澜起科技 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 雅克科技 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 江丰电子 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |

### Hong Kong Candidates

| Candidate | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 中芯国际 | HK | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |
| 长飞光纤光缆 | HK | Available | Available | Available | Available | Optional Data Missing | Available | Source: yfinance |

### US / ETF

| Candidate | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| DRAM ETF | US / ETF | Data Missing | Data Missing | Data Missing | Data Missing | Optional Data Missing | Needs Manual Mapping | Mapping not forced |

## Safety Verification

| Rule | Result |
|---|---|
| No private portfolio amount stored | PASS |
| No `portfolio.local.yaml` allocation modification | PASS |
| No CDE modification | PASS |
| No Decision Brief strategy logic modification | PASS |
| No new Engine created | PASS |
| No uncertain ticker forced | PASS |
| Optional valuation missing does not fail test | PASS |

## Known Limitations

- This smoke test verifies provider access and ticker mapping only.
- It does not authorize CDE precision for unmapped holdings.
- It does not implement dashboard polish for mixed A-share / HK display.
- It does not implement Rebalance Execution Plan.
