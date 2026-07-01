# 采购库存定价表（非快照）调用链梳理

## 概述

采购库存定价表用于展示采购订单商品行的已定价、已入库、差值等详细信息，是采购库存定价快照计算的数据源。

**入口方法**：`ReportController.procurementInventoryPricingTable(QueryPricingTableReq)`  
**核心Service**：`ReceiptDeliveryDetailsServiceImpl.getProcurementInventoryPricingTableNew()`

---

## 一、完整调用链

```
Controller层：
  ReportController.procurementInventoryPricingTable()     [GET /api/report/procurementInventoryPricingTable]
    └─ ReceiptDeliveryDetailsServiceImpl.getProcurementInventoryPricingTableNew()

Service层（ReceiptDeliveryDetailsServiceImpl）：
  ├─ Step 1：日期处理
  │   └─ 解析查询日期，获取月初和月末
  │
  ├─ Step 2：排除RB/RS业务板块商品
  │   ├─ SysBusinessSegmentMapper.selectByExample()     [查sys_business_segment表]
  │   └─ ProductMapper.selectByExample()                [查product表]
  │
  ├─ Step 3：SQL查询主数据
  │   └─ MyReceiptDeliveryDetailsMapper.getProcurementInventoryPricingMainframeTest()
  │       └─ SQL：3个CTE + 主查询
  │
  ├─ Step 4：补充数据查询
  │   ├─ PhysicalDealLineMapper.selectByExample()       [定价参数解析]
  │   ├─ ProductService.getProductAccountingGroupType() [商品会计分组类型]
  │   ├─ MovementPriceMapper.selectList()               [已定价明细]
  │   ├─ DocumentsMapper.getDocInQuantityByLineIdAndDate() [截至月份入库量]
  │   ├─ PurchaseEngagamentAdjustdifferenceService.getSumDiiference() [调差数据]
  │   ├─ PriceTriggeringMapper.getPriceTriggeringDetails() [价格触发明细]
  │   ├─ PriceTriggeringMapper.selectList()             [价格触发]
  │   └─ EomStorageService.listDetailEntrisValueEvaluation() [库存估值明细]
  │
  └─ Step 5：逐行计算
      ├─ 数量计算（已定价量、已入库量、已定价未入库量）
      ├─ 金额计算（已定价未入库金额、成本价）
      └─ 完成状态判定
```

---

## 二、数据来源表

### 核心业务表

| 表名 | 用途 |
|------|------|
| `physical_deal_line` | 采购订单商品行（主表） |
| `physical_deals` | 采购订单主表（`ps_flag='P'`） |
| `document_items` | 入库单据明细 |
| `documents` | 入库单据 |
| `movement_price` | 定价明细表 |
| `product` | 商品信息 |
| `counterparty` | 交易对手 |
| `currency` | 币种 |
| `unit` | 计量单位 |
| `sys_company` | 业务机构 |

### 补充数据表

| 表名 | 用途 |
|------|------|
| `price_triggering` | 价格触发（点价） |
| `price_triggering_warehouse_rela` | 价格触发与入库关联 |
| `sales_engagament_adjustdifference` | 调差主表 |
| `sales_engagament_adjustdifference_details` | 调差明细 |
| `eom_storage_detail` | 库存估值明细 |
| `eom_storage_added_value` | 库存附加价明细 |

---

## 三、数据收集阶段详细逻辑

### Step 1：日期处理

```java
String date = req.getDate(); // 格式：2024-05-01
YearMonth yearMonth = YearMonth.parse(date, formatter);
LocalDate firstDayOfMonth = yearMonth.atDay(1);
LocalDate lastDayOfMonth = yearMonth.atEndOfMonth();
req.setBeginDay(firstDayOfMonth.format(...));
req.setEndDay(LocalDate.parse(date, formatter).toString());
```

### Step 2：排除RB/RS业务板块商品

```java
// 查询名称以 "RB-" 或 "RS-" 开头的业务板块
sysBusinessSegmentExample → sys_business_segment WHERE name LIKE 'RB-' OR name LIKE 'RS-'

// 查询这些板块下所有有效商品
productExample → product WHERE inative_flag=false AND business_segment_id IN (RB/RS板块IDs)

// 设置排除列表
req.setNotInProductIds(products.stream().map(x -> x.getId()).collect(Collectors.toList()));
```

### Step 3：SQL查询主数据

**SQL位置**：`MyReceiptDeliveryDetailsMapper.xml` L2752-2905

**SQL结构（3个CTE + 主查询）**：

```sql
-- CTE1: movement_data
-- 从 movement_price 按 physical_deal_line_id 汇总已定价数量
WITH movement_data AS (
    SELECT physical_deal_line_id, SUM(quantity) 
    FROM movement_price 
    WHERE priced = 1
    GROUP BY physical_deal_line_id
),

-- CTE2: document_check
-- 入库量：action_id=42, offset_flag='N', status IN (2,10), sap_push_status=2
document_check AS (
    SELECT physical_deal_line_id, SUM(quantity)
    FROM document_items JOIN documents
    GROUP BY physical_deal_line_id
),

-- CTE3: document_offset_check
-- 冲销量：offset_flag='Y'
document_offset_check AS (
    SELECT physical_deal_line_id, SUM(quantity)
    FROM document_items JOIN documents
    GROUP BY physical_deal_line_id
)

-- 主查询关联
SELECT ...
FROM physical_deal_line 
JOIN physical_deals ON ps_flag = 'P' AND contract_type != 'ShortTerm'
LEFT JOIN product, counterparty, currency, unit, sys_company
WHERE ABS(movement_qty) != ABS(doc_check_qty - offset_qty)  -- 只返回有差异的记录
```

**关键过滤条件**：
- `ps_flag = 'P'`：仅采购
- `contract_type != 'ShortTerm'`：排除短期合同
- 定价量与入库量存在差异（超过 0.01%）
- 排除 RB/RS 业务板块

### Step 4：补充数据查询

#### 4a. 定价参数解析

```java
// 查询合同行信息
PhysicalDealLineExample pdLineExample = new PhysicalDealLineExample();
pdLineExample.createCriteria().andIdIn(pdLineIds);
List<PhysicalDealLine> pdLines = physicalDealLineMapper.selectByExample(pdLineExample);

// 解析定价参数
pricingParamMap = riskUtil.parsePdLineBasicPriceParam(pdLines);
```

#### 4b. 已定价明细

```java
LambdaQueryWrapper<MovementPrice> movementPriceQueryWrapper = new LambdaQueryWrapper<>();
movementPriceQueryWrapper.eq(MovementPrice::getInactiveFlag, false);
movementPriceQueryWrapper.eq(MovementPrice::getPriced, 1);
movementPriceQueryWrapper.in(MovementPrice::getPhysicalDealLineId, pdLineIds);
movementPriceQueryWrapper.le(MovementPrice::getDailySettlementDate, req.getEndDay());
List<MovementPrice> movementPriceList = movementPriceMapper.selectList(movementPriceQueryWrapper);
```

#### 4c. 截至月份入库量

```java
List<PhysicalDealLine> docInQuantityList = documentsMapper.getDocInQuantityByLineIdAndDate(pdLineIds, req.getEndDay());
Map<Long, Double> docInQuantityMap = docInQuantityList.stream()
    .collect(Collectors.toMap(x -> x.getId(), y -> y.getQuantity(), (z1, z2) -> z1));
```

#### 4d. 调差数据

```java
Map<Long, PurchaseEngagamentAdjustdifferenceDto> sumDiiferenceMap = 
    purchaseEngagamentAdjustdifferenceService.getSumDiiference(pdLineIds, LocalDate.parse(date));
```

#### 4e. 价格触发明细

```java
List<PriceTriggeringAndMoementPrice> priceTriggeringDetailList = 
    priceTriggeringMapper.getPriceTriggeringDetails(pdLineIds);
Map<Long, List<PriceTriggeringAndMoementPrice>> priceTriggeringDetailMap = 
    priceTriggeringDetailList.stream()
    .collect(Collectors.groupingBy(PriceTriggeringAndMoementPrice::getPhysicalDealLineId));
```

#### 4f. 库存估值明细

```java
DetailEntrisValueEvaluationQuery evaluationQuery = new DetailEntrisValueEvaluationQuery();
evaluationQuery.setPhysicalDealLineIds(pdLineIds);
evaluationQuery.setAccountingDate(LocalDate.parse(req.getDate()));
List<DetailEntrisValueEvaluation> evaluationList = 
    eomStorageService.listDetailEntrisValueEvaluation(evaluationQuery);
Map<Long, List<DetailEntrisValueEvaluation>> evaluationMap = 
    evaluationList.stream()
    .collect(Collectors.groupingBy(DetailEntrisValueEvaluation::getPhysicalDealLineId));
```

---

## 四、计算公式详解

### 1. 数量计算

#### (a) 已定价量（quantityAlreadyPriced）

```java
// 情景一：未定价（没有定价明细）或者加和为0
if (CollectionUtils.isEmpty(movementPrices) || quantityCheck.equals(0.0)) {
    resultPricingTableRes.setQuantityAlreadyPriced(0.0);
} else {
    // 有定价明细
    Double QuantityAlreadyPriced = -1 * quantityCheck;  // 取相反数
    resultPricingTableRes.setQuantityAlreadyPriced(QuantityAlreadyPriced);
}
```

#### (b) 已入库量（quantityAlready）

```java
// 不需要单位转换
resultPricingTableRes.setQuantityAlready(resultPricingTableRes.getDociQuantity());
```

#### (c) 已定价未入库量（pricedButNotInStock）

```java
// 情景一：未定价
if (CollectionUtils.isEmpty(movementPrices) || quantityCheck.equals(0.0)) {
    resultPricingTableRes.setPricedButNotInStock(
        NumberUtil.minusMuchParam(0.0, resultPricingTableRes.getQuantityAlready(), diffQuantity)
    );
} else {
    // 有定价明细
    Double pricedButNotInStock = NumberUtil.minusMuchParam(
        QuantityAlreadyPriced, 
        resultPricingTableRes.getDociQuantity(), 
        diffQuantity
    );
    resultPricingTableRes.setPricedButNotInStock(pricedButNotInStock);
}
```

#### (d) KG单位转换

```java
// 数量单位转换KG转换率
Double DocUnitConversion = 1.0;
if (resultPricingTableRes.getPdlUnitId() != null && !resultPricingTableRes.getPdlUnitId().equals(83l)) {
    DocUnitConversion = riskUnitConversionUtil.getUnitConversionNew(
        resultPricingTableRes.getPdlUnitId(), 
        kgUnitId, 
        resultPricingTableRes.getProductId()
    );
}

// 调差数据KG转换
Double diffQuantityKg = NumberUtil.multiply(diffQuantity, DocUnitConversion);

// 已入库量(kg)
resultPricingTableRes.setQuantityAlreadyKg(
    NumberUtil.multiply(resultPricingTableRes.getQuantityAlready(), DocUnitConversion)
);

// 已定价量(kg)
resultPricingTableRes.setQuantityAlreadyPricedKg(QuantityAlreadyPricedKg);

// 已定价未入库量(kg)
resultPricingTableRes.setPricedButNotInStockKg(
    NumberUtil.minusMuchParam(
        resultPricingTableRes.getQuantityAlreadyPricedKg(), 
        resultPricingTableRes.getQuantityAlreadyKg(), 
        diffQuantityKg
    )
);
```

### 2. 金额计算

#### (a) 已定价未入库金属金额

```java
// 从库存估值明细表获取
List<DetailEntrisValueEvaluation> evaluations = evaluationMap.get(resultPricingTableRes.getPhysicalDealLineId());

BigDecimal estMetalValue = BigDecimal.ZERO;
BigDecimal estMetalValueBaseCur = BigDecimal.ZERO;
BigDecimal receivableCDAmount = BigDecimal.ZERO;
BigDecimal receivableCDAmountBaseCur = BigDecimal.ZERO;

if(!CollectionUtils.isEmpty(evaluations)){
    for (DetailEntrisValueEvaluation evaluation : evaluations) {
        if(evaluation.getMetalValue() != null) 
            estMetalValue = estMetalValue.add(evaluation.getMetalValue());
        if(evaluation.getBaseCurMetalValue() != null) 
            estMetalValueBaseCur = estMetalValueBaseCur.add(evaluation.getBaseCurMetalValue());
        if(evaluation.getReceivableCDAmount() != null) 
            receivableCDAmount = receivableCDAmount.add(evaluation.getReceivableCDAmount());
        if(evaluation.getBaseCurReceivableCDAmount() != null) 
            receivableCDAmountBaseCur = receivableCDAmountBaseCur.add(evaluation.getBaseCurReceivableCDAmount());
    }
}

// 已定价未入库金额-结算币种
resultPricingTableRes.setPricedButNotInAmount1(
    pricedMetalValue.subtract(estMetalValue).subtract(receivableCDAmount)
);

// 已定价未入库金额-本位币
resultPricingTableRes.setPricedButNotInAmountEur1(
    pricedMetalValueBaseCur.subtract(estMetalValueBaseCur).subtract(receivableCDAmountBaseCur)
);
```

#### (b) 成本价计算

```java
if(resultPricingTableRes.getPricedButNotInStockKg() != null){
    BigDecimal targetUnitPricedButNotInStock = 
        resultPricingTableRes.getPricedButNotInStockKg() == null 
            ? BigDecimal.ZERO 
            : new BigDecimal(resultPricingTableRes.getPricedButNotInStockKg().toString());

    // 目标单位转换
    if(targetUnit != null) {
        Long targetUnitId = req.getUnitId();
        Long productId = resultPricingTableRes.getProductId();
        Double targetUnitConversion = riskUnitConversionUtil.getUnitConversionNew(kgUnitId, targetUnitId, productId);
        if(targetUnitConversion != null) {
            targetUnitPricedButNotInStock = targetUnitPricedButNotInStock.multiply(new BigDecimal(targetUnitConversion.toString()));
        }
        resultPricingTableRes.setPriceUnit(targetUnit.getName());
    }

    // 成本价 = 已定价未入库金额 ÷ 已定价未入库量
    resultPricingTableRes.setPricedButNotInAmount(
        resultPricingTableRes.getPricedButNotInAmount1().divide(targetUnitPricedButNotInStock, 9, RoundingMode.HALF_UP).doubleValue()
    );
    resultPricingTableRes.setPricedButNotInAmountEur(
        resultPricingTableRes.getPricedButNotInAmountEur1().divide(targetUnitPricedButNotInStock, 9, RoundingMode.HALF_UP).doubleValue()
    );
}
```

### 3. 完成状态判定

```java
Iterator<ResultPricingTableRes> quaryFilterIterator = procurementInventoryPricingMainframe.iterator();
while (quaryFilterIterator.hasNext()) {
    ResultPricingTableRes resultPricingTableRes = quaryFilterIterator.next();
    BigDecimal son = BigDecimal.valueOf(resultPricingTableRes.getQuantityAlreadyPriced()).setScale(5, RoundingMode.HALF_UP);
    BigDecimal mom = BigDecimal.valueOf(resultPricingTableRes.getQuantityAlready()).setScale(5, RoundingMode.HALF_UP);
    
    if (mom.compareTo(BigDecimal.ZERO) != 0) {
        BigDecimal ratio = son.divide(mom, 5, RoundingMode.HALF_UP);
        if (ratio.compareTo(new BigDecimal("0.9999")) >= 0 && ratio.compareTo(new BigDecimal("1.0001")) <= 0) {
            // 比值在 [99.99% ~ 100.01%] 之间 → 完成
            resultPricingTableRes.setInWarehouseStatus(CompleteStatusEnum.COMPLATE.getCode());
        } else {
            // 比值不在 [99.99% ~ 100.01%] 之间 → 未完成
            resultPricingTableRes.setInWarehouseStatus(CompleteStatusEnum.UNCOMPLATE.getCode());
        }
    } else if (mom.compareTo(BigDecimal.ZERO) == 0 || son.compareTo(BigDecimal.ZERO) == 0) {
        // 未完成
        resultPricingTableRes.setInWarehouseStatus(CompleteStatusEnum.UNCOMPLATE.getCode());
    }
}
```

---

## 五、字段映射关系

### 数量字段

| 字段 | 计算公式 | 说明 |
|------|---------|------|
| `quantityAlready` | `dociQuantity` | 已入库量（原始单位） |
| `quantityAlreadyKg` | `quantityAlready × DocUnitConversion` | 已入库量（KG） |
| `quantityAlreadyPriced` | `-1 × Σ movementPrice.quantity` | 已定价量（原始单位） |
| `quantityAlreadyPricedKg` | `Σ movementPrice.parentProductQuantity × -1` 或 `quantityAlreadyPriced × MovUnitConversion` | 已定价量（KG） |
| `pricedButNotInStock` | `quantityAlreadyPriced - quantityAlready - diffQuantity` | 已定价未入库量（原始单位） |
| `pricedButNotInStockKg` | `quantityAlreadyPricedKg - quantityAlreadyKg - diffQuantityKg` | 已定价未入库量（KG） |
| `diffQuantity` | 调差表汇总.sumQuantity | 调差数量（原始单位） |
| `diffQuantityKg` | `diffQuantity × DocUnitConversion` | 调差数量（KG） |

### 金额字段

| 字段 | 计算公式 | 说明 |
|------|---------|------|
| `pricedButNotInAmount1` | `pricedMetalValue - estMetalValue - receivableCDAmount` | 已定价未入库金额（结算币种） |
| `pricedButNotInAmountEur1` | `pricedMetalValueBaseCur - estMetalValueBaseCur - receivableCDAmountBaseCur` | 已定价未入库金额（本位币） |
| `pricedButNotInAmount` | `pricedButNotInAmount1 ÷ targetUnitPricedButNotInStock` | 成本价（结算币种） |
| `pricedButNotInAmountEur` | `pricedButNotInAmountEur1 ÷ targetUnitPricedButNotInStock` | 成本价（本位币） |

### 状态字段

| 字段 | 计算公式 | 说明 |
|------|---------|------|
| `inWarehouseStatus` | `quantityAlreadyPriced ÷ quantityAlready ∈ [0.9999, 1.0001]` → COMPLATE，否则 UNCOMPLATE | 入库完成状态 |

---

## 六、关键业务逻辑总结

1. **数据粒度**：报表以**订单商品行**(`physical_deal_line.id`)为最小粒度，每行一条记录。

2. **三大数量来源**：
   - **已定价量** ← `movement_price`表（已计价记录）
   - **已入库量** ← `documents`表（截至月份的入库量）
   - **差值量** ← `purchase_engagament_adjustdifference`表（人工录入的调差记录）

3. **核心等式**：`已定价未入库量 = 已定价量 - 已入库量 - 差值量`

4. **单位统一**：所有数量统一转换为**KG**（单位ID=83）。

5. **金额计算**：
   - 已定价未入库金额 = 已定价金属价值 - 库存估值金属价值 - 应收应付金额
   - 成本价 = 已定价未入库金额 ÷ 已定价未入库量

6. **完成状态**：比较`quantityAlreadyPriced`和`quantityAlready`（均保留5位小数），比值在[99.99%, 100.01%]之间则标记为完成。

7. **计价方式判断**：
   - BasicFixedPrice（固定价）
   - BasicTriggeredPrice（点价）
   - BasicAveragePrice（均价）

---

## 七、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/ReportController.java:1143` |
| Service接口 | `bcadmin-system/.../service/ReceiptDeliveryDetailsService.java` |
| Service实现 | `bcadmin-system/.../service/impl/ReceiptDeliveryDetailsServiceImpl.java:2591` |
| Mapper接口 | `bcadmin-db/.../dao/MyReceiptDeliveryDetailsMapper.java` |
| Mapper XML | `bcadmin-db/src/main/resources/system/MyReceiptDeliveryDetailsMapper.xml:2752` |
| DTO | `bcadmin-db/.../dto/ResultPricingTableRes.java` |
| Query | `bcadmin-db/.../dto/QueryPricingTableReq.java` |

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
