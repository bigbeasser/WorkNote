---
title: E-service 送货预约需求
tags: [Eservice, 送货预约, Delivery Booking, 物料限制, 仓库管理, 供应商]
module: 仓储物流
date: 2025-04-01
type: requirement
related: []
---

# REQ-004 E-service 送货预约需求

> 需求编号: REQ-004
> 提出日期: 2025-04-01
> 优先级: 高
> 状态: 已确认
> 原始文档: [Eservice.docx](Eservice.docx)

---

## 一、需求背景

工厂一天的存放能力有限，所以需要供应商可以**预定自己哪天送货**以及把实际的送货跟预定关联起来（释放预定）。

- **仓库人员**：更清楚地知道未来几天可能会收到哪些量 & 种类的货
- **生产工厂**：据此提醒采购团队 push 送哪些种类的货
- **采购团队**：更清楚地管理供应商的送货情况，避免同一天送太多工厂放不下

---

## 二、功能模块

### 2.1 设定限制 — Material Constraints Management

概述：Article Group 层面上，可以设置月度最大收货量、某一天不能收货等规则。

物料组管理：对接配置 → 商品组，初始化数据。

#### 2.1.1 Monthly Constraints List — 月度限制

**筛选条件**：工厂 / 物料组 / 开始年份-月份 / 结束年份-月份

| 字段(英文) | 字段(中文) | 说明 |
|-----------|-----------|------|
| Identification | 唯一标识 | 年月递增，如 250401、250402 |
| Company | 业务机构 | — |
| Plant | 工厂 | — |
| Article group | 物料组 | 编码+描述，取自对接配置-商品组 |
| Month | 月份 | — |
| Year | 年份 | — |
| Max quantity(TO) | 最多送货量 | — |

**操作按钮**：

- **新增(Add)**：弹窗录入，确认后显示在列表页
  - 校验：同一个物料组 + 同一年份 + 同一月份只能有一条数据（错误提示：`already exist {{identification}}`）
- **编辑**：单选一条数据，弹窗字段同录入页
- **删除**：单选一条从列表删除

#### 2.1.2 Constraints List — 日度限制（新页面）

规定某一天（如工厂休息）不能收货。

| 字段(英文) | 字段(中文) | 说明 |
|-----------|-----------|------|
| Plant | 工厂 | — |
| Start date | 开始日期 | — |
| End date | 结束日期 | 默认=开始日期，允许修改 |
| Max qty(TO) | 重量限制 | — |

**操作按钮**：新增 / 编辑（其他字段置灰只允许修改最大重量）/ 删除

#### 2.1.3 Summary 报表

概述：物料组维度的、按日的、允许收货和实际收货情况以及汇总值。

**查询条件**：工厂 / 物料组 / 开始日期 / 结束日期（不能跨自然月）

**汇总值计算**：

| 汇总字段(英文) | 说明 |
|---------------|------|
| Arrived total | 开始日期截至查询当日，booking list 里状态为"已收货"的物料对应到物料组的数量汇总 |
| Expired total | 开始日期截至查询当日，booking list 里状态为"未收货"的数量汇总 |
| Reservation total | booking list 里物料所属物料组当月且结束日期在查询日期之后已预定数量汇总 |
| Total from the template | 该物料组在查询月度限制的总量 |
| Reserved and arrival total | 查询日前的实际收货量 + 查询日至月底的预定量 |
| Available to be reserved total | `Total from the template - Reserved and arrival total` |

!!! warning "收货物料与预定不一致时"
    在 booking list 上点了收货后，如果实际收到的物料跟预定的不一致，会在 Summary 表里自动**减少**预定物料所属物料组的 `Total from the template`，并自动**增加**实际送达物料所属物料组的月度限定量。

#### 2.1.4 Booking List — 预约送货清单

功能 2 提交完出现在这个表（功能 2 收了之后也更新这张表）。

**查询条件**：工厂 / 物料组 / 物料 / 开始日期 / 结束日期

---

### 2.2 预约送货功能 — Delivery Booking

**筛选条件**：供应商 / 工厂 / 物料 / 预定号 / 状态 / 开始日期 / 结束日期

| 字段(英文) | 字段(中文) | 说明 |
|-----------|-----------|------|
| Reserv. num | 预定号 | — |
| Movement code | 物料移动码 | — |
| Date | 实际送货日期 | 收货之后更新 |
| Slot Duration | 预定送货时间 | — |
| Quantity | 预定送货量 | — |
| Status | 状态 | 码值：未收货 / 已收货 / 已删除 / 已拒收 |
| Plant | 工厂 | — |
| Supplier | 供应商 | — |
| Article | 实际送货物料 | — |
| Original article | 原定物料 | 取 delivery booking 的预定送货量(TO) |
| Original Qty | 原定数量 | 取 delivery booking 的预定送货量(TO) |
| Original booking date | 原定日期 | — |
| Create date | 创建日期 | — |
| Create time | 创建时间 | — |

**状态码值**：

| 英文 | 中文 |
|------|------|
| Not arrived | 未收货 |
| Arrived | 已收货 |
| Deleted | 已删除 |
| Rejected | 已拒收 |

---

*最后更新: 2026-06-02*
