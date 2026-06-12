# Claim Report SAP 对接服务 — 完整技术文档

> **文件**: `ClaimReportDockingServiceImpl.java`
> **模块**: `bcadmin-system` (HME CTRM 后端)
> **作者**: yuting.zhang2 | **创建日期**: 2024-10-25
> **文档整理日期**: 2026-06-03

---

## 一、系统架构概览

```
 ┌─────────┐      ┌──────────┐      ┌─────────────────────┐      ┌─────────┐
 │  LAB    │ ───▶ │  CTRM    │ ───▶ │ ClaimReportDocking  │ ───▶ │   SAP   │
 │ (实验室) │      │ (前端UI) │      │     ServiceImpl     │      │ (物料过账)│
 └─────────┘      └──────────┘      └─────────────────────┘      └─────────┘
  卸货/质检结果      状态变更操作        组装SAP请求报文             HTTP POST
  状态回传          回滚/冲销          解析响应 & 回写DB           返回物料凭证号
```

这是 **HME（贺利氏金属）CTRM 系统**（大宗商品贸易风险管理），管理金属货物到港后的质量索赔流程：

1. 货物到港 → **LAB（实验室）** 进行质检
2. LAB 将质检结果推送至 CTRM → 系统生成 **Claim Report**
3. CTRM 根据 Claim Report 的处理状态 → 向 **SAP** 推送物料移动过账请求
4. SAP 完成库存变动 → 返回物料凭证号

---

## 二、涉及的单据实体

| 实体类 | 数据表方向 | 支持的 businessType | 说明 |
|--------|-----------|-------------------|------|
| **Conversion** | 销售侧（客户） | 3 委托加工、4 外仓转移 | 客户侧的索赔处理单据 |
| **Purchasing** | 采购侧（供应商） | 1 全价采购、2 供应商寄售 | 供应商侧的索赔处理单据 |
| **Documents** | 入库登记 | 继承自上游 Claim Report | Claim Report 关闭后自动生成的入库单据 |

---

## 三、核心魔法数字字典

### 3.1 businessType — 业务类型

| 值 | 常量名 | 含义 | 所属实体 |
|----|--------|------|---------|
| **1** | `Bussiness_TYPE_1` | 全价采购 (Full Price Procurement) | Purchasing |
| **2** | `Bussiness_TYPE_2` | 供应商寄售 (Vendor Consignment) | Purchasing |
| **3** | `Bussiness_TYPE_3` | 委托加工 (Conversion / Subcontracting) | Conversion |
| **4** | `Bussiness_TYPE_4` | 外仓转移 (External Warehouse Transfer) | Conversion |

### 3.2 state — 单据状态

| 值 | 常量名 | 含义 | 是否触发 SAP 推送 |
|----|--------|------|------------------|
| **5** | New | 新建 | ❌ |
| **1** | Open | 开启 | ❌ |
| **2** | InProcess | 处理中 | ❌ |
| **6** | Approved | 已批准 | ✅ |
| **3** | Accepted | 已接受 | ✅ |
| **4** | Settled | 已结算 | ✅ |
| **7** | Rejected | 已拒绝 | ✅ |
| **-1** | Closed | 已关闭 | ✅ |

### 3.3 offSetFlag — 冲抵标志

| 值 | 含义 | 说明 |
|----|------|------|
| **0** | 正向推送 | 正常业务流程（批准/接受/结算/拒绝/关闭） |
| **1** | 冲销推送 | 回滚操作，生成反向 SAP 物料凭证 |

> **编号规律**：所有移动类型（BWART）遵循 **奇数 = 正向，偶数 = 冲销** 的配对规则。

### 3.4 reasonForMovement (GRUND) — 移动原因码

| 代码 | 含义 | 对应业务类型 |
|------|------|-------------|
| **701** | 采购类移动原因 | businessType 1（全价采购）、2（供应商寄售） |
| **702** | 委托加工移动原因 | businessType 3（委托加工） |
| **821** | 外仓转移移动原因 | businessType 4（外仓转移） |

### 3.5 movementType (BWART) — SAP 移动类型完整字典

> **配对规律**：奇数编号 = 正向流程，偶数编号 = 冲销流程

| 代码 | 正向/冲销 | 适用业务类型 | 适用状态 | 业务含义 |
|------|----------|-------------|---------|---------|
| **Y01** | 正向 | 采购(1)、寄售(2)、委托加工(3) | Approved(6) | **已审批收货入库** — 货物通过审批，执行入库过账 |
| **Y02** | 冲销 | 采购(1)、寄售(2)、委托加工(3) | Approved(6) | **已审批收货冲销** — 撤销之前的审批入库 |
| **Y03** | 正向 | 采购(1)、寄售(2)、委托加工(3) | Rejected(7) | **已拒绝** — 索赔被拒绝，执行相应库存调整 |
| **Y04** | 冲销 | 采购(1)、寄售(2)、委托加工(3) | Rejected(7) | **已拒绝冲销** — 撤销拒绝操作的库存调整 |
| **Y05** | 正向 | 采购(1)、寄售(2) | Accepted(3) / Settled(4) | **已接受/已结算入库** — 接受索赔方案或完成结算 |
| **Y06** | 冲销 | 采购(1)、寄售(2) | Accepted(3) / Settled(4) | **已接受/已结算冲销** — 撤销接受或结算操作 |
| **Y07** | 正向 | 委托加工(3)、外仓转移(4) | Closed(-1) | **已关闭** — 单据关闭时的库存处理 |
| **Y08** | 冲销 | 委托加工(3)、外仓转移(4) | Closed(-1) | **已关闭冲销** — 撤销关闭操作 |
| **Z01** | 正向 | 委托加工(3) | Accepted(3) / Settled(4) | **委托加工已接受/结算** — 委托加工专用 |
| **Z02** | 冲销 | 委托加工(3) | Accepted(3) / Settled(4) | **委托加工接受/结算冲销** |
| **Z19** | 正向 | 外仓转移(4) | Rejected(7) | **外仓转移已拒绝** — 外仓转移专用 |
| **Z20** | 冲销 | 外仓转移(4) | Rejected(7) | **外仓转移拒绝冲销** |
| **Z21** | 正向 | 外仓转移(4) | Accepted(3) / Settled(4) | **外仓转移已接受/结算** — 外仓转移专用 |
| **Z22** | 冲销 | 外仓转移(4) | Accepted(3) / Settled(4) | **外仓转移接受/结算冲销** |
| **101** | 正向 | 外仓转移(4)、入库登记 | Approved(6) | **SAP 标准收货入库** — SAP 标准移动类型 |
| **102** | 冲销 | 外仓转移(4)、入库登记 | Approved(6) | **SAP 标准收货冲销** — SAP 标准移动类型 |

### 3.6 其他 SAP 字段魔法值

| 字段 | 值 | 含义 |
|------|-----|------|
| **INSMK** (库存类型) | `"3"` | 质检库存 — 正常状态（state ≠ -1）时使用 |
| | `""` (空) | 无限制库存 — 关闭状态（state = -1）或外仓转移批准时 |
| **SOBKZ** (特殊库存) | `"K"` | 供应商寄售库存 — businessType = 2 时使用 |
| | `""` (空) | 普通库存 — 其他业务类型 |
| **ZNETPR** (净价格) | `"1"` | 标记有价格 — 供应商寄售(businessType=2) 且 state ≠ -1 时 |
| | `""` (空) | 无价格标记 — 其他情况 |

### 3.7 SapPushStatus — 推送状态枚举

| 值 | 枚举名 | 含义 |
|----|--------|------|
| **0** | Init | 未推送（初始状态 / 推送失败后重置） |
| **1** | wait | 待推送 |
| **2** | Pushed | 已推送成功 |
| **3** | Failed | 推送失败 |
| **4** | CANNOT_BE_PUSHED | 不可推送 |
| **10** | REVERSAL | 冲销推送失败 |

> ⚠️ **注意**：Conversion / Purchasing 表的 `sapPushStatus` 是 **Integer** 类型；Documents 表的是 **String** 类型。

---

## 四、四个推送方法详解

### 4.1 `claimReportConversionPushToSap(id, offSetFlag)` — 销售侧推送

**适用单据**：Conversion（委托加工 businessType=3、外仓转移 businessType=4）

**SAP 接口**：`sendClaimReportToSap()`

#### MovementType 决策矩阵

**委托加工 (businessType = 3)，reasonForMovement 固定 = 702**

| state \ offSetFlag | 0（正向） | 1（冲销） |
|-------------------|----------|----------|
| 6 — Approved | **Y01** 已审批收货 | **Y02** 审批收货冲销 |
| 3 — Accepted | **Z01** 已接受/结算 | **Z02** 接受/结算冲销 |
| 4 — Settled | **Z01** 已接受/结算 | **Z02** 接受/结算冲销 |
| 7 — Rejected | **Y03** 已拒绝 | **Y04** 拒绝冲销 |
| -1 — Closed | **Y07** 已关闭 | **Y08** 关闭冲销 |

**外仓转移 (businessType = 4)，reasonForMovement 固定 = 821**

| state \ offSetFlag | 0（正向） | 1（冲销） |
|-------------------|----------|----------|
| 6 — Approved | **101** 标准收货入库 | **102** 标准收货冲销 |
| 3 — Accepted | **Z21** 已接受/结算 | **Z22** 接受/结算冲销 |
| 4 — Settled | **Z21** 已接受/结算 | **Z22** 接受/结算冲销 |
| 7 — Rejected | **Z19** 已拒绝 | **Z20** 拒绝冲销 |
| -1 — Closed | **Y07** 已关闭 | **Y08** 关闭冲销 |

#### 物料编码选择规则

| 条件 | 使用的物料编码 |
|------|---------------|
| 默认 | **验证质量** (verifiedQuality) 的 SAP 编码 |
| state=6 (Approved) 且 offSetFlag=1 (冲销) | **申报质量** (declaredQuality) 的 SAP 编码 |
| state=7 (Rejected) | **申报质量** (declaredQuality) 的 SAP 编码 |

#### 重量取值规则

| 条件 | 重量来源 |
|------|---------|
| businessType=3 且 state ≠ 7,6 | ConversionResolution 表的 `weightToGetInCharge`（结算重量） |
| businessType=3 且 state = 7 或 6 | `conversion.verifiedWeight`（验证重量） |
| businessType=4 且 state ≠ 6 | ConversionResolution 表的 `weightToGetInCharge` |
| businessType=4 且 state = 6 | `conversion.verifiedWeight` |

---

### 4.2 `claimReportProcurementPushToSap(id, offSetFlag)` — 采购侧推送

**适用单据**：Purchasing（全价采购 businessType=1、供应商寄售 businessType=2）

**SAP 接口**：`sendClaimReportToSap()`

#### MovementType 决策矩阵

**全价采购 (businessType = 1) 和 供应商寄售 (businessType = 2) 使用相同的移动类型映射，reasonForMovement 固定 = 701**

| state \ offSetFlag | 0（正向） | 1（冲销） |
|-------------------|----------|----------|
| 6 — Approved | **Y01** 已审批收货 | **Y02** 审批收货冲销 |
| 3 — Accepted | **Y05** 已接受/结算 | **Y06** 接受/结算冲销 |
| 4 — Settled | **Y05** 已接受/结算 | **Y06** 接受/结算冲销 |
| 7 — Rejected | **Y03** 已拒绝 | **Y04** 拒绝冲销 |

> 注意：采购侧 **没有 Closed(-1)** 状态的推送，Closed 时走的是入库登记推送（见 4.3）。

#### 与 Conversion 推送的关键差异

| 差异点 | Conversion（销售侧） | Purchasing（采购侧） |
|--------|---------------------|---------------------|
| 客商编码 | 取 `customerCodes`（客户编码） | 取 `supplierCodes`（供应商编码） |
| reasonForMovement | 702 / 821 | **701** |
| SOBKZ（特殊库存） | 始终为空 | businessType=2 时设为 **"K"**（供应商寄售） |
| 明细行数 | 始终 1 行 | state=6/7 时 1 行；state=3/4 时**按关联订单行生成** |
| 关联订单 | 不涉及 | 需查 PurchasingOrderRela → PhysicalDealLine → PhysicalDeals |
| ZNETPR | 始终为空 | businessType=2 且 state≠-1 时设为 **"1"** |

---

### 4.3 `claimReportRegisterPushToSap(id, offSetFlag)` — 入库登记推送

**适用单据**：Documents（Claim Report 关闭后生成的入库登记单据）

**SAP 接口**：`sendPRInfoToSap2()`（与上面两个方法使用不同的 SAP 端点逻辑）

#### MovementType 规则

| offSetFlag | BWART | GRUND | 说明 |
|-----------|-------|-------|------|
| 0 | **101** | 701 | 标准收货入库 |
| 1 | **102** | 701 | 标准收货冲销 |

#### 明细行逻辑（offSetFlag=0 时生成 2 行）

| 行号 ZEILE | BWART | INSMK | SOBKZ | 仓库来源 | 说明 |
|-----------|-------|-------|-------|---------|------|
| 2 | **101** | `""` | `""` | 入库登记明细的仓库 | 正常入库到工厂仓库 |
| 1 | **Y06** | `"3"` (质检) | `"K"` (仅寄售) | Claim Report 关联的仓库 | 质检/寄售库存转移 |

> offSetFlag=1 时只生成 1 行（102 冲销）。

#### 与其他方法的本质区别

| 对比项 | Conversion/Purchasing 推送 | Register 入库登记推送 |
|--------|--------------------------|---------------------|
| 数据来源 | Conversion / Purchasing 表 | **Documents + DocumentItems** 表 |
| SAP 接口 | `sendClaimReportToSap` | **`sendPRInfoToSap2`** |
| 移动类型 | 根据 state 动态决定 | **固定 101/102** |
| 物料编码 | 申报/验证质量二选一 | 直接用**入库登记商品编码** |
| 数量 | verifiedWeight 或 Resolution 重量 | **DocumentItems.quantity** |
| 单位转换 | 无 | 需做**计量单位转换**（quantityUnit → 主计量单位） |
| 回写目标 | Conversion / Purchasing 表 | **Documents + DocumentItems** 表 |

---

### 4.4 `noClaimReportRegisterPushToSap(id, offSetFlag)` — 非 Claim Report 入库推送

**接口编号**：MM-013

**当前状态**：⚠️ **无外部调用**（代码中未找到任何调用点，可能预留或已废弃）

**适用场景**：非 Claim Report 来源的普通入库登记推送 SAP

---

## 五、完整调用链路

### 5.1 触发入口全景图

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                              触发入口全景图                                        │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ▶ 前端手动操作                                                                    │
│                                                                                   │
│    POST /api/conversion/updateState                                               │
│      └─▶ ConversionServiceImpl.doUpdateState                                      │
│            └─▶ claimReportConversionPushToSap(id, 0)     ← 状态变更推送            │
│                                                                                   │
│    POST /api/conversion/linkSap                                                   │
│      └─▶ ConversionServiceImpl.pushToSap                                          │
│            └─▶ claimReportConversionPushToSap(id, 0)     ← 直接触发推送            │
│                                                                                   │
│    POST /api/conversion/rollBack                                                  │
│      └─▶ ConversionServiceImpl                                                    │
│            └─▶ claimReportConversionPushToSap(id, 1)     ← 回滚冲销               │
│                                                                                   │
│    POST /api/purchasing/updateState                                               │
│      └─▶ PurchasingServiceImpl.updateState                                        │
│            ├─ Approved  ─▶ claimReportProcurementPushToSap(id, 0)                 │
│            ├─ Accepted/Settled/Rejected ─▶ claimReportProcurementPushToSap(id, 0) │
│            └─ Closed    ─▶ 生成入库登记 ─▶ claimReportRegisterPushToSap(docId, 0)  │
│                                                                                   │
│    POST /api/purchasing/connectOrder                                              │
│      └─▶ PurchasingServiceImpl.linkOrder                                          │
│            └─▶ claimReportProcurementPushToSap(id, 0)    ← 关联订单后推送          │
│                                                                                   │
│    POST /api/purchasing/rollBack                                                  │
│      └─▶ PurchasingServiceImpl                                                    │
│            └─▶ claimReportProcurementPushToSap(id, 1)    ← 回滚冲销               │
│                                                                                   │
│  ▶ LAB 卸货接口自动触发                                                             │
│                                                                                   │
│    POST /api/ClaimReport/receiveClaimReportApproved                               │
│      └─▶ ClaimReportDockingServiceImpl.receiveClaimReportApproved                 │
│            ├─ businessType 1/2 ─▶ writePurApprovedToDataBase                      │
│            │                        └─▶ claimReportProcurementPushToSap(id, 0)    │
│            └─ businessType 3/4 ─▶ writeConApprovedToDataBase                      │
│                                     └─▶ claimReportConversionPushToSap(id, 0)     │
│                                                                                   │
│  ▶ 定时任务                                                                        │
│                                                                                   │
│    VendorConsignmentGrPushSapTask（每月1-5号执行）                                   │
│      └─▶ 筛选: dataSource="CLAIM-REPORT" & sapPushStatus="0"                      │
│              & businessType=2(寄售) & titleTransferDate 在当月                      │
│      └─▶ claimReportRegisterPushToSap(docId, 0)                                   │
│                                                                                   │
│  ▶ 手动运维接口                                                                      │
│                                                                                   │
│    POST /api/systemOps/generationInRegisterByClaim                                │
│      └─▶ 手动生成入库登记并推送                                                      │
│            └─▶ claimReportRegisterPushToSap(docId, 0)                              │
│                                                                                   │
│    POST /api/document/register/pushToSap                                          │
│      └─▶ DocumentsServiceImpl.registerPushToSap                                   │
│            └─▶ 根据 dataSource=="CLAIM-REPORT" 分流                                │
│                  └─▶ claimReportRegisterPushToSap(docId, offSetFlag)               │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 单次推送的执行链路（以 Conversion Approved 为例）

```
前端点击「批准」
    │
    ▼
ConversionController.updateState(batchIds)
    │
    ▼
ConversionServiceImpl.doUpdateState(ids, targetState=6)
    │  遍历每个 Conversion id，使用 Redis 分布式锁
    │
    ▼
claimReportDockingService.claimReportConversionPushToSap(id, offSetFlag=0)
    │
    ├─ ① 参数校验：id 不能为空
    │
    ├─ ② 加载基础数据（4 张映射表）
    │    ├─ personMap:        userId → 工号（用于 SAP 采购组 ZEKGRP）
    │    ├─ customerCodes:    counterpartyId → SAP 客户编码（KUNNR）
    │    ├─ productSapCodes:  productId → SAP 物料编码（MATNR）
    │    └─ groupByUnitCode:  unitId → Unit 对象（ERFME/MEINS）
    │
    ├─ ③ 查询 Conversion 记录（by id）
    │
    ├─ ④ 构建 SAP 请求抬头 SapPRRequestHeader
    │    ├─ ZXTBS = "CTRM"          ← 系统标识（固定值）
    │    ├─ BUDAT = 当天日期          ← 过账日期 (Posting Date)
    │    ├─ BLDAT = arrivalDate     ← 凭证日期 (Document Date)
    │    ├─ FRBNR = claimReportCode ← Claim Report 编号
    │    ├─ BKTXT = movementCode    ← Movement Code
    │    └─ XBLNR = deliveryDoc     ← 交货单号
    │
    ├─ ⑤ 核心决策：根据 businessType × offSetFlag × state 确定
    │    ├─ movementType (BWART)    ← SAP 移动类型
    │    ├─ reasonForMovement (GRUND) ← SAP 移动原因
    │    └─ businessType            ← 传给 SAP 的业务类型编号 (1/10/2/20/3/30/4/40)
    │
    ├─ ⑥ 构建 SAP 请求明细 SapPRRequestItem
    │    ├─ 物料编码选择（申报质量 vs 验证质量）
    │    ├─ 重量取值（结算重量 vs 验证重量）
    │    ├─ 计量单位（ERFME / MEINS）
    │    ├─ 库存类型 INSMK（质检库存 vs 无限制库存）
    │    ├─ 工厂 WERKS / 仓库 LGORT
    │    ├─ 交货单 VBELN_IM / VBELP_IM
    │    └─ 采购组 ZEKGRP（业务员工号）
    │
    ├─ ⑦ 调用 SAP 接口（同步 HTTP POST）
    │    │
    │    ▼
    │    SapDockingServiceImpl.sendClaimReportToSap(req, logInfo, state, businessType)
    │         ├─ 从 DB 配置表读取 SAP URL 和登录信息
    │         ├─ HttpClientHelper.doPost(url, login, req, SapCRResponse.class)
    │         ├─ 判断 res.isSuccess()
    │         └─ 异步记录 SAP 对接日志（新线程 → writeToFile2）
    │
    └─ ⑧ 处理 SAP 返回结果
         │
         ├─ 成功：
         │    ├─ conversion.sapPushStatus = 2 (Pushed)
         │    ├─ conversion.sapCode = response.MBLNR  ← SAP 物料凭证号
         │    ├─ conversion.sapYear = response.MJAHR  ← SAP 会计年度
         │    └─ conversionMapper.updateById(conversion)
         │
         └─ 失败：
              ├─ conversion.sapPushStatus = 0 (Init)  ← 重置，允许重试
              ├─ conversionMapper.updateById(conversion)
              └─ 返回 BaseResultEntity.fail(错误信息)
```

---

## 六、调用成功/失败后的数据库变更

### 6.1 Conversion / Purchasing 推送

| 字段 | 成功时 | 失败时 |
|------|-------|-------|
| `sapPushStatus` | → **2** (Pushed) | → **0** (Init)，允许重试 |
| `sapCode` | → SAP 物料凭证号 (MBLNR) | 不变 |
| `sapYear` | → SAP 会计年度 (MJAHR) | 不变 |

### 6.2 Register 入库登记推送

| 表 | 字段 | 成功时 | 失败时 |
|----|------|-------|-------|
| **Documents** | `sapPushStatus` | → **"2"** (String 类型) | → **"0"** |
| **Documents** | `sapCode` | → SAP 物料凭证号 | 不变 |
| **Documents** | `sapAccountYear` | → SAP 会计年度 | 不变 |
| **Documents** | `updatedBy` | → 当前用户名 | → 当前用户名 |
| **Documents** | `updatedTime` | → 当前时间 | → 当前时间 |
| **DocumentItems** | `sapCode` | → "1" | 不变 |

---

## 七、状态流转与 SAP 推送时序

### 7.1 正常正向流程

```
 ┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐
 │ New  │ ──▶ │ Approved │ ──▶ │ Accepted │ ──▶ │ Settled  │ ──▶ │ Closed │
 │  (5) │     │   (6)    │     │   (3)    │     │   (4)    │     │  (-1)  │
 └──────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └───┬────┘
                   │                │                │               │
                   ▼                ▼                ▼               ▼
              推送 SAP         推送 SAP         推送 SAP      生成入库登记
              Y01/101          Z01/Z21/Y05     Z01/Z21/Y05   推送 SAP 101
              (审批收货)        (接受/结算)      (接受/结算)    (入库登记)
```

### 7.2 Rejected 分支

```
 ┌──────────┐     ┌──────────┐
 │ Approved │ ──▶ │ Rejected │
 │   (6)    │     │   (7)    │
 └──────────┘     └────┬─────┘
                       │
                       ▼
                  推送 SAP
                  Y03/Z19
                  (拒绝)
```

### 7.3 回滚/冲销流程

```
 任意已推送状态
      │
      │  前端点击「回滚」
      ▼
 ① sapPushStatus → 10 (REVERSAL) 或 0 (Init)
 ② 单据状态回退到上一状态
 ③ 调用推送方法，offSetFlag = 1
      │
      ▼
 SAP 生成反向物料凭证
 （如 Y01→Y02, 101→102, Z01→Z02）
      │
      ▼
 回写 sapPushStatus=2, sapCode=反向凭证号
```

---

## 八、LAB → CTRM → SAP 完整数据流

```
                    ┌─────────────────────────────────────────────┐
                    │              LAB（实验室系统）                  │
                    └──────────────────────────┬──────────────────┘
                                               │
               ① 卸货接口 POST /api/ClaimReport/receiveClaimReportApproved
               │  （推送 Approved 状态 + 质检数据）
               ▼
       ClaimReportDockingController.receiveClaimReportApproved()
               │
               ├─ 根据 businessType 分流：
               │    ├─ 1/2 → writePurApprovedToDataBase()  → 创建/更新 Purchasing
               │    └─ 3/4 → writeConApprovedToDataBase()  → 创建/更新 Conversion
               │
               ├─ ② 立即推送 SAP（offSetFlag=0）
               │    claimReportConversionPushToSap / claimReportProcurementPushToSap
               │
               └─ ③ 异步记录对接日志（writeToFile → abutment_log 表）
                       │
                       ▼
               ┌──────────────┐
               │     SAP      │  生成物料凭证，返回 MBLNR + MJAHR
               └──────┬───────┘
                      │
               ④ 回写 CTRM 数据库
               │  sapPushStatus=2, sapCode=凭证号
               │
               ⑤ 后续状态流转（前端操作）
               │  Accepted → Settled → Closed
               │  每次状态变更都重新推送 SAP（更新物料凭证）
               │
               ⑥ Closed 后生成入库登记 Documents
               │  claimReportRegisterPushToSap
               │  （供应商寄售 businessType=2 由定时任务每月1-5号推送）
               │
               ⑦ 申诉状态回传 LAB
                  POST /api/ClaimReport/pushClaimReportAppealStatus
```

---

## 九、SAP 日志分类（DockingBusinessType）

每次 SAP 推送都会在 `abutment_log` 表中记录日志，日志类型由 `businessType(传SAP)` × `state` 组合决定：

| 传SAP的 type 值 | 业务场景 | state=6 Approved | state=3 Accepted | state=4 Settled | state=7 Rejected | state=-1 Closed |
|----------------|---------|-----------------|-----------------|-----------------|-----------------|----------------|
| **1** | 全价采购 正向 | ProcurementApproved (107) | ProcurementAccepted (109) | ProcurementSettled (110) | ProcurementRejected (113) | — |
| **10** | 全价采购 冲销 | ProcurementApprovedReverse (108) | ProcurementAcceptedRollback (111) | ProcurementSettledRollback (112) | ProcurementRejectedRollback (114) | — |
| **2** | 供应商寄售 正向 | ConsignmentApproved (115) | ConsignmentAccepted (117) | ConsignmentSettled (118) | ConsignmentRejected (121) | — |
| **20** | 供应商寄售 冲销 | ConsignmentApprovedReverse (116) | ConsignmentAcceptedRollback (119) | ConsignmentSettledRollback (120) | ConsignmentRejectedRollback (122) | — |
| **3** | 委托加工 正向 | ConversionApproved (91) | ConversionAccepted (93) | ConversionSettled (94) | ConversionRejected (97) | ConversionClose (127) |
| **30** | 委托加工 冲销 | ConversionApprovedReverse (92) | ConversionAcceptedRollback (95) | ConversionSettledRollback (96) | ConversionRejectedRollback (98) | ConversionCloseRollback (128) |
| **4** | 外仓转移 正向 | TransferApproved (99) | TransferAccepted (101) | TransferSettled (102) | TransferRejected (105) | TransferClose (129) |
| **40** | 外仓转移 冲销 | TransferApprovedReverse (100) | TransferAcceptedRollback (103) | TransferSettledRollback (104) | TransferRejectedRollback (106) | TransferCloseRollback (130) |

> **入库登记推送**的日志分类：BWART=102 → PurchaseRegisterReverse(35)；其他 → PurchaseRegister(20)

---

## 十、特殊业务规则汇总

| 规则 | 说明 |
|------|------|
| **2181 工厂跳过** | Conversion 非委托加工（businessType≠3）且 plantId="2181" 时，**不推送 SAP** |
| **意大利外仓跳过** | companyId=4375905320173570（意大利）且 businessType=4（外仓转移）且 state≠6 时，**不推送 SAP** |
| **寄售 BLDAT 日期** | 供应商寄售(businessType=2)：只有 Y06/101 移动类型使用 arrival date，其他使用当前日期 |
| **LAB 来源先推 LAB** | dataSource="2" 且 state≠6 且 state≠-1 时，先推送 LAB 申诉状态接口，再推送 SAP |
| **Closed 不直推采购** | Purchasing 的 Closed 状态不直接推送 SAP，而是生成入库登记 Documents 后推入库登记 |
| **寄售入库定时推** | 供应商寄售(businessType=2)的入库登记不自动推送，由定时任务每月1-5号集中推送 |
| **分布式锁** | 每次推送使用 Redis 分布式锁（`ConversionPushToSap:{id}` / `purchasing:updateState:{id}`）防止并发 |
| **失败可重试** | 推送失败后 sapPushStatus 重置为 0（Init），允许后续重新触发推送 |

---

## 十一、SAP 请求报文结构速查

### 抬头 (SapPRRequestHeader)

| 字段 | 说明 | 数据来源 |
|------|------|---------|
| ZXTBS | 系统标识 | 固定 `"CTRM"` |
| BUDAT | 过账日期 (Posting Date) | 当天日期 `LocalDate.now()` |
| BLDAT | 凭证日期 (Document Date) | arrivalDate（到货日期） |
| FRBNR | Claim Report 编号 | conversion.claimReportCode |
| BKTXT | Movement Code | conversion.movementCode |
| XBLNR | 交货单号 | conversion.deliveryDoc |

### 明细 (SapPRRequestItem) — 核心字段

| 字段 | 说明 | 数据来源 |
|------|------|---------|
| ZEILE | 行项目号 | 固定 `"1"` 或递增 |
| BWART | 移动类型 | 由 businessType × offSetFlag × state 决策 |
| GRUND | 移动原因 | 由 businessType 决定 (701/702/821) |
| MATNR | 物料编码 | 申报/验证质量的 SAP 编码 |
| ERFMG | 入库数量 | 结算重量或验证重量 |
| MENGE | 数量（主单位） | 同 ERFMG 或经单位转换 |
| ERFME | 入库单位 | conversion.quantityUnitId 对应的单位编码 |
| MEINS | 主计量单位 | 同 ERFME 或商品主计量单位 |
| INSMK | 库存类型 | `"3"` (质检) 或 `""` (无限制) |
| WERKS | 工厂 | conversion.plantId |
| LGORT | 仓库 | storageFacility.code |
| KUNNR | 客户编码 | 销售侧使用 |
| LIFNR | 供应商编码 | 采购侧使用 |
| SOBKZ | 特殊库存标志 | `"K"` (寄售) 或 `""` |
| ZEKGRP | 采购组 | 当前用户对应的工号 |
| VBELN_IM | 交货单号 | conversion.deliveryDoc |
| VBELP_IM | 交货单行项目 | conversion.deliveryDocItem |
| ZNETPR | 净价格标记 | `"1"` 或 `""` |
| ZZCTRM_NOTES | 备注 | conversion.notes |

---

## 十二、快速定位指南

| 我想了解... | 查看位置 |
|------------|---------|
| 移动类型决策逻辑 | `ClaimReportDockingServiceImpl.java` L198-261 (Conversion), L468-519 (Purchasing) |
| 物料编码选择逻辑 | 同上 L282-298 |
| 重量取值逻辑 | 同上 L300-330 |
| SAP HTTP 调用 | `SapDockingServiceImpl.java` L3927 `sendClaimReportToSap()` |
| 入库登记推送 | `ClaimReportDockingServiceImpl.java` L1105 `claimReportRegisterPushToSap()` |
| LAB 卸货接口 | 同上 L1664 `receiveClaimReportApproved()` |
| 状态常量定义 | `ClaimReportStateConstants.java` |
| 推送状态枚举 | `SapPushStatus.java` |
| 日志类型枚举 | `DockingBusinessType.java` |
| Conversion 状态流转 | `ConversionServiceImpl.java` `doUpdateState()` / `pushToSap()` |
| Purchasing 状态流转 | `PurchasingServiceImpl.java` `updateState()` / `doSubmitUpdate*()` |
| 定时任务 | `VendorConsignmentGrPushSapTask.java` |
| SAP URL 配置 | 数据库表 `abutment_config` + `abutment_config_details`，code="ClaimReport" |
