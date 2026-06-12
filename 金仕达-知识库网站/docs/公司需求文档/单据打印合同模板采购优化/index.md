---
title: 单据打印合同模板（采购）优化
tags: [单据打印, 合同模板, 采购, 商品主数据, 销售视图, SAP对接]
module: 采购管理-单据打印
date: 2025-12-01
type: requirement
related: []
---

# REQ-006 单据打印合同模板（采购）优化

> 需求编号: REQ-006
> 提出日期: 2025-12-01
> 优先级: 中
> 状态: 已确认
> 原始文档: [单据打印合同模板（采购）优化.docx](单据打印合同模板（采购）优化.docx)

---

## 一、需求背景

德意法三个 Brass 厂针对半成品 & 成品采购的打印模板，需要补充商品的信息。

> Regarding the finished goods purchase order template, the following information should be included on the purchase order to correctly describe the goods: **shape, dimensions, length, ends, alloy, temper, and packaging**.

---

## 二、整体流程

修改"单据打印合同模板"后，用于合同打印的时候，下拉选择对应模板。

---

## 三、详细设计

### 3.1 商品主数据

参考 SAP 对接文档：`HLGF_ERP_GLOBAL_HME_FS_【MM-001】_Material master data Interface from SAP to CTRM & CRM_20251023_V3.8.xlsx`

#### 3.1.1 新增"旧系统包装"字段

原来商品定义的包装是从包装 Z004 接过来匹配包装 ID 的，这个保留不动。

在商品 VAT 类别后面新增字段 **"旧系统包装"**：

| 项目 | 说明 |
|------|------|
| 中文 | 旧系统包装 |
| 英文 | Old system packaging |
| 字段值 | 包装代码-包装描述 |
| 数据来源 | 直接从 `ET_RTN001E` 接入（不需要从 Z004 匹配） |
| 多语言 | 包装描述根据接入的多语言展示，类似 `ET_RTN001A` 接入商品名称多语言 |

#### 3.1.2 修改海关编码

| 项目 | 说明 |
|------|------|
| 原逻辑 | 海关编码取 STAWN |
| 新逻辑 | 如果 STAWN 有值，取 STAWN 值；如果 STAWN 没有值，取 `ZHME_STCDOG` |
| 优先级 | STAWN 优先 |

### 3.2 销售视图 (Sales View)

新增页签：**销售视图**，类似统计属性，支持新增、打勾（保存）和打叉（不修改）。

#### 3.2.1 相关字段

| 序号 | 英文 | 中文 | 处理方式 | 类型 | 长度 | 必填 | 说明 |
|------|------|------|---------|------|------|------|------|
| 1 | Additional Description | 额外的描述 | 新增 | CHAR | 80 | 否 | — |
| 2 | (dim 1) Length in mm | 长度（MM） | 新增 | DEC | 13.3 | 否 | — |
| 3 | Article Typology Code | 商品类型代码 | 新增 | CHAR | 2 | 否 | 下拉选，根据当前系统语言展示"代码-描述" |
| 4 | Product Shape Code | 商品形状代号 | 新增 | CHAR | 3 | 否 | 下拉选，"代码-描述" |
| 5 | Official Material Description | 官方材料描述 | 新增 | CHAR | 80 | 否 | — |
| 6 | Sales text | 销售文本 | 新增 | CHAR | 132 | 否 | 根据当前系统语言展示对应描述 |

**商品类型代码**展示规则：根据当前系统语言选择 Language Key，将字段拼接，中间用空格隔开。
- 示例：`"B4 Profiles in straight lengths"`
- 码值维护到对接配置中

**商品形状代号**展示规则：将三个字段拼接，中间用空格隔开。
- 示例：`"S05 PFL P"`
- 码值维护到对接配置中

#### 3.2.2 销售文本

| 项目 | 说明 |
|------|------|
| 中文 | 销售文本 |
| 英文 | Sales Text |
| 字段值 | 销售文本信息 |
| 位置 | 销售视图最后一列 |
| 多语言 | 根据当前系统语言展示对应的销售文本 |

---

## 四、合同打印模板字段

| 序号 | 英文 | 说明 | 模板展示规则 |
|------|------|------|-------------|
| 1 | Additional Description | 额外的描述 | 不加 |
| 2 | Packaging | 包装代码-包装描述 | 根据当前系统模板展示对应语种的包装描述（法语/英语） |
| 3 | Official Material Description | 官方材料描述 | 不加 |
| 4 | Sales Text | 销售文本 | 根据当前系统模板展示对应语种的销售文本（法语/英语） |

---

## 五、SAP 对接字段汇总

### 5.1 商品定义

| 序号 | 英文 | 中文 | 处理方式 | 类型 | 长度 | 必填 |
|------|------|------|---------|------|------|------|
| 3.1.1 | Old system packaging | 旧系统包装 | 新增 | CHAR | 107 | 否 |
| 3.1.2 | HS Code | 海关编码 | 修改 | CHAR | 20 | 否 |

### 5.2 销售视图

| 序号 | 英文 | 中文 | 处理方式 | 类型 | 长度 | 必填 |
|------|------|------|---------|------|------|------|
| 3.2.1 | Additional Description | 额外的描述 | 新增 | CHAR | 80 | 否 |
| 3.2.2 | (dim 1) Length in mm | 长度（MM） | 新增 | DEC | 13.3 | 否 |
| 3.2.3 | Article Typology Code | 商品类型代码 | 新增 | CHAR | 2 | 否 |
| 3.2.4 | Product Shape Code | 商品形状代号 | 新增 | CHAR | 3 | 否 |
| 3.2.5 | Official Material Description | 官方材料描述 | 新增 | CHAR | 80 | 否 |
| 3.2.6 | Sales text | 销售文本 | 新增 | CHAR | 132 | 否 |

---

*最后更新: 2026-06-02*
