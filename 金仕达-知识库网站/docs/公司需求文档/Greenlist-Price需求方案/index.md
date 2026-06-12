---
title: Greenlist Price 需求方案
tags: [Greenlist, 价格, 市场行情, LME, 原材料, Alloy, 公允价格]
module: 市场风险-日内市场行情
date: 2026-05-14
type: requirement
related: [EOD日结流程]
---

# REQ-001 Greenlist Price 需求方案

> 需求编号: REQ-001
> 提出日期: 2026-05-14
> 优先级: 高
> 状态: 已确认
> 原始文档: [geenlist price 需求方案.xlsx](geenlist%20price%20需求方案.xlsx)

---

## 一、需求背景

按 **业务机构 + 物料号** 维度，计算商品的 **公允价格 (Greenlist Price)**。该表为商品价格的基底数据，需持久化存储，同时配置定时任务，**每月最后一个交易日次日凌晨 2 点** 更新当日市场行情值。

## 二、需求描述

### 2.1 功能描述

在菜单 **【市场风险 → 日内市场行情】** 下新建三级菜单：

- 中文：**Greenlist 价格**
- 英文：**Greenlist Price**

### 2.2 基本规则

1. **静态截面表**，不支持拖动汇总
2. 最小统计维度：**业务机构 + 物料号 + 日期**
3. 金额显示 **五位小数**，数字加 **千分符**
4. 仅针对 **原材料** 和 **Alloy** 类别商品

### 2.3 定时任务

- 触发时间：每月最后一个交易日次日凌晨 2:00
- 执行内容：更新当日市场行情值

---

## 三、筛选查询条件

| 序号 | 筛选项 | 控件类型 | 必输 | 说明 |
|------|--------|----------|------|------|
| 1 | **业务机构** | 下拉框 | 否 | 支持多选，默认空（查全部）。取自：业务设置 → 组织管理 → 业务机构管理（启用状态的机构） |
| 2 | **商品编号** | 下拉框 | 否 | 支持多选、模糊搜索，默认空（查全部）。取自：商品定义有效商品编号 |
| 3 | **日期** | 日期选择器 | 是 | 年份+月份+日期，具体日期，默认系统日期 |
| 3 | **月份** | 月份选择器 | 是 | 年月选择器；查询时自动取所选月份的最后一日。示例：选择 2026-03，默认查询 2026-03-31 |
| 4 | **商品大类** | 下拉框 | 否 | 支持多选，默认空（查全部）。取自：商品大类 |
| 5 | **Family** | 下拉框 | 否 | 支持多选、模糊搜索，默认空（查全部）。取自：对接配置 → Family → 对接明细 → 值 |

---

## 四、字段定义

### 4.1 基础信息字段

| 字段(英文) | 字段(中文) | 取值规则 |
|-----------|-----------|---------|
| Company | 业务机构 | 默认呈现全部启用状态的业务机构 |
| Article Code | 商品编号 | 取 [商品定义-商品编号]，业务机构 + 商品编号为唯一主键 |
| Article Description | 商品名称 | 取「商品定义 → 商品名称」 |
| Article Category | 商品大类 | 取「商品定义 → 商品大类」 |
| Family | Family | 取「商品定义 → 统计属性 → Family」 |
| Alloy Code | 对应合金内部编号 | 取「商品定义 → 父商品 → 商品编号」，需取最顶层父商品，无父商品则为空。示例：BA1 最顶层父商品编号 C32 |
| Date | 行情日期 | 查询日为交易日则取当日，否则取上一交易日 |

### 4.2 金属成分字段 (CU/ZN/PB/AL/SN/NI)

| 字段 | 取值规则 |
|------|---------|
| CU, ZN, PB, AL, SN, NI | 优先取 [对应合金内部编号] 对应的金属成分值（质检类型默认值=Fixation），无则取 [商品编号] 对应的金属成分值；取值来源于「商品定义 → 质检类型 → 类别=Fixation」的成分值，无数据则取 0 |

### 4.3 Fixation / Factory 字段（2026.5.20 补充）

每种金属各有 **Fixation** 和 **Factory** 两个字段：

| 商品大类 | 取值规则 |
|---------|---------|
| **原材料** | 取该商品本身 Fixation/Factory 金属成分的默认值，无值为 0 |
| **Alloy** | 取 [对应合金内部编号] 的 Fixation/Factory 金属成分默认值，无值为 0 |

### 4.4 Yield 折率字段（2026.5.20 补充）

| 商品大类 | 取值规则 |
|---------|---------|
| **原材料** | 取该商品本身对应工厂 Yield 的默认值，无值为 0 |
| **Alloy** | 取 [对应合金内部编号] 商品对应工厂 Yield 的默认值，无值为 0 |

### 4.5 Marker 标记字段

| 商品大类 | Family | Marker 值 |
|---------|--------|-----------|
| Alloy、半成品、成品 | — | **Alloy** |
| 原材料 | New metal | **Cash** |
| 原材料 | Scrap | **Lowest** |
| 其他 | — | 空 |

### 4.6 LME 行情字段 (LME CU/ZN/PB/AL/SN/NI)

取各金属成分对应的 LME 市场行情值，查找规则：

- **合约文本**：符号=CU/ZN/Pb/AL/SN/Ni & 作价市场=LME & 币种=Euro & 类型=现货
- **行情日期**：查询日期，是交易日取当天，不是则取上一个交易日
- **行情类型**：结算价
- **Session**：0
- **标记**：Family=New metal → Cash，Family=Scrap → Lowest，其它为空

### 4.7 Curve 价格曲线字段

取合约文本名称，查找规则：

1. 商品 = [对应合金内部编号] 对应的 [商品名称]
2. 根据业务机构映射确定作价市场：

| 业务机构 (Company) | 作价市场 |
|-------------------|---------|
| HME Brass Italy SpA | **MEB** |
| HME Brass France SAS | **TMB** |
| HME Brass Germany GmbH | **KMB** |

3. 根据作价市场匹配对应合约文本
4. 无对应业务机构则取第一个合约文本，无匹配合约文本为空

### 4.8 LME For Greenlist（原 LME Equivalent）

> 2026.5.20 字段名称修改：LME Equivalent → LME For Greenlist

| 商品大类 | 计算规则 |
|---------|---------|
| **Alloy、半成品、成品** | 取对应市场行情值：合约文本=本表【价格曲线】，行情日期=查询日期（交易日取当天，否则取上一交易日），行情类型=结算价，Session=0，标记=Cash |
| **原材料 (Scrap/New metal)** | `LME For Greenlist = ∑(CU/ZN/PB/AL/SN/NI-Fixation × 对应 LME 行情值)` |
| **其他** | 取 0 |

**LME 行情值补充说明（2026.5.20）**：
- 取各金属成分对应的 LME 市场行情值，然后根据 **Bloomberg 汇率** 将美元转换为欧元
- LME 合约：符号=CU/ZN/Pb/AL/SN/Ni & 作价市场=LME & 币种=**USD** & 类型=现货
- 行情日期/行情类型/Session 同上
- 标记：Family=Scrap → Lowest，其它为 Cash
- 汇率转换：取 USD-EUR-Bloomberg 的行情值

### 4.9 LME Equivalent（2026.5.20 新增）

```
LME Equivalent = ∑(CU/ZN/PB/AL/SN/NI-Factory × LME CU/ZN/PB/AL/SN/NI × Yield 折率)
```

### 4.10 Average Premium/Discount 月均折扣

> 2026.5.14 修改

- **适用范围**：仅商品大类 = **原材料**，其余品类取值为 0
- **计算维度**：业务机构 + 商品
- **计算公式**：

```
月均折扣 = ∑(入库数量(TO) × 同行标准折扣) ÷ ∑入库数量(TO)
```

- **收货明细表筛选条件**：
  - 过账开始日期 = 查询月第一天
  - 过账结束日期 = 查询月最后一天
  - 业务机构 = 查询机构
  - 商品 = 查询商品名称
  - SAP 推送状态 = 已推送
- **无数据回溯**：若当前查询月无交货订单，逐月向前追溯最近有交货订单的月份取值
  - 示例：计算 2026-05 月均折扣，优先取 2026-05-01~2026-05-31 数据；5 月无数据则取 2026-04 月

### 4.11 Greenlist Price 单价

```
Greenlist 单价 = LME For Greenlist + 月均折扣
```

### 4.12 Adder GL-LME（2026.5.20 新增）

```
Adder = Greenlist 单价 - LME Equivalent
```

---

## 五、数据示例

| 业务机构 | 商品编号 | 商品名称 | 大类 | Family | 合金编号 | 日期 | Marker | LME For GL | 月均折扣 | GL 单价 |
|---------|---------|---------|------|--------|---------|------|--------|-----------|---------|--------|
| HME Brass Italy SpA | 4000071 | COPPER SCRAPS CEN S-CU-10/C GRAN. | Raw materials | Scrap | — | 2026-03-31 | Scrap | 10580.15 | 0 | 10580.15 |
| HME Brass France SAS | 4000071 | COPPER SCRAPS CEN S-CU-10/C GRAN. | Raw materials | Scrap | — | 2026-03-31 | Scrap | 10580.15 | 0 | 10580.15 |
| HME Brass Germany GmbH | 4000071 | COPPER SCRAPS CEN S-CU-10/C GRAN. | Raw materials | Scrap | — | 2026-03-31 | Scrap | 10580.15 | 0 | 10580.15 |
| HME Brass Italy SpA | 4000046 | ZINC INGOTS SECONDARY FUSION | Raw materials | New metal | — | 2026-03-31 | New metal | 2771.30 | 0 | 2771.30 |
| HME Brass Italy SpA | BA1 | B17 | Alloy | — | C32 | 2026-03-31 | Alloy | 7495.20 | 0 | 7495.20 |
| HME Brass France SAS | BA1 | B17 | Alloy | — | C32 | 2026-03-31 | Alloy | 7492.80 | 0 | 7492.80 |
| HME Brass Germany GmbH | BA1 | B17 | Alloy | — | C32 | 2026-03-31 | Alloy | 7503.90 | 0 | 7503.90 |
| HME Brass Italy SpA | 4000087 | BINARY BRASS SCRAPS 67/33 S-CUZN-1/C | Raw materials | — | — | 2026-03-31 | Scrap | 8003.29 | 0 | 8003.29 |

---

## 六、变更记录

| 日期 | 变更内容 |
|------|---------|
| 2026-05-14 | 初始版本：月均折扣计算逻辑修改（仅原材料、按月回溯）、定时任务改为每月最后交易日次日凌晨 2 点 |
| 2026-05-20 | 补充字段：每种金属增加 Fixation/Factory 双列、增加 Yield 折率列、增加 LME Equivalent 和 Adder 列、LME Equivalent 更名为 LME For Greenlist、LME 行情值改用 USD 币种 + Bloomberg 汇率转换 EUR |

---

*最后更新: 2026-06-02*
