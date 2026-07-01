# 库存价值报表（listDetailedEntriesValue）调用链梳理

## 概述

库存价值报表用于展示未开票库存价值（accounting value）和库存附加价（added value），是月结系统的核心报表之一。

**入口方法**：`EOMStorageController.listDetailedEntriesValue(DetailedEntriesValueQuery)`  
**核心Service**：`EomStorageServiceImpl.listDetailedEntriesValue()`

---

## 一、完整调用链

```
Controller层：
  EOMStorageController.listDetailedEntriesValue()
    └─ EomStorageServiceImpl.listDetailedEntriesValue()

Service层（EomStorageServiceImpl）：
  ├─ 阶段1：Redis缓存控制
  │   └─ 读取 offsetFlag 控制是否显示冲销数据
  │
  ├─ 阶段2：SQL查询（4层CTE + 最终SELECT）
  │   ├─ CTE1: latest          [为每个document_item_id找最新月份]
  │   ├─ CTE2: new_accounting  [获取最新月份的未开票库存价值]
  │   ├─ CTE3: new_added       [获取最新月份的库存附加价]
  │   ├─ CTE4: main            [合并accounting和added value]
  │   └─ SELECT: 关联维度表，补全名称字段
  │
  ├─ 阶段3：补充数据查询
  │   ├─ DocumentsService.selectOffsetQuantityByItemIds()  [冲销数量]
  │   └─ EomStorageMapper.listInvoiceInfo()                 [发票信息]
  │
  └─ 阶段4：Java层计算
      ├─ 含税发票金额计算
      ├─ 金属价值计算
      ├─ 会计总价值调整
      ├─ CD Added Value发票调整
      ├─ 已开票/未开票数量计算
      ├─ 冲销数量回填
      └─ 冲销单据特殊处理
```

---

## 二、数据来源表

### 核心业务表

| # | 表名 | 用途 |
|---|------|------|
| 1 | `eom_storage` | 库存月结主表 |
| 2 | `eom_storage_detail` | 未开票库存价值明细（accounting value） |
| 3 | `eom_storage_added_value` | 当月库存附加价明细（added value） |

### 关联维度表

| # | 表名 | 用途 |
|---|------|------|
| 4 | `physical_deals` | 实物交易/合同 |
| 5 | `document_items` | 单据行项目 |
| 6 | `document_actions` | 单据动作类型 |
| 7 | `storage_facility` | 仓储设施 |
| 8 | `product` | 产品信息 |
| 9 | `unit` | 计量单位 |
| 10 | `currency` | 币种 |
| 11 | `sys_company` | 公司/法人实体 |
| 12 | `counterparty` | 交易对手 |
| 13 | `sys_department` | 部门 |
| 14 | `sys_business_segment` | 业务板块 |
| 15 | `abutment_config` / `abutment_config_details` | 工厂名称映射 |
| 16 | `invoice_documents` | 发票行项目 |
| 17 | `invoice` | 发票主表 |

---

## 三、SQL查询结构详解

### 3.1 CTE1：latest（最新月份定位）

**目的**：为每个 `document_item_id` 找到最新的 `accounting_month_value`

**数据来源**：
- `eom_storage_detail`（type='esd'）
- `eom_storage_added_value`（type='esav'）
- 两者通过 UNION ALL 合并

**过滤条件**：
- `eom_storage.inactive_flag = 0, status != 10`
- `eom_storage_detail/eom_storage_added_value.inactive_flag = 0, status != 10, latest = 1`
- 各种动态查询条件（合同号、法人实体、日期范围等）

**输出**：`document_item_id → MAX(accounting_month_value)`

### 3.2 CTE2：new_accounting（未开票库存价值）

**目的**：获取最新月份的未开票库存价值数据

**数据来源**：
- `eom_storage_detail main`
- INNER JOIN `eom_storage`（过滤有效月结记录）
- INNER JOIN `latest`（匹配最新月份）

**关键字段**：
- `quantity`（入库数量）
- `offset_quantity`（冲销数量，取反 * -1）
- `accounting_total_value`（会计总价值）
- `base_cur_accounting_total_value`（本位币会计总价值）

### 3.3 CTE3：new_added（库存附加价）

**目的**：获取最新月份的库存附加价数据

**数据来源**：
- `eom_storage_added_value main`
- INNER JOIN `eom_storage`
- INNER JOIN `latest`

**关键字段**：
- `quantity`
- `offset_quantity`（取反 * -1）
- `invoiced_quantity`（已开票数量）
- `uninvoiced_quantity`（未开票数量）
- `added_value`（附加价值）
- `base_cur_added_value`（本位币附加价值）

### 3.4 CTE4：main（合并数据）

**目的**：合并 accounting 和 added value 数据

**逻辑**：
```
Part A: new_accounting LEFT JOIN new_added（以 accounting 为主）
UNION ALL
Part B: new_added LEFT JOIN new_accounting WHERE accounting 不存在（仅有 added value 的记录）
```

**关键字段合并**：
- `quantity, offset_quantity`：来自任一侧
- `accounting_total_value, base_cur_accounting_total_value`：优先取 accounting 侧
- `invoiced_quantity, uninvoiced_quantity, added_value, base_cur_added_value`：优先取 added 侧

### 3.5 最终SELECT（关联维度表）

**目的**：main 数据关联维度表，补全名称等展示字段

**关联表**：
- `physical_deals` → contract_number
- `document_items` → source_document_item_id, warehouseQuantity(di.quantity)
- `sys_company` → legalEntityName
- `document_actions` → actionName（含冲销标记 ' reverse'）
- `storage_facility` → storageName
- `counterparty` → counterpartyName
- `sys_department` → businessDepartmentName
- `sys_business_segment` → businessSegmentName
- `unit × 2` → deliveryInQuantityUnitName, quantityUnitName
- `product × 2` → productName, parentProductName
- `currency × 2` → currencyName, baseCurrencyName
- `abutment_config_details` → factoryName

---

## 四、Java层计算公式

### 4.1 前置处理

```java
// 1. Redis 缓存 offsetFlag 控制
String key = "EomControl:DetailedEntriesValue_offsetFlag";
Integer offsetFlag = redisUtils.get(key);
if (offsetFlag != null) query.setOffsetFlag(offsetFlag);

// 2. 会计月份 → 月末日期
YearMonth yearMonth = YearMonth.parse(query.getAccountingMonth());
LocalDate lastDate = yearMonth.atEndOfMonth();

// 3. 结果缓存（全量查询时 size==-1，缓存120秒）
String resultKey = "DetailedEntriesValue:" + query.hashCode();
```

### 4.2 补充数据获取

**A. 冲销数量（offsetQuantity）**
```java
// 从 documents 表查询冲销单据的关联数量
List<DocumentItems> offsetItems = documentsService.selectOffsetQuantityByItemIds(documentItemIds, lastDate);
// 映射：sourceDocumentItemId → 冲销数量
Map<Long, Double> offsetQuantityMap;
```

**B. 发票信息（invoiceInfo）**
```java
// 分批查询发票信息（每批500条，超过则并行查询，最多8线程）
List<InvoiceDocumentsRes> invoiceInfos = baseMapper.listInvoiceInfo(documentItemIds, lastDate);
// 按 documentItemId 聚合，区分 metal value 和 added value 发票
// invoiceMap: 金属价值发票
// addedValueInvoiceMap: 附加价值发票（cdValuationType == "ADDED_VALUE"）
```

### 4.3 核心计算公式

**① 含税发票金额 `taxIncInvoiceAmount`**
```
if offsetFlag == true:
    taxIncInvoiceAmount = exclTaxAmount × (-1)
else:
    taxIncInvoiceAmount = exclTaxAmount

同理：
baseCurTaxIncInvoiceAmount = baseCurrencyExclTaxAmount × (offsetFlag ? -1 : 1)
```

**② 金属价值 `metalValue`**
```
metalValuePart1 = accountingTotalValue × (unmatchQuantity / warehouseQuantity)
metalValuePart2 = taxIncInvoiceAmount - addedValue
metalValue = metalValuePart1 + metalValuePart2
```

其中：
- `unmatchQuantity = warehouseQuantity(di.quantity) - invoiceQuantity`
- `warehouseQuantity` = document_items.quantity（入库登记数量）

**本位币版本：**
```
baseCurMetalValuePart1 = baseCurAccountingTotalValue × (unmatchQuantity / warehouseQuantity)
baseCurMetalValuePart2 = baseCurTaxIncInvoiceAmount - baseCurAddedValue
baseCurMetalValue = baseCurMetalValuePart1 + baseCurMetalValuePart2
```

**③ 会计总价值 `accountingTotalValue`**
```
if invoiceStage == "final" 或 unmatchQuantity <= 0:
    // 已完全开票 → 直接用发票金额
    accountingTotalValue = taxIncInvoiceAmount
    baseCurAccountingTotalValue = baseCurTaxIncInvoiceAmount
else:
    // 未完全开票 → 保持 SQL 查出的原始值不变
    accountingTotalValue = 原值（来自 eom_storage_detail）
    baseCurAccountingTotalValue = 原值
```

**④ 附加价值调整（CD Added Value 发票）**
```
if addedValueInvoiceInfo 存在:
    cdAddedValue = addedValueInvoice.exclTaxAmount
    
    newAddedValue = addedValue + cdAddedValue
    newMetalValue = metalValue - cdAddedValue
    
    // 本位币按比例调整
    if addedValue > 0:
        baseCurAddedValue = (addedValue + cdAddedValue) / addedValue × baseCurAddedValue（原值）
    if metalValue > 0:
        baseCurMetalValue = (metalValue - cdAddedValue) / metalValue × baseCurMetalValue（原值）
```

**⑤ 已开票/未开票数量**
```java
// 单位换算
Double unitConversion = riskUnitConversionUtil.getUnitConversionNew(quantityUnitId, deliveryInQuantityUnitId, productId);
if (unitConversion != null) {
    invoicedQuantity = unitConversion × invoiceInfo.quantity
}
uninvoicedQuantity = deliveryInQuantity - invoicedQuantity
```

**⑥ 冲销数量回填**
```java
if (offsetQuantityMap.containsKey(documentItemId)):
    offsetQuantity = (-1) × offsetQuantityMap[documentItemId]
```

**⑦ 冲销单据的 accounting value 特殊处理**
```
// 当冲销单据(offsetFlag=true)的 accountingTotalValue == 0 时：
// 递归查找源单据，用源单据的值取反
offset.accountingTotalValue = source.accountingTotalValue × (-1)
offset.baseCurAccountingTotalValue = source.baseCurAccountingTotalValue × (-1)
offset.addedValue = source.addedValue × (-1)
offset.baseCurAddedValue = source.baseCurAddedValue × (-1)
offset.metalValue = source.metalValue × (-1)
offset.baseCurMetalValue = source.baseCurMetalValue × (-1)
```

---

## 五、字段映射关系

### 5.1 基础信息字段

| 输出字段 | 来源 | 说明 |
|----------|------|------|
| `documentItemId` | eom_storage_detail / eom_storage_added_value | 单据行ID |
| `physicalDealId` | 同上 | 实物交易ID |
| `actionId` | 同上 | 单据动作ID |
| `legalEntityId` | 同上 | 法人实体ID |
| `storageId` | 同上 | 仓库ID |
| `counterpartyId` | 同上 | 交易对手ID |
| `businessDepartmentId` | 同上 | 业务部门/组合ID |
| `businessSegmentId` | 同上 | 业务板块ID |
| `quantityUnitId` | 同上 | 数量单位ID |
| `productId` | 同上 | 产品ID |
| `currencyId` | 同上 | 结算币种ID |
| `offsetFlag` | 同上 | 冲销标记（0/1） |
| `factoryCode` | 同上 | 工厂代码 |
| `accountingMonth` | eom_storage | 会计月份 |
| `titleTransferDate` | eom_storage_detail/added_value | 物权转移日期 |
| `documentNumber` | 同上 | 单据编号 |
| `postingDate` | 同上 | 过账日期 |
| `documentLineNumber` | 同上 | 单据行号 |
| `contractLineNumber` | 同上 | 合同行号 |
| `deliveryInQuantity` | 同上 | 入库数量 |
| `deliveryInQuantityUnitId` | 同上 | 入库数量单位ID |
| `sapBatchNumber` | 同上 | SAP批次号 |
| `sapContractCode` | 同上 | SAP合同代码 |
| `sapContractLineCode` | 同上 | SAP合同行代码 |
| `sapDocumentCode` | 同上 | SAP单据代码 |
| `sapDocumentAccountYear` | 同上 | SAP单据会计年度 |
| `sapDocumentItemCode` | 同上 | SAP单据行代码 |
| `baseCurrencyId` | 同上 | 本位币ID |

### 5.2 计算字段

| 输出字段 | 计算公式 | 说明 |
|----------|---------|------|
| `quantity` | 来自SQL | 数量 |
| `offsetQuantity` | Java层计算 | 冲销数量（取反） |
| `accountingTotalValue` | eom_storage_detail + Java调整 | 会计总价值（未开票库存价值） |
| `baseCurAccountingTotalValue` | 同上 + Java调整 | 本位币会计总价值 |
| `invoicedQuantity` | Java层从发票聚合 | 已开票数量 |
| `uninvoicedQuantity` | Java层计算 | 未开票数量 = deliveryInQuantity - invoicedQuantity |
| `addedValue` | eom_storage_added_value + Java调整 | 附加价值 |
| `baseCurAddedValue` | 同上 | 本位币附加价值 |
| `taxIncInvoiceAmount` | Java层计算 | 含税发票金额 |
| `baseCurTaxIncInvoiceAmount` | Java层计算 | 本位币含税发票金额 |
| `metalValue` | Java层计算 | 金属价值 |
| `baseCurMetalValue` | Java层计算 | 本位币金属价值 |
| `warehouseQuantity` | document_items.quantity | 入库登记数量（用于比例计算） |
| `sourceDocumentItemId` | document_items.source_document_item_id | 源单据行ID（冲销关联） |

### 5.3 名称字段

| 输出字段 | 来源 | 说明 |
|----------|------|------|
| `actionName` | document_actions + Java | 动作名称（冲销加 ' reverse' 后缀） |
| `counterpartyName` | counterparty.name | 交易对手名称 |
| `storageName` | storage_facility.name | 仓库名称 |
| `legalEntityName` | sys_company.COMPANY_NAME | 法人实体名称 |
| `businessDepartmentName` | sys_department.DEPT_NAME | 业务部门名称 |
| `businessSegmentName` | sys_business_segment.business_segment_name | 业务板块名称 |
| `deliveryInQuantityUnitName` | unit.name | 入库数量单位名称 |
| `quantityUnitName` | unit.name | 数量单位名称 |
| `productName` | product.code + '-' + product.name | 产品编码-名称 |
| `parentProductName` | product.code + '-' + product.name | 父产品编码-名称 |
| `productCode` | product.code | 产品编码 |
| `currencyName` | currency.name | 结算币种名称 |
| `baseCurrencyName` | currency.name | 本位币名称 |
| `factoryName` | abutment_config_details.code_name | 工厂名称 |

---

## 六、关键业务逻辑总结

1. **双数据源合并**：报表同时展示「未开票库存价值」（accounting）和「库存附加价」（added value），通过 `document_item_id` 关联。以 accounting 为主 LEFT JOIN added value，再 UNION 仅有 added value 无 accounting 的记录。

2. **最新月份定位**：通过 `latest` CTE，为每个 `document_item_id` 找到最大的 `accounting_month_value`，确保展示的是最新月结周期的数据。

3. **发票信息聚合**：`listInvoiceInfo` 按 `document_item_id` + `cd_valuation_type` 分组聚合发票金额和数量，区分金属价值发票和附加价值发票。

4. **金属价值核心公式**：
   - 未完全开票：`metalValue = accountingTotalValue × (未匹配数量/入库数量) + (发票金额 - 附加价值)`
   - 已完全开票（final 或 unmatchQuantity ≤ 0）：`accountingTotalValue` 直接用发票金额替代

5. **冲销单据处理**：
   - 冲销单据（offsetFlag=true）的金额字段取反
   - 当冲销单据 accounting value 为 0 时，递归查找源单据，用源单据值 × (-1) 填充

6. **CD 附加价值发票调整**：当存在 `cdValuationType = ADDED_VALUE` 的发票时，将发票金额加到 `addedValue`，同时从 `metalValue` 中扣减，保持总值不变。

7. **单位换算**：已开票数量通过 `riskUnitConversionUtil` 进行计量单位换算（quantityUnit → deliveryInQuantityUnit）。

8. **缓存策略**：全量查询（size==-1）时结果缓存到 Redis，TTL 120秒。

---

## 七、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/EOMStorageController.java:112` |
| Service接口 | `bcadmin-system/.../service/EomStorageService.java:30` |
| Service实现 | `bcadmin-system/.../service/impl/EomStorageServiceImpl.java:280` |
| Mapper接口 | `bcadmin-db/.../dao/EomStorageMapper.java:25` |
| Mapper XML | `bcadmin-db/src/main/resources/system/EomStorageMapper.xml` |
| DTO | `bcadmin-db/.../domain/DetailedEntriesValue.java` |
| Query | `bcadmin-db/.../dto/DetailedEntriesValueQuery.java` |

---

## 八、数据流全景图

```
┌─────────────────────────────────────────────────────────────┐
│              阶段1：Redis缓存控制                             │
│                                                             │
│  读取 offsetFlag 控制是否显示冲销数据                          │
│                                                             │
│  → 产出：查询参数                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          阶段2：SQL查询（4层CTE + 最终SELECT）                │
│                                                             │
│  CTE1: latest          [为每个document_item_id找最新月份]     │
│  CTE2: new_accounting  [获取最新月份的未开票库存价值]           │
│  CTE3: new_added       [获取最新月份的库存附加价]              │
│  CTE4: main            [合并accounting和added value]          │
│  SELECT: 关联维度表，补全名称字段                              │
│                                                             │
│  → 产出：基础数据列表                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              阶段3：补充数据查询                                │
│                                                             │
│  DocumentsService.selectOffsetQuantityByItemIds()            │
│    → 冲销数量                                                │
│                                                             │
│  EomStorageMapper.listInvoiceInfo()                          │
│    → 发票信息（分批查询，并行处理）                             │
│                                                             │
│  → 产出：补充数据Map                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              阶段4：Java层计算                                 │
│                                                             │
│  ① 含税发票金额计算                                          │
│  ② 金属价值计算                                              │
│  ③ 会计总价值调整                                             │
│  ④ CD Added Value发票调整                                    │
│  ⑤ 已开票/未开票数量计算                                      │
│  ⑥ 冲销数量回填                                              │
│  ⑦ 冲销单据特殊处理                                          │
│                                                             │
│  → 产出：完整的报表数据                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
                  前端报表展示
```

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
