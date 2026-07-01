# 金属头寸表（getMetalBollettinoReport）调用链梳理

## 概述

金属头寸表是HME系统中用于展示金属采购、销售、头寸情况的核心报表，包含三大计算区域：采购区域、销售区域、头寸区域。

**入口方法**：`ReportController.getMetalBollettinoReport(MetalBollettinoDto, BasePage)`  
**核心Service**：`FixationAdjustmentServiceImpl.getMetalBollettinoReportNewMethodNew()`

---

## 一、完整调用链

```
Controller层：
  ReportController.getMetalBollettinoReport()
    └─ FixationAdjustmentService.getMetalBollettinoReportNewMethodNew()

Service层（FixationAdjustmentServiceImpl）：
  ├─ 阶段1：分组骨架查询
  │   ├─ movementQuantityMapper.getSuitableMovementQuantity()        [现货分组]
  │   ├─ futuresMovementQuantityMapper.getSuitableFuturesMovementPriceCollectIds()  [期货分组]
  │   └─ fixationAdjustmentMapper.getSuitableFixationAdjustmentCollectIds()         [调整分组]
  │
  ├─ 阶段2：Java内存合并分组
  │   └─ 按groupKeyName合并三源数据
  │
  ├─ 阶段3：手动分页
  │   └─ 根据page/size截取数据
  │
  ├─ 阶段4：明细数据批量查询
  │   ├─ fixationAdjustmentMapper.getMetalBollettinoDataPS()         [现货明细]
  │   ├─ futuresMovementQuantityMapper.getFuturesMovementToMaterialReport()  [期货明细]
  │   └─ fixationAdjustmentMapper.getFixationAdjustmentToReportPS()           [调整明细]
  │
  ├─ 阶段5：单位/币种换算
  │   └─ conversionToKgAndEUR()
  │       ├─ 重量：unit → KG (unitId=83)
  │       └─ 币种：settlementCurrency → EUR (currencyId=2)
  │
  └─ 阶段6：三大区域计算
      ├─ calculatePay()       [采购区域]
      ├─ calculateSell()      [销售区域]
      └─ calculatePosition()  [头寸区域]
```

---

## 二、数据来源表

### 核心业务表

| # | 表名 | 用途 |
|---|------|------|
| 1 | `movement_quantity` | **现货计价量**（核心主表） |
| 2 | `futures_movement_quantity` | **期货计价量**（LME头寸数据） |
| 3 | `fixation_adjustment` | **现货数量调整**（手工调整） |

### 关联维度表

| # | 表名 | 用途 |
|---|------|------|
| 4 | `sys_company` | 业务机构名称 |
| 5 | `sys_business_segment` | 业务板块名称 + `is_preserve_value`过滤 |
| 6 | `specification_type` | 金属成分（质检类型）名称/描述 |
| 7 | `product` | 商品名称 |
| 8 | `product_specification` | 商品-金属成分关联（`pricing_or_not`过滤） |
| 9 | `physical_deals` | 实物交易主表（`intercompany`过滤） |
| 10 | `physical_deal_line` | 实物交易行 |

---

## 三、分组键（groupKeyName）构造规则

分组键决定数据合并粒度，按`isSummary`参数区分：

```java
// 非汇总模式（按天）
groupKeyName = "{legalEntityId}_{businessSegmentId}_{productSpecificationId}_{dailySettlementDay}"

// 汇总模式（跨天）
groupKeyName = "{legalEntityId}_{businessSegmentId}_{productSpecificationId}"
```

三个数据源（现货/期货/调整）使用相同规则构造分组键，在Java内存中合并。

---

## 四、数据收集阶段详解

### 4.1 第一阶段：分组骨架查询

从`movement_quantity`表按分组键聚合，得到**所有有数据的分组列表**作为报表行的骨架。

**关键字段映射**（SQL → Java）：

| SQL字段 | Java字段 | 说明 |
|---------|----------|------|
| `mq.total_price` | `elementMetalValue` | 金属价值 |
| `mq.settlement_price` | `elementMetalPrice` | 金属单价 |
| `mq.added_value` / `added_price` | 同名字段 | 附加价值/附加单价 |
| `mq.net_weright` | `netWeight` | 净重 |
| `mq.gross_weight` | `grossWeight` | 毛重 |
| `mq.element_metal_value_base_cur` | 同名字段 | 金属价值（本位币） |
| `mq.element_metal_price_base_cur` | 同名字段 | 金属单价（本位币） |
| `mq.added_value_base_cur` / `added_price_base_cur` | 同名字段 | 附加价值/单价（本位币） |

**过滤条件**：
- `mq.inactive_flag = 0` 且 `mq.valid IN (0,1)`
- `mq.specification_type_id IS NOT NULL`
- 日期区间过滤
- `is_preserve_value`业务板块保值过滤
- `intercompany`内部交易类型过滤

### 4.2 第二阶段：Java内存内分组聚合

对第一阶段的分组结果按`groupKeyName`累加：

```java
For each movementQuantity row:
  // 单位换算（→ KG）
  toKgConversion = riskUnitConversionUtil.getUnitConversionNew(pdQuantityUnitId, KG, productId)
  grossWeight_KG = grossWeight × toKgConversion
  netWeight_KG   = netWeight   × toKgConversion

  // 币种换算（→ EUR）
  toEuroExchange = riskCurveUtil.getExchangeRate(settlementCurrencyId, EUR, dailySettlementDay)

  // 仅对采购方向 (psFlag="P") 做金额汇总：
  addedValue          = addedPrice × netWeight           → × toEuroExchange
  elementMetalValue   = elementMetalPrice × netWeight    → × toEuroExchange
  addedValueBaseCur   = addedPriceBaseCur × netWeight    → × toEuroExchange
  elementMetalValueBaseCur = elementMetalPriceBaseCur × netWeight → × toEuroExchange

  // 销售方向 (psFlag="S") 只作为占位分组，金额初始化为 0
```

**分组汇总后统一乘 `-1`**（factor = -1），把采购的负数翻转为正数展示：

```java
grossWeight  × -1
netWeight    × -1
addedValue   × -1
elementMetalValue × -1
```

**反算单价**（汇总后加权平均）：

```java
divideNetWeight = netWeight == 0 ? 1 : netWeight
addedPrice          = addedValue          ÷ divideNetWeight   (5位小数 HALF_UP)
addedPriceBaseCur   = addedValueBaseCur   ÷ divideNetWeight
elementMetalPrice   = elementMetalValue   ÷ divideNetWeight
elementMetalPriceBaseCur = elementMetalValueBaseCur ÷ divideNetWeight

purchaseValue        = addedValue + elementMetalValue
purchaseValueBaseCur = addedValueBaseCur + elementMetalValueBaseCur
purchasePrice        = purchaseValue        ÷ divideNetWeight
purchasePriceBaseCur = purchaseValueBaseCur ÷ divideNetWeight
```

### 4.3 第三阶段：关联期货/调整分组

```java
遍历 futuresMovementQuantity 分组 → 匹配 groupKeyName → 设置 fmovIds
遍历 fixationAdjustment 分组 → 匹配 groupKeyName → 设置 adjustmentIds
未匹配到现货骨架的期货/调整分组 → 单独加入 temp → 合并到 groupMovementList
```

### 4.4 第四阶段：手动分页

```java
startIndex = (page - 1) × size
endIndex = min(startIndex + size, groupMovementList.size)
suitableMovementPriceCollectIdsNew = groupMovementList.subList(start, end)
```

### 4.5 第五阶段：明细数据批量查询

对分页后的分组收集所有`legalEntityId / businessSegmentId / productSpecificationId / dailySettlementDate`，组装三个查询对象`query1/query2/query3`，分别查询：

| 查询 | Mapper方法 | 数据源 |
|------|------------|--------|
| `result1` | `getMetalBollettinoDataPS` | `movement_quantity` 明细 |
| `futureMovementList` | `getFuturesMovementToMaterialReport` | `futures_movement_quantity` 明细 |
| `adjustmentList` | `getFixationAdjustmentToReportPS` | `fixation_adjustment` 明细 |

**关键SQL处理**（`getMetalBollettinoDataPS`）：
```sql
-- 采购方向 (P) 数量取反（负数）
CASE WHEN ps_flag='P' THEN gross_weight * (-1) ELSE gross_weight END AS grossWeight
CASE WHEN ps_flag='P' THEN net_weright * (-1) ELSE net_weright END   AS netWeight
```

明细数据按相同`legalEntityId-businessSegmentId-productSpecificationId[-dailySettlement]`分组到Map。

---

## 五、单位/币种换算（conversionToKgAndEUR）

### 重量换算
```java
grossWeight_KG = grossWeight × riskUnitConversionUtil.getUnitConversionNew(contractQuantityUnitId, 83=KG, productId)
netWeight_KG   = netWeight   × 同上
```

### 汇率换算（结算币 → EUR，EUR的currencyId = 2）
```java
if (settlementCurrencyId == null || settlementCurrencyId == 2) skip
exchangeRate = riskCurveUtil.getExchangeRate(settlementCurrencyId, 2, dailySettlementDate)
settlementPrice_EUR = settlementPrice × exchangeRate
purchasePrice_EUR   = purchasePrice   × exchangeRate
lmePrice_EUR        = lmePrice        × exchangeRate   // 期货
```

---

## 六、三大区域计算公式

### 6.1 采购区域 calculatePay

| 字段 | 公式 | 说明 |
|------|------|------|
| `grossQuantity` | `Σ(grossWeight)` | 毛重合计 |
| `netQuantity` | `Σ(netWeight)` | 净重合计 |
| `purchaseValue` | `Σ(netQuantity × settlementPrice)` | **采购价值 = ∑(净重 × 计价价格)** |
| `purchasePrice` | `Σ(purchaseValue where priced=1) ÷ Σ(netWeight where priced=1)` | 采购价格（仅已计价行加权平均） |
| `technicalLoss` | `Σ((grossQuantity - netQuantity) × settlementPrice) where priced=1` | 技术损耗 |
| `addedValue` | `0`（硬编码） | 附加价值（采购区未使用） |
| `adjustmentQuantityP` | `Σ(fixationAdjustment.quantity)` | 调整数量 |
| `adjustmentValueP` | `Σ(fixationAdjustment.value)` | 调整价值 |
| `lmeCashPrice` | `adjustmentValue ÷ adjustmentQuantity` | LME Cash Price（调整单价） |
| `freePlantCost` | `purchasePrice + addedValue` | 到厂成本 |
| `lmeQuantityP` | `Σ(futuresMovement.transactionQuantity)` | 期货 LME 数量 |
| `lmeGrossPriceP` | `Σ(lmePrice × transactionQuantityNotConvert) ÷ Σ(transactionQuantity)` | LME 加权毛价 |
| `contangoOrBackguardationlP` | `lmeGrossPrice - lmeCashPrice` | 溢价/贴水 |
| `totalQuantity` | `lmeQuantityP + netQuantity + adjustmentQuantityP` | 采购总数量 |
| `mediumCost` | `(netQuantity × freePlantCost + adjustmentValueP + lmeQuantityP × lmeGrossPrice) ÷ (netQuantity + adjustmentQuantityP + lmeQuantityP)` | **中间成本**（加权平均成本） |

### 6.2 销售区域 calculateSell

数据先按`dataSource`分类：
- **CRM**（非CAN/CNY动作）→ 销售
- **CRM + CAN/CNY** → 关闭
- **CTRM** → 交易

| 字段 | 公式 | 说明 |
|------|------|------|
| `salesQuantity` | `Σ(netWeight) where dataSource='CRM' and action ∉ {CAN,CNY}` | 销售数量 |
| `salesValue` | `Σ(netQuantity × settlementPrice)` (CRM) | 销售价值 |
| `closedQuantity` | `Σ(netWeight) where dataSource='CRM' and action ∈ {CAN,CNY}` | 关闭数量 |
| `closedValue` | `Σ(netQuantity × settlementPrice)` (CAN/CNY) | 关闭价值 |
| `tradingQuantity` | `Σ(netWeight) where dataSource='CTRM'` | 交易数量 |
| `tradingValue` | `Σ(netWeight × settlementPrice)` (CTRM) | 交易价值 |
| `adjustmentQuantityS` | `Σ(fixationAdjustment.quantity)` | 销售侧调整数量 |
| `adjustmentValueS` | `Σ(fixationAdjustment.value)` | 销售侧调整价值 |
| `lmeCashPriceS` | `adjustmentValueS ÷ adjustmentQuantityS` | 销售 LME Cash Price |
| `lmeQuantityS` | `Σ(futuresMovement.transactionQuantity)` | 销售 LME 数量 |
| `lmeGrossPriceS` | `Σ(lmePrice × transactionQuantityNotConvert) ÷ Σ(transactionQuantity)` | 销售 LME 毛价 |
| `contangoOrBackguardationlS` | `lmeGrossPriceS - lmeCashPriceS` | 销售溢价/贴水 |
| `totalQuantityS` | `tradingQuantity + adjustmentQuantityS + lmeQuantityS - salesQuantity - closedQuantity` | **销售总数量** |
| `grossPriceS` | `(lmeQuantityS × lmeGrossPriceS - salesValue + adjustmentValueS + tradingValue) ÷ totalQuantityS` | **Gross Price（销售均价）** |

### 6.3 头寸区域 calculatePosition

| 字段 | 公式 | 说明 |
|------|------|------|
| `physicalBalance` | `(adjustmentQuantityP + netQuantity + salesQuantity + closedQuantity) - (tradingQuantity + adjustmentQuantityS)` | **现货余额** |
| `physicalValue` | `(purchaseValue + adjustmentValueP + salesValue) - (adjustmentValueS + tradingValue)` | **现货价值** |
| `lmeBalance` | `lmeQuantityP - lmeQuantityS` | **期货余额**（购买LME - 销售LME） |
| `balanceQuantity` | `physicalBalance + lmeBalance` | **Balance Quantity**（现货+期货） |
| `lmeValue` | `lmeQuantityP × lmeGrossPriceP - lmeQuantityS × lmeGrossPriceS` | **期货价值** |

---

## 七、字段映射关系

### 7.1 来自分组骨架（MetalBollettinoGroup → MetalBollettinoDto）

| DTO字段 | 来源 | 说明 |
|---------|------|------|
| `legalEntityId/Name` | 分组 | 业务机构 |
| `businessSegmentId/Name` | 分组 | 业务板块 |
| `productSpecificationId/productName` | 分组 | 金属成分 |
| `specificationTypeDesc` | 分组 | 金属成分描述 |
| `dailySettlement/Date` | 分组 | 日结日期 |
| `grossQuantity` | `groupItem.grossWeight × -1` | 毛重 |
| `netQuantity` | `groupItem.netWeight × -1` | 净重 |
| `purchasePrice/PriceBaseCur` | 分组加权平均 | 采购单价 |
| `purchaseValue/ValueBaseCur` | 分组汇总 | 采购总价值 |
| `addedPrice/PriceBaseCur` | 分组加权平均 | 附加单价 |
| `addedValue/ValueBaseCur` | 分组汇总 | 附加价值 |
| `metalPrice/PriceBaseCur` | `elementMetalPrice` | 金属价 |
| `metalValue/ValueBaseCur` | `elementMetalValue` | 金属价值 |

### 7.2 来自calculatePay计算（采购区字段）

| DTO字段 | 说明 |
|---------|------|
| `grossQuantity` | 采购毛重（重新计算覆盖） |
| `netQuantity` | 采购净重 |
| `purchaseValue` | 采购价值 |
| `purchasePrice` | 采购价格 |
| `technicalLoss` | 技术损耗 |
| `adjustmentQuantityP` / `adjustmentValueP` | 采购调整 |
| `lmeCashPrice` | 采购 LME 现货价 |
| `freePlantCost` | 到厂成本 |
| `lmeQuantityP` | 采购 LME 数量 |
| `lmeGrossPriceP` | 采购 LME 毛价 |
| `contangoOrBackguardationlP` | 采购溢价/贴水 |
| `totalQuantity` | 采购总数量 |
| `mediumCost` | 中间成本 |

### 7.3 来自calculateSell计算（销售区字段）

| DTO字段 | 说明 |
|---------|------|
| `salesQuantity` / `salesValue` | 销售数量/价值 |
| `closedQuantity` / `closedValue` | 关闭数量/价值 |
| `tradingQuantity` / `tradingValue` | 交易数量/价值 |
| `adjustmentQuantityS` / `adjustmentValueS` | 销售调整 |
| `lmeCashPriceS` | 销售 LME 现货价 |
| `lmeQuantityS` | 销售 LME 数量 |
| `lmeGrossPriceS` | 销售 LME 毛价 |
| `contangoOrBackguardationlS` | 销售溢价/贴水 |
| `totalQuantityS` | 销售总数量 |
| `grossPriceS` | 销售 Gross Price |

### 7.4 来自calculatePosition计算（头寸区字段）

| DTO字段 | 说明 |
|---------|------|
| `physicalBalance` | 现货余额 |
| `physicalValue` | 现货价值 |
| `lmeBalance` | 期货余额 |
| `balanceQuantity` | Balance Quantity（现货+期货） |
| `lmeValue` | 期货价值 |

---

## 八、关键业务逻辑总结

1. **三源数据合并**：报表数据来自三个独立的计价量模型（现货`movement_quantity`、期货`futures_movement_quantity`、调整`fixation_adjustment`），以现货分组为骨架，通过`groupKeyName`在Java内存中合并。

2. **采购方向翻转**：`movement_quantity`中采购方向(`psFlag='P'`)的数量在库内存储为负数，SQL查询时`× (-1)`翻转为正；分组汇总后统一再乘`-1`，最终反算单价。

3. **非采购分组占位**：销售方向(`psFlag='S'`)在第一阶段只用于建立分组骨架，金额字段初始化为0，实际销售数据从明细查询中重新计算。

4. **内部交易过滤**：通过`physical_deals.intercompany`字段过滤，支持`No/BTO/BTS`三种模式。

5. **业务板块保值过滤**：`sys_business_segment.is_preserve_value`控制是否统计不保值业务板块数据。

6. **日期区间计算**：根据`dateCycle`（year/month/day）或`dailySettlementStart`计算查询的起止日期。

7. **手动分页**：由于三源合并后数据量不确定，采用Java内存分页而非数据库分页。

8. **精度控制**：所有金额/单价字段统一5位小数`HALF_UP`，数量字段部分使用2位小数。

9. **幂等性**：报表为只读查询，不涉及落库，每次调用都重新计算。

10. **单位换算基准**：重量统一换算到KG（unitId=83），币种统一换算到EUR（currencyId=2）。

---

## 九、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/ReportController.java:1055` |
| Service接口 | `bcadmin-system/.../service/FixationAdjustmentService.java:111` |
| Service实现 | `bcadmin-system/.../service/impl/FixationAdjustmentServiceImpl.java:2191` |
| 采购计算 | 同上 `:1070` `calculatePay()` |
| 销售计算 | 同上 `:1153` `calculateSell()` |
| 头寸计算 | 同上 `:1256` `calculatePosition()` |
| 单位/币种换算 | 同上 `:1297` `conversionToKgAndEUR()` |
| 现货分组查询 | `MovementQuantityMapper.xml:288` `getSuitableMovementQuantity` |
| 现货明细查询 | `FixationAdjustmentMapper.xml:588` `getMetalBollettinoDataPS` |
| 期货分组查询 | `FuturesMovementQuantityMapper.xml:296` `getSuitableFuturesMovementPriceCollectIds` |
| 期货明细查询 | `FuturesMovementQuantityMapper.xml:161` `getFuturesMovementToMaterialReport` |
| 调整分组查询 | `FixationAdjustmentMapper.xml:741` `getSuitableFixationAdjustmentCollectIds` |
| 调整明细查询 | `FixationAdjustmentMapper.xml:804` `getFixationAdjustmentToReportPS` |
| DTO | `bcadmin-db/.../dto/MetalBollettinoDto.java` |
| 分组BO | `bcadmin-db/.../bo/MetalBollettinoGroup.java` |

---

## 十、数据流全景图

```
┌─────────────────────────────────────────────────────────────┐
│                    阶段1：分组骨架查询                         │
│                                                             │
│  movement_quantity (现货)                                     │
│  futures_movement_quantity (期货)                             │
│  fixation_adjustment (调整)                                   │
│                                                             │
│  → 按 groupKeyName 分组，得到分组列表                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  阶段2：Java内存合并                           │
│                                                             │
│  以现货分组为骨架，关联期货/调整分组                             │
│  单位换算：→ KG                                              │
│  币种换算：→ EUR                                             │
│  采购方向翻转：× (-1)                                         │
│                                                             │
│  → 产出：完整的分组数据（含汇总金额）                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  阶段3：手动分页                               │
│                                                             │
│  根据 page/size 截取数据                                      │
│                                                             │
│  → 产出：当前页的分组数据                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              阶段4：明细数据批量查询                            │
│                                                             │
│  对分页后的分组，批量查询明细数据                                │
│  按相同分组键分组到Map                                         │
│                                                             │
│  → 产出：明细数据Map                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              阶段5：三大区域计算                                │
│                                                             │
│  calculatePay()      - 采购区域                               │
│  calculateSell()     - 销售区域                               │
│  calculatePosition() - 头寸区域                               │
│                                                             │
│  → 产出：完整的报表DTO                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
                  前端报表展示
```

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
