# -*- coding: utf-8 -*-
from pathlib import Path

BASE = Path(__file__).parent

ARTICLES = [
    {
        "file": "Multi-Agent Harness-生产级架构评估记忆成本与MCP接入.md",
        "body_file": "_body_Multi-Agent Harness-生产级架构评估记忆成本与MCP接入.md",
        "frontmatter": """---
tags:
  - tech-article
  - Multi-Agent
  - Harness
  - MCP
  - Agent架构
  - 生产实践
created: 2026-05-13
category: 技术文章/AI
aliases:
  - Multi-Agent Harness
  - 生产级Harness设计
  - Harness操作系统
source: https://mp.weixin.qq.com/s/JPhcyDc4JwRmnMQ-76A-FQ
author: 李伟山（腾讯云开发者社区）
---""",
        "h1": "# Multi-Agent Harness：生产级架构、评估、记忆、成本与 MCP 接入",
        "meta": """> **原文链接**: [微信公众号](https://mp.weixin.qq.com/s/JPhcyDc4JwRmnMQ-76A-FQ)

> **原标题**: 从零设计生产级 Multi-Agent Harness：架构、评估、记忆、成本与 MCP 工具接入全拆解

> **一句话总结**: Harness 是 Multi-Agent 的「操作系统」——Agent 出主意、Harness 拿决定；五大模块（编排、Tool Registry、状态/记忆、四层 Eval、Token Budget）+ MCP 安全网关，是从 Demo 到生产的全景地图。

> **前置知识检查**:
> - [ ] 了解单 Agent vs 多 Agent 协作
> - [ ] 知道 MCP、Tool Calling 基本概念
> - [ ] （可选）读过 [[Harness工程化-五层架构与门禁阻断实践]]""",
        "img_note": "> **图片说明**: 正文配图 8 张位于 `assets/Multi-Agent Harness-生产级架构评估记忆成本与MCP接入/`（图1–8 为架构图；提取时含尾部推广图已裁剪）。",
        "analysis": r"""
## 核心概念脑图

```mermaid
mindmap
  root((Multi-Agent Harness))
    定位
      Agent操作系统
      非多Prompt拼盘
    五大模块
      架构编排
      Tool Registry
      状态与记忆
      四层Eval
      Token Budget
    原则
      Agent局部智能
      Harness全局控制
      声明式计划
    MCP
      标准化接入
      Registry网关
      白名单与HITL
```

## 与你已有知识的关联

**《[[Harness工程化-五层架构与门禁阻断实践|Harness 五层架构]]》**：国内五层门禁与本文 Orchestrator 硬终止、Tool Registry 同属 Harness 纪律；本文更偏 Multi-Agent 全景与 MCP。

**《[[Agent Harness Engineering-ETCLOVG七层框架综述|Agent Harness 综述]]》**：CMU 等 ETCLOVG 七层学术框架；本文是腾讯云视角的生产级五模块落地拆解，互补阅读。

**《[[Function Calling与MCP-Skills本质差异与最佳实践|MCP 与 Skills]]》**：MCP 标准化工具接入；本文第 07 节强调 MCP 须经 Tool Registry，不可裸奔直连 Agent。

**《[[Token成本控制-AI Coding Agent五层优化框架|Token 成本控制]]》**：五层优化框架与本文 Model Routing、Context Compression、Budget 分级降级同构。

**《[[企业级Agent-多智能体架构与选型指南|企业级多智能体]]》**：选型指南偏架构模式；本文补全运行时底座（记忆分层、轨迹 Eval、成本看板）。

## 重难点理解

- **重点1**: Agent 负责局部智能，Harness 负责全局控制 — Orchestrator 独占生命周期、路由、失败处理、硬终止；Planner 输出声明式计划而非命令式调用。
- **重点2**: Tool Registry 是安全边界 — 九项元信息（Schema、RBAC、风险等级、审计）；工具是「授权点」不是普通函数。
- **难点1**: 状态 vs 记忆 — Working/Session/Execution Log 三层状态 + Episodic/Semantic 记忆；混合检索时机 + 遗忘机制防污染。
- **难点2**: 四层 Eval — 组件、轨迹、任务完成度、端到端业务；LLM-as-Judge 不能替代事实/SQL/权限的确定性检查。
- **误区**: 「更强模型就能上生产」— Demo 与生产鸿沟在 Harness，不在 Prompt。

## 原文内容流程图

```mermaid
flowchart TD
  Demo[Demo: 多Agent拼盘] --> Gap[生产鸿沟]
  Gap --> H[Multi-Agent Harness]
  H --> M1[架构编排]
  H --> M2[Tool Registry]
  H --> M3[状态与记忆]
  H --> M4[四层Eval]
  H --> M5[Token Budget]
  H --> M6[MCP网关]
  M1 --> Phase[MVP→Hardening→Scale]
```

## 经验

1. **Day1 强制 Tool Registry**: 哪怕只有 3 个工具也走统一关口 — **应用场景**: 任何生产 Agent — **预期效果**: 避免「散落特权代码」后期无法收回。
2. **声明式计划**: Planner 输出 intent/agent/input 结构，Harness 可重排、拒绝、并行 — **应用场景**: 多步工作流 — **预期效果**: 不把方向盘交给 LLM。
3. **Eval 进 CI**: Prompt/模型/工具变更跑回归 — **应用场景**: 团队迭代 — **预期效果**: 优化从「凭感觉」变可度量。
4. **单位业务结果成本**: 监控「每完成一个合格任务多少钱」— **应用场景**: 成本运营 — **预期效果**: Agent 进入可运营阶段。

## 知识

| 知识点 | 定义 | 关键要素 | 关联概念 |
| --- | --- | --- | --- |
| Multi-Agent Harness | 收束多 Agent、工具、状态、编排、监控的运行时底座 | Orchestrator、Registry、Budget | Agent OS、LangGraph |
| 声明式计划 | 描述 step intent 而非直接 await 调用 | Harness 可介入、安全审查 | 条件边、工作流 |
| Trajectory Eval | 评估中间步骤与工具轨迹 | 防「答案对过程错」 | trace-native 评估 |
| Token Budget | 实时预算与绿黄红熔断 | Model Routing、压缩、降级 | 五层 Token 优化 |
| MCP 网关 | 标准化工具经 Registry 治理 | 白名单、配额、HITL、Trace | USB-C 类比 |

## 可复用建议

1. **落地三阶段**: Phase1 单链路 MVP → Phase2 Budget/权限/轨迹 Eval → Phase3 多租户/MCP 平台 — **适用场景**: 团队规划 — **预期效果**: 避免一步到位失败。
2. **记忆花园**: 低分删、中分压缩、高分保留 — **适用场景**: 长期记忆系统 — **预期效果**: 防检索噪声与成本爆炸。
3. **MCP 五实践**: 不经 Registry 不暴露、单 Server 配额、白名单、高风险 HITL、全 Trace — **适用场景**: MCP 接入 — **预期效果**: 便宜接入 + 可信调用。
4. **十个自检问题**: 任务怎么进、谁调度、状态放哪、预算怎么控… — **适用场景**: 方案评审 — **预期效果**: 越过 Demo 边界。

## 实施办法

1. **第1步**: 画任务状态机 + 四道硬闸（max_steps/tokens/duration/tool_calls）。
2. **第2步**: 实现最小 Tool Registry（3 工具也登记九项元信息）。
3. **第3步**: 分层 State/Session/Log + 混合记忆注入。
4. **第4步**: 建四层 Eval 数据集并进 CI；对照 [[专题/Claude-Code专题]] 与 [[Devix-7x24自动化运维Harness Engineering实践]] 看垂直场景。
""",
    },
    {
        "file": "Agent Harness Engineering-ETCLOVG七层框架综述.md",
        "body_file": "_body_Agent Harness Engineering-ETCLOVG七层框架综述.md",
        "frontmatter": """---
tags:
  - tech-article
  - Harness
  - Agent架构
  - ETCLOVG
  - 综述
  - 可观测性
created: 2026-05-27
category: 技术文章/AI
aliases:
  - Agent Harness综述
  - ETCLOVG
  - Harness Engineering
source: https://mp.weixin.qq.com/s/pG39PRnZFjSIxwYcPKD47A
author: Datawhale（译介 CMU/Yale/JHU 等论文）
---""",
        "h1": "# Agent Harness Engineering：ETCLOVG 七层框架综述",
        "meta": """> **原文链接**: [微信公众号](https://mp.weixin.qq.com/s/pG39PRnZFjSIxwYcPKD47A)

> **原标题**: 刚刚，一篇最全Agent Harness综述来了！

> **论文主页**: [Agent Harness Engineering: A Survey](https://picrew.github.io/LLM-Harness/)

> **一句话总结**: CMU 等 71 页综述：Agent 工程从 Prompt → Context → Harness 三阶段演进；ETCLOVG 七层（执行、工具、上下文、生命周期、可观测、验证、治理）+ trace-native 评估，竞争在模型外的工程外壳。

> **前置知识检查**:
> - [ ] 区分 Prompt / Context / Harness Engineering
> - [ ] 了解 Agent benchmark 与 pass rate 局限""",
        "img_note": "> **图片说明**: 配图 6 张位于 `assets/Agent Harness Engineering-ETCLOVG七层框架综述/`。",
        "analysis": r"""
## 核心概念脑图

```mermaid
mindmap
  root((Harness Engineering))
    三阶段演进
      Prompt Engineering
      Context Engineering
      Harness Engineering
    ETCLOVG七层
      Execution
      Tooling
      Context
      Lifecycle
      Observability
      Verification
      Governance
    核心判断
      同模型换外壳差10倍
      trace-native评估
      Framework到Platform
```

## 与你已有知识的关联

**《[[Multi-Agent Harness-生产级架构评估记忆成本与MCP接入|Multi-Agent Harness 生产拆解]]》**：本文学术七层框架；该文是腾讯云生产五模块实践，可对照 ETCLOVG 填具体实现。

**《[[Harness工程化-五层架构与门禁阻断实践|Harness 五层架构]]》**：国内 Harness 门禁实践落在 Lifecycle + Verification + Governance 层。

**《[[Token成本控制-AI Coding Agent五层优化框架|Token 成本]]》**：Context 层压缩与 Budget 策略；综述强调 harness coupling——改一层影响全局。

**《[[Claude Code记忆系统-得物自我进化与Hook观测实践|Hook 观测]]》**：Observability 层实例；Agent 行动后必须知道「做了什么、允许做什么」。

**《[[OpenClaw与Hermes-AI Agent架构源码复盘|OpenClaw/Hermes 复盘]]》**：Platform 级 durable workspace、sandbox、治理闭环与综述「Framework → Platform」趋势一致。

## 重难点理解

- **重点1**: 三阶段迁移 — Prompt 怎么说话 → Context 看见什么 → Harness 怎么可靠干活；长任务失败常因系统没管好模型。
- **重点2**: ETCLOVG 七层缺一不可 — 工具调用只是 Tooling 一层；缺 Observability/Governance 只能 demo 不能上线。
- **难点1**: trace-native 评估 — 记录全轨迹判结果、路径、评估器可信度；防重试刷分、过程不合规。
- **难点2**: harness coupling — 工具描述占上下文、沙箱影响 Eval；局部优化可能改变全系统行为。
- **误区**: 只换更强模型 — 论文案例：仅改 harness 格式可达 10×；GPT-5.2-Codex 同模型 52.8%→66.5%。

## 原文内容流程图

```mermaid
flowchart LR
  PE[Prompt Eng] --> CE[Context Eng] --> HE[Harness Eng]
  HE --> ETCLOVG[ETCLOVG七层]
  ETCLOVG --> Eval[trace-native评估]
  ETCLOVG --> Plat[Framework→Platform]
```

## 经验

1. **同模型对比 harness**: 优化前先固定模型测外壳 — **应用场景**: 团队归因失败 — **预期效果**: 避免误判为「模型不够强」。
2. **Observability+Governance 独立成层**: 不是 logging 附属 — **应用场景**: 生产 Agent — **预期效果**: 失败可定位、成功敢用。
3. **会删控制**: 模型变强后去掉过时 reset/verifier — **应用场景**: harness 维护 — **预期效果**: 降成本不损质量（Anthropic 长任务案例）。

## 知识

| 知识点 | 定义 | 关键要素 | 关联概念 |
| --- | --- | --- | --- |
| ETCLOVG | Agent Harness 七层分类 | Execution~Governance | 生产架构 |
| Harness Engineering | 模型外工程外壳 | 状态、工具、权限、验证、trace | Context Eng 下一阶段 |
| trace-native Eval | 以完整执行轨迹为评估对象 | 工具调用、重试、成本 | Trajectory Eval |
| harness coupling | 各层相互影响 | 工具占窗口、沙箱影响 benchmark | 系统思维 |
| Agent Platform | 超越 framework 的完整生产系统 | sandbox、identity、billing、HITL | 商业竞争 |

## 可复用建议

1. **用七层做架构评审表**: 每层打勾/缺口 — **适用场景**: 方案设计 — **预期效果**: 发现「只有模型+工具」的 demo 架构。
2. **建立 trace 标准字段**: 模型输出、工具返回、上下文快照、token、延迟 — **适用场景**: 评估流水线 — **预期效果**: 从排行榜回到质量控制。
3. **读论文 + 读生产文**: 综述 + [[Multi-Agent Harness-生产级架构评估记忆成本与MCP接入]] — **适用场景**: 学习路径 — **预期效果**: 理论框架落地对照。

## 实施办法

1. **第1步**: 打开 [论文主页](https://picrew.github.io/LLM-Harness/) 对照 ETCLOVG 给现有 Agent 打分。
2. **第2步**: 选一层最短板（多为 Observability 或 Verification）做最小补齐。
3. **第3步**: 固定模型做 harness A/B，记录 pass rate 与 trace 差异。
""",
    },
    {
        "file": "LLM Wiki-直播数据知识底座编译实践.md",
        "body_file": "_body_LLM Wiki-直播数据知识底座编译实践.md",
        "frontmatter": """---
tags:
  - tech-article
  - LLM-Wiki
  - 知识工程
  - RAG
  - 数据仓库
  - 得物
created: 2026-06-26
category: 技术文章/AI
aliases:
  - LLM Wiki实践
  - 直播数据Wiki
  - 知识编译器
source: https://mp.weixin.qq.com/s/6-xg2jJqIPbrqHcbjHBuTg
author: 楚翎、程知微
---""",
        "h1": "# LLM Wiki：直播数据知识底座编译实践",
        "meta": """> **原文链接**: [微信公众号](https://mp.weixin.qq.com/s/6-xg2jJqIPbrqHcbjHBuTg)

> **原标题**: 构建 AI 时代的知识底座：直播数据 LLM Wiki 实践

> **一句话总结**: 用「LLM 编译器」把散落 DDL/任务代码/文档编译为 Schema 约束的 Wiki 知识图，检索前解决口径矛盾；Wiki（编译时）+ RAG（运行时）+ 7 skill 编排，模型迭代影响分析提效 15–72×。

> **前置知识检查**:
> - [ ] 了解数仓分层、血缘、指标口径
> - [ ] 知道 RAG 局限（chunk 不解决知识质量）
> - [ ] （可选）读过 [[GBrain-Agent时代知识自组织与自进化体系]]""",
        "img_note": "> **图片说明**: 配图 12 张位于 `assets/LLM Wiki-直播数据知识底座编译实践/`。",
        "analysis": r"""
## 核心概念脑图

```mermaid
mindmap
  root((LLM Wiki))
    问题
      知识散落腐化
      RAG不编译源材料
    编译器
      提取生成归类聚合链接验证
      代码即真相
      生成与判断分离
    结构
      frontmatter+正文
      graph.json关系图
      域树渐进披露
    消费
      意图识别
      多路召回
      LLM精排
    运维
      增量编译
      持续Lint
```

## 与你已有知识的关联

**《[[GBrain-Agent时代知识自组织与自进化体系|GBrain 知识自组织]]》**：同属 LLM Wiki / 知识编译路线；本文是直播数据域落地细节（7 skill、graph.json、model-iteration 编排）。

**《[[verify-data一个端到端的数据验数Agent Skill|verify-data]]》**：数据验数 Skill；Wiki 支撑 SQL 生成与口径召回，验数做执行层校验。

**《[[得物活动Agent-从表单到LangGraph的社区活动搭建实践|得物活动 Agent]]》**：同厂 Agent 实践；Wiki 解决「知识喂不进去」，LangGraph 解决流程编排。

**《[[业务需求专家Agent-端到端搭建指南|需求专家 Agent]]》**：端到端 Agent 需领域知识底座；LLM Wiki 是数据团队侧的基础设施。

**《[[Token成本控制-AI Coding Agent五层优化框架|Token 成本]]》**：渐进式披露、域推断缩小召回范围，直接降低检索阶段上下文开销。

## 重难点理解

- **重点1**: Wiki 是编译时产物，RAG 是运行时手段 — 先编译高质量页面，再精准召回；不是二选一。
- **重点2**: 四可 — 结构可解析、层级可下钻、关系可遍历、正确性可度量（结构/语义/人工三层）。
- **难点1**: 生成与判断分离 — domain 等推断字段生成时留空，全局判断后人工确认；防 LLM 主观幻觉。
- **难点2**: 编排/干活分离 — wiki-orchestrator 只调度；6 个 skill 高内聚、文件系统契约交互。
- **误区**: 「上 RAG 就能答口径」— 源材料矛盾过期，RAG 只把「找不到」变「答不准」。

## 原文内容流程图

```mermaid
flowchart TD
  Raw[散落源材料] --> P0[Phase0材料预处理]
  P0 --> P1[Phase1基础+高阶Wiki]
  P1 --> Graph[graph.json]
  P1 --> HC[Phase2健康检查]
  HC --> Query[意图识别→多路召回→精排]
  Query --> Agent[SQL生成/模型迭代]
```

## 经验

1. **代码即真相**: 多源冲突以任务代码为准 — **应用场景**: 口径仲裁 — **预期效果**: 统一「以谁为准」。
2. **批内并行批间串行**: 基础 Wiki 每批 5 对象隔离上下文 — **应用场景**: 大规模编译 — **预期效果**: 提速且防张冠李戴。
3. **精排必读详情**: 不允许前几名匹配高就停 — **应用场景**: 表推荐 — **预期效果**: 枢纽表不被漏推。
4. **增量只对变化量**: sources 对账触发局部重跑 — **应用场景**: 日常维护 — **预期效果**: 成本与规模解耦。

## 知识

| 知识点 | 定义 | 关键要素 | 关联概念 |
| --- | --- | --- | --- |
| LLM 编译器 | 源材料→结构化 Wiki 的流水线 | 六步：提取~验证 | 知识工程 |
| frontmatter 契约 | YAML 承载关系字段 | upstream、domain、sources | Schema |
| graph.json | 8 种节点 8 种边 | 只存正向边、回填 downstream | 血缘影响分析 |
| 渐进式披露 | 域树逐层下钻 | index.md 域推断 | 上下文预算 |
| model-iteration-analysis | 6 步模型迭代编排 | 血缘完整性、风险矩阵 | 数据研发提效 |

## 可复用建议

1. **先 Wiki 后 RAG**: 编译期固化口径与血缘 — **适用场景**: 数据/业务知识库 — **预期效果**: 召回质量质变。
2. **三态 raw 目录**: ready/pending/archive — **适用场景**: 材料治理 — **预期效果**: 低质量不进编译。
3. **每周 Lint**: 健康检查规则持续跑 — **适用场景**: 运维期 — **预期效果**: 断链/孤岛早发现。
4. **复用 model-iteration 六步**: 需求拆解→召回→血缘→风险→SQL→报告 — **适用场景**: 数仓变更 — **预期效果**: 半天→小时级（文内数据）。

## 实施办法

1. **第1步**: 定 KB_ROOT 目录树（pre/raw/wiki/log/schema）与 5 类页面 Schema。
2. **第2步**: Phase0 脚本化抓取 DDL+任务代码，三态分流。
3. **第3步**: 基础 Wiki 批内并行生成，判断阶段回填 domain。
4. **第4步**: graph.json 构建 + 健康检查；检索侧实现域推断与多路召回；对照 [[GBrain-Agent时代知识自组织与自进化体系]] 看企业级扩展。
""",
    },
]

for art in ARTICLES:
    body = (BASE / art["body_file"]).read_text(encoding="utf-8")
    parts = [
        art["frontmatter"],
        "",
        art["h1"],
        "",
        art["meta"],
        "",
        "## 原文",
        "",
        body.rstrip(),
        "",
        art["img_note"],
        "",
        "---",
        art["analysis"].strip(),
    ]
    (BASE / art["file"]).write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("Wrote", art["file"])

# cleanup temp
for art in ARTICLES:
    (BASE / art["body_file"]).unlink(missing_ok=True)
(BASE / "_gen_bodies.py").unlink(missing_ok=True)
