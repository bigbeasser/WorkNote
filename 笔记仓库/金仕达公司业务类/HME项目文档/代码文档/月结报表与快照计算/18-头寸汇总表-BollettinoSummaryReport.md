# 头寸汇总表（getBollettinoSummaryReport）调用链梳理

## 概述

头寸汇总表用于按金属成分维度汇总现货、期货、调整的头寸数据，展示采购、销售、交易、LME等维度的数量和金额。

**入口方法**：`ReportController.getBollettinoSummaryReport(BollettinoSummaryDto, BasePage)`  
**核心Service**：`FixationAdjustmentServiceImpl.getBollettinoSummaryReport()`

---

## 一、完整调用链

```
Controller层：
  ReportController.getBollettinoSummaryReport()     [GET /api/report/getBollettinoSummaryReport]
    └─ FixationAdjustmentServiceImpl.getBollettinoSummaryReport()

Service层（FixationAdjustmentServiceImpl）：
  ├─ Step 1：参数预处理
  │   ├─ 合并金属成分ID和金属描述ID
  │   └─ 处理isCu参数（y→yes, n→no）
  │
  ├─ Step 2：三源数据分组查询
  │   ├─ FixationAdjustmentMapper.getBollettinoSummarySumReport()  [现货分组骨架]
  │   ├─ FuturesMovementQuantityMapper.getFuturesMovementToSummaryReport()  [期货分组]
  │   └─ FixationAdjustmentMapper.getFixationAdjustmentToSummaryReport()  [调整分组]
  │
  ├─ Step 3：Java内存合并分组
  │   └─ 按groupKeyName合并三源数据
  │
  ├─ Step 4：手动分页
  │   └─ 根据page/size截取数据
  │
  ├─ Step 5：明细数据批量查询
  │   ├─ FixationAdjustmentMapper.getSummaryDataPS()  [现货明细]
  │   ├─ FuturesMovementQuantityMapper.getFuturesMovementToSummary()  [期货明细]
  │   └─ FixationAdjustmentMapper.getFixationAdjustmentToSummaryPS()  [调整明细]
  │
  ├─ Step 6：单位换算
  │   └─ 重量：unit → KG (unitId=83)
  │
  └─ Step 7：数量计算
      ├─ 采购净重
      ├─ 销售净重
      ├─ 交易数量
      ├─ LME数量
      └─ 总计
```

---

## 二、数据来源表

### 核心业务表

| 表名 | 用途 |
|------|------|
| `movement_quantity` | 现货计价量（核心主表） |
| `futures_movement_quantity` | 期货计价量（LME头寸数据） |
| `fixation_adjustment` | 现货数量调整（手工调整） |

### 关联维度表

| 表名 | 用途 |
|------|------|
| `sys_company` | 业务机构名称 |
| `sys_business_segment` | 业务板块名称 + `is_preserve_value`过滤 |
| `specification_type` | 金属成分（质检类型）名称/描述 |
| `product` | 商品名称 |
| `product_specification` | 商品-金属成分关联 |
| `physical_deals` | 实物交易主表（`intercompany`过滤） |
| `physical_deal_line` | 实物交易行 |

---

## 三、数据收集阶段详细逻辑

### Step 1：参数预处理

```java
// 合并金属成分ID和金属描述ID（这俩都是一个东西）
queryDto.getProductSpecificationIds().addAll(queryDto.getProductSpecificationDescIds());
queryDto.setProductSpecificationIds(
    queryDto.getProductSpecificationIds().stream().distinct().collect(Collectors.toList())
);

// 处理isCu参数
if("y".equalsIgnoreCase(queryDto.getIsCu())) {
    queryDto.setIsCu("yes");
} else if("n".equalsIgnoreCase(queryDto.getIsCu())){
    queryDto.setIsCu("no");
}

queryDto.setIsPreserveValue(true);
```

### Step 2：三源数据分组查询

#### 2a. 现货分组骨架

```java
List<MetalBollettinoGroup> bollettinoSummaryReport = 
    fixationAdjustmentMapper.getBollettinoSummarySumReport(queryDto);
```

#### 2b. 期货分组（仅Normal模式）

```java
List<MetalBollettinoGroup> futuresMovementToMaterialReport = new ArrayList<>();
if (IntercompanyEnum.Normal.getValue().equals(queryDto.getIntercompany()) || queryDto.getIntercompany() == null) {
    futuresMovementToMaterialReport = 
        futuresMovementQuantityMapper.getFuturesMovementToSummaryReport(queryDto);
}
```

#### 2c. 调整分组（仅Normal模式）

```java
List<MetalBollettinoGroup> fixationAdjustmentReport = new ArrayList<>();
if (IntercompanyEnum.Normal.getValue().equals(queryDto.getIntercompany()) || queryDto.getIntercompany() == null) {
    fixationAdjustmentReport = 
        fixationAdjustmentMapper.getFixationAdjustmentToSummaryReport(queryDto);
}
```

### Step 3：Java内存合并分组

```java
// 合并期货分组
List<MetalBollettinoGroup> temp = new ArrayList<>();
if (CollectionUtils.isNotEmpty(futuresMovementToMaterialReport)) {
    for (MetalBollettinoGroup item : futuresMovementToMaterialReport) {
        String keyName = item.getGroupKeyName();
        Optional<MetalBollettinoGroup> any = bollettinoSummaryReport.stream()
            .filter(x -> x.getGroupKeyName().equals(keyName)).findAny();
        if (any.isPresent()) {
            // 已存在，设置fmovIds
            bollettinoSummaryReport.stream()
                .filter(x -> x.getGroupKeyName().equals(keyName))
                .forEach(x -> x.setFmovIds(item.getFmovIds()));
        } else {
            // 不存在，添加到临时列表
            temp.add(item);
        }
    }
}
bollettinoSummaryReport.addAll(temp);  // 分组的内容加到总和里

// 合并调整分组（逻辑相同）
temp.clear();
if (CollectionUtils.isNotEmpty(fixationAdjustmentReport)) {
    for (MetalBollettinoGroup item : fixationAdjustmentReport) {
        String keyName = item.getGroupKeyName();
        Optional<MetalBollettinoGroup> any = bollettinoSummaryReport.stream()
            .filter(x -> x.getGroupKeyName().equals(keyName)).findAny();
        if (any.isPresent()) {
            bollettinoSummaryReport.stream()
                .filter(x -> x.getGroupKeyName().equals(keyName))
                .forEach(x -> x.setFmovIds(item.getFmovIds()));
        } else {
            temp.add(item);
        }
    }
}
bollettinoSummaryReport.addAll(temp);  // 分组的内容加到总和里

// 按日期排序
bollettinoSummaryReport.sort(Comparator.comparing(MetalBollettinoGroup::getDailySettlementDay));
```

### Step 4：手动分页

```java
Integer size = basePage.getSize();
Integer page = basePage.getPage();

// 计算分页起始位置
int startIndex = (basePage.getPage() - 1) * basePage.getSize();
int endIndex = Math.min(startIndex + basePage.getSize(), bollettinoSummaryReport.size());

List<MetalBollettinoGroup> suitableMovementPriceCollectIdsNew = bollettinoSummaryReport;

// 获取分页数据
if (endIndex > 0) {  // 需要分页
    suitableMovementPriceCollectIdsNew = bollettinoSummaryReport.subList(startIndex, endIndex);
}
```

### Step 5：明细数据批量查询

#### 5a. 收集查询条件

```java
List<Long> LegalEntityIdQuery = new ArrayList<>();
List<Integer> sessionQuery = new ArrayList<>();
List<Long> ProductSpecificationIdQuery = new ArrayList<>();
List<Long> BusinessSegmentIdQuery = new ArrayList<>();
List<String> DailySettlementQuery = new ArrayList<>();

for (MetalBollettinoGroup group : suitableMovementPriceCollectIdsNew) {
    if (group.getLegalEntityId() != null) {
        LegalEntityIdQuery.add(group.getLegalEntityId());
    }
    if (group.getSession() != null) {
        sessionQuery.add(group.getSession());
    }
    if (group.getProductSpecificationId() != null) {
        ProductSpecificationIdQuery.add(group.getProductSpecificationId());
    }
    if (group.getDailySettlementDay() != null) {
        DailySettlementQuery.add(group.getDailySettlementDay().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")));
    }
    if (group.getBusinessSegmentId() != null) {
        BusinessSegmentIdQuery.add(group.getBusinessSegmentId());
    }
}

// 去重
LegalEntityIdQuery = LegalEntityIdQuery.stream().distinct().collect(Collectors.toList());
sessionQuery = sessionQuery.stream().distinct().collect(Collectors.toList());
ProductSpecificationIdQuery = ProductSpecificationIdQuery.stream().distinct().collect(Collectors.toList());
BusinessSegmentIdQuery = BusinessSegmentIdQuery.stream().distinct().collect(Collectors.toList());
DailySettlementQuery = DailySettlementQuery.stream().distinct().collect(Collectors.toList());
```

#### 5b. 现货明细查询

```java
MetalBollettinoDto queryMetalBollettinoDto = new MetalBollettinoDto();
queryMetalBollettinoDto.setIntercompany(queryDto.getIntercompany());
queryMetalBollettinoDto.setIsPreserveValue(true);
queryMetalBollettinoDto.setLegalEntityIds(LegalEntityIdQuery);
queryMetalBollettinoDto.setSessions(sessionQuery);
queryMetalBollettinoDto.setProductSpecificationIds(ProductSpecificationIdQuery);
queryMetalBollettinoDto.setBusinessSegmentIdsOrNull(BusinessSegmentIdQuery);
queryMetalBollettinoDto.setDailySettlementDates(DailySettlementQuery);

List<MetalBollettinoDto> bolleListAll = 
    fixationAdjustmentMapper.getSummaryDataPS(queryMetalBollettinoDto);
```

#### 5c. 期货明细查询

```java
FuturesMovementQuantityMatrialReport queryFutures = new FuturesMovementQuantityMatrialReport();
queryFutures.setIsPreserveValue(true);
queryFutures.setLegalEntityIds(LegalEntityIdQuery);
queryFutures.setSessions(sessionQuery);
queryFutures.setProductSpecificationIds(ProductSpecificationIdQuery);
queryFutures.setBusinessSegmentIdsOrNull(BusinessSegmentIdQuery);
queryFutures.setDailySettlementDates(DailySettlementQuery);

List<FuturesMovementQuantityMatrialReport> futuresListAll = 
    futuresMovementQuantityMapper.getFuturesMovementToSummary(queryFutures);
```

#### 5d. 调整明细查询

```java
MetalBollettinoDto queryAdjustData = new MetalBollettinoDto();
queryAdjustData.setIsPreserveValue(true);
queryAdjustData.setLegalEntityIds(LegalEntityIdQuery);
queryAdjustData.setSessions(sessionQuery);
queryAdjustData.setProductSpecificationIds(ProductSpecificationIdQuery);
queryAdjustData.setBusinessSegmentIdsOrNull(BusinessSegmentIdQuery);
queryAdjustData.setDailySettlementDates(DailySettlementQuery);

List<FixationAdjustmentDto> FixationAdjustmentAll = 
    fixationAdjustmentMapper.getFixationAdjustmentToSummaryPS(queryAdjustData);
```

### Step 6：单位换算

```java
HashMap<String, Double> unitConversionMap = new HashMap<>();

// 1. 预处理 bolleListAll → 转为 KG
for (MetalBollettinoDto dto : bolleListAll) {
    String key = dto.getContractQuantityUnitId() + "-" + dto.getProductId();
    unitConversionMap.computeIfAbsent(key, k ->
        riskUnitConversionUtil.getUnitConversion(dto.getContractQuantityUnitId(), 83L, dto.getProductId()));
    dto.setGrossWeight(NumberUtil.multiply(unitConversionMap.get(key), dto.getGrossWeight()));
    dto.setNetWeight(NumberUtil.multiply(unitConversionMap.get(key), dto.getNetWeight()));
}

// 2. 预处理 futuresListAll → 转为 KG
for (FuturesMovementQuantityMatrialReport dto : futuresListAll) {
    String key = dto.getQuantityUnitId() + "-" + dto.getProductId();
    unitConversionMap.computeIfAbsent(key, k ->
        riskUnitConversionUtil.getUnitConversion(dto.getQuantityUnitId(), 83L, dto.getProductId()));
    dto.setTransactionQuantity(NumberUtil.multiply(unitConversionMap.get(key), dto.getTransactionQuantity()));
}
```

### Step 7：构建分组索引

```java
Map<BollettinoSummaryReportGroupKey, List<MetalBollettinoDto>> bolleIndex = 
    bolleListAll.stream().collect(Collectors.groupingBy(BollettinoSummaryReportGroupKey::fromBollettinoDto));

Map<BollettinoSummaryReportGroupKey, List<FuturesMovementQuantityMatrialReport>> futuresIndex = 
    futuresListAll.stream().collect(Collectors.groupingBy(BollettinoSummaryReportGroupKey::fromFuturesDto));

Map<BollettinoSummaryReportGroupKey, List<FixationAdjustmentDto>> fixationIndex = 
    FixationAdjustmentAll.stream().collect(Collectors.groupingBy(BollettinoSummaryReportGroupKey::fromFixationDto));
```

---

## 四、计算公式详解

### 1. 采购净重（purchaseQuantity）

```java
// 采购净重 = CTRM数据源 + P方向 + 净重之和
Double PurchaseNetQuantity = bolleList.stream()
    .filter(s -> "CTRM".equalsIgnoreCase(s.getDataSource()))
    .filter(a -> "P".equalsIgnoreCase(a.getPsFlag()))
    .mapToDouble(MetalBollettinoDto::getNetWeight)
    .sum();

// 调整数量（P方向）
Double Psum = Optional.ofNullable(FixationAdjustmentTotal).orElse(Collections.emptyList())
    .stream()
    .filter(a -> "P".equalsIgnoreCase(a.getPsFlag()))
    .mapToDouble(FixationAdjustmentDto::getQuantity)
    .sum();
Psum = NumberUtil.division(Psum, 1000.0, 5);  // KG → 吨

// 采购净重（吨）
bollettinoSummaryDto.setPurchaseQuantity(
    NumberUtil.add(NumberUtil.division(PurchaseNetQuantity, 1000.0, 5), Psum)
);
```

### 2. 销售净重（saleQuantity）

```java
// 销售净重 = CRM数据源 + S方向 + 净重之和
Double saleNetQuantity = bolleList.stream()
    .filter(s -> "CRM".equalsIgnoreCase(s.getDataSource()))
    .filter(a -> "S".equalsIgnoreCase(a.getPsFlag()))
    .mapToDouble(MetalBollettinoDto::getNetWeight)
    .sum();

// 调整数量（S方向）
Double Ssum = Optional.ofNullable(FixationAdjustmentTotal).orElse(Collections.emptyList())
    .stream()
    .filter(a -> "S".equalsIgnoreCase(a.getPsFlag()))
    .mapToDouble(FixationAdjustmentDto::getQuantity)
    .sum();
Ssum = NumberUtil.division(Ssum, 1000.0, 5);  // KG → 吨

// 销售净重（吨）= 销售净重 - 调整数量
bollettinoSummaryDto.setSaleQuantity(
    NumberUtil.minus(NumberUtil.division(saleNetQuantity, 1000.0, 5), Ssum)
);
```

### 3. 交易数量（tradingQuantity）

```java
// 交易数量 = CTRM数据源 + S方向 + 净重之和
Double TradingQuantity = bolleList.stream()
    .filter(s -> "CTRM".equalsIgnoreCase(s.getDataSource()))
    .filter(a -> "S".equalsIgnoreCase(a.getPsFlag()))
    .mapToDouble(MetalBollettinoDto::getNetWeight)
    .sum();

// 转换为吨（取负）
bollettinoSummaryDto.setTradingQuantity(
    NumberUtil.division(TradingQuantity, -1000.0, 5)
);
```

### 4. LME数量（lmeQuantity）

```java
// LME数量 = 买方向交易数量 - 卖方向交易数量
Double lemQuantityPay = futuresList.stream()
    .filter(a -> "B".equalsIgnoreCase(a.getBsFlag()))
    .mapToDouble(FuturesMovementQuantityMatrialReport::getTransactionQuantity)
    .sum();

Double lemQuantitySale = futuresList.stream()
    .filter(a -> "S".equalsIgnoreCase(a.getBsFlag()))
    .mapToDouble(FuturesMovementQuantityMatrialReport::getTransactionQuantity)
    .sum();

Double LmeQuantityKG = NumberUtil.minus(lemQuantityPay, lemQuantitySale);

// 转换为吨
bollettinoSummaryDto.setLmeQuantity(
    NumberUtil.division(LmeQuantityKG, 1000, 5)
);
```

### 5. 总计（total）

```java
// 总计 = 采购净重 + LME数量 + 销售净重 + 交易数量
Double purchaseQuantitAndLmeQuantity = NumberUtil.add(
    bollettinoSummaryDto.getPurchaseQuantity(), 
    bollettinoSummaryDto.getLmeQuantity(), 
    5
);

Double saleQuantityAndTradingQuantit = NumberUtil.add(
    bollettinoSummaryDto.getSaleQuantity(), 
    bollettinoSummaryDto.getTradingQuantity(), 
    5
);

Double total = NumberUtil.add(
    purchaseQuantitAndLmeQuantity, 
    saleQuantityAndTradingQuantit, 
    5
);

bollettinoSummaryDto.setTotal(total);
```

### 6. BTS/BTO模式特殊处理

```java
// BTS/BTO模式下，期货和调整数据为空
if (StringUtils.equalsAnyIgnoreCase(
    queryDto.getIntercompany(), 
    IntercompanyEnum.BTS.getValue(), 
    IntercompanyEnum.BTO.getValue()
)) {
    futuresList = new ArrayList<>();
    FixationAdjustmentTotal = new ArrayList<>();
}
```

---

## 五、字段映射关系

| 字段 | 计算公式 | 说明 |
|------|---------|------|
| `settlementDate` | `group.getDailySettlementDay()` | 结算日期 |
| `session` | `group.getSession()` | 会话 |
| `legalEntityName` | `group.getLegalEntityName()` | 业务机构名称 |
| `productName` | `group.getProductSpecificationName()` | 商品名称 |
| `specificationTypeDesc` | `group.getSpecificationTypeDesc()` | 金属成分描述 |
| `businessSegmentName` | `group.getBusinessSegmentName()` | 业务板块名称 |
| `businessSegmentId` | `group.getBusinessSegmentId()` | 业务板块ID |
| `purchaseQuantity` | `(CTRM+P净重 + P调整) ÷ 1000` | 采购净重（吨） |
| `saleQuantity` | `(CRM+S净重 - S调整) ÷ 1000` | 销售净重（吨） |
| `tradingQuantity` | `(CTRM+S净重) ÷ -1000` | 交易数量（吨） |
| `lmeQuantity` | `(B方向 - S方向) ÷ 1000` | LME数量（吨） |
| `total` | `采购净重 + LME数量 + 销售净重 + 交易数量` | 总计（吨） |

---

## 六、关键业务逻辑总结

1. **三源数据合并**：报表数据来自三个独立的计价量模型（现货`movement_quantity`、期货`futures_movement_quantity`、调整`fixation_adjustment`），以现货分组为骨架，通过`groupKeyName`在Java内存中合并。

2. **数据源过滤**：
   - `CTRM`：交易数据源
   - `CRM`：销售数据源
   - `P`/`S`：采购/销售方向
   - `B`/`S`：买/卖方向（期货）

3. **单位统一**：所有数量统一转换为**KG**（单位ID=83），最终展示时转换为**吨**（÷1000）。

4. **内部交易过滤**：BTS/BTO模式下，期货和调整数据为空，只统计现货数据。

5. **手动分页**：由于三源合并后数据量不确定，采用Java内存分页而非数据库分页。

6. **精度控制**：所有数量字段统一5位小数`HALF_UP`。

7. **幂等性**：报表为只读查询，不涉及落库，每次调用都重新计算。

---

## 七、数据流总览图

```
前端请求 BollettinoSummaryDto (筛选条件)
    │
    ▼
Controller ──→ Service (参数预处理)
    │
    ├─ Step 1: 参数预处理
    │   └─ 合并金属成分ID，处理isCu参数
    │
    ├─ Step 2: 三源数据分组查询
    │   ├─ 现货分组骨架 (getBollettinoSummarySumReport)
    │   ├─ 期货分组 (getFuturesMovementToSummaryReport)
    │   └─ 调整分组 (getFixationAdjustmentToSummaryReport)
    │
    ├─ Step 3: Java内存合并分组
    │   └─ 按groupKeyName合并三源数据
    │
    ├─ Step 4: 手动分页
    │   └─ 根据page/size截取数据
    │
    ├─ Step 5: 明细数据批量查询
    │   ├─ 现货明细 (getSummaryDataPS)
    │   ├─ 期货明细 (getFuturesMovementToSummary)
    │   └─ 调整明细 (getFixationAdjustmentToSummaryPS)
    │
    ├─ Step 6: 单位换算
    │   └─ 重量：unit → KG (unitId=83)
    │
    └─ Step 7: 数量计算
        ├─ 采购净重 = (CTRM+P净重 + P调整) ÷ 1000
        ├─ 销售净重 = (CRM+S净重 - S调整) ÷ 1000
        ├─ 交易数量 = (CTRM+S净重) ÷ -1000
        ├─ LME数量 = (B方向 - S方向) ÷ 1000
        └─ 总计 = 采购净重 + LME数量 + 销售净重 + 交易数量
            │
            ▼
返回 CommonPage<BollettinoSummaryDto>
```

---

## 八、关键文件清单

| 文件 | 路径 |
|------|------|
| Controller | `bcadmin-system/.../rest/ReportController.java:1102` |
| Service接口 | `bcadmin-system/.../service/FixationAdjustmentService.java:66` |
| Service实现 | `bcadmin-system/.../service/impl/FixationAdjustmentServiceImpl.java:202` |
| Mapper接口 | `bcadmin-db/.../dao/FixationAdjustmentMapper.java` |
| Mapper XML | `bcadmin-db/src/main/resources/system/FixationAdjustmentMapper.xml` |
| DTO | `bcadmin-db/.../dto/BollettinoSummaryDto.java` |
| Group | `bcadmin-db/.../bo/MetalBollettinoGroup.java` |

---

**文档版本**: v1.0  
**生成日期**: 2026-07-01  
**最后更新**: 2026-07-01
