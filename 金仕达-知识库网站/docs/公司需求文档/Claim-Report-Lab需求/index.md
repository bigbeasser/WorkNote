---
title: Claim Report & Lab 需求
tags: [Claim Report, Lab, 索赔报告, SAP, 入库登记, 状态转移库]
module: 采购管理-Lab模块
date: 2024-10-12
type: requirement
related: []
---

# REQ-003 Claim Report & Lab 需求

> 需求编号: REQ-003
> 提出日期: 2024-10-12
> 优先级: 高
> 状态: 已确认
> 原始文档: [Claim report&Lab.docx](Claim%20report&Lab.docx)

---

## 一、需求背景

LAB 模块卸货触发生成索赔报告，或根据收货单和检测结果手动录入索赔报告，生成后自动传给 SAP 进入状态转移库。

- 索赔报告判定是否收货，入库登记告知 SAP 结果
- 收货之后、入库之前（整个索赔报告阶段）都在 SAP 的状态转移库里
- 索赔报告关闭节点（关联订单之后指定状态）触发生成入库登记
- 入库登记触发 SAP 生成实物库存的数据

---

## 二、业务流程

### 2.1 PART 1 — CTRM 内部（LAB → Claim Report → LAB）

参见接口文档：`【LAB-001】_Unloaded lots transfer from LAB to CR_V1.0`

### 2.2 PART 2 — CTRM Claim Report → SAP

1. **Approved** 进入状态转移库
2. **Accepted / Settled / Rejected**
3. 对于**全价采购和寄售**：Close 触发生成入库登记，同时触发接口给 SAP 从状态转移库进入实物库存
4. 对于**委托加工和外仓货物转移**：Close 触发 SAP 接口，SAP 进行移库

### 2.3 PART 3 — CTRM 内部（Claim Report → Good Receipt）

1. 从 Link to Order 触发改为由 **Close 触发**生成 Good Receipt
2. Claim Report → 入库登记的现有接口增加字段

---

## 三、修改方案逻辑（CTRM → SAP）

### 3.1 Submit / Link / Reject / Close

推送 SAP 成功后，不用修改，保持原状；推送 SAP 失败后，把单据 Status 状态恢复成之前的状态（Close：状态、类型、仓库都变成上一版）。

### 3.2 Link（to SAP / to Order）

先推送 SAP，推送成功后再调用申诉状态回传接口，将新状态传 LAB；推送失败，把单据 Status 状态恢复成之前的状态，推送失败不需要再调用申诉状态回传接口。

### 3.3 Reject

Claim Report 手工新建的单据，先推送 SAP，推送成功后再调用申诉状态回传接口，将新状态传 LAB；推送失败，把 Status 状态恢复成之前的状态，推送失败不需要再调用申诉状态回传接口。

### 3.4 Roll Back

推送 SAP 成功后，不用修改，保持原状，并记录 sapCode；推送 SAP 失败后，把 Status 状态恢复成之前的状态。

### 3.5 Modify 限制

不允许修改商品 Link（to SAP / to Order）和 Reject 校验申报和验证的商品是否一致：
- 一致 → 不用修改
- 不一致 → 只能点 Reject，Link 按钮报错：*"申报和验证的商品不一致，只能 reject"*
- Reject（和 Reject-Roll Back）推送申报的商品

---

## 四、接口清单

| 序号 | 接口 | 方向 | 触发节点 |
|------|------|------|---------|
| 1 | LAB → Claim Report | CTRM 内部 | 卸货节点 |
| 2 | Claim Report → SAP | CTRM → SAP | 卸货节点 |
| 3 | LAB → Claim Report | CTRM 内部 | 检测完成节点 |
| 4 | Claim Report → LAB | CTRM 内部 | 谈判完成节点 |
| 5 | Claim Report → SAP | CTRM → SAP | 谈判完成节点 |

!!! note "接口顺序调整"
    原逻辑：先接口 4 后接口 5
    修改后：**先接口 5 后接口 4**

---

## 五、仓库状态变化

| 阶段 | 仓库 |
|------|------|
| Close 之前 | Lab |
| Close 之后 | （根据业务类型转入对应仓库） |

---

*最后更新: 2026-06-02*
