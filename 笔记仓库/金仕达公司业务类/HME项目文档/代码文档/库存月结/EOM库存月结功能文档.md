# EOM 库存月结功能文档

> **路由路径**：`warehouse/action/eom`  
> **前端目录**：`hmefront/src/views/business/warehouse_eom/`  
> **后端 Controller**：`EOMStorageController.java`（`/api/eomstorage/`）  
> **后端核心 Service**：`EomStorageServiceImpl.java`（~3700行）  
> **数据库 Schema**：`systemdb`

---

## 一、页面整体结构

```
warehouse/action/eom
├── 主列表页 (index.vue)              ← 月结单据管理（入口）
├── 新建/编辑 (add.vue)               ← 月结单据基础信息
├── 月结明细 (detail.vue)             ← 月结行项目（月结数量/价格）
├── 未开票库存价值 (entryNotInvoiced/index.vue)   ← Accounting Value
├── 当月库存附加价 (monlyInventory/index.vue)     ← Added Value
└── 部分冲销 (eomWriteoff/add.vue)               ← 部分冲销单据
    ├── 选择未开票弹窗 (notInvoiced/selectDialog.vue)
    └── 选择附加价弹窗 (currentMonth/selectDialog.vue)
```

---

## 二、数据库表结构

### 2.1 核心表关系

```
eom_storage (月结主表)
  ├── 1:N → eom_storage_detail (未开票库存价值明细)
  ├── 1:N → eom_storage_added_value (当月库存附加价明细)
  ├── N:1 → eom_storage (冲销→源单据, 通过 sourceId)
  │
  ├── 冲销关联表:
  │   ├── eom_storage_detail_write_off_rela (明细冲销关联)
  │   └── eom_storage_added_value_write_off_rela (附加价冲销关联)
  │
  └── 关联报表:
      ├── eom_engagement_report_data (Engagement手工录入)
      └── eom_committed_stock_valuation_small_hedge (小额对冲)
```

### 2.2 eom_storage（月结主表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 主键 |
| number | varchar | 单据号 |
| legal_entity_id | bigint | 业务机构 |
| accounting_month | varchar | 会计月 (YYYY-MM) |
| status | int | 单据状态（见枚举） |
| monthly_closing_status | int | 月结执行状态（见枚举） |
| sap_push_status | varchar | SAP推送状态 |
| is_write_off_doc | int | 是否冲销单据 (0否/1是) |
| source_id | bigint | 源月结ID（冲销时指向原单据） |
| source_number | varchar | 源月结单据号 |
| comment | varchar | 备注 |

### 2.3 eom_storage_detail（未开票库存价值明细）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 主键 |
| eom_storage_id | bigint FK | 月结主表ID |
| action_id | bigint | 单据类型 |
| document_id | bigint | 入库登记ID |
| document_item_id | bigint | 入库登记明细ID |
| source_document_item_id | bigint | 上游单据明细ID |
| document_number | varchar | 单据号 |
| document_line_number | int | 行号 |
| title_transfer_date | date | 货权转移日期 |
| posting_date | date | 过账日期 |
| counterparty_id | bigint | 交易对手 |
| storage_id | bigint | 仓库 |
| legal_entity_id | bigint | 业务机构 |
| business_department_id | bigint | 业务组合 |
| business_segment_id | bigint | 业务板块 |
| physical_deal_id | bigint | 合同ID |
| physical_deal_line_id | bigint | 合同行ID |
| contract_line_number | int | 合同行号 |
| contract_number | varchar | 合同号（关联查询） |
| product_id | bigint | 商品 |
| delivery_in_quantity | decimal | 已入库数量 |
| delivery_in_quantity_unit_id | bigint | 入库单位 |
| quantity | decimal | 入库登记数量 |
| quantity_unit_id | bigint | 入库登记数量单位 |
| offset_quantity | decimal | 冲销数量 |
| **eom_quantity** | **decimal** | **月结数量（可编辑）** |
| **eom_price** | **decimal** | **月结单价（可编辑）** |
| priced_quantity | decimal | 已定价数量 |
| related_quantity | decimal | 已关联数量 |
| related_avg_price | decimal | 关联均价 |
| unrelated_quantity | decimal | 未关联数量 |
| unrelated_avg_price | decimal | 未关联均价 |
| invoiced_quantity | decimal | 已开票数量 |
| uninvoiced_quantity | decimal | 未开票数量 |
| currency_id | bigint | 结算币种 |
| base_currency_id | bigint | 本位币种 |
| fixed_price | decimal | 已定单价 |
| prov_price | decimal | 暂估单价 |
| **accounting_total_value** | **decimal** | **记账金额（可编辑）** |
| **base_cur_accounting_total_value** | **decimal** | **本位币记账金额（可编辑）** |
| tax_inc_invoice_amount | decimal | 含税发票金额 |
| tax_inc_invoice_amount_base_cur | decimal | 含税发票金额(本位币) |
| fixed_price_base_cur | decimal | 已定单价(本位币) |
| sap_batch_number | varchar | SAP批次号 |
| sap_contract_code | varchar | SAP订单号 |
| sap_contract_line_code | varchar | SAP订单行号 |
| sap_document_code | varchar | SAP物料凭证号 |
| sap_document_account_year | varchar | SAP物料凭证年度 |
| sap_document_item_code | varchar | SAP物料凭证行号 |
| factory_code | varchar | 工厂 |
| offset_flag | boolean | 冲销标识 (0正常/1冲销) |
| latest | boolean | 是否最新 |
| status | int | 状态 |
| write_off_time | datetime | 冲销时间 |
| write_off_by | varchar | 冲销人 |
| write_off_eom_storage_id | bigint | 冲销月结ID |
| accounting_month_value | int | 会计月数值 |

### 2.4 eom_storage_added_value（当月库存附加价）

与 detail 表结构类似，核心差异字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 主键 |
| eom_storage_id | bigint FK | 月结主表ID |
| added_price | decimal | 附加单价 |
| **added_value** | **decimal** | **附加价（可编辑）** |
| **base_cur_added_value** | **decimal** | **本位币附加价（可编辑）** |
| metal_value | decimal | 金属价 |
| accounting_total_value | decimal | 库存价值 |
| （其余维度字段同 detail） | | |

### 2.5 冲销关联表

**eom_storage_detail_write_off_rela**（未开票价值冲销关联）：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 被冲销的明细ID |
| eom_storage_id | bigint | 原始月结主表ID |
| eom_storage_write_off_id | bigint | 冲销月结主表ID |
| eom_storage_write_off_number | varchar | 冲销月结单据号 |

**eom_storage_added_value_write_off_rela**（附加价冲销关联）：结构同上。

### 2.6 状态枚举

| 枚举 | 值 | 含义 |
|------|-----|------|
| **单据状态 (EomStorageStatus)** | | |
| Init | 1 | 初始状态 |
| Committed | 2 | 审批完成（已提交） |
| Posted | 9 | 已过账（明细被冲销后的标记） |
| WriteOff | 10 | 已冲销 |
| WriteOffPartly | 11 | 部分冲销 |
| **月结执行状态 (MonthlyClosingStatus)** | | |
| NotExecuted | 1 | 未执行 |
| Executing | 2 | 执行中 |
| Executed | 3 | 已完成 |
| **SAP推送状态** | | |
| CANNOT_BE_PUSHED | 1 | 未推送/不可推送 |
| Pushed | 2 | 推送成功 |
| Failed | 3 | 推送失败 |

---

## 三、核心业务流程

### 3.1 月结完整生命周期

```
① 新建月结 (saveEomStorage)
   → status=Init(1), closing=NotExecuted(1), sapPush=1

② 编辑明细/未开票价值/附加价
   → 行内编辑 eomQuantity/eomPrice, accountingTotalValue, addedValue

③ 执行月结 (executeEomStorage)
   → closing=Executed(3)
   → 从入库登记数据计算生成 Detail + AddedValue 明细

④ 提交 (commitEomStorage)
   → status=Committed(2)
   → 如为冲销单据：被冲销明细→WriteOff(10)，源单据→WriteOffPartly(11)

⑤ 推送SAP (pushEomStorageToSap)
   → 接口A(MM070): 月结数量/单价
   → 接口B(061A): 库存价值 → 接口C(061B): 附加价值
   → sapPushStatus = Pushed(2) 或 Failed(3)

⑥ 冲销
   ├── 完全冲销 (writeOffEomStorage): status→WriteOff(10)
   └── 部分冲销 (writeOffEomStoragePart): 生成冲销单据→再提交生效

↩ 撤销提交 (revertEomStorage)
   → status回退Init(1), 被冲销明细恢复Posted(9)
```

### 3.2 执行月结 (executeEomStorage) — 完整计算过程

> 代码位置：`EomStorageServiceImpl.java` 第 2081-2687 行（约 600 行核心逻辑）

整个执行过程分为 **校验 → 准备 → 加载数据 → Accounting Value 计算落库 → Added Value 计算落库 → 收尾** 六个阶段。

---

#### 阶段一：前置校验（5 项）

```
① eomStorageId 不能为空
② EomStorage 记录必须存在且 inactiveFlag=false
③ legalEntityId（业务机构）不能为空
④ accountingMonth（会计月）不能为空
⑤ monthlyClosingStatus 不能是 Executing（防重复执行）
⑥ 该月结下不能已有明细数据（查 eom_storage_detail，避免重复执行）
```

---

#### 阶段二：数据准备

```java
// 解析会计月
YearMonth yearMonth = YearMonth.parse("2026-06");
LocalDate firstDate = yearMonth.atDay(1);       // 2026-06-01
LocalDate lastDate  = yearMonth.atEndOfMonth();  // 2026-06-30

// 获取工厂代码
String factoryCode = basicDataService.getFactoryCode(legalEntityId);

// 初始化全局工具
riskUnitConversionUtil.initUnitConversionMap("product", allProductIdList);  // 单位转换映射
riskCurveUtil.initExchangeMap(null, allDates);                               // 汇率映射
```

---

#### 阶段三：加载源数据（4 次 SQL 查询）

##### 查询 1：Accounting Value 框架数据

```sql
-- SQL: getEomAccountingValueForCalcFrame(legalEntityId, firstDate, lastDate, null)
-- 从 document_items(入库登记) 出发，关联 physical_deals(合同)、product(商品)、
-- storage_facility(仓库)、sys_company(机构) 等 15+ 张表
-- 查出该机构在该会计月内所有入库记录的框架信息
```

返回字段：documentItemId, productId, deliveryInQuantity, postingDate, physicalDealLineId, offsetFlag 等

##### 查询 2：排除已生成的明细

```sql
-- SQL: getEomAccountingValueForCalcNoDocItemIds(lastDate, docItemIdList)
-- 排除 eom_storage_detail 中已存在的 documentItemId
-- 避免同一个月内重复执行月结时重复生成
```

##### 查询 3：Accounting Value 明细数据（定价/冲销信息）

```sql
-- SQL: getEomAccountingValueForCalcDetail(firstDate, lastDate, docItemIdList, pdLineIdList)
-- 对每条入库记录补充关键计算字段
```

| 补充字段 | 含义 | 来源 |
|---------|------|------|
| offsetFlag | 是否冲销行 | document_items.offset_flag |
| offsetDocumentNumber/Id/ItemId | 被冲销的原始单据信息 | 冲销关联查询 |
| relatedQuantity | 已关联数量（点价关联） | price_triggering 关联汇总 |
| relatedAvgPrice | 关联均价 | 点价关联计算 |
| unrelatedQuantity | 未关联数量 | 总量 - 已关联量 |
| unrelatedAvgPrice | 未关联均价 | 未关联点价计算 |
| provPrice | 暂估价 | 合同定价 |
| fixedPrice | 已定价 | movement_price.settlement_net_price |
| basicPriceFormulaName | 定价公式名 | 合同公式配置 |

##### 查询 4：Added Value 框架数据

```sql
-- SQL: getEomAddedValueForFrame(legalEntityId, addedValueFirstDate, lastDate, null)
-- 注意：addedValueFirstDate = 当年1月1日（附加价是年度累计，从年初算起！）
-- SQL: getEomAddedValueNotInIds()  -- 排除不需要附加价的 documentItemId
```

---

#### 阶段四：Accounting Value 计算并落库

##### 4.1 加载发票数据

```sql
-- invoiceMapper.selectListSumForEom(documentItemIds, lastDate)
-- 按 documentItemId 汇总：已开票数量(quantity) + 开票金额(exclTaxAmount) + 本位币开票金额
```

##### 4.2 逐条计算记账金额（核心逻辑）

对每条入库记录，根据开票状态分两种情况：

**情况 A：完全开票**（已开票量 > 0 且 未开票量 ≤ 0）

```
accountingTotalValue = 开票金额
baseCurAccountingTotalValue = 开票金额(本位币)
fixedPrice = 开票金额 / 入库数量
fixedPriceBaseCur = 开票金额(本位币) / 入库数量
```

**情况 B：部分开票 / 未开票**

```
if (定价公式 == "BasicTriggeredPrice") {  // 点价定价
    if (已关联量 < 已开票量) {
        // 极端情况：关联量不够覆盖已开票
        accountingValue = (入库量 - 已开票量) × 未关联均价 + 开票金额
    } else {
        // 正常情况：拆分为已关联未开票 + 未关联 + 已开票三部分
        accountingValue = (已关联量 - 已开票量) × 关联均价    // 已关联但未开票部分
                        + (入库量 - 已关联量) × 未关联均价     // 未关联部分
                        + 开票金额                             // 已开票部分
    }
} else {  // BasicFixedPrice 或 BasicAveragePrice（非点价）
    accountingValue = (入库量 - 已开票量) × 关联均价 + 开票金额
    // 注：如果 relatedAvgPrice 为空，则回退使用 provPrice（暂估价）
    // 注：如果 unrelatedQuantity ≈ 0（<0.00001），则 unrelatedAvgPrice 回退使用 provPrice
}

fixedPrice = accountingValue / 入库数量
```

##### 4.3 单位转换（至父商品主计量单位）

```
unitConversion = getUnitConversion(当前入库单位, 父商品主单位, productId)

入库数量 *= unitConversion
已定单价 /= unitConversion
暂估单价 /= unitConversion
// 注：已开票数量和未开票数量不做单位转换（代码已注释掉）
```

##### 4.4 本位币转换

```
exchangeRate = getExchangeRate(结算币种, 本位币种, 过账日期)
baseCurAccountingTotalValue = accountingTotalValue × exchangeRate
fixedPriceBaseCur = fixedPrice × exchangeRate
```

##### 4.5 冲销行处理（offsetFlag=true 时生成反向记录）

```
原始行正常保存（offsetFlag 改为 false）

额外生成一条反向记录（reverse），所有数量/金额 × -1：
  reverse.deliveryInQuantity       *= -1
  reverse.pricedQuantity           *= -1
  reverse.relatedQuantity          *= -1
  reverse.unrelatedQuantity        *= -1
  reverse.eomQuantity              *= -1
  reverse.invoicedQuantity         *= -1
  reverse.uninvoicedQuantity       *= -1
  reverse.accountingTotalValue     *= -1
  reverse.baseCurAccountingTotalValue *= -1

反向记录的单据信息指向被冲销的原始单据：
  reverse.documentNumber     = offsetDocumentNumber
  reverse.documentItemId     = offsetDocumentItemId
  reverse.sourceDocumentItemId = 原始 documentItemId
  reverse.documentLineNumber = offsetDocumentLineNumber
  reverse.sapDocumentCode    = offsetSapDocumentCode
  reverse.postingDate        = offsetPostDate
```

##### 4.6 加载额外冲销记录

```sql
-- SQL: getOffsetEomAccountingValueForCalc(已处理的冲销itemId, legalEntityId, lastDate)
-- 查出当前会计月内产生的冲销入库记录（如退货），同样生成明细
```

##### 4.7 落库

```sql
-- 1. 更新历史记录：同 documentItemId 的旧记录标记为非最新
UPDATE eom_storage_detail SET latest = false
WHERE document_item_id IN (oldDocItemIds)

-- 2. 精度处理：所有数量/金额字段统一保留 5 位小数 (HALF_UP)
-- procDetailAccuracy() 方法处理

-- 3. 批量插入
INSERT eom_storage_detail ... (addList)      -- 正常行
INSERT eom_storage_detail ... (offsetList)   -- 额外冲销行
INSERT eom_storage_detail ... (reverseList)  -- 反向记录行
```

---

#### 阶段五：Added Value 计算并落库

##### 5.1 加载明细数据

```sql
-- SQL: getEomAddedValueForDetail(docItemIdSet, pdLineIdSet, lastDate)
-- 与 Accounting Value 类似但使用 additional_price 而非 settlement_net_price
```

##### 5.2 过滤商品财务属性

```sql
-- 查询 product_financial_attributes 表
-- 只有 accountingGroup 为 Z002 或 Z003 的商品才需要计算附加价
-- Z001（原材料）附加价 = 0，不参与计算
```

##### 5.3 逐条计算

```
if (已有附加价 addedValue != null) {
    // 已定价情况：SQL 已算好附加价，直接做单位转换
    addedValue *= unitConversion
} else if (Z002/Z003 商品 && 未定价) {
    // 未定价情况：用暂估价减去 Scorproi 价格
    provPrice /= unitConversion
    latestFinancialDate = getLatestFinancialDate(76, 合同日期, -1, true)
    scoPrice = getScoPrice(productId, latestFinancialDate, 父单位, 币种, 机构)
    addedPrice = provPrice - scoPrice
    addedValue = addedPrice × 转换后的入库数量
}

// 本位币转换
if (baseCurAddedValue 已有) {
    baseCurAddedValue *= unitConversion
} else {
    exchangeRate = getExchangeRate(结算币种, 本位币种, 合同日期)
    baseCurAddedValue = addedValue × exchangeRate
}
```

##### 5.4 冲销行处理（同 Accounting Value，数量/金额 × -1）

##### 5.5 落库

```sql
-- 1. 更新历史记录
UPDATE eom_storage_added_value SET latest = false
WHERE document_item_id IN (oldDocItemIds)

-- 2. 精度处理 (procAddedAccuracy)

-- 3. 批量插入
INSERT eom_storage_added_value ... (addList)      -- 正常行
INSERT eom_storage_added_value ... (reverseList)   -- 反向记录行
INSERT eom_storage_added_value ... (offsetList)    -- 额外冲销行
```

---

#### 阶段六：收尾

```java
// 1. 更新月结状态
eomStorage.setMonthlyClosingStatus(Executed);  // 1 → 3
eomStorage.setUpdatedTime(now);
eomStorage.setUpdatedBy(currentUser);
updateById(eomStorage);

// 2. 清除库存价值报表的 Redis 缓存
redisUtils.delByPrex("DetailedEntriesValue:");
```

---

#### 完整数据流图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        执行月结 数据流                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ① 校验: ID存在 + 机构非空 + 会计月非空 + 未在执行中 + 无已有明细     │
│                                                                     │
│  ② 查源数据:                                                        │
│     ┌──────────────────────────────────────────────────────────┐    │
│     │ document_items (入库登记)                                 │    │
│     │   JOIN physical_deals (合同)                              │    │
│     │   JOIN product (商品)                                     │    │
│     │   JOIN movement_price / price_triggering (定价/点价)      │    │
│     │   JOIN invoice_documents (发票)                           │    │
│     └──────────────────────────────────────────────────────────┘    │
│                    │                                                │
│  ③ 计算:           ▼                                                │
│     ┌─────────────────────────────┐  ┌─────────────────────────┐   │
│     │ Accounting Value            │  │ Added Value              │   │
│     │ 完全开票 → 取开票金额        │  │ Z002/Z003 商品才计算     │   │
│     │ 点价 → 关联均价+未关联均价   │  │ 已定价 → SQL已算好        │   │
│     │ 非点价 → 关联均价           │  │ 未定价 → 暂估价-ScoPrice  │   │
│     │ + 冲销反向记录(×-1)         │  │ + 冲销反向记录(×-1)       │   │
│     │ + 单位转换 + 汇率转换       │  │ + 单位转换 + 汇率转换     │   │
│     └──────────┬──────────────────┘  └───────────┬──────────────┘   │
│                │                                  │                  │
│  ④ 落库:       ▼                                  ▼                  │
│     eom_storage_detail              eom_storage_added_value          │
│     (旧记录 latest=false)           (旧记录 latest=false)            │
│     (新记录 latest=true)            (新记录 latest=true)             │
│     (status=Posted=9)               (status=Posted=9)               │
│                                                                     │
│  ⑤ 收尾: monthlyClosingStatus → Executed(3)                         │
│         清除 Redis 缓存                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 SAP 推送 — 三个接口

#### 接口一：MM070 — 月结库存推送（主推送）

**调用**：`sapDockingService.sendEomStorage()`  
**配置key**：`EomStorage`，DockingBusinessType=71  
**数据来源**：`EomStorageDetail`（已提交月结的明细行）

| SAP字段 | 说明 | 映射来源 |
|---------|------|---------|
| ZXTBS | 系统标识 | 固定 "CTRM" |
| EBELN | SAP订单号 | sapContractCode |
| EBELP | SAP订单行号 | sapContractLineCode |
| MBLNR | SAP物料凭证号 | sapDocumentCode |
| MJAHR | SAP物料凭证年度 | sapDocumentAccountYear |
| ZEILE | SAP物料凭证行号 | sapDocumentItemCode |
| ZFIXATION_MONTH | 会计月 | accountingMonth (去"-") |
| ZMENGE | **月结数量** | eomQuantity |
| ZMEINS | 数量单位 | unit.code |
| ZFIXATION_PRICE | **月结单价** | eomPrice |

#### 接口二：FICO-061A — 金属采购价值推送

**调用**：`sapDockingService.sendMetalPurchaseValueA()`  
**配置key**：`SapEomA`  
**数据来源**：`EomStorageDetail`（latest=1 的明细）

| SAP字段 | 说明 | 映射来源 |
|---------|------|---------|
| BUKRS | 公司代码 | sysCompany.companyCode |
| GJAHR / MONAT | 年度 / 月份 | accountingMonth 解析 |
| CTRMMCDN | CTRM月结单据号 | eomStorage.number |
| CTRMEBELN / CTRMEBELP | CTRM采购订单号/行号 | contractNumber / contractLineNumber |
| AEDAT | 收货日期 | postingDate (yyyyMMdd) |
| EBELN / EBELP | SAP采购订单号/行号 | sapContractCode / sapContractLineCode |
| MBLNR / ZEILE | SAP入库单号/行号 | sapDocumentCode / sapDocumentItemCode |
| MATNR / MAKTX | 物料编码/描述 | product.code / product.name |
| MEINS / MENGE | 单位/收货数量 | unit.code / quantity |
| DKPSL | **待开票数量** | uninvoicedQuantity |
| **FAVTC** | **记账金额(交易货币)** | **accountingTotalValue** |
| WAERS | 交易货币 | currency.code |
| **FAVLC** | **记账金额(本位币)** | **baseCurAccountingTotalValue** |
| ZINVOICED_AMT_T | 开票金额(交易货币) | taxIncInvoiceAmount |
| ZINVOICED_AMT_L | 开票金额(本位币) | taxIncInvoiceAmountBaseCur |

#### 接口三：FICO-061B — 附加价值推送

**调用**：`sapDockingService.sendMetalPurchaseValueB()`  
**配置key**：`SapEomB`  
**数据来源**：`EomStorageAddedValue`（latest=1 的附加价明细）

| SAP字段 | 说明 | 映射来源 |
|---------|------|---------|
| （维度字段同061A） | | |
| **AVTC** | **附加价(交易货币)** | **addedValue** |
| **AVLC** | **附加价(本位币)** | **baseCurAddedValue** |

#### 推送结果处理
- 所有接口成功 → `sapPushStatus = Pushed(2)`
- 任一失败 → `sapPushStatus = Failed(3)`，返回错误信息

### 3.4 冲销机制

#### 完全冲销 (writeOffEomStorage)
直接将 EomStorage + 所有 Detail + 所有 AddedValue 的 status 设为 `WriteOff(10)`

#### 部分冲销 (writeOffEomStoragePart)
1. **生成冲销单据**：`isWriteOffDoc=1`，`sourceId` 指向源单据，`monthlyClosingStatus=Executed`
2. **保存冲销关联**：
   - `eom_storage_detail_write_off_rela` — 记录哪些 Detail 行被冲销
   - `eom_storage_added_value_write_off_rela` — 记录哪些 AddedValue 行被冲销
3. **提交生效**：冲销单据需再通过 `commitEomStorage` 提交
   - 提交时：被冲销明细 → `WriteOff(10)`，源单据 → `WriteOffPartly(11)`

#### 撤销提交 (revertEomStorage)
- `Committed(2)` → 回退 `Init(1)`
- 被冲销的明细恢复为 `Posted(9)`，清除冲销信息
- 重新计算源单据状态

---

## 四、子页面功能详解

### 4.1 主列表页 (index.vue)

**查询条件**：会计月、单据号、业务机构、制单人

**表格列**：

| 列名 | 字段 | 说明 |
|------|------|------|
| 单据号 | number | |
| 业务机构 | legalEntityName | |
| 会计月 | accountingMonth | |
| 月结状态 | monthlyClosingStatus | 字典渲染 |
| 单据状态 | status | 字典渲染 |
| SAP推送状态 | sapPushStatus | 字典渲染 |

**操作按钮及权限**：

| 操作 | 权限标识 | 可用条件 |
|------|---------|---------|
| 新建 | add | — |
| 编辑-未开票价值 | notEdit | — |
| 编辑-附加价 | monthEdit | — |
| 编辑-单据 | docEdit | 仅冲销单据 |
| 删除 | del | 仅初始状态 |
| 查看-未开票/附加价/单据 | not/month | — |
| **执行月结** | excute | 月结状态=未执行 |
| **推送SAP** | pushToSap | — |
| 部分冲销 | part | — |
| 整单冲销 | writeOff | 已推送可点击，已冲销禁用 |
| 提交 | submit | — |
| 撤销提交 | undoSubmit | — |

**特殊逻辑**：执行月结前调用 `checkEomStorage` 校验，如有未推送SAP的单据会弹窗提示确认

### 4.2 新建/编辑页 (add.vue)

**表单字段**：
- 单据号（必填，自动生成，key: `eom_storage`）
- 业务机构（必填，级联选择）
- 会计月（必填，月份选择器，默认当前月）
- 备注

### 4.3 月结明细 (detail.vue)

**查询条件**：单据号、合同号、交易对手、业务组合、产品、货权转移日期范围、制单人、SAP批次号/合同号/单据号、会计月、未开票数量(默认>0)

**表格列（可编辑标 ★）**：

| 列名 | 字段 | 可编辑 |
|------|------|--------|
| 业务类型 | actionName | |
| 货权转移日期 | titleTransferDate | |
| 单据号 | documentNumber | |
| 交易对手 | counterpartyName | |
| 仓库 | storageName | |
| 业务机构 | legalEntityName | |
| 业务组合 | businessDepartmentName | |
| 业务板块 | businessSegmentName | |
| 行号 | documentLineNumber | |
| 合同号 | contractNumber | |
| 合同行号 | contractLineNumber | |
| 入库数量 | deliveryInQuantity | |
| 入库单位 | deliveryInQuantityUnitName | |
| 产品 | productName | |
| SAP批次号 | sapBatchNumber | |
| SAP合同号 | sapContractCode | |
| SAP合同行号 | sapContractLineCode | |
| SAP单据号 | sapDocumentCode | |
| SAP会计年度 | sapDocumentAccountYear | |
| SAP项目号 | sapDocumentItemCode | |
| 已定价数量 | pricedQuantity | |
| 关联数量 | relatedQuantity | |
| 关联均价 | relatedAvgPrice | |
| 未关联数量 | unrelatedQuantity | |
| 未关联均价 | unrelatedAvgPrice | |
| **月结数量** | **eomQuantity** | **★** |
| **月结价格** | **eomPrice** | **★** |
| 币种 | currencyName | |
| 已开票数量 | invoicedQuantity | |
| 未开票数量 | uninvoicedQuantity | |

### 4.4 未开票库存价值 (entryNotInvoiced/index.vue)

**数据来源表**：`eom_storage_detail`  
**查询API**：`listAccountingValue`  
**导出API**：`exportAccountingValueList`

在明细页列基础上增加：

| 列名 | 字段 | 可编辑 |
|------|------|--------|
| 状态 | status | |
| 会计月 | accountingMonth | |
| 过账日期 | postingDate | |
| 数量 | quantity | |
| 冲销数量 | offsetQuantity | |
| 母合金 | parentProductName | |
| 工厂 | factoryName | |
| 暂估价 | provPrice | |
| 固定价 | fixedPrice | |
| 合同暂估价 | contractProvPrice | |
| 定价 | fixationPrice | |
| **记账金额** | **accountingTotalValue** | **★** |
| 含税发票金额 | taxIncInvoiceAmount | |
| 本位币 | baseCurrencyName | |
| **本位币记账金额** | **baseCurAccountingTotalValue** | **★** |
| 本位币含税发票金额 | taxIncInvoiceAmountBaseCur | |

### 4.5 当月库存附加价 (monlyInventory/index.vue)

**数据来源表**：`eom_storage_added_value`  
**查询API**：`listAddedValue`  
**导出API**：`exportAddedValueList`

在未开票页列基础上，差异列：

| 列名 | 字段 | 可编辑 |
|------|------|--------|
| 附加单价 | addedPrice | |
| **附加价** | **addedValue** | **★** |
| **本位币附加价** | **baseCurAddedValue** | **★** |

### 4.6 部分冲销 (eomWriteoff/add.vue)

**表单字段**：单据号、源单据号(只读)、业务机构(只读)、会计月、备注

**Tab页**：
1. 未开票库存价值 — 已选择的冲销行
2. 当月库存附加价 — 已选择的冲销行

**操作**：增加（打开选择弹窗）→ 选择行 → 保存

---

## 五、API 接口完整清单

### 月结主操作

| HTTP | 端点 | 功能 |
|------|------|------|
| POST | `/api/eomstorage/listEomStorage` | 月结列表查询 |
| POST | `/api/eomstorage/saveEomStorage` | 新建/编辑月结 |
| DELETE | `/api/eomstorage/deleteEomStorage` | 删除月结 |
| POST | `/api/eomstorage/executeEomStorage` | ⭐ 执行月结 |
| POST | `/api/eomstorage/checkEomStorage` | 执行前校验 |
| POST | `/api/eomstorage/commitEomStorage` | ⭐ 提交 |
| POST | `/api/eomstorage/revertEomStorage` | 撤销提交 |
| POST | `/api/eomstorage/pushEomStorageToSap` | ⭐ 推送SAP |
| POST | `/api/eomstorage/writeOffEomStorage` | ⭐ 完全冲销 |
| POST | `/api/eomstorage/writeOffEomStoragePart` | ⭐ 部分冲销保存 |
| GET | `/api/eomstorage/writeOffEomStoragePartInfo` | 查看部分冲销 |

### 明细/价值操作

| HTTP | 端点 | 功能 |
|------|------|------|
| POST | `/api/eomstorage/listEomStorageDetail` | 月结明细列表 |
| POST | `/api/eomstorage/saveEomStorageDetail` | 保存明细 |
| DELETE | `/api/eomstorage/deleteEomStorageDetail` | 删除明细 |
| POST | `/api/eomstorage/listAccountingValue` | 未开票库存价值列表 |
| POST | `/api/eomstorage/listAccountingValueForDetailed` | 未开票(详细-弹窗用) |
| POST | `/api/eomstorage/saveAccountingValue` | 保存未开票价值 |
| DELETE | `/api/eomstorage/deleteAccountingValue` | 删除未开票价值 |
| POST | `/api/eomstorage/listAddedValue` | 当月附加价列表 |
| POST | `/api/eomstorage/saveAddedValue` | 保存附加价 |
| DELETE | `/api/eomstorage/deleteAddedValue` | 删除附加价 |

### 导出

| HTTP | 端点 | 功能 |
|------|------|------|
| POST | `/api/eomstorage/exportAccountingValueList` | 导出未开票价值 |
| POST | `/api/eomstorage/exportAddedValueList` | 导出附加价 |

### 辅助

| HTTP | 端点 | 功能 |
|------|------|------|
| GET | `/api/eomstorage/getLatestEomMonth` | 获取最新会计月 |
| GET | `/api/eomstorage/getExistEomMonth` | 获取已有会计月列表 |
| GET | `/api/eomstorage/getFirstDayOfCurrentAccountingMonth` | 当前会计区间首日 |

### Engagement 报表（另一个 Controller）

| HTTP | 端点 | 功能 |
|------|------|------|
| POST | `/api/eomEngagementReport/getDetailReport` | 已定价未交割明细 |
| POST | `/api/eomEngagementReport/getSummaryReport` | 金属已定价未交割汇总 |
| POST | `/api/eomEngagementReport/reportData/save` | 手工录入-新增 |
| POST | `/api/eomEngagementReport/reportData/update` | 手工录入-修改 |
| DELETE | `/api/eomEngagementReport/reportData/delete` | 手工录入-删除 |
| POST | `/api/eomEngagementReport/reportData/list` | 手工录入-列表 |

---

## 六、数据来源追溯

### 执行月结时数据从哪来？

```
入库登记 (document_items)
  ├── 合同 (physical_deals / physical_deal_line)
  ├── 定价 (movement_price / price_triggering / trigger_rela / trigger_unrela)
  ├── 发票 (invoice_documents)
  ├── 商品 (product / product_line)
  ├── 财务属性 (商品 Z002/Z003 决定是否需要附加价)
  └── 冲销单据 (document_items WHERE offset_flag='Y')
        ↓
    SQL 聚合计算
        ↓
  ┌─ eom_storage_detail (Accounting Value)
  └─ eom_storage_added_value (Added Value)
```

### 推送SAP时数据从哪来？

```
eom_storage_detail (latest=1, status=Committed)
  → 接口A(MM070): eomQuantity, eomPrice
  → 接口B(061A): accountingTotalValue, baseCurAccountingTotalValue, uninvoicedQuantity

eom_storage_added_value (latest=1)
  → 接口C(061B): addedValue, baseCurAddedValue
```

---

## 七、关键文件索引

| 层级 | 文件路径 | 说明 |
|------|---------|------|
| **前端API** | `hmefront/src/api/business/action/eom.js` | 所有前端API调用 |
| **前端路由** | `hmefront/src/router/warehouse.js` | EOM路由定义 |
| **前端主页** | `hmefront/src/views/business/warehouse_eom/index.vue` | 月结列表 |
| **前端新建** | `hmefront/src/views/business/warehouse_eom/add.vue` | 新建/编辑 |
| **前端明细** | `hmefront/src/views/business/warehouse_eom/detail.vue` | 月结明细 |
| **前端未开票** | `hmefront/src/views/business/warehouse_eom/entryNotInvoiced/index.vue` | 未开票价值 |
| **前端附加价** | `hmefront/src/views/business/warehouse_eom/monlyInventory/index.vue` | 附加价 |
| **前端冲销** | `hmefront/src/views/business/warehouse_eom/eomWriteoff/add.vue` | 部分冲销 |
| **后端Controller** | `bcadmin-system/.../rest/EOMStorageController.java` | REST API入口 |
| **后端Controller** | `bcadmin-system/.../rest/EomEngagementReportController.java` | Engagement报表 |
| **后端核心** | `bcadmin-system/.../service/impl/EomStorageServiceImpl.java` | **核心逻辑(~3700行)** |
| **后端Service** | `bcadmin-system/.../service/impl/EomStorageDetailServiceImpl.java` | 明细CRUD |
| **后端Service** | `bcadmin-system/.../service/impl/EomStorageAddedValueServiceImpl.java` | 附加价CRUD |
| **后端Service** | `bcadmin-system/.../service/impl/EomEngagementServiceImpl.java` | Engagement快照聚合 |
| **后端Service** | `bcadmin-system/.../service/impl/EomEngagementDetailServiceImpl.java` | Engagement明细报表 |
| **后端Service** | `bcadmin-system/.../service/impl/EomEngagementSummaryServiceImpl.java` | Engagement汇总报表 |
| **后端Service** | `bcadmin-system/.../service/impl/EomCommittedStockValuationServiceImpl.java` | 月底净库存估值 |
| **Entity** | `bcadmin-db/.../domain/EomStorage.java` | 月结主表实体 |
| **Entity** | `bcadmin-db/.../domain/EomStorageDetail.java` | 明细实体 |
| **Entity** | `bcadmin-db/.../domain/EomStorageAddedValue.java` | 附加价实体 |
| **Entity** | `bcadmin-db/.../domain/EomStorageDetailWriteOffRela.java` | 明细冲销关联 |
| **Entity** | `bcadmin-db/.../domain/EomStorageAddedValueWriteOffRela.java` | 附加价冲销关联 |
| **Mapper XML** | `bcadmin-db/.../EomStorageMapper.xml` | **核心SQL(~1500行)** |
| **Mapper XML** | `bcadmin-db/.../EomStorageDetailMapper.xml` | 明细SQL |
| **Mapper XML** | `bcadmin-db/.../EomStorageAddedValueMapper.xml` | 附加价SQL |
| **SAP DTO** | `bcadmin-docking/.../EomStorage/EomStorageRequest.java` | MM070接口结构 |
| **SAP DTO** | `bcadmin-docking/.../MetalPurchaseValue/MetalPurchaseValueRequestA.java` | 061A接口结构 |
| **SAP DTO** | `bcadmin-docking/.../MetalPurchaseValue/MetalPurchaseValueRequestB.java` | 061B接口结构 |
| **枚举** | `bcadmin-system/.../common/EomStorageStatus.java` | 单据状态枚举 |
| **枚举** | `bcadmin-system/.../common/EomStorageMonthlyClosingStatusEnum.java` | 月结执行状态 |
| **枚举** | `bcadmin-system/.../common/EomActionEnum.java` | 冲销动作枚举 |
| **建表SQL** | `bcadmin-db/delta-script/20260129/` | 部分冲销字段 |
| **建表SQL** | `bcadmin-db/delta-script/20260123/` | 部分开票支持 |
| **建表SQL** | `bcadmin-db/delta-script/20260508/` | Engagement报表表 |
| **建表SQL** | `bcadmin-db/delta-script/202605/` | 小额对冲表 |
