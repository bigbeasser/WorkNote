# 订单保存 → 现金流生成 · 计价公式使用全链路

> 追踪从订单保存触发现金流引擎，到计价公式被解析、拆分、计算的全过程

---

## 一、触发链路

```
订单保存/提交
  │
  ▼
PhysicalDealsServiceImpl.submit()                    [L5087]
  │
  ├── 构建 CashModelQueryCriteria
  │     linkId = physicalDealId
  │     headerType = "PO"(采购) 或 "SO"(销售)
  │
  ▼
CashFlowProjectionServiceImpl.generateCashFlowModel() [L1275]
  │
  ├── riskUtil.calculateModelCategory()               → 确定模型类别 = PHYSICAL
  │
  ▼
a155.a1208(inputModel)                                [L1346]
  │
  ▼
a156.a1208()  ── 引擎调度器（策略模式）                 [L77-123]
  │
  ├── 匹配 PHYSICAL 类别 → a10 引擎
  │
  ▼
a10.a4()  ── 实货现金流引擎                            [L30-54]
  │
  ├── 按优先级执行子引擎流水线 ↓
```

---

## 二、引擎流水线

`a10` 引擎按固定优先级顺序执行子引擎：

| 优先级 | 引擎 | 类 | 职责 |
|---|---|---|---|
| 0 | HeaderValues | `a66` | 创建 `CashflowModelHeaderValues`（每个收发行创建 SETTLEMENT + MTM 两条） |
| 10 | ModelValues | `a67` | 创建 `CashflowModelValues`（设置 quantity、spread、币种、税率） |
| 20 | MTI | `a64` | Mark-to-market 指数计算 |
| **30** | **Pricing** | **`a65`** | **核心：根据计价类型计算 settlementPrice** |
| 31 | PricingHeader | `a47` | 定价头部信息 |
| **32** | **PricingModel** | **`a49`** | **公式表达式求值（JS 引擎）** |
| 40-41 | Tax | `a68/a69` | 税费现金流行 |
| 99 | Clear | `a63` | 清理过期记录 |
| 100-199 | Trigger | - | 点价触发场景 |

---

## 三、a65 PricingEngine — 计价类型分支

**文件**: `bcadmin-cashflowmodel/src/main/java/com/resrun/cash/d/a65.java`

a65 根据合同行的 `pricingType` 字段（不是 abbreviation，是 `PricingType` 枚举）做四路分支：

```java
// L71-85: 固定价
if (pricingType == PricingType.FIXED && modelLevel == PRODUCT_LINE) {
    pricingStatus = FIXED;
    settlementPrice = line.getPrice();              // 直接取合同行价格
    settlementNetPrice = settlementPrice + spread;   // 叠加升贴水
}

// L86-89: 均价
else if (pricingType == PricingType.AVERAGE && modelLevel == PRODUCT_LINE) {
    a729(context, result, line, model);
    // → 调用 a153.a1492() 从远期曲线计算期间均价
}

// L90-93: 点价
else if (pricingType == PricingType.TRIGGER && modelLevel == PRODUCT_LINE) {
    a728(result, line, model);
    // → 调用 a153.a1498() 从点价触发记录取价
}

// L94-101: 公式（组合计价）
else if (pricingType == PricingType.FORMULA && modelLevel == PRODUCT_LINE) {
    a724(context, result, dealId, line, model);
    // → 调用 a153.a1485() → executePy() → Python 公式引擎
}
```

### 关键理解：`pricingType` vs `abbreviation`

| 概念 | 来源 | 说明 |
|---|---|---|
| `pricingType` | `PhysicalDealLine.pricingType` | 枚举值：FIXED / AVERAGE / TRIGGER / FORMULA。决定 a65 的分支 |
| `abbreviation` | `pricing_formula_id_parameters` JSON | 字符串：BasicFixedPrice / BasicTriggeredPrice / BasicAveragePrice 等。决定具体参数解析 |

**对应关系**：

| pricingType | 对应 abbreviation | 触发方式 |
|---|---|---|
| `FIXED` | `BasicFixedPrice` | 合同行价格已确定 |
| `AVERAGE` | `BasicAveragePrice` | 需要按期间均价计算 |
| `TRIGGER` | `BasicTriggeredPrice` | 需要点价触发 |
| `FORMULA` | 组合公式（含多个 abbreviation） | 调用 Python 引擎 |

> **重要**：当合同行只选了一个基础价公式时，`pricingType` 直接映射。
> 当选择了组合公式（如 BasicFixedPrice + BasicFixedPremium + ProcessingFee），
> `pricingType = FORMULA`，走 Python 引擎路径。

---

## 四、FORMULA 路径 — Python 公式引擎

当 `pricingType = FORMULA` 时，调用链：

```
a65.a724()
  → a153.a1485(pricingFormulaId, pricingFormulaIdParameters)   [L170-233]
    → a153.executePy()                                          [L57-168]
      → RiskValuationUtil.calculateCompositionPrice()           [L67-102]
        → PythonUtils.exec_python(pyFilePath, formulaParams, context)
```

### Python 引擎做什么

1. 读取 `pricing_formulas.py_file_path`（每个公式有一个 Python 脚本）
2. 传入 `pricingFormulaIdParameters` JSON 和上下文数据（合同行、汇率、曲线等）
3. Python 脚本根据 JSON 中的 abbreviation 组合计算价格
4. 返回 `a119` 结果对象：

```java
class a119 {
    Double finalPrice;       // 最终价格（base + spread + other）
    Double basicPrice;       // 基础价
    Double spread;           // 升贴水
    Double otherCostPrice;   // 其他费用
    String pricingType;      // 定价类型
    List<PriceDetail> priceDetail;  // 按日期的定价明细
}
```

### a153 拿到结果后设置现金流值

```java
// a153.java L214-232
model.setSpread(result.getSpread());
model.setOtherCostPrice(result.getOtherCostPrice());
model.setSettlementPrice(result.getFinalPrice() - result.getSpread() - result.getOtherCostPrice());
model.setSettlementNetPrice(round(finalPrice, pricingRoundingDigits));
```

---

## 五、a49 PricingModel — 公式表达式求值

**文件**: `bcadmin-cashflowmodel/src/main/java/com/resrun/cash/d/h/a49.java`

a49 在 a65 之后执行（优先级 32），用于**点价场景下的公式表达式求值**。

### 核心逻辑

```java
// 1. 从 pricingFormulaDescription JSON 中提取公式表达式
String formulaDescription = deal.getPricingFormulaDescription();
JsonObject json = new Gson().fromJson(formulaDescription, JsonObject.class);
String totalFormula = json.getAsJsonObject("value").get("totalFormula").getAsString();
// totalFormula 例如: "BasicTriggeredPrice + BasicFixedPremium"

// 2. 准备变量映射
ScriptEngineManager manager = new ScriptEngineManager();
ScriptEngine engine = manager.getEngineByName("js");

// 3. 根据公式中的 abbreviation 设置变量
if (totalFormula.contains("BasicFloatPremium")) {
    engine.put("BasicFloatPremium", model.getSpread());
} else {
    engine.put("BasicFixedPremium", model.getSpread());
}

if (totalFormula.contains("Freight")) {
    engine.put("Freight", model.getOtherCostPrice());
} else {
    engine.put("PackingFee", model.getOtherCostPrice());
}

// 基础价变量
engine.put("BasicFixedPrice", settlementPrice);
engine.put("BasicTriggeredPrice", settlementPrice);
engine.put("BasicAveragePrice", settlementPrice);

// 4. 执行表达式求值
Double result = (Double) engine.eval(totalFormula);
// 例如: "BasicTriggeredPrice + BasicFixedPremium" → 1500 + 25 = 1525

// 5. 设置最终价格
model.setSettlementPrice(result - spread - otherCostPrice);
model.setSettlementNetPrice(round(result, digits));
```

> **关键理解**：`totalFormula` 是一个 JS 表达式字符串，abbreviation 作为变量名。
> JS 引擎执行 `BasicTriggeredPrice + BasicFixedPremium` 就是把基础价和升贴水相加。
> 这意味着公式表达式决定了各组件如何组合（加减乘除都可以）。

---

## 六、RiskUtil.parseBasicPriceParam — 公式参数解析

**文件**: `bcadmin-cashflowmodel/src/main/java/com/resrun/utils/RiskUtil.java` L1196-1311

这是系统中最广泛使用的公式参数解析方法。它遍历 JSON 数组，按 `level` 和 `abbreviation` 分支提取参数：

```
遍历 pricing_formula_id_parameters JSON 数组:
  │
  ├── level=1 (基础价)
  │   ├── 提取: pricingFormulaId, abbreviation
  │   ├── 提取: pricingCurrencyId, forexMarketId, pricingQuantityUnitId
  │   ├── 提取: fixedPrice / beginDate / endDate / marker / basicValence
  │   └── 存入 Map: "abbreviation" → "BasicFixedPrice"/"BasicTriggeredPrice"/...
  │
  ├── level=2, abbreviation="BasicFixedPremium" (固定升贴水)
  │   ├── 提取: percentage.value → "spreadIsPercentage"
  │   ├── 提取: basicSpread.value → "spreadValue"
  │   ├── 提取: pricingCurrency.value → "spreadCurrencyId"
  │   ├── 提取: pricingQuantityUnit.value → "spreadUnitId"
  │   └── 提取: forexMarketId.value → "spreadForexMarketId"
  │
  ├── level=2, abbreviation="PercentPremium" (百分比升贴水) ← 新增
  │   └── 提取: basicSpread.value → "percentSpreadValue"
  │
  ├── level=3, abbreviation="ProcessingFee" (加工费)
  │   └── 提取: value → "ProcessingFee"
  │
  └── level=4, abbreviation="AddedValue" (附加价)
      ├── 提取: pricingCurrency.value → "AddedValueCurrencyId"
      ├── 提取: pricingQuantityUnit.value → "AddedValueUnitId"
      └── 提取: fixedPrice.value → "AddedValueFixedPrice"
```

### BasicFixedPremium vs PercentPremium 的解析差异

| 字段 | BasicFixedPremium | PercentPremium |
|---|---|---|
| Map key | `spreadIsPercentage` | _(无)_ |
| 升贴水值 key | `spreadValue` | `percentSpreadValue` |
| 币种 key | `spreadCurrencyId` | _(无)_ |
| 单位 key | `spreadUnitId` | _(无)_ |
| 外汇市场 key | `spreadForexMarketId` | _(无)_ |

> **设计意图**：PercentPremium 只提取一个百分比值（如 0.05 = 5%），
> 不需要币种/单位/外汇市场，因为百分比升贴水的币种和单位自动继承自基础价。

---

## 七、MovementPrice 中升贴水的计算

**文件**: `bcadmin-system/.../service/impl/MovementPriceServiceImpl.java` `fillPriceInfo()` 方法

```
if 基础价是 BasicFixedPrice:
    basePrice = 公式参数中的 fixedPrice（或现金流模型的 settlementPrice）

if 基础价是 BasicTriggeredPrice:
    basePrice = 点价单上的 basePrice（或远期曲线计算值）

if 基础价是 BasicAveragePrice:
    basePrice = 该定价日的远期曲线价格

// 升贴水计算（与基础价类型无关）
if BasicFixedPremium 且 percentage = "n":
    spread = basicSpread
    → 币种转换（spreadCurrency → settlementCurrency）
    → 单位转换（spreadUnit → contractUnit）

if BasicFixedPremium 且 percentage = "y":
    spread = spreadValue × basePrice

if PercentPremium:
    spread = percentSpreadValue × basePrice
    // 效果与 BasicFixedPremium percentage="y" 相同
    // 但 abbreviation 不同，用于区分和报表展示
```

---

## 八、PercentPremium 改造分析

### 改造前

```
BasicFixedPremium (level=2)
  ├── percentage = "n" → 固定升贴水（绝对值）
  └── percentage = "y" → 百分比升贴水（basePrice × 百分比）
```

一个公式类型承载了两种业务含义，通过参数区分。

### 改造后

```
BasicFixedPremium (level=2)
  └── percentage = "n" → 固定升贴水（绝对值）

PercentPremium (level=2)  ← 新增独立类型
  └── basicSpread → 百分比值（如 0.05 = 5%）
```

### 改造涉及的代码层

| 层 | 文件 | 改动 |
|---|---|---|
| **后端参数解析** | `RiskUtil.parseBasicPriceParam()` L1272 | 新增 `PercentPremium` 分支，提取 `percentSpreadValue` |
| **后端报表 SQL** | `SysReportMapper.xml` L909-929 | 新增 CTE `pdlPercentPremium`，搜索 PercentPremium abbreviation |
| **后端报表 Java** | `SysReportServiceImpl` L542 | 新增 `percentPremiumNumber` 变量 |
| **前端** | _(暂无改动)_ | 前端仍使用 `BasicFixedPremium` + `percentage` 参数 |

### 当前状态

| 端 | 状态 |
|---|---|
| 后端 | 已支持 PercentPremium 作为独立 abbreviation 解析 |
| 前端 | **未改动** — 仍使用 BasicFixedPremium + percentage="y" |
| SQL 报表 | 已支持 — WHERE 条件 OR 连接两种类型 |

> **待完成**：前端需要在 `presetFormula.vue` 和 `jsonConfig/` 中新增 PercentPremium
> 作为独立的公式组件，让用户直接选择"百分比升贴水"而非在固定升贴水中选 percentage="y"。

---

## 九、计价公式修改对现金流的影响

### 修改公式参数会怎样？

| 修改操作 | 影响范围 | 生效时机 |
|---|---|---|
| 修改 `fixedPrice` | MovementPrice.basePrice → settlementNetPrice → settlementAmount | 下次日结 EOD 重算 |
| 修改 `basicSpread` | MovementPrice.spread → settlementNetPrice → settlementAmount | 下次日结 EOD 重算 |
| 修改 `percentage` y/n | spread 计算方式改变（绝对值 vs 百分比） | 下次日结 EOD 重算 |
| 修改 `pricingCurrency` | 汇率转换路径改变 | 下次现金流生成 |
| 修改 `beginDate/endDate`（均价） | 定价日期范围改变 → MP 记录数量改变 | 需要重新审批合同 |
| 添加/删除公式组件 | 整个 pricingType 可能改变（如 FIXED→FORMULA） | 需要重新审批合同 |

### 影响链路图

```
计价公式参数变更
  │
  ├── pricingFormulaIdParameters JSON 更新
  │
  ▼
MovementPrice 重算（fillPriceInfo）
  ├── basePrice 变化
  ├── spread 变化
  └── otherCostPrice 变化
  │
  ▼
settlementNetPrice = base + spread + other    ← 核心公式
  │
  ▼
现金流重算（a65 PricingEngine）
  ├── settlementPrice = netPrice - spread - other
  ├── settlementAmount = netPrice × qty × taxRate × fxRate × sign
  └── 写入 CashflowModelValues
  │
  ▼
报表数据变化
  ├── 升贴水明细报表 (spreadDetailsNew)
  ├── 采购库存定价表 (getProcurementInventoryPricingTableNew)
  └── 合同执行监控
```

---

## 十、完整数据流（新开发者速查）

```
┌─────────────────────────────────────────────────────────────────┐
│ 前端: pricingFormula.vue                                         │
│ 用户选择公式组件 → 构建 pricingFormulaIdParameters JSON          │
│ 保存到 physicalDealLine.pricingFormulaIdParameters               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ PhysicalDealsServiceImpl.submit()                                │
│ 调用 cashFlowProjectionService.generateCashFlowModel()           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ a65 PricingEngine — 按 pricingType 分支                          │
│                                                                  │
│ FIXED ──── settlementPrice = line.price                          │
│ AVERAGE ── settlementPrice = 曲线均价                            │
│ TRIGGER ── settlementPrice = 点价触发价                           │
│ FORMULA ── Python引擎计算 → a119(finalPrice, spread, other)      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ a49 PricingModel — JS 表达式求值                                  │
│ totalFormula = "BasicTriggeredPrice + BasicFixedPremium"         │
│ 变量替换 → JS eval → settlementNetPrice                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ CashflowModelValues 写入数据库                                    │
│ settlementPrice · settlementNetPrice · settlementAmount          │
│ spread · otherCostPrice · quantity · taxRate · fxRate            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ MovementPriceServiceImpl.fillPriceInfo()                         │
│ 解析 pricingFormulaIdParameters JSON:                            │
│                                                                  │
│ level=1: abbreviation → 决定 basePrice 取值方式                  │
│ level=2: BasicFixedPremium → spread (固定值或百分比)              │
│          PercentPremium → spread = percentValue × basePrice      │
│ level=3: ProcessingFee → otherCostPrice                          │
│                                                                  │
│ settlementNetPrice = basePrice + spread + otherCostPrice         │
└─────────────────────────────────────────────────────────────────┘
```
