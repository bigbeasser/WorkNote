# Position Monitor Sub Report（夜盘保值头寸统计表）调用链分析

## 一、概述

**报表名称**：夜盘保值头寸统计表（Position Monitor Sub Report）  
**入口方法**：`ReportController.getPositionMonitorSubReport()`  
**业务含义**：按基础金属（Base Metal）维度汇总头寸统计，是主表（Main Report）的聚合视图  
**核心特点**：**只有数量字段，没有价格和金额字段**

---

## 二、完整调用链路

### 2.1 Controller 层

```java
// 文件：ReportController.java (第1128-1132行)
@GetMapping("/getPositionMonitorSubReport")
public BaseResultEntity<?> getPositionMonitorSubReport(PositionMonitorMainDto queryDto, BasePage basePage) {
    return fixationAdjustmentService.getPositionMonitorSubReport(queryDto, basePage);
}
```

### 2.2 Service 层

```java
// 文件：FixationAdjustmentServiceImpl.java (第1928-1962行)
@Override
public BaseResultEntity<List<PositionMonitorSubDto>> getPositionMonitorSubReport(
        PositionMonitorMainDto queryDto, BasePage basePage) {
    
    // 步骤1：调用主表方法获取明细数据
    List<PositionMonitorMainDto> positionMonitorMainReport = 
            getPositionMonitorMainReport(queryDto, basePage);
    
    // 步骤2：按 baseMetalId 分组
    Map<Long, List<PositionMonitorMainDto>> baseMetalGroupBy = 
            positionMonitorMainReport.stream()
                .collect(Collectors.groupingBy(a -> a.getBaseMetalId()));
    
    // 步骤3：对每个金属分组求和
    List<PositionMonitorSubDto> positionMonitorSubDtos = new ArrayList<>();
    for (Map.Entry<Long, List<PositionMonitorMainDto>> entry : baseMetalGroupBy.entrySet()) {
        PositionMonitorSubDto dto = new PositionMonitorSubDto();
        List<PositionMonitorMainDto> value = entry.getValue();
        
        // 基础金属名称
        dto.setBaseMetalSum(value.get(0).getBaseMetal());
        dto.setBaseMetalDesc(value.get(0).getBaseMetalDesc());
        
        // 初始头寸汇总
        Double initialPositionSum = value.stream()
                .mapToDouble(PositionMonitorMainDto::getInitialPosition).sum();
        dto.setInitialPositionSum(NumberUtil.multiply(initialPositionSum, 1.0, 5));
        
        // 现货头寸汇总
        Double physicalPositionSum = value.stream()
                .mapToDouble(PositionMonitorMainDto::getPhysicalMovement).sum();
        dto.setPhysicalPositionSum(NumberUtil.multiply(physicalPositionSum, 1.0, 5));
        
        // LME交易头寸汇总
        Double lmeMovementSum = value.stream()
                .mapToDouble(PositionMonitorMainDto::getLmeMovement).sum();
        dto.setLmeMovementSum(NumberUtil.multiply(lmeMovementSum, 1.0, 5));
        
        // LME到期头寸汇总
        Double exprieLMESum = value.stream()
                .mapToDouble(PositionMonitorMainDto::getExprieLME).sum();
        dto.setExprieLMESum(NumberUtil.multiply(exprieLMESum, 1.0, 5));
        
        // 最终头寸汇总
        Double finalPositionSum = value.stream()
                .mapToDouble(PositionMonitorMainDto::getFinalPosition).sum();
        dto.setFinalPositionSum(NumberUtil.multiply(finalPositionSum, 1.0, 5));
        
        positionMonitorSubDtos.add(dto);
    }
    
    return BaseResultEntity.success(positionMonitorSubDtos);
}
```

### 2.3 主表方法（核心数据计算）

```java
// 文件：FixationAdjustmentServiceImpl.java (第1414-1634行)
public List<PositionMonitorMainDto> getPositionMonitorMainReport(
        PositionMonitorMainDto queryDto, BasePage basePage) {
    
    // 1. 获取前一交易日
    LocalDate prevDate = getPreviousTradeDate(queryDto.getDailySettlementDate());
    
    // 2. 获取分组维度（机构+金属组合）
    List<MetalBollettinoGroup> groups = getMovementQuantityGroups(queryDto, prevDate);
    
    // 3. 查询期货明细数据（按交易日和到期日分别查询）
    List<FuturesMovementQuantityMatrialReport> futuresByTradingDay = 
            queryFuturesByTradingDay(queryDto);
    List<FuturesMovementQuantityMatrialReport> futuresByDueDate = 
            queryFuturesByDueDate(queryDto);
    
    // 4. 对每个分组计算5个头寸字段
    for (MetalBollettinoGroup group : groups) {
        PositionMonitorMainDto returnObj = new PositionMonitorMainDto();
        
        // 4.1 初始头寸 = 前一天最终头寸（从历史表查询）
        returnObj.setInitialPosition(getFinalPositionFromHistory(
                group, prevDate, queryDto));
        
        // 4.2 现货头寸 = 采购净重 + 销售毛重 - 销售净重 + 调整量
        Double physicalMovement = calculatePhysicalMovement(
                group, queryDto);
        returnObj.setPhysicalMovement(physicalMovement / 1000.0); // KG转吨
        
        // 4.3 LME交易头寸 = 买方交易数量 + 卖方交易数量（按交易日）
        Double lmeMovement = calculateLmeMovementByTradingDay(
                group, futuresByTradingDay);
        returnObj.setLmeMovement(lmeMovement / 1000.0); // KG转吨
        
        // 4.4 LME到期头寸 = |卖方| - |买方|（按到期日）
        Double exprieLME = calculateLmeMovementByDueDate(
                group, futuresByDueDate);
        returnObj.setExprieLME(exprieLME / 1000.0); // KG转吨
        
        // 4.5 最终头寸 = 初始 + 现货 + LME交易 + LME到期
        Double finalPosition = returnObj.getInitialPosition() 
                + returnObj.getPhysicalMovement() 
                + returnObj.getLmeMovement() 
                + returnObj.getExprieLME();
        returnObj.setFinalPosition(finalPosition);
    }
    
    return positionMonitorMainDtos;
}
```

---

## 三、数据来源表

### 3.1 核心数据表

| 序号 | 表名 | 用途 | 关键字段 |
|------|------|------|----------|
| 1 | `movement_quantity` | 现货计价量模型 | legal_entity_id, product_specification_id, ps_flag, data_source, net_weight, gross_weight |
| 2 | `futures_movement_quantity` | 期货计价量模型 | legal_entity_id, base_metal_id, bs_flag, trade_date, due_date, transaction_quantity |
| 3 | `position_monitor_history` | 头寸监控历史表 | date, legal_entity_id, base_metal, final_position |
| 4 | `fixation_adjustment` | 现货数量调整表 | legal_entity_id, product_specification_id, ps_flag, quantity |
| 5 | `curvedate_session` | 交易日日历表 | date, prev_date |
| 6 | `futures_contract` | 期货合约表 | id, due_date |
| 7 | `product_specification` | 金属成分定义表 | id, name |

### 3.2 数据查询方法

#### 3.2.1 获取分组维度（5个数据源合并）

```java
// 1. 现货计价量分组
movementQuantityMapper.getMovementQuantityGroupToPositionMonitor(query)
// SQL: SELECT CONCAT(legal_entity_id, '_', product_specification_id) AS groupKeyName,
//           legal_entity_id, product_specification_id, ...
//      FROM movement_quantity
//      WHERE daily_settlement_date = ? AND legal_entity_id = ?
//      GROUP BY legal_entity_id, product_specification_id

// 2. 期货交易日分组
futuresMovementQuantityMapper.getFuturesMovementToSummaryTradingGroup(query)
// SQL: SELECT CONCAT(legal_entity_id, '_', base_metal_id) AS groupKeyName, ...
//      FROM futures_movement_quantity fm
//      LEFT JOIN futures_contract fc ON fm.futures_contract_id = fc.id
//      WHERE DATE_FORMAT(fm.trade_date, '%Y-%m-%d') = ?
//      GROUP BY legal_entity_id, base_metal_id

// 3. 期货到期日分组
futuresMovementQuantityMapper.getFuturesMovementToSummaryDueDateGroup(query)
// SQL: SELECT CONCAT(legal_entity_id, '_', base_metal_id) AS groupKeyName, ...
//      FROM futures_movement_quantity fm
//      LEFT JOIN futures_contract fc ON fm.futures_contract_id = fc.id
//      WHERE DATE_FORMAT(fc.due_date, '%Y-%m-%d') = ?
//      GROUP BY legal_entity_id, base_metal_id

// 4. 历史头寸分组
positionMonitorHistoryMapper.getBollettinoGroupList(query)
// SQL: SELECT CONCAT(legal_entity_id, '_', base_metal) AS groupKeyName, ...
//      FROM position_monitor_history
//      WHERE date = ? AND legal_entity_id = ?
//      GROUP BY legal_entity_id, base_metal

// 5. 现货数量调整分组
futuresMovementQuantityMapper.getFixationAdjustToSummaryTradingGroup(query)
// SQL: SELECT CONCAT(legal_entity_id, '_', specification_type_id) AS groupKeyName, ...
//      FROM fixation_adjustment fa
//      LEFT JOIN futures_contract fc ON fa.futures_contract_id = fc.id
//      WHERE DATE_FORMAT(fa.trade_date, '%Y-%m-%d') = ?
//      GROUP BY legal_entity_id, specification_type_id
```

#### 3.2.2 查询明细数据

```java
// 1. 查询现货明细（用于计算现货头寸）
fixationAdjustmentMapper.getMetalBollettinoDataPS(query)
// SQL: SELECT id, ps_flag, data_source, net_weight, gross_weight, ...
//      FROM movement_quantity
//      WHERE legal_entity_id = ? AND product_specification_id = ?
//        AND daily_settlement_date = ?

// 2. 查询历史最终头寸（用于计算初始头寸）
positionMonitorHistoryMapper.selectList(query)
// SQL: SELECT final_position
//      FROM position_monitor_history
//      WHERE date = ? AND legal_entity_id = ? AND base_metal = ?

// 3. 查询调整明细（用于计算现货头寸）
fixationAdjustmentMapper.getFixationAdjustmentToReportPS(query)
// SQL: SELECT id, ps_flag, quantity, ...
//      FROM fixation_adjustment
//      WHERE legal_entity_id = ? AND product_specification_id = ?
//        AND daily_settlement_date = ?

// 4. 查询期货明细（按交易日）
futuresMovementQuantityMapper.getFuturesMovementToPositionMonitorReport(query)
// SQL: SELECT bs_flag, transaction_quantity, ...
//      FROM futures_movement_quantity
//      WHERE legal_entity_id = ? AND daily_settlement_day = ?

// 5. 查询期货明细（按到期日）
futuresMovementQuantityMapper.getFuturesMovementToPositionMonitorReport(query)
// SQL: SELECT bs_flag, transaction_quantity, ...
//      FROM futures_movement_quantity fm
//      LEFT JOIN futures_contract fc ON fm.futures_contract_id = fc.id
//      WHERE legal_entity_id = ? AND DATE_FORMAT(fc.due_date, '%Y-%m-%d') = ?
```

---

## 四、计算公式详解

### 4.1 初始头寸（Initial Position）

**公式**：
```
初始头寸 = 前一交易日的最终头寸
```

**计算逻辑**：
```java
// 1. 获取前一交易日
CurvedateSessionCriteria criteria = new CurvedateSessionCriteria();
criteria.setDate(queryDate);
List<CurvedateSessionRes> result = myMapper.selectList(criteria);
LocalDate prevDate = result.get(0).getPrevDate();

// 2. 从历史表查询前一天的最终头寸
LambdaQueryWrapper<PositionMonitorHistory> queryWrapper = new LambdaQueryWrapper<>();
queryWrapper.eq(PositionMonitorHistory::getDate, prevDate);
queryWrapper.eq(PositionMonitorHistory::getLegalEntityId, legalEntityId);
queryWrapper.eq(PositionMonitorHistory::getBaseMetal, baseMetalId);
List<PositionMonitorHistory> histories = positionMonitorHistoryMapper.selectList(queryWrapper);

Double initialPosition = histories.isEmpty() ? 0.0 : histories.get(0).getFinalPosition();
```

**数据来源**：`position_monitor_history` 表  
**单位**：吨

---

### 4.2 现货头寸（Physical Movement）

**公式**：
```
现货头寸(KG) = 采购净重(CTRM) + 销售毛重(CRM) - 销售净重(CTRM) + 采购调整量(P) - 销售调整量(S)
现货头寸(吨) = 现货头寸(KG) / 1000
```

**计算逻辑**：
```java
// 文件：FixationAdjustmentServiceImpl.java (第1888-1923行)
Double calculateInItAndNowPosition(
        List<MetalBollettinoDto> initData, 
        List<FixationAdjustmentDto> fixationAdjustmentList) {
    
    // 1. 分离采购和销售数据
    List<MetalBollettinoDto> purchaseData = initData.stream()
            .filter(b -> "P".equalsIgnoreCase(b.getPsFlag()))
            .collect(Collectors.toList());
    List<MetalBollettinoDto> salesData = initData.stream()
            .filter(b -> "S".equalsIgnoreCase(b.getPsFlag()))
            .collect(Collectors.toList());
    
    // 2. 单位转换（KG）
    conversionToKgAndEUR(purchaseData, null, salesData, null, ...);
    
    // 3. 计算各分量
    // 采购净重（CTRM来源）
    Double payNetWeight = purchaseData.stream()
            .filter(s -> "CTRM".equalsIgnoreCase(s.getDataSource()))
            .mapToDouble(MetalBollettinoDto::getNetWeight)
            .sum();
    
    // 销售毛重（CRM来源）
    Double sellGrossWeight = salesData.stream()
            .filter(s -> "CRM".equalsIgnoreCase(s.getDataSource()))
            .mapToDouble(MetalBollettinoDto::getGrossWeight)
            .sum();
    
    // 销售净重（CTRM来源）
    Double sellNetWeight = salesData.stream()
            .filter(s -> "CTRM".equalsIgnoreCase(s.getDataSource()))
            .mapToDouble(MetalBollettinoDto::getNetWeight)
            .sum();
    
    // 采购调整量
    Double purchaseAdjust = fixationAdjustmentList.stream()
            .filter(b -> "P".equalsIgnoreCase(b.getPsFlag()))
            .mapToDouble(FixationAdjustmentDto::getQuantity)
            .sum();
    
    // 销售调整量
    Double salesAdjust = fixationAdjustmentList.stream()
            .filter(b -> "S".equalsIgnoreCase(b.getPsFlag()))
            .mapToDouble(FixationAdjustmentDto::getQuantity)
            .sum();
    
    // 4. 计算现货头寸
    Double physicalMovementKG = (purchaseAdjust + payNetWeight + sellGrossWeight) 
            - sellNetWeight - salesAdjust;
    
    return physicalMovementKG;
}

// 转换为吨
returnObj.setPhysicalMovement(physicalMovementKG / 1000.0);
```

**数据来源**：
- `movement_quantity` 表（采购净重、销售毛重、销售净重）
- `fixation_adjustment` 表（采购调整量、销售调整量）

**单位**：吨（计算过程为KG，最后除以1000转换）

---

### 4.3 LME交易头寸（LME Movement）

**公式**：
```
LME交易头寸(KG) = 买方交易数量(B) + 卖方交易数量(S)
LME交易头寸(吨) = LME交易头寸(KG) / 1000
```

**注意**：卖方交易数量为负数，因此相加即等效于"买方 - |卖方|"

**计算逻辑**：
```java
// 1. 按交易日筛选期货数据
List<FuturesMovementQuantityMatrialReport> futuresByTradingDay = 
        futuresMovementQuantityMapper.getFuturesMovementToPositionMonitorReport(query);

// 2. 分离买方和卖方
List<FuturesMovementQuantityMatrialReport> buyData = futuresByTradingDay.stream()
        .filter(b -> "B".equalsIgnoreCase(b.getBsFlag()))
        .filter(c -> baseMetalId.equals(c.getBaseMetalId()))
        .filter(e -> legalEntityId.equals(e.getLegalEntityId()))
        .collect(Collectors.toList());

List<FuturesMovementQuantityMatrialReport> sellData = futuresByTradingDay.stream()
        .filter(b -> "S".equalsIgnoreCase(b.getBsFlag()))
        .filter(c -> baseMetalId.equals(c.getBaseMetalId()))
        .filter(e -> legalEntityId.equals(e.getLegalEntityId()))
        .collect(Collectors.toList());

// 3. 单位转换（KG）
conversionToKgAndEUR(null, null, null, null, null, null, buyData, sellData, query);

// 4. 求和
Double buyQuantity = buyData.stream()
        .mapToDouble(FuturesMovementQuantityMatrialReport::getTransactionQuantity)
        .sum();
Double sellQuantity = sellData.stream()
        .mapToDouble(FuturesMovementQuantityMatrialReport::getTransactionQuantity)
        .sum();

Double lmeMovementKG = buyQuantity + sellQuantity; // sellQuantity是负数

// 5. 转换为吨
returnObj.setLmeMovement(lmeMovementKG / 1000.0);
```

**数据来源**：`futures_movement_quantity` 表（按交易日筛选）  
**单位**：吨

---

### 4.4 LME到期头寸（Expire LME）

**公式**（2024-07-16 变更后）：
```
LME到期头寸(KG) = |卖方交易数量| - |买方交易数量|
LME到期头寸(吨) = LME到期头寸(KG) / 1000
```

**注意**：此字段在 2024-07-16 从"买方 - 卖方"变更为"|卖方| - |买方|"

**计算逻辑**：
```java
// 1. 按到期日筛选期货数据
List<FuturesMovementQuantityMatrialReport> futuresByDueDate = 
        futuresMovementQuantityMapper.getFuturesMovementToPositionMonitorReport(query);

// 2. 分离买方和卖方
List<FuturesMovementQuantityMatrialReport> buyData = futuresByDueDate.stream()
        .filter(b -> "B".equalsIgnoreCase(b.getBsFlag()))
        .collect(Collectors.toList());

List<FuturesMovementQuantityMatrialReport> sellData = futuresByDueDate.stream()
        .filter(b -> "S".equalsIgnoreCase(b.getBsFlag()))
        .collect(Collectors.toList());

// 3. 单位转换（KG）
conversionToKgAndEUR(null, null, null, null, null, null, buyData, sellData, query);

// 4. 求和并取绝对值
Double buyQuantity = buyData.stream()
        .mapToDouble(FuturesMovementQuantityMatrialReport::getTransactionQuantity)
        .sum();
Double sellQuantity = sellData.stream()
        .mapToDouble(FuturesMovementQuantityMatrialReport::getTransactionQuantity)
        .sum();

Double expireLMEKG = Math.abs(sellQuantity) - Math.abs(buyQuantity);

// 5. 转换为吨
returnObj.setExprieLME(expireLMEKG / 1000.0);
```

**数据来源**：`futures_movement_quantity` 表（按到期日筛选）  
**单位**：吨

---

### 4.5 最终头寸（Final Position）

**公式**：
```
最终头寸 = 初始头寸 + 现货头寸 + LME交易头寸 + LME到期头寸
```

**计算逻辑**：
```java
Double finalPosition = returnObj.getInitialPosition() 
        + returnObj.getPhysicalMovement() 
        + returnObj.getLmeMovement() 
        + returnObj.getExprieLME();

returnObj.setFinalPosition(finalPosition);
```

**单位**：吨

---

### 4.6 子表汇总字段

**公式**：
```
initialPositionSum = SUM(所有机构的 initialPosition)
physicalPositionSum = SUM(所有机构的 physicalMovement)
lmeMovementSum = SUM(所有机构的 lmeMovement)
exprieLMESum = SUM(所有机构的 exprieLME)
finalPositionSum = SUM(所有机构的 finalPosition)
```

**计算逻辑**：
```java
// 按 baseMetalId 分组
Map<Long, List<PositionMonitorMainDto>> baseMetalGroupBy = 
        positionMonitorMainReport.stream()
            .collect(Collectors.groupingBy(a -> a.getBaseMetalId()));

// 对每个金属分组求和
for (List<PositionMonitorMainDto> group : baseMetalGroupBy.values()) {
    Double initialPositionSum = group.stream()
            .mapToDouble(PositionMonitorMainDto::getInitialPosition).sum();
    Double physicalPositionSum = group.stream()
            .mapToDouble(PositionMonitorMainDto::getPhysicalMovement).sum();
    Double lmeMovementSum = group.stream()
            .mapToDouble(PositionMonitorMainDto::getLmeMovement).sum();
    Double exprieLMESum = group.stream()
            .mapToDouble(PositionMonitorMainDto::getExprieLME).sum();
    Double finalPositionSum = group.stream()
            .mapToDouble(PositionMonitorMainDto::getFinalPosition).sum();
}
```

---

## 五、单位转换逻辑

### 5.1 重量单位转换（转KG）

```java
// 文件：FixationAdjustmentServiceImpl.java (第1308-1349行)
void convertWeightsInMultipleLists(...) {
    // 目标单位 ID = 83 (KG)
    
    // 1. movement_quantity 表的 gross_weight, net_weight
    for (MetalBollettinoDto dto : metalBollettinoDtos) {
        Double unitConversion = riskUnitConversionUtil.getUnitConversionNew(
                dto.getContractQuantityUnitId(),  // 源单位ID
                83L,                               // 目标：KG
                dto.getProductId());
        dto.setGrossWeight(dto.getGrossWeight() * unitConversion);
        dto.setNetWeight(dto.getNetWeight() * unitConversion);
    }
    
    // 2. futures_movement_quantity 表的 transaction_quantity
    for (FuturesMovementQuantityMatrialReport futures : futuresMovement) {
        Double unitConversion = riskUnitConversionUtil.getUnitConversionNew(
                futures.getQuantityUnitId(),  // 源单位ID
                83L,                           // 目标：KG
                futures.getProductId());
        futures.setTransactionQuantity(
                futures.getTransactionQuantity() * unitConversion);
    }
}
```

### 5.2 币种转换（转EUR）

```java
// 文件：FixationAdjustmentServiceImpl.java (第1352-1396行)
// 目标币种 ID = 2 (EUR)

// 1. movement_quantity 表的 settlement_price, purchase_price
for (MetalBollettinoDto dto : metalBollettinoDtos) {
    if (dto.getSettlementCurrencyId() == null || 
            dto.getSettlementCurrencyId().equals(2L)) {
        continue; // 已经是EUR，跳过
    }
    BigDecimal exchangeRate = riskCurveUtil.getExchangeRate(
            dto.getSettlementCurrencyId(),  // 源币种ID
            2L,                              // 目标：EUR
            date);                           // 日期
    dto.setSettlementPrice(dto.getSettlementPrice() * exchangeRate.doubleValue());
    dto.setPurchasePrice(dto.getPurchasePrice() * exchangeRate.doubleValue());
}

// 2. futures_movement_quantity 表的价格字段
for (FuturesMovementQuantityMatrialReport futures : futuresMovement) {
    if (futures.getCurrencyId() == null || futures.getCurrencyId().equals(2L)) {
        continue;
    }
    BigDecimal exchangeRate = riskCurveUtil.getExchangeRate(
            futures.getCurrencyId(), 2L, date);
    futures.setSettlementPrice(
            futures.getSettlementPrice() * exchangeRate.doubleValue());
}
```

---

## 六、字段映射关系

### 6.1 主表字段（PositionMonitorMainDto）

| 字段名 | Java属性 | 类型 | 说明 | 单位 |
|--------|----------|------|------|------|
| legalEntityName | legalEntityName | String | 业务机构名称 | - |
| legalEntityId | legalEntityId | Long | 业务机构ID | - |
| baseMetal | baseMetal | String | 基础金属名称 | - |
| baseMetalId | baseMetalId | Long | 基础金属ID | - |
| baseMetalDesc | baseMetalDesc | String | 金属成分描述 | - |
| initialPosition | initialPosition | Double | 初始头寸 | 吨 |
| physicalMovement | physicalMovement | Double | 现货头寸 | 吨 |
| lmeMovement | lmeMovement | Double | LME交易头寸 | 吨 |
| exprieLME | exprieLME | Double | LME到期头寸 | 吨 |
| finalPosition | finalPosition | Double | 最终头寸 | 吨 |

### 6.2 子表字段（PositionMonitorSubDto）

| 字段名 | Java属性 | 类型 | 说明 | 单位 |
|--------|----------|------|------|------|
| baseMetalSum | baseMetalSum | String | 基础金属名称 | - |
| baseMetalDesc | baseMetalDesc | String | 金属成分描述 | - |
| initialPositionSum | initialPositionSum | Double | 初始头寸汇总 | 吨 |
| physicalPositionSum | physicalPositionSum | Double | 现货头寸汇总 | 吨 |
| lmeMovementSum | lmeMovementSum | Double | LME交易头寸汇总 | 吨 |
| exprieLMESum | exprieLMESum | Double | LME到期头寸汇总 | 吨 |
| finalPositionSum | finalPositionSum | Double | 最终头寸汇总 | 吨 |

---

## 七、关键业务逻辑

### 7.1 分组维度合并

```java
// 文件：FixationAdjustmentServiceImpl.java (第1456-1483行)
// 以 movementQuantityGroup 为基础，依次合并其他数据源的分组

// 1. 合并期货交易日分组
for (MetalBollettinoGroup item : futuresMovementTradingGroup) {
    boolean exists = movementQuantityGroup.stream()
            .anyMatch(g -> g.getGroupKeyName().equalsIgnoreCase(item.getGroupKeyName()));
    if (!exists) {
        movementQuantityGroup.add(item);
    }
}

// 2. 合并期货到期日分组
for (MetalBollettinoGroup item : futuresMovementDueDateGroup) {
    boolean exists = movementQuantityGroup.stream()
            .anyMatch(g -> g.getGroupKeyName().equalsIgnoreCase(item.getGroupKeyName()));
    if (!exists) {
        movementQuantityGroup.add(item);
    }
}

// 3. 合并历史头寸分组
for (MetalBollettinoGroup item : positionMonitorHistoryGroup) {
    boolean exists = movementQuantityGroup.stream()
            .anyMatch(g -> g.getGroupKeyName().equalsIgnoreCase(item.getGroupKeyName()));
    if (!exists) {
        movementQuantityGroup.add(item);
    }
}

// 4. 合并现货数量调整分组
for (MetalBollettinoGroup item : fixationAdjustGroup) {
    boolean exists = movementQuantityGroup.stream()
            .anyMatch(g -> g.getGroupKeyName().equalsIgnoreCase(item.getGroupKeyName()));
    if (!exists) {
        movementQuantityGroup.add(item);
    }
}
```

**说明**：groupKeyName = `legalEntityId_productSpecificationId`，确保所有数据源中的机构+金属组合都被包含。

### 7.2 allBaseMetal 参数处理

```java
// 文件：FixationAdjustmentServiceImpl.java (第1430-1434行)
if (queryDto.getAllBaseMetal()) {
    // 获取所有金属成分
    List<ProductSpecificationRes> productSpecification = 
            productSpecificationMapper.getProductSpecification();
    
    // 过滤掉铜（AZZ），保留其他金属
    queryDto.setBaseMetalIds(productSpecification.stream()
            .filter(s -> !"AZZ".equalsIgnoreCase(s.getName()))
            .map(ProductSpecificationRes::getId)
            .collect(Collectors.toList()));
}
```

**说明**：当 `allBaseMetal = true` 时，汇总所有非铜金属的头寸。

### 7.3 日期处理

```java
// 获取前一交易日
CurvedateSessionCriteria criteria = new CurvedateSessionCriteria();
criteria.setDate(queryDate);
List<CurvedateSessionRes> result = myMapper.selectList(criteria);
LocalDate prevDate = result.isEmpty() ? queryDate : result.get(0).getPrevDate();
```

---

## 八、数据流图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Controller Layer                              │
│  ReportController.getPositionMonitorSubReport()                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                 │
│  FixationAdjustmentServiceImpl.getPositionMonitorSubReport()    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
              ┌───────────────────────────────┐
              │ 调用主表方法获取明细数据         │
              │ getPositionMonitorMainReport() │
              └───────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         获取分组维度（5个数据源）          │
        ├─────────────────────────────────────────┤
        │ 1. movement_quantity (现货计价量)         │
        │ 2. futures_movement_quantity (期货交易日) │
        │ 3. futures_movement_quantity (期货到期日) │
        │ 4. position_monitor_history (历史头寸)    │
        │ 5. fixation_adjustment (现货数量调整)     │
        └─────────────────────────────────────────┘
                              ↓
              ┌───────────────────────────────┐
              │ 合并分组（按groupKeyName去重）   │
              └───────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         查询明细数据                      │
        ├─────────────────────────────────────────┤
        │ • 现货明细 (movement_quantity)           │
        │ • 历史最终头寸 (position_monitor_history)│
        │ • 调整明细 (fixation_adjustment)         │
        │ • 期货明细-交易日 (futures_movement_     │
        │   quantity)                              │
        │ • 期货明细-到期日 (futures_movement_     │
        │   quantity + futures_contract)           │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         单位转换                          │
        ├─────────────────────────────────────────┤
        │ • 重量 → KG (目标单位ID=83)              │
        │ • 币种 → EUR (目标币种ID=2)              │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         计算5个头寸字段（主表）           │
        ├─────────────────────────────────────────┤
        │ 1. 初始头寸 = 前一天最终头寸              │
        │ 2. 现货头寸 = 采购净重 + 销售毛重         │
        │           - 销售净重 + 调整量             │
        │ 3. LME交易头寸 = 买方 + 卖方 (按交易日)   │
        │ 4. LME到期头寸 = |卖方| - |买方|         │
        │           (按到期日)                      │
        │ 5. 最终头寸 = 初始 + 现货 + LME交易       │
        │           + LME到期                       │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         按baseMetalId分组汇总（子表）     │
        ├─────────────────────────────────────────┤
        │ • initialPositionSum = SUM(initialPos)   │
        │ • physicalPositionSum = SUM(physicalMov) │
        │ • lmeMovementSum = SUM(lmeMovement)      │
        │ • exprieLMESum = SUM(exprieLME)          │
        │ • finalPositionSum = SUM(finalPosition)  │
        └─────────────────────────────────────────┘
                              ↓
              ┌───────────────────────────────┐
              │ 返回子表数据                    │
              │ List<PositionMonitorSubDto>    │
              └───────────────────────────────┘
```

---

## 九、关键代码位置索引

| 功能 | 文件 | 行号 |
|------|------|------|
| Controller入口 | ReportController.java | 1128-1132 |
| Service方法 | FixationAdjustmentServiceImpl.java | 1928-1962 |
| 主表方法 | FixationAdjustmentServiceImpl.java | 1414-1634 |
| 现货头寸计算 | FixationAdjustmentServiceImpl.java | 1888-1923 |
| 单位转换 | FixationAdjustmentServiceImpl.java | 1297-1396 |
| DTO定义 | PositionMonitorMainDto.java | 全文 |
| DTO定义 | PositionMonitorSubDto.java | 全文 |
| Mapper XML | MovementQuantityMapper.xml | 357-380 |
| Mapper XML | FuturesMovementQuantityMapper.xml | 543-670 |
| Mapper XML | PositionMonitorHistoryMapper.xml | getBollettinoGroupList |
| Mapper XML | FixationAdjustmentMapper.xml | 588-803 |

---

## 十、总结

### 10.1 核心特点

1. **只有数量，没有价格和金额**：Position Monitor 是头寸统计报表，不涉及金额计算
2. **子表是主表的聚合视图**：按基础金属维度汇总所有机构的头寸
3. **5个数据源合并**：确保所有机构+金属组合都被包含
4. **单位统一**：重量转KG，币种转EUR，最终头寸以吨为单位展示

### 10.2 计算公式汇总

| 字段 | 公式 | 单位 |
|------|------|------|
| 初始头寸 | = 前一天最终头寸 | 吨 |
| 现货头寸 | = (采购净重 + 销售毛重 - 销售净重 + 采购调整 - 销售调整) / 1000 | 吨 |
| LME交易头寸 | = (买方交易数量 + 卖方交易数量) / 1000 | 吨 |
| LME到期头寸 | = (|卖方交易数量| - |买方交易数量|) / 1000 | 吨 |
| 最终头寸 | = 初始 + 现货 + LME交易 + LME到期 | 吨 |

### 10.3 数据来源表汇总

| 表名 | 用途 |
|------|------|
| movement_quantity | 现货计价量（采购/销售净重、毛重） |
| futures_movement_quantity | 期货计价量（交易数量） |
| position_monitor_history | 历史头寸（前一天最终头寸） |
| fixation_adjustment | 现货数量调整（调整量） |
| futures_contract | 期货合约（到期日） |
| curvedate_session | 交易日日历（前一交易日） |
| product_specification | 金属成分定义 |
