---
tags:
  - 索引
  - MOC
  - LangGraph
  - 个人学习
created: 2026-06-25
category: 个人学习/LangGraph
aliases:
  - LangGraph索引
  - LangGrash索引
---

# 📋 LangGraph 学习索引

> LangGraph 企业级落地与 Agent 工作流编排知识入口。

---

## 📊 文章总览

| # | 文章 | 核心主题 |
| --- | --- | --- |
| 1 | [[LangGraph 企业级落地实战报告]] | 生产数据、四行业落地案例、部署架构、ROI |

---

## 🏭 企业落地案例速查

| 案例 | 行业 | LangGraph 关键能力 | 核心指标 |
| --- | --- | --- | --- |
| 智能质检 | 制造业 | 多 Agent 并行 + 人工复核 + Checkpoint | 准确率 99.2%，速度 +300% |
| 风控审批 | 金融科技 | 条件边分流 + 审计追踪 + 中断恢复 | 审批 3-5天→2小时，自动化 78% |
| 旅行规划 | 互联网 | 并行查询 + 长任务持久化 | 可用性 99.99%，客服 -60% |
| 库存优化 | 零售电商 | 7×24 长运行 + K8s 弹性扩缩 | 库存准确率 +40% |

详见 [[LangGraph 企业级落地实战报告#三、企业落地案例与量化效果]]。

---

## 🔧 架构要点速查

| 能力 | 说明 | 详见 |
| --- | --- | --- |
| StateGraph + Reducer | 不可变快照、增量更新、并行聚合 | [[LangGraph 企业级落地实战报告#2.2 StateGraph 状态管理机制]] |
| Checkpoint | exit / async / sync 三档持久化 | [[LangGraph 企业级落地实战报告#2.3 持久化执行（Durable Execution）]] |
| interrupt() | 人机协作原生支持 | [[LangGraph 企业级落地实战报告#2.1 核心架构对比]] |
| 生产部署 | LB → Server Cluster → Redis → PostgreSQL | [[LangGraph 企业级落地实战报告#5.2 生产部署架构建议]] |
| 常见陷阱 | 状态过大、Reducer 错误、无限循环等 | [[LangGraph 企业级落地实战报告#5.3 常见陷阱与规避]] |

---

## 📖 推荐阅读路径

### 🟢 入门：理解 LangGraph 定位

1. [[LangGraph 企业级落地实战报告#二、LangGraph 架构深度解析]] — 与 LangChain LCEL 对比、StateGraph 机制
2. [[../../大厂技术文章-DailyTech/从表单到 Agent：得物社区活动搭建的 AI 实践之路|得物活动 Agent 实践]] — 国内 Interrupt/Resume 落地

### 🟡 工程实践：选型与部署

1. [[LangGraph 企业级落地实战报告#5.1 适用场景判断]] — 何时选 LangGraph vs 低代码
2. [[LangGraph 企业级落地实战报告#5.2 生产部署架构建议]] — Redis + PostgreSQL 分层存储
3. [[LangGraph 企业级落地实战报告#5.3 常见陷阱与规避]] — 上线前 checklist

### 🔴 深度：行业案例与 ROI

1. [[LangGraph 企业级落地实战报告#案例二：城商行智能风控审批系统]] — 金融合规 + 条件边
2. [[LangGraph 企业级落地实战报告#案例一：汽车零部件制造商智能质检系统]] — 工业多 Agent 并行
3. [[LangGraph 企业级落地实战报告#四、LangGraph ROI 与效能数据]] — 开发/运维量化数据

---

## 🔗 关联笔记（跨库双向链接）

| 方向 | 笔记 | 关联点 |
| --- | --- | --- |
| 国内实战 | [[../../大厂技术文章-DailyTech/从表单到 Agent：得物社区活动搭建的 AI 实践之路\|得物活动 Agent]] | LangGraph Workflow、Checkpointer、interrupt |
| Agent 架构 | [[../../大厂技术文章-DailyTech/如何搭建一个端到端业务需求专家 Agent\|需求专家 Agent]] | 四层架构、纵向闭环 |
| 告警排查 | [[../../大厂技术文章-DailyTech/用 LLM Agent 重构告警排查流程｜得物技术\|告警排查 Agent]] | ReAct、多 Agent 协作 |
| LLM 基础 | [[../../LLM大模型类相关知识/LLM大模型学习\|LLM 大模型学习]] | Agent 概念、SSE 等基础 |
| 总索引 | [[../../大厂技术文章-DailyTech/📋 文章索引\|技术文章总索引]] | DailyTech 全库入口 |

---

## 🏷️ 标签

`#LangGraph` `#Agent架构` `#AI落地` `#Human-in-the-loop` `#Checkpoint` `#生产实践`

---

## 🔧 维护说明

新增 LangGraph 相关笔记时：

1. 在「文章总览」末尾追加一行
2. 在「推荐阅读路径」中找到合适位置追加
3. 更新「关联笔记」表
4. 在新笔记 frontmatter 中添加 `category: 个人学习/LangGraph` 并在文末链接回 [[📋 LangGraph索引]]

---

*最后更新: 2026-06-25（+LangGraph 企业级落地实战报告）*
