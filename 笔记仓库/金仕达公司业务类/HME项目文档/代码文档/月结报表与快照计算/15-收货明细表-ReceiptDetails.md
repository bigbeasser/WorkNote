# 收货明细表（receiptDetails）调用链梳理

## 概述

收货明细表用于展示采购入库登记的详细信息，包括入库数量、暂估金额、折扣等。是Greenlist价格快照计算的重要数据源。

**入口方法**：`ReportController.receiptDetails(ShipmentNotInvoicedReq, BasePage)`  
**核心Service**：`ReportServiceImpl.receiptDetails()`

---

## 一、完整调用链

```
Controller层：
  ReportController.receiptDetails()                    [GET /api/report/receiptDetails]
    └─ ReportServiceImpl.receiptDetails()              [Service层：数据权限 + 后处理]

Service层（ReportServiceImpl）：
  ├─ 阶段1：数据权限过滤
  │   └─ SecurityUtils.getCurrentUserDataScope()      [获取当前用户数据权限]
  │
  ├─ 阶段2：SQL查询
  │   ├─ PageHelper.startPage()                       [分页]
  │   └─ ReportMapper.receiptDetails()                [MyBatis SQL查询]
  │       └─ ReportMapper.xml#receiptDetails          [SQL：多表JOIN查询]
  │
  ├─ 阶段3：后处理
  │   ├─ DictCommonService.getOneDictDetailBytName()  [字典翻译：单据状态、SAP推送状态]
  │   └─ RiskUnitConversionUtil.getUnitConversion()   [单位转换：原始→主计量KG]
  │
  └─ 阶段4：扩展字段计算
      └─ fillReceiptDetailsExtendedFields()
          ├─ UnitService.getByName("TO")              [获取吨单位]
          ├─ RiskUnitConversionUtil.getUnitConversion() [单位转换：主计量→吨]
          └─ querySpreadDetailByPdlIdMap()            [批量查询升贴水]
              └─ SysReportService.spreadDetails()     [升贴水明细表服务，每批500条]
```

---

## 二、数据来源表

### 核心业务表

| 表名 | 别名/角色 | 说明 |
|------|-----------|------|
| `systemdb.document_items` | **主表** | 入库登记明细行（每条明细一行记录） |
| `systemdb.documents` | 主表头 | 入库登记单据头（`action_id=42` 标识入库登记） |
| `systemdb.physical_deal_line` | 合同行 | 现货/长单合同行信息 |
| `systemdb.physical_deals` | 合同头 | 现货/短单/长单合同（`ps_flag='P'` 采购方向） |
| `systemdb.contract_execution_monitor` | 合同监控 | 订单状态（`close_contract_status`） |
| `systemdb_ext.physical_deal_line_ext` | 合同行扩展 | **暂估价格**（`estimated_price`） |

### 冲销关联表

| 表名 | 角色 | 说明 |
|------|------|------|
| `systemdb.document_items` (dioff) | 冲销明细 | 通过 `source_document_item_id` 关联原明细 |
| `systemdb.documents` (docoff) | 冲销单据 | `action_id=42 AND status=2` 的冲销单据 |

### 基础数据表

| 表名 | 说明 |
|------|------|
| `admindb.counterparty` | 交易对手名称 |
| `admindb.sys_company` | 业务机构（公司）名称 |
| `admindb.sys_department` | 业务部门名称 |
| `admindb.sys_business_segment` | 业务板块名称 |
| `admindb.sys_personnel` | 业务员名称 |
| `systemdb.storage_facility` | 仓库名称 |
| `systemdb.product` | 商品信息（CODE-NAME） |
| `systemdb.unit` | 计量单位（原始单位 + 主计量KG） |
| `systemdb.abutment_config_details` | SAP工厂名称 |
| `systemdb.currency` | 结算币种 |

---

## 三、计算公式详解

### 1. 数量计算

#### (a) SQL层直接取值
```
quantity = document_items.quantity   -- 原始入库数量（原始单位）
```

#### (b) Service层：主计量单位数量（mainQuantity）
```java
// 初始赋值
mainQuantity = quantity

// 当原始单位 ≠ 主计量单位(KG)时，进行单位转换：
if (unitId ≠ mainUnitId) {
    unitConversion = RiskUnitConversionUtil.getUnitConversion(unitId, mainUnitId, productId)
    mainQuantity = quantity × unitConversion
}

// 冲销单据取反：
if (offsetFlag == "Y") {
    mainQuantity = mainQuantity × (-1)
    quantity = quantity × (-1)
}
```

#### (c) 扩展字段：入库数量（吨）（receiptQuantityTo）
```java
// 获取吨(TO)单位ID
tonUnitId = unitService.getByName("TO").getId()

if (unitId == tonUnit) {
    // 原始单位就是吨
    receiptQuantityTo = quantity
} else {
    // 从主计量(KG)转换到吨(TO)
    unitConversion = RiskUnitConversionUtil.getUnitConversion(mainUnitId, tonUnitId, productId)
    receiptQuantityTo = mainQuantity × unitConversion   // 保留5位小数
}
```

### 2. 金额计算

#### (a) 暂估金额（estimated_amount）— SQL层计算
```sql
estimated_amount = physical_deal_line_ext.estimated_price × document_items.quantity
--                  合同行暂估单价                     ×  入库数量
```

#### (b) 交货总折扣（totalDiscount）— Service层计算
```java
unitaryDiscount = spreadDetailByPdlIdMap.get(pdlId).getUnitaryDiscount()  // 标准折扣（来自升贴水明细表）
totalDiscount = unitaryDiscount × receiptQuantityTo   // 保留5位小数
//               标准折扣       ×  入库数量（吨）
```

### 3. 冲销判定（reversed）— SQL层
```sql
CASE
    WHEN docoff.id IS NULL THEN 'N'   -- 未被冲销
    ELSE 'Y'                           -- 已被冲销（存在action_id=42且status=2的冲销单）
END AS reversed
```

---

## 四、字段映射关系

### 单据基本信息
| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `documents.document_number` | `documentNumber` | 入库单据号 |
| `documents.document_date` | `documentDate` | 单据日期 |
| `documents.title_transfer_date` | `titleTransferDate` | 货权转移日期 |
| `documents.post_date` | `postDate` | 过账日期 |
| `documents.status` → 字典翻译 | `documentStatus` | 单据状态（中文） |
| `documents.sap_push_status` → 字典翻译 | `documentSapPushStatus` | SAP推送状态（中文） |
| `documents.offset_flag` | `offsetFlag` | 是否冲销单据 |
| `documents.sap_dn_code` | `sapDnCode` | SAP DN码 |
| `documents.intercompany` | `intercompany` | 内贸交易类型 |

### 合同信息
| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `physical_deals.contract_number` | `contractNumber` | 合同编号 |
| `physical_deals.sap_code` | `sapCode` | 合同SAP编码 |
| `physical_deal_line.line_number` | `physicalLineNumber` | 合同行号 |
| `physical_deal_line.id` | `pdlId` | 合同行ID |
| `physical_deal_line.pricing_formula_id_parameters` | `pricingFormulaIdParameters` | 计价公式参数 |

### 数量/金额字段
| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `document_items.quantity` | `quantity` → `mainQuantity` | 原始数量→经转换后的主计量数量 |
| `unit.id` / `unit.name` | `unitId` / `unitName` | 原始计量单位 |
| `unit_main.id` / `unit_main.name` | `mainUnitId` / `unitMainName` | 主计量单位（固定KG） |
| `estimated_price × quantity` | `estimatedAmount` | 暂估金额 |
| `document_items.offset_quantity` | `offsetQuantity` | 冲销数量 |
| `currency.name` | `settlementCurrencyName` | 结算币种名称 |

### 冲销信息
| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `CASE WHEN docoff.id IS NULL THEN 'N' ELSE 'Y'` | `reversed` | 是否被冲销 |
| `docoff.document_number` | `reversedDocumentNumber` | 冲销单据号 |
| `dioff.line_number` | `reversedLineNumber` | 冲销单据行号 |

### 扩展字段（Service层计算填充）
| 字段 | 计算方式 | 说明 |
|------|----------|------|
| `receiptQuantityTo` | `mainQuantity × 转换率(KG→TO)` | 入库数量（吨） |
| `unitaryDiscount` | 来自 `spreadDetails()` | 标准折扣 |
| `totalDiscount` | `unitaryDiscount × receiptQuantityTo` | 交货总折扣 |

---

## 五、关键业务逻辑

### 1. 数据权限过滤
```java
// 获取当前用户的数据权限（rdDefId=1001 代表业务机构维度）
List<DataScopeDto> dataScopeDtoList = SecurityUtils.getCurrentUserDataScope();
List<String> legalEntityIds = dataScopeDtoList.stream()
    .filter(x -> "1001".equals(x.getRdDefId()))
    .map(DataScopeDto::getKeyId)
    .collect(Collectors.toList());
// 与请求参数中的legalEntityIds合并
```

### 2. SQL过滤条件（核心业务约束）
| 条件 | 说明 |
|------|------|
| `physical_deals.contract_type IN ('Spot','ShortTerm','LongTerm')` | 仅现货、短期、长期合同 |
| `physical_deals.ps_flag = 'P'` | **仅采购方向** |
| `documents.action_id = 42` | **仅入库登记类型单据** |
| `documents.inactive_flag = 0` | 有效单据 |
| `document_items.inactive_flag = false` | 有效明细行 |
| `GROUP BY document_items.id` | 按明细行去重 |
| `ORDER BY documents.id DESC` | 按单据ID倒序 |

### 3. 单位转换链路
```
原始数量 (quantity, 原始单位)
    ↓ RiskUnitConversionUtil.getUnitConversion(unitId, mainUnitId=KG, productId)
主计量数量 (mainQuantity, KG)
    ↓ 冲销时 × (-1)
最终主计量数量
    ↓ RiskUnitConversionUtil.getUnitConversion(mainUnitId=KG, tonUnitId=TO, productId)
入库吨数 (receiptQuantityTo, TO)
```

### 4. 冲销处理逻辑
- SQL通过LEFT JOIN自关联`document_items`（别名`dioff`）和`documents`（别名`docoff`）判断是否被冲销
- 冲销判定条件：`docoff.action_id = 42 AND docoff.status = 2`
- Service层对`offsetFlag = "Y"`的单据，将`quantity`和`mainQuantity`取反（× -1）

### 5. 升贴水数据批量填充
- 收集所有`pdlId`（合同行ID），分批（每批500条）调用`SysReportService.spreadDetails()`
- 构建`Map<pdlId, SpreadDetailVo>`映射
- 从中提取`unitaryDiscount`（标准折扣），计算`totalDiscount = unitaryDiscount × receiptQuantityTo`

### 6. 字典值翻译
```java
// 将状态码翻译为中文显示
item.setDocumentStatus(documentStatusDict.get(item.getDocumentStatus()));
item.setDocumentSapPushStatus(sapPushStatusDict.get(item.getDocumentSapPushStatus()));
```

---

## 六、数据流总览图

```
前端请求 ShipmentNotInvoicedReq (筛选条件)
    │
    ▼
Controller ──→ Service (权限过滤 + 参数合并)
    │
    ▼
ReportMapper.xml SQL查询
    │  20+张表 LEFT JOIN
    │  核心: document_items + documents + physical_deals
    │  过滤: action_id=42, ps_flag='P', contract_type IN (...)
    │  计算: estimated_price × quantity = estimated_amount
    │  判定: 是否被冲销 (reversed Y/N)
    │
    ▼
Service 后处理
    │  ① 单位转换: quantity → mainQuantity (KG)
    │  ② 冲销取反: offsetFlag=Y → ×(-1)
    │  ③ 字典翻译: status → 中文
    │  ④ 吨转换:   mainQuantity → receiptQuantityTo (TO)
    │  ⑤ 升贴水:   spreadDetails → unitaryDiscount
    │  ⑥ 折扣计算: totalDiscount = unitaryDiscount × receiptQuantityTo
    │
    ▼
返回 List<ShipmentNotInvoicedRes>
```

---

## 七、被其他模块引用

`receiptDetails`的数据还被**Greenlist价格快照计算**（⑤）引用：

- `GreenlistPriceSnapshotServiceImpl.fillReceiptDetailsMapWithMonthLookback()`调用`reportService.receiptDetails()`获取收货折扣均价
- 计算方式：`totalDiscount合计 ÷ receiptQuantityTo合计`（保留5位小数）
- **当月无数据时向前回补最多3个月**
- 最终用于计算`averagePremiumDiscount`（月均折扣/溢价），参与Greenlist单价的计算：
  ```
  GreenlistPrice = 手工价 或 LmeForGreenlist + averagePremiumDiscount
  ```

---

## 八、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/ReportController.java:1179` |
| Service接口 | `bcadmin-system/.../service/report/ReportService.java:36` |
| Service实现 | `bcadmin-system/.../service/report/ReportServiceImpl.java:225` |
| Mapper接口 | `bcadmin-db/.../dao/report/ReportMapper.java:36` |
| Mapper XML | `bcadmin-db/src/main/resources/system/report/ReportMapper.xml` |
| DTO | `bcadmin-db/.../dto/ShipmentNotInvoicedRes.java` |
| Query | `bcadmin-db/.../dto/ShipmentNotInvoicedReq.java` |

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
