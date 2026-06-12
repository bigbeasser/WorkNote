# 金仕达 CTRM 系统知识库

> **大宗商品贸易 ERP 系统** — 涉及合金、半成品、产成品等商品的贸易与风险管理

---

## 快速导航

| 模块 | 说明 | 文档数量 |
|------|------|---------|
| [:material-code-braces: 代码分析](公司代码文档/index.md) | 代码调用链分析、类/方法详解、架构图 | 1 |
| [:material-file-document: 需求文档](公司需求文档/index.md) | 业务需求、功能规格、接口定义 | 6 |
| [:material-bug: 问题排查](问题排查记录/index.md) | 故障排查记录、解决方案、经验总结 | 0 |
| [:material-book-open: 业务概念](业务概念/index.md) | CTRM 业务术语、流程说明、概念解释 | 1 |
| [:material-file-edit: 文档模板](模板/index.md) | 标准文档模板，新建文档时直接复制使用 | 3 |

---

## 高频问题速查

!!! tip "如何使用本知识库"
    1. **搜索功能**：使用页面右上角的搜索框，支持中英文关键词搜索
    2. **标签筛选**：每篇文档头部都有标签，可以通过标签快速定位相关文档
    3. **问题排查**：遇到问题先到「问题排查」模块查找是否有类似记录
    4. **贡献文档**：解决问题后，请使用「文档模板」记录，方便后续查阅

---

## 最近更新

| 日期 | 类型 | 内容 |
|------|------|------|
| 2026-06-02 | :material-file-document: | 新增 [升贴水明细表优化](公司需求文档/升贴水明细表优化/index.md) |
| 2026-06-02 | :material-file-document: | 新增 [Greenlist Price 需求方案](公司需求文档/Greenlist-Price需求方案/index.md) |
| 2026-06-02 | :material-file-document: | 新增 [Claim Report & Lab 需求](公司需求文档/Claim-Report-Lab需求/index.md) |
| 2026-06-02 | :material-file-document: | 新增 [E-service 送货预约需求](公司需求文档/Eservice送货预约需求/index.md) |
| 2026-06-02 | :material-file-document: | 新增 [升贴水报表涉及主数据优化](公司需求文档/升贴水报表主数据优化/index.md) |
| 2026-06-02 | :material-file-document: | 新增 [单据打印合同模板（采购）优化](公司需求文档/单据打印合同模板采购优化/index.md) |
| 2026-06-02 | :material-book-open: | 新增 [CTRM 业务术语表](业务概念/CTRM业务术语表/index.md) |
| 2026-06-02 | :material-rocket: | 知识库初始化搭建 |
| 2026-06-01 | :material-code-braces: | 新增 [ExecuteHMEFlowTask 调用链分析](公司代码文档/ExecuteHMEFlowTask调用链分析/index.md) |

---

## 系统架构概览

```
金仕达 CTRM 系统
├── bcadmin-system     # 系统核心模块（Quartz 调度、Activiti 工作流、EOD 日结）
├── bcadmin-common     # 公共工具模块（Redis 工具、任务跟踪、枚举常量）
├── bcadmin-db         # 数据层模块（实体类、Mapper）
└── 外部系统
    ├── CRM            # 客户关系管理（定价锁定/解锁、交易时段推送）
    └── SAP            # 企业资源计划（交易时段推送、库存数据同步）
```

---

## 技术栈

| 技术 | 用途 |
|------|------|
| Java + Spring | 核心业务框架 |
| Quartz | 定时任务调度 |
| Activiti | BPMN 工作流引擎 |
| Redis | 状态管理 & 缓存 |
| CRM / SAP | 外部系统集成 |
