# Market Data Provider Smoke Test Result

Generated: 2026-06-30T22:09:26

## Executive Summary

- Overall provider status: PARTIAL
- Current holdings data status: Partial
- A-share candidate data status: Available
- Hong Kong candidate data status: Available
- US / ETF data status: Blocked
- Main blockers: 泰金新能 and DRAM ETF remain Needs Manual Mapping; valuation and turnover are optional and often missing.

## Ticker Registry Status

| Name | Code | Market | Provider Symbol | Identity Status | Notes |
| --- | --- | --- | --- | --- | --- |
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

| Holding | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Source | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 雅克科技 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 建滔集团 | HK | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 东山精密 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 泰金新能 | A-share | Data Missing | Data Missing | Data Missing | Data Missing | Optional Data Missing | Needs Manual Mapping | None | Local registry previously mentioned 688813, but mapping requires manual confirmation. |
| DRAM ETF | US / ETF | Data Missing | Data Missing | Data Missing | Data Missing | Optional Data Missing | Needs Manual Mapping | None | Local portfolio uses descriptive DRAM ETF exposure but no executable ticker mapping. |

## A-share Candidates

| Candidate | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Source | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 赛腾股份 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 澜起科技 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 雅克科技 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 江丰电子 | A-share | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |

## Hong Kong Candidates

| Candidate | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Source | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 中芯国际 | HK | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |
| 长飞光纤光缆 | HK | Available | Available | Available | Available | Optional Data Missing | Available | yfinance | turnover; market_cap (optional); pe (optional); pb (optional) |

## US / ETF

| Candidate | Market | Latest | History 60d | Volume | MA20/MA60 | Valuation | Status | Source | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DRAM ETF | US / ETF | Data Missing | Data Missing | Data Missing | Data Missing | Optional Data Missing | Needs Manual Mapping | None | Local portfolio uses descriptive DRAM ETF exposure but no executable ticker mapping. |

## Final Decision

PARTIAL

## Next Step

Confirm executable ticker mappings for 泰金新能 and DRAM ETF.

## Safety

- No private portfolio amount stored.
- No portfolio allocation modified.
- No CDE logic modified.
- No Decision Brief strategy logic modified.
- No new Engine created.
