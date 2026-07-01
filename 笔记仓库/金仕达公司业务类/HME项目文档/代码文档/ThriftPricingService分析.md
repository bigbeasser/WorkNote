---
type: 代码文档
---

# ThriftPricingService 类分析

> [!info] 文档信息
> - **生成日期**：2026-07-01
> - **源码位置**：`bcadmin-rpc/src/main/java/com/resrun/thrift/Implements/ThriftPricingService.java`
> - **关联文档**：[[Thrift跨语言调用链路说明]] · [[定价明细价格字段计算逻辑文档]] · [[movement-price-lifecycle]] · [[计价公式变更与算价链路分析]]

---

## 一、类的作用

`ThriftPricingService` 是一个 **Thrift RPC 服务端点**，注册名为 `API.Pricing`，它的核心职责是：

> **为 Python 计价公式脚本提供 Java 侧的核心定价计算能力**

它是一个"桥梁"——Python 公式脚本在运行过程中，需要查询远期曲线价格、做币种/单位转换、按计价类型估值时，通过 Thrift RPC 反向调用这个 Java 类来获取结果。

### 1.1 类定义

```java
@Slf4j
@Component(value = "API.Pricing")
public class ThriftPricingService {
```

- `@Component(value = "API.Pricing")`：注册为 Spring Bean，名称为 `API.Pricing`
- `ThriftServiceManagerProcessor` 通过 `SpringContextHolder.getBean("API.Pricing")` 动态获取该 Bean
- Python 侧通过 `_c.execute("API.Pricing", "fetch", {...})` 调用

### 1.2 注入的依赖

| 依赖 | 类型 | 用途 |
|---|---|---|
| `_a159` | `RiskValuationUtil` | 核心估值工具（均价/触发/特定合约估值 + 币种转换） |
| `_pythonPyPathService` | `PythonPyPathService` | 获取 Python 脚本文件路径 |
| `_riskUtil` | `RiskUtil` | 获取曲线日期（curveDate） |
| `productSpecificationMapper` | `ProductSpecificationMapper` | 查询产品规格 |
| `myProductSpecificationMapper` | `MyProductSpecificationMapper` | 查询有效产品规格 |
| `forwardCurveMapper` | `ForwardCurveMapper` | 查询远期曲线元数据 |
| `forwardContractMapper` | `ForwardContractMapper` | 查询远期合约 |
| `specificationTypeMapper` | `SpecificationTypeMapper` | 查询规格类型 |
| `riskUnitConversionUtil` | `RiskUnitConversionUtil` | 单位转换工具 |

---

## 二、调用关系全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        上游调用方                                │
│                                                                 │
│  Python utils.py                                                │
│  ├── valueIndex()      → _c.execute("API.Pricing","fetch",...)  │
│  ├── valueIndexNew()   → _c.execute("API.Pricing","fetch",...)  │
│  ├── valueIndex()      → _c.execute("API.Pricing",              │
│  │                       "getPricingRangeRulePyPath",...)       │
│  └── valueIndexNew()   → _c.execute("API.Pricing",              │
│                          "getPricingRangeRulePyPath",...)       │
│                                                                 │
│  触发链路:                                                       │
│  前端 → PricingController → PricingServiceImpl                  │
│       → PythonUtils.exec_python → Python脚本 → utils.py         │
│       → ctrm_thrift_client.execute → ThriftServer(9000)         │
│       → ThriftServiceManagerProcessor                           │
│       → SpringContextHolder.getBean("API.Pricing")              │
│       → 反射调用 fetch / getPricingRangeRulePyPath               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ThriftPricingService                           │
│                                                                 │
│  fetch() ──────────────┐                                        │
│    │                   │                                        │
│    ├── fetchImpl()     │  按 PricingType 分支:                   │
│    │   ├── TRIGGER     │  → _a159.triggerValuation()            │
│    │   ├── SPEC_MONTH  │  → _a159.specificContractValuation()   │
│    │   └── AVERAGE     │  → _a159.averageValuation()            │
│    │                   │                                        │
│    ├── 币种转换 ────────┤  → _a159.getPriceAtTargetCurrency()    │
│    ├── 单位转换 ────────┤  → riskUnitConversionUtil              │
│    └── 成分系数 ────────┤  → ProductSpecification 含量/收率       │
│                         │                                        │
│  getPricingRangeRulePyPath() → PythonPyPathService              │
│  getEventTypePyPath()        → PythonPyPathService              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      下游依赖                                    │
│                                                                 │
│  RiskValuationUtil (_a159)                                      │
│  ├── averageValuation()          → 批量查 ForwardPrice 取均值     │
│  ├── triggerValuation()          → 回溯查最近 ForwardPrice        │
│  ├── specificContractValuation() → 委托给 averageValuation       │
│  └── getPriceAtTargetCurrency()  → 币种×汇率 ÷ 单位转换          │
│                                                                 │
│  数据库表:                                                       │
│  ├── ForwardContract      (远期合约)                             │
│  ├── ForwardPrice         (远期价格曲线)                          │
│  ├── ForwardCurve         (远期曲线元数据: 币种/单位)              │
│  ├── ProductSpecification (产品成分: 含量系数/收率)               │
│  └── SpecificationType    (规格类型: content/proportion)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、三个方法详解

### 3.1 fetch() — 定价主入口

这是核心方法，计算 **"某个产品在某个计价区间内的成分加权价格"**。

#### 处理步骤

**Step 1: 获取产品成分（ProductSpecification）**

```
按 productId 查询有效成分
→ 过滤 category="Fixation"（固定成分类别）
→ 如果 Fixation 为空且 factoryCode 不为空 → 按 factoryCode 过滤
→ 获取对应的 SpecificationType（规格类型）
→ 识别 Yield（收率）成分
```

**Step 2: 按成分逐个计算价格（核心循环）**

对每个 `pricingOrNot=true` 的成分：

| 步骤 | 计算内容 | 说明 |
|---|---|---|
| ① | 查远期合约 | `ForwardContractMapper.selectByCurveIdAndMarker(curveId, marker)` |
| ② | 按计价类型估值 | 调用 `fetchImpl()` → TRIGGER/SPECIFICATION_MONTH/AVERAGE 三种分支 |
| ③ | 取平均市场价 | `pds.stream().mapToDouble(forwardPrice.marketPriceValue).average()` |
| ④ | 获取源币种/单位 | 从 `ForwardCurve` 获取 `currencyId` 和 `unitId` |
| ⑤ | 币种+单位转换 | `getPriceAtTargetCurrency(sourceCurrency → targetCurrency, sourceUnit → targetUnit)` |
| ⑥ | 乘以规格系数 | 按规格类型分支计算（见下表） |
| ⑦ | 乘以收率 | `convertedValue × yield`（如果有 Yield 成分） |
| ⑧ | 设置金属权重因子 | `metalWeightFactor` 写入每个定价明细 |

**规格系数计算规则：**

| SpecificationType.type | convertedValue 计算 | metalWeightFactor 计算 |
|---|---|---|
| `content`（含量） | `price × coefficient × unitConversion(分子单位, 分母单位)` | `factor × coefficient × unitConversion(分子单位, 分母单位)` |
| `proportion`（比例） | `price × coefficient` | `factor × coefficient × unitConversion(目标单位, 源单位)` |

**Step 3: 返回结果**

返回 JSON 格式的 `List<Tuple5>`：

```json
[
  {
    "item1": "原始市场价 (sourcePrice)",
    "item2": "源币种ID (sourceCurrencyId)",
    "item3": "源单位ID (sourceUnitId)",
    "item4": "转换后价格 (convertedValue, 含系数×收率)",
    "item5": "每日定价明细列表 List<a117>"
  }
]
```

#### 代码流程图

```
fetch(executeArgs)
  │
  ├── 解析参数 → ThriftPricingModel
  │
  ├── 查询产品成分 compositions
  │     ├── myProductSpecificationMapper.selectValidProductSpecification(productId)
  │     ├── 过滤 category="Fixation"
  │     └── 识别 yieldComposition (SpecificationType.name="Yield")
  │
  ├── 查询规格类型 specificationTypes
  │
  └── 对每个 pricingOrNot=true 的成分:
        │
        ├── 查 ForwardContract (by curveId + marker)
        │
        ├── 调用 fetchImpl(model) → 获取定价明细 pds
        │
        ├── 计算平均市场价 price = avg(pds.forwardPrice.marketPriceValue)
        │
        ├── 获取源币种/单位 (from ForwardCurve)
        │
        ├── 币种+单位转换 → convertedValue
        │     getPriceAtTargetCurrency(marketPrice, forexMarketId,
        │       sourceCurrency, targetCurrency, sourceUnit, targetUnit,
        │       date, date, productId)
        │
        ├── 应用规格系数 (content / proportion)
        │
        ├── 应用收率 (yieldComposition)
        │
        ├── 设置 metalWeightFactor 到每个 pd
        │
        └── 收集到 prices 列表
```

---

### 3.2 fetchImpl() — 按计价类型分支估值

`fetchImpl()` 是 `fetch()` 的内部方法，根据 `PricingType` 分发到不同的估值策略：

```
fetchImpl(model)
  │
  ├── 构建 a103 averageModel
  │     ├── pricingBegDate = model.beginDate
  │     ├── pricingEndDate = model.endDate
  │     └── curveDate = model.curveDate (若空则取 _riskUtil.getCurveDate())
  │
  ├── PricingType == TRIGGER ?
  │     │
  │     └── YES → 构建 a109 triggerModel
  │               ├── triggerLastTriggerDate = model.lastTriggerDate
  │               └── return _a159.triggerValuation(triggerModel)
  │                     → 回溯查最近一条有效 ForwardPrice
  │                     → 返回单条 a117
  │
  ├── PricingType == SPECIFICATION_MONTH ?
  │     │
  │     └── YES → 构建 a108 specificContractModel
  │               └── return _a159.specificContractValuation(model)
  │                     → 实际委托给 averageValuation()
  │
  └── ELSE (默认 AVERAGE)
        │
        └── return _a159.averageValuation(averageModel)
              → 批量查区间内所有 ForwardPrice
              → 跳过节假日和未来日期
              → 返回 List<a117>
```

#### 三种估值策略对比

| 策略 | PricingType | 输入模型 | 返回 | 核心逻辑 |
|---|---|---|---|---|
| 触发计价 | `TRIGGER` | `a109` | 单条 `a117` | 从 curveDate 向前回溯，找最近一条有效 ForwardPrice |
| 特定合约 | `SPECIFICATION_MONTH` | `a108` | `List<a117>` | 委托给 averageValuation（本质相同） |
| 平均计价 | 其他（默认） | `a103` | `List<a117>` | 遍历定价区间每一天，查 ForwardPrice，跳过节假日 |

---

### 3.3 getPricingRangeRulePyPath() — 获取区间规则脚本路径

```java
public String getPricingRangeRulePyPath(String executeArgs) {
    Long rangeRuleId = JSONObject.parseObject(executeArgs, Long.class);
    return _pythonPyPathService.getPricingRangeRulePyFilePathById(rangeRuleId);
}
```

- **调用方**：Python `utils.py` 中的 `valueIndex()` 和 `valueIndexNew()`
- **用途**：获取定价区间规则（PricingRangeRule）对应的 Python 脚本文件路径
- **缓存**：Python 侧使用 `getAndSetCache()` 缓存结果，避免重复 Thrift 调用

### 3.4 getEventTypePyPath() — 获取事件类型脚本路径

```java
public String getEventTypePyPath(String executeArgs) {
    Long eventTypeId = JSONObject.parseObject(executeArgs, Long.class);
    return _pythonPyPathService.getEventTypePyFilePathById(eventTypeId);
}
```

- **调用方**：当前代码中**未找到**调用方（可能是预留接口或已废弃）
- **用途**：获取事件类型（EventType）对应的 Python 脚本文件路径

---

## 四、RiskValuationUtil 核心估值方法

`ThriftPricingService` 的核心计算全部委托给 `RiskValuationUtil`（变量名 `_a159`），以下是四个关键方法的分析：

### 4.1 averageValuation(a103) — 平均计价

```
输入: a103 (pricingBegDate, pricingEndDate, forwardContractId, forwardCurveId, marker)
输出: List<a117>

逻辑:
1. 查 ForwardContract → 获取 forwardCurveId
2. 批量查定价区间内的 ForwardPrice 列表
3. 获取节假日列表
4. 遍历每一天 (begDate → endDate):
   ├── 日期 > curveDate → 跳过（不能用未来数据）
   ├── 是节假日 → 跳过
   ├── 能查到 ForwardPrice → 复制价格数据
   ├── 当天 = curveDate 且无价格 → 跳过
   └── 其他（无价格）→ 构建零值 ForwardPrice
5. 构建 a117 对象列表
```

### 4.2 triggerValuation(a109) — 触发计价

```
输入: a109 (forwardContractId, triggerLastTriggerDate, beginDate, endDate)
输出: a117 (单条)

逻辑:
1. 查 ForwardContract
2. 从 curveDate 向前回溯，逐日查找最近有效 ForwardPrice
   └── 条件: date + forwardContractId + marketPriceType + (session=0 或 null)
   └── 找到即 break
3. 确定 endDate:
   ├── endDate 为 null → 用 triggerLastTriggerDate
   └── endDate > lastTradingDay → 截断
4. 未找到 → 构建零值 ForwardPrice
5. Delta 调整: marketPriceValue += delta (若非零)
6. 构建 a117
```

### 4.3 specificContractValuation(a108) — 特定合约计价

```java
public List<a117> specificContractValuation(a108 a1548) {
    return averageValuation(a1548);  // 直接委托
}
```

本质是 `averageValuation` 的别名，`a108` 继承自 `a103` 且无新增字段。

### 4.4 getPriceAtTargetCurrency() — 币种+单位转换

```
输入: 原始价格, 远期合约ID, 源币种, 目标币种, 源单位, 目标单位, 曲线日期, 定价日期, 产品ID
输出: double (转换后价格)

逻辑:
1. 源币种 == 目标币种 且 源单位 == 目标单位 → 直接返回
2. 货币转换率:
   ├── 源 ≠ 目标 → getCurrencyConversion(合约ID, 源币, 目标币, 曲线日, 定价日, SETTLEMENT_PRICE)
   └── 相同 → 1.0
3. 单位转换率:
   ├── 源 ≠ 目标 → getUnitConversion(源单位, 目标单位, 合约ID)
   └── 相同 → 1.0
4. 最终价格 = 原价 × 货币转换率 ÷ 单位转换率
```

---

## 五、模型类字段说明

### 5.1 ThriftPricingModel（输入参数）

`fetch()` 方法接收的 JSON 参数反序列化为 `ThriftPricingModel`，主要字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `productId` | Long | 产品 ID |
| `marker` | String | 远期合约标记 |
| `beginDate` | LocalDate | 定价开始日期 |
| `endDate` | LocalDate | 定价结束日期 |
| `curveDate` | LocalDate | 曲线基准日期（可空） |
| `pricingType` | PricingType | 计价类型（TRIGGER/SPECIFICATION_MONTH/AVERAGE） |
| `lastTriggerDate` | LocalDate | 最后触发日期 |
| `forexMarketId` | Long | 外汇市场 ID |
| `targetCurrencyId` | Long | 目标币种 ID |
| `targetUnitId` | Long | 目标单位 ID |
| `factoryCode` | String | 工厂代码（成分过滤备用） |
| `forwardContractId` | Long | 远期合约 ID（内部设置） |

### 5.2 a117（计价结果）

```java
public class a117 {
    ForwardPrice forwardPrice;     // 远期价格（含 marketPriceValue）
    Long forwardCurveId;           // 远期曲线 ID
    LocalDate fixingDate;          // 定价基准日
    LocalDate curveDate;           // 曲线基准日期
    LocalDate lastTriggerDate;     // 最后触发日期
    Boolean calculateFixFlag;      // 是否参与固定标志计算
    LocalDate pricingStartDate;    // 定价区间开始日期
    LocalDate pricingEndDate;      // 定价区间结束日期
    Boolean isAverage;             // 是否为平均计价
    Double metalWeightFactor;      // 金属权重因子（系数×收率的累积值）
}
```

### 5.3 模型继承关系

```
a106（基类，含 delta 字段）
  └── a107（mtiCurveId, mtiDate, forwardContractId, marketPriceType）
        ├── a103（pricingEndDate, pricingBegDate, forwardCurveId, marker）
        │     └── a108（空实现，用于 SPECIFICATION_MONTH）
        └── a109（forwardContractId, triggerLastTriggerDate, beginDate, endDate, marker）
```

---

## 六、Python 侧调用详情

### 6.1 valueIndex()（旧版本）

```python
# 文件: utils.py, 函数: valueIndex(index, context), 第158行

# 先获取区间规则 Python 路径（带缓存）
path = getAndSetCache(
    "getpricingrangerulepypath_" + str(rangeRuleId),
    lambda p: _c.execute("API.Pricing", "getPricingRangeRulePyPath", p),
    rangeRuleId
)

# 按计价类型调用 fetch
if pricingType == 'Triggered' and statusType == 'new':
    priceList = _c.execute("API.Pricing", "fetch", {
        'forwardCurveId': ...,
        'beginDate': ..., 'endDate': ...,
        'delta': indexDelta,
        'curveDate': '',
        'pricingType': pricingType,
        'lastTriggerDate': lastTriggerDate
    })
else:
    priceList = _c.execute("API.Pricing", "fetch", {
        'settlementCurveId': ...,
        'beginDate': ..., 'endDate': ...,
        ...
    })
```

### 6.2 valueIndexNew()（新版本）

```python
# 文件: utils.py, 函数: valueIndexNew(index, context), 第363行

# 新版本增加了更多参数
priceList = _c.execute("API.Pricing", "fetch", {
    'forwardCurveId': ...,
    'beginDate': ..., 'endDate': ...,
    'delta': index_delta,
    'curveDate': '',
    'forwardContractId': forward_contract_id,   # ★ 新增
    'pricingType': pricing_type,
    'lastTriggerDate': lastTriggerDate,
    'marketPriceType': market_price_type,        # ★ 新增
    'forexMarketId': ...,                        # ★ 新增
    'productId': ...,                            # ★ 新增
    'targetCurrencyId': ...,                     # ★ 新增
    'targetUnitId': ...,                         # ★ 新增
    'marker': ...,                               # ★ 新增
})
```

> [!note] 新旧版本差异
> 新版本 `valueIndexNew` 增加了 `forwardContractId`、`productId`、`targetCurrencyId`、`targetUnitId`、`marker` 等参数，
> 使得 `fetch()` 方法可以进行更精确的币种转换和成分过滤，而旧版本这些参数可能在 Java 侧使用默认值。

---

## 七、与文档体系的关联

### 7.1 在定价链路中的位置

```
┌──────────────────────────────────────────────────────────────┐
│                    完整定价计算链路                             │
│                                                              │
│  ① 用户操作 → PricingController                              │
│  ② PricingServiceImpl → 找到 pricingFormulaId               │
│  ③ PythonPyPathService → 获取 Python 脚本路径                │
│  ④ PythonUtils.exec_python → 执行 Python 公式                │
│  ⑤ Python 公式 → utils.py → valueIndex/valueIndexNew        │
│  ⑥ ★ ThriftPricingService.fetch() ★ ← 本类所在位置          │
│  ⑦ RiskValuationUtil → 查 ForwardPrice → 估值               │
│  ⑧ 返回 JSON → Python 继续公式计算                            │
│  ⑨ Python 输出 → Java 接收                                   │
│  ⑩ MovementPriceServiceImpl.fillPriceInfo() → 写入 MP 表    │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 与相关文档的关联

| 文档 | 关联关系 |
|---|---|
| [[Thrift跨语言调用链路说明]] | 完整描述了 `API.Pricing` 的调用链路：Python → Thrift → Java |
| [[定价明细价格字段计算逻辑文档]] | `fetch()` 计算的 `convertedValue` 最终被 `fillPriceInfo()` 消费作为 `basePrice` |
| [[movement-price-lifecycle]] | `fetch()` 参与的是 MovementPrice 生命周期中"价格计算"环节的上游 |
| [[计价公式变更与算价链路分析]] | Python 计价公式通过 `valueIndex/valueIndexNew` 调用 `fetch()` |
| [[点价单和定价明细的计算]] | 点价单提交时 `fillPriceInfo()` 中 `onSpotPrice=0` 分支会触发远期曲线计算，与 `fetch()` 逻辑平行 |
| [[pricing-formula-developer-guide]] | 计价公式开发者指南，Python 脚本中调用 `fetch()` 的上下文 |

### 7.3 fetch() 输出如何被消费

```
ThriftPricingService.fetch()
  │
  ▼ 返回 JSON (List<Tuple5>)
  │
Python 公式脚本
  │ 继续计算: 区间规则、升贴水、附加费等
  │
  ▼ 输出结果
  │
Java PricingServiceImpl
  │ 解析 Python 输出
  │ 写入 PriceTriggering 表
  │
  ▼
MovementPriceServiceImpl.fillPriceInfo()
  │ 从 PriceTriggering 读取 basePrice, spread 等
  │ 计算 settlementNetPrice, scorporoPrice, additionalPrice
  │
  ▼ 写入 MovementPrice 表
```

---

## 八、涉及的数据库表

| 表名 | 用途 | 查询方式 |
|---|---|---|
| `product_specification` | 产品成分（含量系数、收率） | `selectValidProductSpecification(productId)` |
| `specification_type` | 规格类型（content/proportion、系数） | `selectByExample(ids)` |
| `forward_contract` | 远期合约（曲线ID、最后交易日） | `selectByCurveIdAndMarker(curveId, marker)` |
| `forward_curve` | 远期曲线元数据（币种、单位） | `selectById(curveId)` |
| `forward_price` | 远期价格（市场价值、日期、场次） | 通过 `RiskCurveUtil.listForwardPrice()` 或 `ForwardPriceMapper.selectOne()` |

---

## 九、总结

> [!summary] 核心要点
>
> `ThriftPricingService` 本身**不直接写入任何数据库表**，它是一个**纯计算服务**：
>
> - **输入**：产品ID、计价区间、计价类型、目标币种/单位
> - **计算**：查远期曲线 → 按成分估值 → 币种/单位转换 → 系数/收率加权
> - **输出**：JSON 格式的成分价格列表，返回给 Python 公式脚本
> - **定位**：Java 核心计算能力的 Thrift RPC 暴露层，是 Python 公式引擎的"计算后端"
>
> 它在整个定价链路中处于 **第⑥步**（见 7.1 节），上游是 Python 公式脚本（通过 Thrift RPC 调用），
> 下游是 `MovementPriceServiceImpl.fillPriceInfo()`（消费计算结果写入 MovementPrice 表）。
