# 销售开票定价表（getSalesEngagament）调用链梳理

## 概述

销售开票定价表用于展示销售订单商品行的已定价、已开票、差值等详细信息，是销售开票定价快照计算的数据源。

**入口方法**：`ReportController.getSalesEngagament(SalesEngagamentRequest, BasePage)`  
**核心Service**：`SalesEngagamentAdjustdifferenceDetailsServiceImpl.getSalesEngagament()`

---

## 一、完整调用链

```
Controller层：
  ReportController.getSalesEngagament()
    └─ SalesEngagamentAdjustdifferenceDetailsServiceImpl.getSalesEngagament()

Service层（SalesEngagamentAdjustdifferenceDetailsServiceImpl）：
  ├─ Step 1：排除RB/RS业务板块商品
  │   ├─ SysBusinessSegmentMapper.selectByExample()     [查sys_business_segment表]
  │   └─ ProductMapper.selectByExample()                [查product表]
  │
  ├─ Step 2：获取订单商品行列表
  │   └─ SalesEngagamentAdjustdifferenceDetailsMapper.getPhysicalDealLineListToPage()
  │       └─ SQL查询多表JOIN
  │
  ├─ Step 3：获取历史调差汇总
  │   └─ SalesEngagamentAdjustdifferenceService.getAllSumDiiference()
  │       └─ SalesEngagamentAdjustdifferenceDetailsMapper.getAllSumDiiference()
  │           └─ SQL查询调差表汇总
  │
  └─ Step 4：遍历每个商品行，分别计算数量和价值
      ├─ [4a] 查已定价记录
      │   └─ MovementPriceMapper.selectList()           [查movement_price表]
      │
      ├─ [4b] 查开票记录
      │   └─ MyFinanceMapper.selectInvoiceAndCreditCount()
      │       └─ SQL查询发票相关表
      │
      └─ [4c] 单位转换
          └─ convertWeightsInMultipleLists()
              ├─ RiskUnitConversionUtil.getCurrencyConversion()  [汇率转换]
              └─ RiskUnitConversionUtil.getUnitConvertedValue()  [重量单位转KG]
```

---

## 二、数据来源表

| 阶段 | 数据库表 | 用途 |
|------|---------|------|
| 排除商品 | `sys_business_segment` | 查找RB/RS业务板块 |
| 排除商品 | `product` | 查找属于RB/RS板块的商品ID |
| 订单行列表 | `physical_deal_line` (pdl) | 销售订单商品行（主数据） |
| 订单行列表 | `physical_deals` (pd) | 订单主表，筛选条件：`status in (2,9)`, `ps_flag='S'` |
| 订单行列表 | `contract_execution_monitor` (cem) | 合同执行监控（订单完成状态） |
| 订单行列表 | `product` (prod) | 商品信息 |
| 订单行列表 | `product_financial_attributes` (pfa) | 商品财务属性（物料类别） |
| 订单行列表 | `counterparty` (cp) | 客商信息 |
| 订单行列表 | `counterparty_erp` (cperp) | 客商ERP编号 |
| 订单行列表 | `sys_company` (sc) | 业务机构 |
| 订单行列表 | `currency` | 币种 |
| 订单行列表 | `sys_business_segment` (sbs) | 业务板块 |
| 已定价数据 | `movement_price` | 现货定价明细表 |
| 开票数据 | `invoice_documents` (i) | 发票物资明细 |
| 开票数据 | `invoice` (ii) | 发票主表 |
| 开票数据 | `cashflow_model_values` (c) | 现金流模型值 |
| 开票数据 | `cashflow_model_header_values` (cv) | 现金流模型头值 |
| 开票数据 | `document_items` (di) | 出入库单据明细 |
| 开票数据 | `documents` (d) | 单据 |
| 开票数据 | `document_actions` (da) | 单据动作 |
| 调差数据 | `sales_engagament_adjustdifference` (sea) | 调差主表 |
| 调差数据 | `sales_engagament_adjustdifference_details` (sead) | 调差明细表 |
| 汇率转换 | `forward_price`（通过工具类） | 外汇汇率 |

---

## 三、数据收集阶段详细逻辑

### Step 1：排除RB/RS业务板块商品

```java
// 查询名称以 "RB-" 或 "RS-" 开头的业务板块
sysBusinessSegmentExample → sys_business_segment WHERE name LIKE 'RB-' OR name LIKE 'RS-'

// 查询这些板块下所有有效商品
productExample → product WHERE inative_flag=false AND business_segment_id IN (RB/RS板块IDs)
```

> ⚠️ **代码缺陷**：第99行`if (CollectionUtils.isEmpty(products))`应为`isNotEmpty`，当前逻辑导致RB/RS板块商品**永远不会被排除**。

### Step 2：获取订单商品行列表（getPhysicalDealLineListToPage）

**SQL核心逻辑：**
```sql
SELECT ... FROM physical_deal_line pdl
  LEFT JOIN physical_deals pd           -- 订单主表
  LEFT JOIN contract_execution_monitor cem  -- 合同执行监控
  LEFT JOIN product prod                -- 商品
  LEFT JOIN product_financial_attributes pfa -- 商品财务属性
  LEFT JOIN counterparty cp             -- 客商
  LEFT JOIN counterparty_erp cperp      -- 客商ERP
  LEFT JOIN sys_company sc              -- 业务机构
  LEFT JOIN currency                    -- 本位币种（通过业务机构的基础币种关联）
  LEFT JOIN currency currency2          -- 结算币种
  LEFT JOIN sys_business_segment sbs    -- 业务板块
WHERE pdl.inative_flag = false
  AND pd.status IN (2, 9)              -- 状态为2(已审批)或9
  AND pd.ps_flag = 'S'                 -- 销售方向
  AND (pd.contract_type = 'Spot'       -- 现货合同
       OR (pd.long_term_contract_number IS NOT NULL 
           AND pd.contract_type IN ('LongTerm', 'ShortTerm')))  -- 或有长协编号的长/短期合同
GROUP BY pdl.id                        -- 按商品行ID去重
```

### Step 3：获取历史调差汇总（getAllSumDiiference）

```sql
SELECT 
  ROUND(SUM(IFNULL(sead.diff_quantity, 0)), 3) AS sumQuantity,
  ROUND(SUM(IFNULL(sead.diff_value, 0)), 5) AS sumValue,
  sea.physical_deal_line_id AS physicalDealLineId
FROM sales_engagament_adjustdifference_details sead
  LEFT JOIN sales_engagament_adjustdifference sea 
    ON sead.sales_engagament_adjustdifference_id = sea.id
WHERE sead.inactive_flag = false
  AND sea.physical_deal_line_id IN (商品行IDs)
  AND STR_TO_DATE(CONCAT(sea.year_month_time, '-01'), '%Y-%m-%d') <= 查询日期
GROUP BY sea.id
```

> 汇总**截至查询月份**的所有历史调差数量和调差价值。

### Step 4a：查已定价记录（movement_price）

```java
// 查询条件
WHERE inactive_flag = false
  AND priced = 1                        -- 已计价
  AND physical_deal_line_id = 当前商品行ID
  AND daily_settlement_date <= 查询日期   -- 日结日期在查询日期之前
```

### Step 4b：查开票记录（selectInvoiceAndCreditCount）

```sql
SELECT i.quantity, pdl.id, i.product_id, ii.settlement_currency_id,
       i.quantity_unit_id, ii.payment_date, i.price, i.id,
       IFNULL(di.quantity, 0) AS diQuantity,
       IFNULL(i.base_currency_excl_tax_amount, 0) AS baseCurrencyExclTaxAmount,
       ii.invoice_date, i.base_currency_amount, ii.post_date
FROM invoice_documents i
  LEFT JOIN invoice ii ON i.invoice_id = ii.id
  LEFT JOIN cashflow_model_values c ON i.cashflow_model_value_id = c.cashflow_model_value_id
  INNER JOIN cashflow_model_header_values cv ON c.cashflow_model_header_vaule_id = cv.cashflow_model_header_value_id
  LEFT JOIN document_items di ON cv.header_id = di.id
  LEFT JOIN documents d ON di.document_id = d.id
  LEFT JOIN document_actions da ON da.id = d.action_id
  LEFT JOIN physical_deals pd ON pd.id = cv.physical_deal_id
  LEFT JOIN physical_deal_line pdl ON pd.id = pdl.physical_deal_id
WHERE i.inactive_flag = 0
  AND ii.gzstatus = 4                   -- 过账状态=4（已过账）
  AND ii.sap_push_status = 2            -- SAP推送状态=2（已推送）
  AND pdl.id = 当前商品行ID
  AND cv.line_number = 商品行行号
  AND ii.post_date <= 查询日期           -- 过账日期 <= 查询日期
```

### Step 4c：单位转换（convertWeightsInMultipleLists）

**MovementPrice转换：**
```java
// 1. 汇率转换：结算币种 → 欧元(ID=2)
exchangeRate = getCurrencyConversion("Bloomberg", currencyId, 2, dailySettlementDate, dailySettlementDate)
// 2. 重算结算净价 = 汇率 × (原结算净价 × 数量)
settlementNetPrice = exchangeRate × (settlementNetPrice × quantity)
// 3. 重量单位 → KG(ID=83)
quantity = getUnitConvertedValue(quantityUnitId, 83, productId, quantity)
```

**InvoiceItemRes转换：**
```java
// 1. 汇率转换：结算币种 → 欧元(ID=2)
exchangeRate = getCurrencyConversion("Bloomberg", settlementCurrencyId, 2, paymentDate, invoiceDate)
// 2. 重算单价 = 汇率 × (原单价 × 数量)
price = exchangeRate × (price × quantity)
// 3. 重量单位 → KG(ID=83)
quantity = getUnitConvertedValue(quantityUnitId, 83, productId, quantity)
```

---

## 四、计算公式汇总

### 数量计算

| 字段 | 公式 | 说明 |
|------|------|------|
| **已定价量** `pricedQuantity` | `Σ movementPrice.quantity` | 所有已计价记录的数量之和（已转KG） |
| **开票数量** `invoiceQuantity` | `Σ invoiceItemRes.quantity + Σ debitOrCrebitInvoiceItemRes.quantity` | 发票数量之和（已转KG）。注：`debitOrCrebitInvoiceItemRes`始终为空列表，实际只有`invoiceItemRes` |
| **差值数量** `diffQuantity` | `调差表汇总.sumQuantity` | 历史调差数量累计值（截至查询月份） |
| **已定价未开票量** `pricedButNotInvoicedQuantity` | `pricedQuantity - invoiceQuantity - diffQuantity` | 减法，保留5位小数 |

### 价值/金额计算

| 字段 | 公式 | 说明 |
|------|------|------|
| **已定价价值** `pricedValue` | `Σ movementPrice.amountBaseCur × 1.0` (5位小数) | 所有已计价记录的本位币金额之和 |
| **开票价值** `invoiceValue` | `(Σ invoiceItemRes.baseCurrencyAmount + Σ debitOrCrebitInvoiceItemRes.baseCurrencyAmount) × 1.0` (5位小数) | 发票本位币金额之和。注：debit/credit列表为空 |
| **差值价值** `diffValue` | `调差表汇总.sumValue` | 历史调差价值累计值 |
| **已定价未开票价值** `pricedButNotInvoicedValue` | `pricedValue - invoiceValue - diffValue` | 减法，保留5位小数 |
| **结算金额** `amountInSettleCurrency` | `pricedValue - invoiceValue - diffValue` | 与已定价未开票价值公式相同 |

### 单价计算

| 字段 | 公式 | 说明 |
|------|------|------|
| **单价（本位币）** `priceInBaseCurrency` | `pricedButNotInvoicedValue ÷ pricedButNotInvoicedQuantity` (5位小数) | 除数为0时按1处理 |
| **单价（结算币）** `priceInSettleCurrency` | `amountInSettleCurrency ÷ pricedButNotInvoicedQuantity` (5位小数) | 除数为0时按1处理 |

### 开票状态判断

```java
pricedQuantity（5位小数） == invoiceQuantity（5位小数）
  → invoiceStatus = 1（已开票/完成）
  → invoiceStatus = 0（未开票/未完成）
```

---

## 五、字段映射关系

### SQL查询 → Response字段映射

| SQL别名 | Response字段 | 来源表.字段 |
|---------|-------------|------------|
| `legalEntityName` | `legalEntityName` | `sys_company.COMPANY_NAME` |
| `legalEntityId` | `legalEntityId` | `physical_deals.legal_entity_id` |
| `businessSegmentId` | `businessSegmentId` | `sys_business_segment.id` |
| `businessSegmentName` | `businessSegmentName` | `sys_business_segment.business_segment_name` |
| `closeContractStatus` | `closeContractStatus` | `contract_execution_monitor.close_contract_status` |
| `contrTypeName` | `contrTypeName` | CASE WHEN `pd.contract_type='Spot'` → 现货，ELSE → 长协 |
| `orderNo` | `orderNo` | `physical_deals.contract_number` |
| `serialNo` | `serialNo` | `physical_deal_line.line_number` |
| `refDoc` | `refDoc` | `physical_deals.contract_number_ext` |
| `customerName` | `customerName` | `counterparty.name` |
| `customerId` | `customerId` | `physical_deals.counterparty_id` |
| `customerCode` | `customerCode` | `counterparty_erp.ERP_customer code` |
| `productId` | `productId` | `product.id` |
| `productName` | `productName` | `CONCAT(product.code, '-', product.name)` |
| `productCode` | `productCode` | `product.code` |
| `currencyName` | `currencyName` | `currency.name`（本位币） |
| `currencyId` | `currencyId` | `physical_deal_line.settlement_currency_id` |
| `settlementCurrencyId` | `settlementCurrencyId` | `currency.id`（通过`sc.BASE_CURRENCY`关联） |
| `productCategory` | `productCategory` | CASE WHEN `pfa.accounting_group` → 1/2/3 |
| `pdlLineNumber` | `pdlLineNumber` | `physical_deal_line.line_number` |
| `physicalDealLineId` | `physicalDealLineId` | `physical_deal_line.id` |

---

## 六、关键业务逻辑总结

1. **数据粒度**：报表以**订单商品行**(`physical_deal_line.id`)为最小粒度，每行一条记录。

2. **三大数量来源**：
   - **已定价量** ← `movement_price`表（已计价记录）
   - **开票量** ← `invoice_documents` + `invoice`表（已过账且已推送SAP的发票）
   - **差值量** ← `sales_engagament_adjustdifference_details`表（人工录入的调差记录）

3. **核心等式**：`已定价未开票量 = 已定价量 - 开票量 - 差值量`

4. **单位统一**：所有数量统一转换为**KG**（单位ID=83），所有币种通过Bloomberg市场汇率转换为**欧元**（币种ID=2）。

5. **价值字段差异**：
   - `pricedValue`直接取`movement_price.amount_base_cur`（本位币金额）
   - `invoiceValue`取`invoice_documents.base_currency_amount`（本位币金额）
   - 两者都是**本位币**口径

6. **开票状态**：比较`pricedQuantity`和`invoiceQuantity`（均保留5位小数），相等则标记为已完成（1），否则未完成（0）。前端可通过`invoiceStatus`筛选。

7. **⚠️ 潜在问题**：
   - `debitOrCrebitInvoiceItemRes`声明后始终为空列表，未被赋值，导致`debitOrCrebitInvoiceQuantity`和`debitOrCrebitInvoiceValue`始终为0
   - RB/RS板块排除逻辑有bug（`isEmpty`应为`isNotEmpty`）
   - `convertWeightsInMultipleLists`中对`MovementPrice.settlementNetPrice`的重算公式`汇率 × (单价 × 数量)`改变了原字段语义（从单价变成了总价），但后续计算`pricedValue`用的是`amountBaseCur`而非`settlementNetPrice`，所以不影响最终结果

---

## 七、数据流总览图

```
前端请求 SalesEngagamentRequest (筛选条件)
    │
    ▼
Controller ──→ Service
    │
    ├─ Step 1: 排除RB/RS板块商品
    │   └─ sys_business_segment + product 表
    │
    ├─ Step 2: 获取订单商品行列表
    │   └─ physical_deal_line + physical_deals + 多表JOIN
    │       过滤: ps_flag='S', status IN (2,9), contract_type IN (...)
    │
    ├─ Step 3: 获取历史调差汇总
    │   └─ sales_engagament_adjustdifference + details 表
    │       汇总: 截至查询月份的调差数量和调差价值
    │
    └─ Step 4: 遍历每个商品行，计算数量和价值
        ├─ 4a: 查已定价记录 (movement_price)
        ├─ 4b: 查开票记录 (invoice_documents + invoice)
        └─ 4c: 单位转换 (KG + EUR)
            │
            ▼
        计算公式:
            pricedQuantity = Σ movementPrice.quantity
            invoiceQuantity = Σ invoiceItemRes.quantity
            diffQuantity = 调差表汇总.sumQuantity
            pricedButNotInvoicedQuantity = pricedQuantity - invoiceQuantity - diffQuantity
            
            pricedValue = Σ movementPrice.amountBaseCur
            invoiceValue = Σ invoiceItemRes.baseCurrencyAmount
            diffValue = 调差表汇总.sumValue
            pricedButNotInvoicedValue = pricedValue - invoiceValue - diffValue
            
            priceInBaseCurrency = pricedButNotInvoicedValue ÷ pricedButNotInvoicedQuantity
            priceInSettleCurrency = amountInSettleCurrency ÷ pricedButNotInvoicedQuantity
            │
            ▼
返回 List<SalesEngagamentResponse>
```

---

## 八、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/ReportController.java:1160` |
| Service接口 | `bcadmin-system/.../service/SalesEngagamentAdjustdifferenceDetailsService.java:31` |
| Service实现 | `bcadmin-system/.../service/impl/SalesEngagamentAdjustdifferenceDetailsServiceImpl.java:84` |
| Mapper接口 | `bcadmin-db/.../dao/SalesEngagamentAdjustdifferenceDetailsMapper.java` |
| Mapper XML | `bcadmin-db/src/main/resources/system/SalesEngagamentAdjustdifferenceDetailsMapper.xml` |
| DTO | `bcadmin-db/.../dto/SalesEngagamentResponse.java` |
| Query | `bcadmin-db/.../dto/SalesEngagamentRequest.java` |

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
