# Atlas OS Git Migration Blueprint v0.2 Alpha

> 本文档整合了 **迁移规范 + Git 建设规范 + Audit 审计规范**。\
> Codex 应仅依据本文件完成 Atlas OS v0.2 Alpha 的初始化与验证。

------------------------------------------------------------------------

# 一、项目目标

Atlas OS 不是传统软件项目，而是 **AI 驱动的投资研究与交易知识系统**。

当前阶段唯一目标：

1.  建立 Git 仓库；
2.  重建 Atlas 核心知识框架；
3.  建立版本管理；
4.  建立知识审计（Audit）机制；
5.  确保 Atlas 可以持续演化，而不会因聊天上下文丢失。

本阶段禁止开发：

-   Dashboard
-   Agent
-   自动抓取
-   Web 前端
-   API
-   数据库程序

------------------------------------------------------------------------

# 二、推荐目录结构

``` text
Atlas-OS/
├── README.md
├── VERSION.md
├── CHANGELOG.md
├── 00_Core/
├── 01_Framework/
├── 02_Databases/
├── 03_Trading_OS/
├── 04_Current_State/
├── 05_Cases/
└── 99_Verification/
```

------------------------------------------------------------------------

# 三、核心知识模块（必须完成）

## 00_Core

-   Atlas Principles
-   Seven Layer Reasoning
-   Trading Discipline

## 01_Framework

-   AI Bottleneck Index
-   Capital Relay
-   ROI Engine
-   Efficiency Multiplier
-   Timing Engine

## 02_Databases

-   AI Shovel 100
-   Alpha Radar
-   Risk Radar
-   Order Book
-   Price Transmission

## 03_Trading_OS

-   Daily Dashboard Template
-   Trading Decision Table
-   Capital Allocation Board
-   Capital Rotation Table

## 04_Current_State

保存当前市场判断、持仓策略、瓶颈地图、第二增长曲线等。

## 05_Cases

保存所有经典案例，作为长期知识资产。

------------------------------------------------------------------------

# 四、Atlas 核心原则

1.  Follow Capital, Not Noise.
2.  Capital Always Follows ROI.
3.  Research the Future. Trade the Transition.
4.  热点只是 Signal，不是 Action。
5.  产业决定方向，交易决定仓位。
6.  高信念 + 高赔率才值得重仓。
7.  如果事实改变，Atlas 必须修正模型。

------------------------------------------------------------------------

# 五、七层推理链

``` text
Fact
↓
Physics
↓
Engineering
↓
Economics
↓
Finance
↓
Capital
↓
Trading
```

所有新闻必须完成七层推理，最终输出交易动作。

------------------------------------------------------------------------

# 六、知识审计（Audit）【新增】

## Audit Philosophy

Git 构建成功 ≠ Atlas 迁移成功。

真正需要验证的是：

> Knowledge Consistency（知识一致性）

------------------------------------------------------------------------

## Audit Level 1：Structure

检查：

-   Git Repository
-   目录
-   VERSION
-   CHANGELOG
-   Git Tag

------------------------------------------------------------------------

## Audit Level 2：Knowledge

必须验证以下知识是否完整：

-   Atlas Principles
-   Seven Layer Reasoning
-   AI Bottleneck Index
-   Capital Relay
-   ROI Engine
-   Efficiency Multiplier
-   Trading OS
-   AI Shovel 100

输出：

Knowledge Coverage %

------------------------------------------------------------------------

## Audit Level 3：Reasoning

必须重新推导以下案例：

-   Apple + CXMT
-   DeepSeek Spark
-   Google / Gemini
-   Corning
-   Nomura FCF
-   Korea Memory CapEx
-   HBM Supercycle
-   DRAM Supercycle

若结论明显偏离历史共识，则 Audit FAIL。

------------------------------------------------------------------------

## Audit Level 4：Trading

验证 Trading OS 是否仍能正确输出：

-   当前 Bottleneck 排名
-   当前 Capital Relay
-   当前仓位建议
-   当前风险等级
-   当前等待条件

------------------------------------------------------------------------

# 七、Regression Test

每次版本发布前至少回归：

-   Apple CXMT
-   DeepSeek Spark
-   Nomura
-   Corning
-   Google Gemini
-   Korea Memory CapEx

任何 FAIL：

禁止发布。

------------------------------------------------------------------------

# 八、Audit Report（必须生成）

Codex 每次迁移完成必须生成：

``` text
Atlas Audit Report

Version:

Structure:

Knowledge:

Reasoning:

Trading:

Knowledge Coverage:

Missing Modules:

Recommendation:
```

不得仅输出：

FINAL_VERIFY_OK

必须提供完整 Audit Report。

------------------------------------------------------------------------

# 九、发布门禁（Release Gate）

只有满足以下条件才允许 Merge：

-   Structure PASS
-   Knowledge PASS
-   Reasoning PASS
-   Trading PASS
-   Regression PASS

------------------------------------------------------------------------

# 十、Codex 执行原则

1.  本阶段目标是建设 Atlas，而不是开发 Atlas。
2.  核心知识优先于功能。
3.  不得修改 Atlas 核心原则。
4.  每次提交必须更新 CHANGELOG。
5.  每次发布必须生成 Audit Report。

------------------------------------------------------------------------

# 十一、版本目标

## v0.1 Alpha

建立 Git 知识仓库。

## v0.2 Alpha

补全核心知识体系并建立完整 Audit。

## v1.0

Atlas 成为可持续演进的 AI Knowledge OS。
