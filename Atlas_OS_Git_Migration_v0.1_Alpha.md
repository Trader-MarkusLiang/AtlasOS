# Atlas OS Git 迁移执行文档 v0.1

> 目标：先解决 Atlas OS 核心框架在 Git 中重建、固化、版本管理的问题。  
> 原则：不做复杂软件工程，不写大篇幅蓝图，不提前开发功能。  
> 当前阶段：Knowledge Repository / Core Framework Migration。

---

## 1. 本次任务边界

本次 Codex 任务不是开发 Atlas 软件系统，而是完成：

1. 新建 Atlas Git 项目；
2. 重建 Atlas OS 核心框架；
3. 将 Atlas 的原则、推理链、交易系统、数据库结构固化为 Markdown；
4. 建立版本管理；
5. 建立迁移验证机制。

本阶段不做：

- Dashboard；
- Web 前端；
- API；
- 自动抓取；
- 数据库开发；
- Agent 自动化；
- 复杂软件架构设计。

一句话：

> 先把 Atlas 的“核心大脑”迁移到 Git，再考虑工具化。

---

## 2. Atlas OS 的本质

Atlas OS 不是传统软件项目，而是：

> AI 模型驱动的投资研究与交易决策知识系统。

核心价值不是代码，而是：

- 研究框架；
- 推理链条；
- 资本迁移逻辑；
- AI 瓶颈地图；
- Trading OS；
- 交易纪律；
- 可持续迭代的知识库。

Git 的作用是：

1. 保存 Atlas 的核心知识资产；
2. 支持版本管理；
3. 让 Codex / ChatGPT / 未来 Agent 能读取同一份框架；
4. 避免 Atlas 只存在于聊天上下文中导致丢失。

---

## 3. 推荐项目结构

Codex 创建单一 Git 仓库即可。

```text
Atlas-OS/
├── README.md
├── VERSION.md
├── CHANGELOG.md
│
├── 00_Core/
│   ├── Atlas_Core.md
│   ├── Atlas_Principles.md
│   ├── Seven_Layer_Reasoning.md
│   └── Trading_Discipline.md
│
├── 01_Framework/
│   ├── AI_Bottleneck_Index.md
│   ├── Capital_Relay.md
│   ├── ROI_Engine.md
│   ├── Efficiency_Multiplier.md
│   └── Timing_Engine.md
│
├── 02_Databases/
│   ├── AI_Shovel_100.md
│   ├── Alpha_Radar.md
│   ├── Order_Book.md
│   ├── Risk_Radar.md
│   └── Price_Transmission.md
│
├── 03_Trading_OS/
│   ├── Daily_Dashboard_Template.md
│   ├── Trading_Decision_Table.md
│   ├── Capital_Allocation_Board.md
│   └── Capital_Rotation_Table.md
│
├── 04_Current_State/
│   ├── AI_Capital_Map_v1.md
│   ├── Bottleneck_Map_v1.md
│   ├── Current_Holdings_Strategy.md
│   └── Second_Growth_Curve.md
│
├── 05_Cases/
│   ├── Apple_CXMT.md
│   ├── DeepSeek_Spark.md
│   ├── Nomura_FCF.md
│   ├── Corning_Bandwidth.md
│   └── Korea_Memory_Capex.md
│
└── 99_Verification/
    ├── Migration_Checklist.md
    ├── Regression_Tests.md
    └── Acceptance_Criteria.md
```

---

## 4. Atlas 核心原则

写入：

```text
00_Core/Atlas_Principles.md
```

必须包含：

1. Follow Capital, Not Noise.  
   追踪资本，而非情绪。

2. Capital Always Follows ROI.  
   资本最终追逐 ROI。

3. Research the Future. Trade the Transition.  
   研究未来，交易拐点。

4. 热点只是 Signal，不是 Action。

5. 产业决定方向，交易决定仓位。

6. 高信念 + 高赔率，才值得重仓。

7. Atlas 不是为了证明自己正确，而是为了不断接近真实世界。

8. 如果事实改变，Atlas 必须修正模型。

---

## 5. 七层推理链

写入：

```text
00_Core/Seven_Layer_Reasoning.md
```

任何新闻、观点、图表、研报都必须经过：

```text
L0 Fact（事实）
 ↓
L1 Physics（物理瓶颈）
 ↓
L2 Engineering（工程实现）
 ↓
L3 Economics（经济学）
 ↓
L4 Finance（财务）
 ↓
L5 Capital（资本）
 ↓
L6 Trading（交易）
```

目标：

不是解释新闻，而是判断：

1. 是否改变事实；
2. 是否改变瓶颈；
3. 是否改变 ROI；
4. 是否改变资本流向；
5. 是否改变交易动作。

---

## 6. AI Bottleneck Index

写入：

```text
01_Framework/AI_Bottleneck_Index.md
```

Atlas 不按传统行业分类，而按 AI 系统瓶颈分类。

| 瓶颈 | 内容 |
|---|---|
| Compute | GPU / ASIC |
| Memory | HBM / DRAM / NAND / SSD |
| Equipment | 刻蚀 / 沉积 / 清洗 / CMP |
| Materials | 靶材 / 前驱体 / CMP材料 / 氢氟酸 / 石英 / 硅片 |
| Bandwidth | 光模块 / CPO / 光纤 / 光互连 |
| Power | 电力 / 液冷 / 变压器 / UPS |
| Workflow | 企业 AI 工作流 |
| Industry AI | 行业 AI / 机器人 / 自动驾驶 |

当前 v0.1 判断：

| 瓶颈 | 当前状态 |
|---|---|
| Memory | S+ |
| Equipment | S+ |
| Materials | S |
| Bandwidth | S |
| Power | A |
| Workflow | B+ |
| Industry AI | B |

---

## 7. Capital Relay

写入：

```text
01_Framework/Capital_Relay.md
```

当前资本迁移路径：

```text
Compute / GPU
 ↓
Memory / HBM / DRAM
 ↓
PCB / CCL / 铜箔
 ↓
Equipment
 ↓
Materials
 ↓
Bandwidth
 ↓
Power
 ↓
Workflow
 ↓
Industry AI
```

当前判断：

> Atlas 目前处于 Memory 强化、Equipment 接力、Materials 启动、Bandwidth 纳入一级主线的阶段。

---

## 8. ROI Engine

写入：

```text
01_Framework/ROI_Engine.md
```

核心原则：

> Capital Always Follows ROI.

重点跟踪：

| 指标 | 含义 |
|---|---|
| AI CapEx | 云厂是否继续投资 |
| AI Revenue | 是否转化收入 |
| FCF | 自由现金流是否被吞噬 |
| Token Growth | 使用量是否增长 |
| Inference Capacity | 推理是否仍供不应求 |
| Enterprise AI ROI | 企业是否愿意持续付费 |

交易判断：

| 情况 | 含义 |
|---|---|
| CapEx 增长 + ROI 改善 | 看多卖铲人 |
| CapEx 增长 + ROI 恶化 | 警惕估值杀 |
| CapEx 放缓 + ROI 不明 | 防守 |
| ROI 改善 + 估值回调 | 加仓窗口 |

---

## 9. Efficiency Multiplier

写入：

```text
01_Framework/Efficiency_Multiplier.md
```

用于判断 AI 算法优化到底是削弱硬件需求，还是放大硬件需求。

典型逻辑：

```text
推理效率提升
 ↓
Token 成本下降
 ↓
调用量增加
 ↓
Agent 更多
 ↓
推理时长增加
 ↓
Memory / GPU / Bandwidth 总需求上升
```

核心经济学：

> Jevons Paradox：效率提升可能扩大资源总消耗。

案例：

- DeepSeek Spark；
- Speculative Decoding；
- Flash Attention；
- MoE；
- KV Cache 优化。

---

## 10. Trading OS

写入：

```text
03_Trading_OS/
```

Trading OS 的目标：

> 把研究结论转化为仓位动作。

每日输出应该控制在一页：

```markdown
# Atlas Daily Trading Dashboard

日期：

## 今日是否交易
YES / NO

## 今日一句话结论

## AI Bottleneck Index
| 模块 | 状态 | 变化 |
|---|---|---|

## Capital Relay
当前资本位置：

## 今日动作
| 动作 | 方向/标的 | 仓位 | 理由 |
|---|---|---:|---|

## 风险等级
低 / 中 / 高

## 等待触发条件
- ...
```

---

## 11. 交易动作模板

写入：

```text
03_Trading_OS/Trading_Decision_Table.md
```

每个交易动作必须包含：

1. Action（动作）；
2. Confidence（信心）；
3. Logic Chain（逻辑链）；
4. Evidence（证据）；
5. Risk / Reward（风险收益比）；
6. Trigger（触发条件）；
7. Counter Argument（反方观点）；
8. Review Plan（复盘计划）。

---

## 12. Capital Allocation Board

写入：

```text
03_Trading_OS/Capital_Allocation_Board.md
```

示例：

| 市场状态 | 是否交易 | 资金来源 | 资金去向 | 建议比例 |
|---|---|---|---|---:|
| AI逻辑继续，指数横盘 | 否 | - | - | 保持现金 |
| 大盘回调8%~10% | 是 | 现金 | Equipment | 现金30%~40% |
| 大盘回调12%~15% | 是 | 现金+部分利润 | Equipment + Memory | 分批 |
| 系统性恐慌但产业未变 | 是 | 预留现金 | 第一、第二增长曲线 | 提高总仓 |

---

## 13. 当前持仓策略

写入：

```text
04_Current_State/Current_Holdings_Strategy.md
```

当前已知持仓：

- 美股资金：约 70% 在 DRAM / Memory 方向；
- 国内资金：
  - 泰金新能 688813；
  - 罗博特科；
  - 东山精密；
  - 德福科技。

已知仓位：

- 泰金成本约 160，当前盈利约 40%，原占约 37%，已平掉 30%；
- 罗博约 14%；
- 东山约 20%；
- 德福约 20%；
- 现金约 20%左右。

当前策略：

| 方向 | 动作 |
|---|---|
| DRAM ETF | 核心持有 |
| 泰金 | 持有，若加速拉升可作为资金来源 |
| 东山 | 持有 |
| 德福 | 持有 |
| 罗博 | 持有观察 |
| 现金 | 等待 Equipment / Materials 回调窗口 |

---

## 14. AI卖铲人100

写入：

```text
02_Databases/AI_Shovel_100.md
```

评分维度：

| 维度 | 权重 |
|---|---:|
| 技术壁垒 | 20% |
| 订单确定性 | 20% |
| 三年业绩弹性 | 20% |
| 资本认可度 | 15% |
| 当前交易位置 | 15% |
| 定价权 | 5% |
| 是否处于当前瓶颈 | 5% |

初始候选池：

### Memory

全球：
- Micron
- SK Hynix
- Samsung

国内：
- DRAM ETF
- 长鑫产业链
- 长江存储产业链
- 兆易创新

### Equipment

全球：
- LRCX
- AMAT
- KLA
- ASML

国内：
- 拓荆科技
- 北方华创
- 中微公司
- 盛美上海
- 华海清科
- 芯源微
- 微导纳米

### Materials

全球：
- Entegris
- JSR
- Shin-Etsu
- SUMCO

国内：
- 鼎龙股份
- 江丰电子
- 安集科技
- 富创精密
- 新莱应材
- 正帆科技
- 多氟多

### Bandwidth

全球：
- Corning
- Coherent
- Lumentum

国内：
- 中际旭创
- 新易盛
- 天孚通信
- 长飞光纤
- 亨通光电

---

## 15. 回归测试案例

写入：

```text
99_Verification/Regression_Tests.md
```

必须保留以下案例：

### Case 1：苹果采购长鑫

期望输出：

- 强化 Memory；
- 强化国产替代；
- 强化 Equipment / Materials；
- 不直接追高长鑫概念。

### Case 2：DeepSeek Spark

期望输出：

- 引入 Jevons Paradox；
- 推理效率提升可能放大 Token 需求；
- Memory / Equipment 仍受益。

### Case 3：野村 FCF 图

期望输出：

- AI 巨头短期重资产化；
- 卖铲人受益；
- 跟踪 ROI / FCF。

### Case 4：Corning

期望输出：

- Bandwidth 升级为一级瓶颈；
- 不直接追高；
- 寻找国内 Bandwidth 受益链。

### Case 5：韩国 Memory CapEx

期望输出：

- 强化 Memory；
- 更强化 Equipment / Materials；
- 不直接认为周期结束。

### Case 6：Google 限制 Meta 使用 Gemini

期望输出：

- 推理算力仍供不应求；
- AI Infrastructure Gap 扩大；
- Memory / Equipment / Materials 继续受益；
- 不追高，等回调。

---

## 16. 迁移验收标准

写入：

```text
99_Verification/Acceptance_Criteria.md
```

迁移成功必须满足：

1. Git 仓库创建完成；
2. 核心目录存在；
3. Atlas 核心原则写入；
4. 七层推理链写入；
5. AI Bottleneck Index 写入；
6. Capital Relay 写入；
7. Trading OS 模板写入；
8. 当前持仓策略写入；
9. AI卖铲人100 初始池写入；
10. 回归测试案例写入；
11. `VERSION.md` 记录 v0.1 Alpha；
12. `CHANGELOG.md` 记录首次迁移；
13. Git tag：`v0.1-alpha`。

---

## 17. Codex 执行命令

```bash
mkdir Atlas-OS
cd Atlas-OS
git init

mkdir -p 00_Core
mkdir -p 01_Framework
mkdir -p 02_Databases
mkdir -p 03_Trading_OS
mkdir -p 04_Current_State
mkdir -p 05_Cases
mkdir -p 99_Verification
```

完成文件拆分后：

```bash
git add .
git commit -m "Initialize Atlas OS knowledge framework v0.1 alpha"
git tag v0.1-alpha
```

如需推送 GitHub：

```bash
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
git push origin v0.1-alpha
```

---

## 18. Codex 注意事项

请 Codex 严格遵守：

1. 本阶段只做 Git 知识框架重建；
2. 不开发 Dashboard；
3. 不开发自动化；
4. 不开发 Agent；
5. 不做数据库；
6. 不扩展复杂软件架构；
7. 不擅自修改 Atlas 核心原则；
8. 完成后输出文件树和迁移验证结果。

---

## 19. 最终目标

本阶段完成后，Atlas OS 应该做到：

> 即使换新聊天、换模型、换Codex，只要加载 Git 仓库，就能恢复 Atlas 的核心框架、推理方式和交易纪律。

这是 v0.1 Alpha 的唯一目标。
