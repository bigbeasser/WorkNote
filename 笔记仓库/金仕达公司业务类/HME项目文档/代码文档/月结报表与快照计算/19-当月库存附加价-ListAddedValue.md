# 当月库存附加价（listAddedValue）调用链梳理

## 概述

当月库存附加价报表用于展示月结时每条入库明细的附加价值（Added Value），包括附加金额、附加单价等。

**入口方法**：`EOMStorageController.listAddedValue(EomStorageAddedValueQuery)`  
**核心Service**：`EomStorageServiceImpl.listEomAddedValue()`

---

## 一、完整调用链

```
Controller层：
  EOMStorageController.listAddedValue()               [POST /api/eomstorage/listAddedValue]
    └─ EomStorageServiceImpl.listEomAddedValue()

Service层（EomStorageServiceImpl）：
  ├─ Step 1：分页处理
  │   └─ PageHelper.startPage()
  │
  ├─ Step 2：数据权限过滤
  │   └─ SecurityUtils.getCurrentUserDataScope()      [获取当前用户数据权限]
  │
  ├─ Step 3：SQL查询
  │   └─ EomStorageMapper.listEomAddedValue()
  │       └─ EomStorageMapper.xml#listEomAddedValue   [SQL：多表JOIN查询]
  │
  └─ Step 4：后处理
      └─ 冲销数量取反：offsetQuantity × (-1)
```

---

## 二、数据来源表

### 核心业务表

| 表名 | 别名 | 用途 |
|------|------|------|
| `systemdb.eom_storage_added_value` | a | **当月库存附加价明细**（主表） |
| `systemdb.eom_storage` | c | 库存月结主表 |
| `systemdb.physical_deals` | b | 实物交易/合同 |

### 关联维度表

| 表名 | 别名 | 用途 |
|------|------|------|
| `admindb.sys_company` | d | 业务机构名称 |
| `systemdb.document_actions` | e | 单据动作类型（含冲销标记） |
| `systemdb.storage_facility` | f | 仓库名称 |
| `admindb.counterparty` | g | 交易对手名称 |
| `admindb.sys_department` | h | 业务部门名称 |
| `admindb.sys_business_segment` | i | 业务板块名称 |
| `systemdb.unit` | j, j2 | 计量单位（入库单位 + 数量单位） |
| `systemdb.product` | k, k2 | 商品信息 + 父商品信息 |
| `systemdb.currency` | l, l2 | 结算币种 + 本位币种 |
| `systemdb.abutment_config` | ac | 对接配置（Factory标记） |
| `systemdb.abutment_config_details` | acd | 工厂名称映射 |

---

## 三、SQL查询结构

### 主查询

```sql
SELECT
    ifnull(a.added_value, 0) AS added_value,
    ifnull(a.base_cur_added_value, 0) AS base_cur_added_value,
    c.accounting_month,
    a.*,
    CONCAT(e.action_name, IF(a.offset_flag = 1, ' reverse', '')) AS actionName,
    g.name AS counterpartyName,
    f.name AS storageName,
    d.COMPANY_NAME AS legalEntityName,
    h.DEPT_NAME AS businessDepartmentName,
    i.business_segment_name AS businessSegmentName,
    b.contract_number,
    j.name AS deliveryInQuantityUnitName,
    j2.name AS quantityUnitName,
    CONCAT(k.code, '-', k.name) AS productName,
    IFNULL(CONCAT(k2.code, '-', k2.name), CONCAT(k.code, '-', k.name)) AS parentProductName,
    l.name AS currencyName,
    l2.name AS baseCurrencyName,
    acd.code_name AS factoryName,
    CAST(IFNULL(a.added_value, 0) / a.delivery_in_quantity AS DECIMAL(18,5)) AS added_price
FROM systemdb.eom_storage_added_value a
    LEFT JOIN systemdb.physical_deals b ON b.id = a.physical_deal_id
    LEFT JOIN systemdb.eom_storage c ON c.id = a.eom_storage_id
    LEFT JOIN admindb.sys_company d ON d.id = a.legal_entity_id
    LEFT JOIN systemdb.document_actions e ON e.id = a.action_id
    LEFT JOIN systemdb.storage_facility f ON f.id = a.storage_id
    LEFT JOIN admindb.counterparty g ON g.id = a.counterparty_id
    LEFT JOIN admindb.sys_department h ON h.id = a.business_department_id
    LEFT JOIN admindb.sys_business_segment i ON i.id = a.business_segment_id
    LEFT JOIN systemdb.unit j ON j.id = a.delivery_in_quantity_unit_id
    LEFT JOIN systemdb.unit j2 ON j2.id = a.quantity_unit_id
    LEFT JOIN systemdb.product k ON k.id = a.product_id
    LEFT JOIN systemdb.product k2 ON k2.id = k.parent_id
    LEFT JOIN systemdb.currency l ON l.id = a.currency_id
    LEFT JOIN systemdb.currency l2 ON l2.id = a.base_currency_id
    LEFT JOIN systemdb.abutment_config ac ON ac.docking_mark = 'Factory'
    LEFT JOIN systemdb.abutment_config_details acd ON acd.abutment_config_id = ac.id AND acd.value = a.factory_code
WHERE 1 = 1
    AND (a.inactive_flag = 0 OR a.inactive_flag IS NULL)
    -- 动态条件...
```

### 动态过滤条件

| 条件 | 说明 |
|------|------|
| `eomStorageId` | 指定月结主表ID |
| `eomStorageStatus` | 月结状态 |
| `documentItemId` | 单据明细ID |
| `documentNumber` | 单据号（模糊匹配） |
| `contractNumber` | 合同号（模糊匹配） |
| `counterpartyId` | 交易对手ID |
| `legalEntityId` | 业务机构ID |
| `legalEntityIds` | 业务机构ID列表（数据权限） |
| `businessDepartmentId` | 业务部门ID |
| `businessSegmentId` | 业务板块ID |
| `titleTransferDateBegin/End` | 货权转移日期范围 |
| `postDateBegin/End` | 过账日期范围 |
| `productId` | 商品ID |
| `accountingMonth` | 会计月份 |
| `documentType` | 单据类型（Y=冲销, N=正常） |
| `excludeStatusList` | 排除状态列表（默认排除WriteOff） |
| `excludeWriteOff` | 排除已冲销记录 |

---

## 四、计算公式

### 1. 附加价值（added_value）

```sql
-- SQL层直接取值
added_value = IFNULL(a.added_value, 0)           -- 附加价值（结算币种）
base_cur_added_value = IFNULL(a.base_cur_added_value, 0)  -- 附加价值（本位币）
```

### 2. 附加单价（added_price）

```sql
-- SQL层计算
added_price = CAST(IFNULL(a.added_value, 0) / a.delivery_in_quantity AS DECIMAL(18,5))
--            附加价值 ÷ 入库数量
```

### 3. 冲销数量取反

```java
// Java层后处理
if (item.getOffsetQuantity() != null) {
    item.setOffsetQuantity(item.getOffsetQuantity().multiply(new BigDecimal("-1")));
}
```

### 4. 冲销标记

```sql
-- SQL层拼接
actionName = CONCAT(e.action_name, IF(a.offset_flag = 1, ' reverse', ''))
-- 当offset_flag=1时，在动作名称后追加 ' reverse'
```

---

## 五、字段映射关系

### 核心数量/金额字段

| SQL字段 | Java字段 | 计算公式 | 说明 |
|---------|----------|---------|------|
| `a.added_value` | `addedValue` | 直接取值 | 附加价值（结算币种） |
| `a.base_cur_added_value` | `baseCurAddedValue` | 直接取值 | 附加价值（本位币） |
| `a.delivery_in_quantity` | `deliveryInQuantity` | 直接取值 | 入库数量 |
| `a.quantity` | `quantity` | 直接取值 | 数量 |
| `a.offset_quantity` | `offsetQuantity` | Java层 × (-1) | 冲销数量（取反） |
| `added_value / delivery_in_quantity` | `addedPrice` | SQL层除法 | 附加单价（结算币种） |

### 基础信息字段

| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `a.document_item_id` | `documentItemId` | 单据明细ID |
| `a.document_id` | `documentId` | 单据ID |
| `a.physical_deal_id` | `physicalDealId` | 实物交易ID |
| `a.physical_deal_line_id` | `physicalDealLineId` | 实物交易行ID |
| `a.product_id` | `productId` | 商品ID |
| `a.legal_entity_id` | `legalEntityId` | 业务机构ID |
| `a.storage_id` | `storageId` | 仓库ID |
| `a.counterparty_id` | `counterpartyId` | 交易对手ID |
| `a.business_department_id` | `businessDepartmentId` | 业务部门ID |
| `a.business_segment_id` | `businessSegmentId` | 业务板块ID |
| `a.currency_id` | `currencyId` | 结算币种ID |
| `a.base_currency_id` | `baseCurrencyId` | 本位币种ID |
| `a.offset_flag` | `offsetFlag` | 冲销标记（0/1） |
| `a.factory_code` | `factoryCode` | 工厂代码 |
| `a.title_transfer_date` | `titleTransferDate` | 货权转移日期 |
| `a.posting_date` | `postingDate` | 过账日期 |
| `a.document_number` | `documentNumber` | 单据号 |
| `a.line_number` | `lineNumber` | 单据行号 |
| `a.contract_line_number` | `contractLineNumber` | 合同行号 |
| `a.sap_batch_no` | `sapBatchNo` | SAP批次号 |
| `a.sap_contract_code` | `sapContractCode` | SAP合同代码 |
| `a.sap_contract_line_code` | `sapContractLineCode` | SAP合同行代码 |
| `a.sap_document_code` | `sapDocumentCode` | SAP单据代码 |
| `a.sap_document_account_year` | `sapDocumentAccountYear` | SAP单据会计年度 |
| `a.sap_document_item_code` | `sapDocumentItemCode` | SAP单据行代码 |

### 名称字段（JOIN获取）

| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `CONCAT(e.action_name, IF(...))` | `actionName` | 单据动作名称（冲销加' reverse'） |
| `g.name` | `counterpartyName` | 交易对手名称 |
| `f.name` | `storageName` | 仓库名称 |
| `d.COMPANY_NAME` | `legalEntityName` | 业务机构名称 |
| `h.DEPT_NAME` | `businessDepartmentName` | 业务部门名称 |
| `i.business_segment_name` | `businessSegmentName` | 业务板块名称 |
| `b.contract_number` | `contractNumber` | 合同号 |
| `j.name` | `deliveryInQuantityUnitName` | 入库数量单位 |
| `j2.name` | `quantityUnitName` | 数量单位 |
| `CONCAT(k.code, '-', k.name)` | `productName` | 商品（code-name） |
| `IFNULL(CONCAT(k2...), CONCAT(k...))` | `parentProductName` | 父商品（code-name） |
| `l.name` | `currencyName` | 结算币种名称 |
| `l2.name` | `baseCurrencyName` | 本位币种名称 |
| `acd.code_name` | `factoryName` | 工厂名称 |
| `c.accounting_month` | `accountingMonth` | 会计月份 |

---

## 六、关键业务逻辑总结

1. **数据来源单一**：直接从`eom_storage_added_value`表查询，不涉及复杂的Java层计算。附加价值数据在月结计算时已经生成并落库。

2. **附加单价计算**：`added_price = added_value ÷ delivery_in_quantity`，在SQL层直接计算，保留5位小数。

3. **冲销处理**：
   - SQL层：通过`offset_flag`字段标识冲销记录，冲销时在动作名称后追加' reverse'
   - Java层：对`offsetQuantity`取反（× -1）

4. **数据权限控制**：通过`SecurityUtils.getCurrentUserDataScope()`获取当前用户的业务机构权限（rdDefId="1001"），过滤可见数据。

5. **状态排除**：默认排除`WriteOff`（冲销）状态的记录，除非指定了`eomStorageId`。

6. **与库存价值报表的关系**：库存价值报表（listDetailedEntriesValue）中的`addedValue`字段来源于本表（`eom_storage_added_value`），通过`document_item_id`关联。

7. **与Greenlist快照的关系**：Greenlist价格快照计算中的`averagePremiumDiscount`（月均折扣/溢价）数据来源于收货明细表（receiptDetails），而非本表。本表存储的是月结时已经计算好的附加价值。

---

## 七、数据流总览图

```
前端请求 EomStorageAddedValueQuery (筛选条件)
    │
    ▼
Controller ──→ Service
    │
    ├─ Step 1: 分页处理
    │   └─ PageHelper.startPage()
    │
    ├─ Step 2: 数据权限过滤
    │   └─ SecurityUtils.getCurrentUserDataScope()
    │       → 获取业务机构权限列表
    │
    ├─ Step 3: SQL查询
    │   └─ EomStorageMapper.listEomAddedValue()
    │       │
    │       │  eom_storage_added_value (主表)
    │       │  + physical_deals (合同)
    │       │  + eom_storage (月结主表)
    │       │  + sys_company (机构)
    │       │  + document_actions (动作类型)
    │       │  + storage_facility (仓库)
    │       │  + counterparty (交易对手)
    │       │  + sys_department (部门)
    │       │  + sys_business_segment (板块)
    │       │  + unit × 2 (单位)
    │       │  + product × 2 (商品+父商品)
    │       │  + currency × 2 (结算币+本位币)
    │       │  + abutment_config_details (工厂)
    │       │
    │       │  SQL计算: added_price = added_value ÷ delivery_in_quantity
    │       │
    │       ▼
    │
    └─ Step 4: Java后处理
        └─ 冲销数量取反: offsetQuantity × (-1)
            │
            ▼
返回 List<EomStorageAddedValueRes>
```

---

## 八、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/EOMStorageController.java:95` |
| Service接口 | `bcadmin-system/.../service/EomStorageService.java` |
| Service实现 | `bcadmin-system/.../service/impl/EomStorageServiceImpl.java:253` |
| Mapper接口 | `bcadmin-db/.../dao/EomStorageMapper.java` |
| Mapper XML | `bcadmin-db/src/main/resources/system/EomStorageMapper.xml:179` |
| DTO | `bcadmin-db/.../dto/EomStorageAddedValueRes.java` |
| 实体类 | `bcadmin-db/.../domain/EomStorageAddedValue.java` |
| Query | `bcadmin-db/.../dto/EomStorageAddedValueQuery.java` |

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
