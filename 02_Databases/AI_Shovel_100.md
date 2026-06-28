# AI Shovel 100

## Scoring Dimensions

| Dimension | Weight |
|---|---:|
| Technical barrier | 20% |
| Order certainty | 20% |
| Three-year earnings elasticity | 20% |
| Capital recognition | 15% |
| Current trading position | 15% |
| Pricing power | 5% |
| Current bottleneck exposure | 5% |

## Company-Level Scoring Table

Use this table to turn the candidate pool into a research database. Scores use a 0-5 scale for each
dimension, then apply the weights above.

| Date | Company | Ticker / Chain | Bottleneck | Region | Technical Barrier | Order Certainty | 3Y Earnings Elasticity | Capital Recognition | Trading Position | Pricing Power | Bottleneck Exposure | Weighted Score | Evidence | Review Trigger |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2026-06-29 | Example entry | Ticker or chain | Memory / Equipment / Materials / Bandwidth | Global / Domestic | 0-5 | 0-5 | 0-5 | 0-5 | 0-5 | 0-5 | 0-5 | 0-100 | Link to Order Book, Price Transmission, case, or source note | Event or date for re-score |

## Scoring Rule

- A company cannot be ranked as core unless it has evidence in at least one of Order Book, Price Transmission, or a case replay.
- If evidence is missing, keep the company in the candidate pool and leave it unranked.
- Review scores when orders, pricing, margins, bottleneck ranking, or capital position changes.

## Living Database Rules

- Priority S records current or core portfolio exposure and must be reviewed first.
- Priority A records Atlas core research names and must be updated after Priority S.
- Priority B records watch-pool names and can remain observation-only until evidence improves.
- Scores must be evidence-backed. If no public or repository evidence is recorded, write `Unverified`.
- Unknown portfolio weight, customer, order, capacity, shipment, or financial data must be written as `Unknown`.

## Priority S: Portfolio / Core Holdings

| Company | Industry | AI Bottleneck | Atlas Priority | Portfolio | Current Position | Current Weight | Conviction | Capital Action | Investment Thesis | Current Drivers | Key Risks | Next Trigger | Evidence | Confidence | Last Update | Review Frequency | Review Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 泰金新能（688813） | Materials / equipment supply chain exposure | Materials | S | YES | Current Holding | Original about 37%; 30% sold; current exact weight Unknown | High | Hold; possible source of funds if sharp acceleration continues | Domestic AI infrastructure supply chain exposure tied to Materials theme | Portfolio note says profit about 40% and partial profit-taking completed | Price already reflects thesis; company-specific evidence not yet recorded | New order, margin, or valuation reset evidence | `04_Current_State/Current_Holdings_Strategy.md` | Medium | 2026-06-29 | Weekly / event-driven | Atlas |
| 罗博特科 | Equipment / automation exposure | Equipment | S | YES | Current Holding | About 14% | Medium | Hold and observe | Domestic equipment/automation exposure within Equipment relay | Portfolio note lists current holding | Company-specific order evidence not yet recorded | Confirm order, backlog, or margin evidence | `04_Current_State/Current_Holdings_Strategy.md` | Medium | 2026-06-29 | Weekly / event-driven | Atlas |
| 东山精密 | PCB / CCL / electronics supply chain exposure | Bandwidth / PCB | S | YES | Current Holding | About 20% | Medium | Hold | AI capital relay includes PCB / CCL / Copper Foil before Equipment | Portfolio note lists current holding | Customer exposure and AI revenue linkage are Unverified | Confirm AI-related revenue, customer, or margin evidence | `04_Current_State/Current_Holdings_Strategy.md`; `01_Framework/Capital_Relay.md` | Medium | 2026-06-29 | Weekly / event-driven | Atlas |
| 德福科技 | Copper foil / materials exposure | Materials / PCB | S | YES | Current Holding | About 20% | Medium | Hold | Materials and PCB-related exposure may benefit from AI infrastructure relay | Portfolio note lists current holding | AI-specific order and pricing evidence are Unverified | Confirm copper foil demand, pricing, or margin transmission | `04_Current_State/Current_Holdings_Strategy.md`; `01_Framework/Capital_Relay.md` | Medium | 2026-06-29 | Weekly / event-driven | Atlas |
| DRAM ETF | Memory exposure vehicle | Memory | S | YES | Core Hold | US funds about 70% in DRAM / Memory direction; exact ETF weight Unknown | High | Core hold | Memory is ranked S+ and remains the strongest current bottleneck | Memory ranked S+; DRAM / Memory core exposure in holdings note | DRAM ASP decline, inventory reversal, or AI demand slowdown | DRAM ASP trend, capex discipline, or Memory ranking change | `04_Current_State/Current_Holdings_Strategy.md`; `04_Current_State/Bottleneck_Map_v1.md` | Medium | 2026-06-29 | Weekly / earnings cycle | Atlas |
| Micron（MU） | Memory semiconductor | Memory | S | YES | Current Holding / Core US Memory exposure | Unknown | High | Hold / research first among US Memory names | Direct DRAM / HBM exposure aligns with Memory S+ bottleneck | Memory ranked S+; user identified MU as core US position | DRAM pricing reversal, HBM execution, capex/FCF deterioration | Earnings, DRAM ASP, HBM demand, FCF update | `04_Current_State/Bottleneck_Map_v1.md`; user v0.5 request | Medium | 2026-06-29 | Weekly / earnings cycle | Atlas |

## Priority A: Atlas Core Research Pool

| Company | Industry | AI Bottleneck | Atlas Priority | Portfolio | Current Position | Current Weight | Conviction | Capital Action | Investment Thesis | Current Drivers | Key Risks | Next Trigger | Evidence | Confidence | Last Update | Review Frequency | Review Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SK Hynix | Memory semiconductor | Memory | A | NO | Research Pool | Unknown | High | Watch / score when evidence recorded | Memory S+ exposure through DRAM / HBM | Memory ranked S+; listed in AI Shovel 100 candidate pool | Pricing reversal, supply expansion, execution risk | Earnings, HBM demand, DRAM ASP, capex discipline | `02_Databases/AI_Shovel_100.md`; `04_Current_State/Bottleneck_Map_v1.md` | Medium | 2026-06-29 | Earnings cycle | Atlas |
| LRCX | Semiconductor equipment | Equipment | A | NO | Research Pool | Unknown | High | Watch / score when evidence recorded | Equipment S+ relay exposure | Equipment ranked S+; listed in candidate pool | Customer capex cuts, order slowdown | Orders, backlog, memory capex | `02_Databases/AI_Shovel_100.md`; `04_Current_State/Bottleneck_Map_v1.md` | Medium | 2026-06-29 | Earnings cycle | Atlas |
| AMAT | Semiconductor equipment | Equipment | A | NO | Research Pool | Unknown | High | Watch / score when evidence recorded | Broad equipment exposure to AI capacity expansion | Equipment ranked S+; listed in candidate pool | Capex cycle slowdown, valuation | Orders, backlog, segment growth | `02_Databases/AI_Shovel_100.md` | Medium | 2026-06-29 | Earnings cycle | Atlas |
| 拓荆科技 | Domestic semiconductor equipment | Equipment | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Domestic equipment exposure to capacity expansion | Equipment ranked S+; listed in candidate pool | Order certainty Unverified | Order/backlog/customer evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 北方华创 | Domestic semiconductor equipment | Equipment | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Domestic equipment exposure to Equipment relay | Equipment ranked S+; listed in candidate pool | Order certainty and margin transmission Unverified | Order/backlog/customer evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 中微公司 | Domestic semiconductor equipment | Equipment | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Etch/equipment exposure within Equipment bottleneck | Equipment ranked S+; listed in candidate pool | Order evidence Unverified | Order/backlog/customer evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 盛美上海 | Domestic semiconductor equipment | Equipment | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Cleaning/equipment exposure within Equipment bottleneck | Equipment ranked S+; listed in candidate pool | Order evidence Unverified | Order/backlog/customer evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 安集科技 | Semiconductor materials | Materials | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Materials S exposure and process intensity beneficiary | Materials ranked S; listed in candidate pool | Pass-through and qualification evidence Unverified | Pricing, qualification, margin evidence | `02_Databases/AI_Shovel_100.md`; `04_Current_State/Bottleneck_Map_v1.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 江丰电子 | Semiconductor materials | Materials | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Materials exposure within AI infrastructure supply chain | Materials ranked S; listed in candidate pool | Customer concentration and pricing evidence Unverified | Qualification, order, margin evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 鼎龙股份 | Semiconductor materials | Materials | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Materials exposure and domestic substitution watch | Materials ranked S; listed in candidate pool | AI-specific transmission Unverified | Qualification, pricing, margin evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 富创精密 | Semiconductor component / materials chain | Materials / Equipment | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Component/materials exposure to equipment and capacity expansion | Listed in Materials candidate pool | AI-specific transmission Unverified | Order, customer, margin evidence | `02_Databases/AI_Shovel_100.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| Corning | Optical / materials / bandwidth infrastructure | Bandwidth | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Bandwidth upgraded to first-level bottleneck in Corning case | Corning case upgrades Bandwidth | Price already reflects thesis; customer adoption risk | Customer adoption, pricing, inventory evidence | `05_Cases/Corning_Bandwidth.md` | Medium | 2026-06-29 | Earnings cycle | Atlas |
| 中际旭创 | Optical module / bandwidth | Bandwidth | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Domestic Bandwidth beneficiary candidate | Listed in Bandwidth candidate pool | Valuation and customer evidence Unverified | Customer adoption, pricing, order evidence | `02_Databases/AI_Shovel_100.md`; `05_Cases/Corning_Bandwidth.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |
| 新易盛 | Optical module / bandwidth | Bandwidth | A | NO | Research Pool | Unknown | Medium | Watch / score when evidence recorded | Domestic Bandwidth beneficiary candidate | Listed in Bandwidth candidate pool | Customer and pricing evidence Unverified | Customer adoption, pricing, order evidence | `02_Databases/AI_Shovel_100.md`; `05_Cases/Corning_Bandwidth.md` | Low | 2026-06-29 | Monthly / event-driven | Atlas |

## Priority B: Watch Pool

| Company / Chain | Industry | AI Bottleneck | Atlas Priority | Portfolio | Observation Reason | Required Evidence To Promote | Current Status | Confidence | Last Update |
|---|---|---|---|---|---|---|---|---|---|
| 长鑫产业链 | Domestic memory supply chain | Memory | B | NO | Domestic Memory substitution watch | Confirmed customer, order, capacity, pricing, or margin evidence | Watch | Low | 2026-06-29 |
| 长江存储产业链 | Domestic NAND / storage supply chain | Memory | B | NO | Domestic storage substitution watch | Confirmed customer, order, capacity, pricing, or margin evidence | Watch | Low | 2026-06-29 |
| 天孚通信 | Optical / bandwidth | Bandwidth | B | NO | Bandwidth beneficiary candidate | Customer adoption, order, pricing, or margin evidence | Watch | Low | 2026-06-29 |
| 长飞光纤 | Fiber / bandwidth | Bandwidth | B | NO | Fiber exposure in Bandwidth bottleneck | Customer adoption, order, pricing, or margin evidence | Watch | Low | 2026-06-29 |
| Coherent | Optical / bandwidth | Bandwidth | B | NO | Global optical beneficiary candidate | Customer adoption, order, pricing, or margin evidence | Watch | Low | 2026-06-29 |
| Lumentum | Optical / bandwidth | Bandwidth | B | NO | Global optical beneficiary candidate | Customer adoption, order, pricing, or margin evidence | Watch | Low | 2026-06-29 |
| Entegris | Semiconductor materials | Materials | B | NO | Global materials beneficiary candidate | Order, pricing, margin, or qualification evidence | Watch | Low | 2026-06-29 |

## Company Score

Scores are not assigned until public or repository evidence exists. Current seed status:

| Company | Atlas Priority | Portfolio | AI Bottleneck | Technical Barrier | Order Certainty | Earnings Elasticity | Pricing Power | Capital Recognition | Current Trading Position | Weighted Score | Capital Action | Current Thesis | Main Risk | Next Trigger | Confidence | Last Update |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 泰金新能（688813） | S | YES | Materials | Unverified | Unverified | Unverified | Unverified | Unverified | Repository holding; exact current position Unknown | Unverified | Hold; possible funding source on sharp acceleration | Portfolio holding aligned with Materials theme | Price already reflects thesis | Company evidence update | Medium | 2026-06-29 |
| 罗博特科 | S | YES | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Repository holding | Unverified | Hold and observe | Portfolio holding aligned with Equipment relay | Order evidence missing | Order/backlog evidence | Medium | 2026-06-29 |
| 东山精密 | S | YES | Bandwidth / PCB | Unverified | Unverified | Unverified | Unverified | Unverified | Repository holding | Unverified | Hold | Portfolio holding aligned with PCB / relay chain | AI revenue linkage Unverified | AI revenue/customer evidence | Medium | 2026-06-29 |
| 德福科技 | S | YES | Materials / PCB | Unverified | Unverified | Unverified | Unverified | Unverified | Repository holding | Unverified | Hold | Portfolio holding aligned with Materials / PCB relay | AI-specific transmission Unverified | Pricing/margin evidence | Medium | 2026-06-29 |
| DRAM ETF | S | YES | Memory | Unverified | Unverified | Unverified | Unverified | Unverified | Core Memory exposure | Unverified | Core hold | Memory is S+ bottleneck | DRAM cycle reversal | DRAM ASP / Memory ranking change | Medium | 2026-06-29 |
| Micron（MU） | S | YES | Memory | Unverified | Unverified | Unverified | Unverified | Unverified | Core US Memory exposure; exact weight Unknown | Unverified | Hold / research | Memory S+ direct exposure | DRAM pricing or HBM execution risk | Earnings / HBM / FCF update | Medium | 2026-06-29 |
| SK Hynix | A | NO | Memory | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Memory S+ candidate | Evidence not yet recorded | Earnings / HBM evidence | Medium | 2026-06-29 |
| LRCX | A | NO | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Equipment S+ candidate | Order slowdown | Orders/backlog evidence | Medium | 2026-06-29 |
| AMAT | A | NO | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Equipment S+ candidate | Capex cycle slowdown | Orders/backlog evidence | Medium | 2026-06-29 |
| 拓荆科技 | A | NO | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Domestic Equipment candidate | Evidence not yet recorded | Order/customer evidence | Low | 2026-06-29 |
| 北方华创 | A | NO | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Domestic Equipment candidate | Evidence not yet recorded | Order/customer evidence | Low | 2026-06-29 |
| 中微公司 | A | NO | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Domestic Equipment candidate | Evidence not yet recorded | Order/customer evidence | Low | 2026-06-29 |
| 盛美上海 | A | NO | Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Domestic Equipment candidate | Evidence not yet recorded | Order/customer evidence | Low | 2026-06-29 |
| 安集科技 | A | NO | Materials | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Materials S candidate | Evidence not yet recorded | Qualification/margin evidence | Low | 2026-06-29 |
| 江丰电子 | A | NO | Materials | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Materials S candidate | Evidence not yet recorded | Qualification/margin evidence | Low | 2026-06-29 |
| 鼎龙股份 | A | NO | Materials | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Materials S candidate | Evidence not yet recorded | Qualification/margin evidence | Low | 2026-06-29 |
| 富创精密 | A | NO | Materials / Equipment | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Materials / Equipment chain candidate | Evidence not yet recorded | Order/customer evidence | Low | 2026-06-29 |
| Corning | A | NO | Bandwidth | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Bandwidth case candidate | Chasing after move | Customer/pricing evidence | Medium | 2026-06-29 |
| 中际旭创 | A | NO | Bandwidth | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Domestic Bandwidth candidate | Evidence not yet recorded | Customer/order evidence | Low | 2026-06-29 |
| 新易盛 | A | NO | Bandwidth | Unverified | Unverified | Unverified | Unverified | Unverified | Research pool | Unverified | Watch | Domestic Bandwidth candidate | Evidence not yet recorded | Customer/order evidence | Low | 2026-06-29 |

## Initial Candidate Pool

### Memory

Global:

- Micron
- SK Hynix
- Samsung

Domestic:

- DRAM ETF
- CXMT supply chain
- YMTC supply chain
- GigaDevice

### Equipment

Global:

- LRCX
- AMAT
- KLA
- ASML

Domestic:

- Piotech
- NAURA
- AMEC
- ACM Research Shanghai
- Hwatsing
- Kingsemi
- Wuxi Lead Intelligent / Weidao Nano

### Materials

Global:

- Entegris
- JSR
- Shin-Etsu
- SUMCO

Domestic:

- Dinglong
- Konfoong Materials
- Anji Microelectronics
- Fuchuang Precision
- Xinlai
- Gentech
- Do-Fluoride

### Bandwidth

Global:

- Corning
- Coherent
- Lumentum

Domestic:

- Zhongji Innolight
- Eoptolink
- TFC Communication
- Yangtze Optical Fibre
- Hengtong Optic-Electric
