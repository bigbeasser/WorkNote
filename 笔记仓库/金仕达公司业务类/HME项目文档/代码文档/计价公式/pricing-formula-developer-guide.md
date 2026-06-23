# 计价公式系统 · 新开发者指南

> 从订单创建到现金流结算，计价公式如何驱动整个定价链路

---

## 一、核心概念

### 1.1 什么是计价公式

计价公式（Pricing Formula）是合同中**决定金属价格**的规则。它存储在 `pricing_formulas` 主数据表中，在创建订单时被选择并绑定到合同行（`physical_deal_line`）。

一个合同行可以组合多个公式，形成**组合计价**，例如：
- 基础固定价 + 固定升贴水
- 点价 + 百分比升贴水 + 加工费
- 均价 + 固定升贴水

### 1.2 公式层级结构

| 层级 | 类型 | 说明 | 可选公式 |
|---|---|---|---|
| **Level 1** | 基础价 (base price) | 决定金属的基础价格 | `BasicFixedPrice` 固定价、`BasicTriggeredPrice` 点价、`BasicAveragePrice` 均价、`MultiMarketAveragePrice` 多网均价 |
| **Level 2** | 升贴水 (premium/spread) | 在基础价上加减的溢价 | `BasicFixedPremium` 固定升贴水（含百分比模式）、`BasicFloatPremium` 浮动升贴水 |
| **Level 3** | 加工费 (other costs) | 加工处理费用 | `ProcessingFee` |
| **Level 4** | 附加价 (added value) | 额外附加费用 | `AddedValue` |

> **关键理解**：Level 1 决定 `basePrice`，Level 2 决定 `spread`，Level 3/4 决定 `otherCostPrice`。
> 三者独立计算后叠加：`settlementNetPrice = basePrice + spread + otherCostPrice`

### 1.3 公式参数存储

合同行上的 `pricing_formula_id_parameters` 字段是一个 **JSON 数组**，每个元素对应一个公式组件：

```json
[
  {
    "value": 99,                              // pricing_formulas.id
    "label": "基础固定价",                      // 显示名称
    "level": 1,                               // 层级
    "abbreviation": "BasicFixedPrice",        // 公式类型标识（代码中用这个判断）
    "formula_parameters": {                   // 该公式的具体参数
      "pricingCurrency": { "value": 51 },     // 计价币种 ID
      "pricingQuantityUnit": { "value": 58 }, // 计价单位 ID
      "fixedPrice": { "value": "666.00" }     // 固定价格
    }
  },
  {
    "value": 102,
    "label": "固定升贴水",
    "level": 2,
    "abbreviation": "BasicFixedPremium",
    "formula_parameters": {
      "percentage": { "value": "n" },         // "y"=百分比, "n"=固定值
      "basicSpread": { "value": "25.00" },    // 升贴水值
      "pricingCurrency": { "value": 51 },     // 升贴水币种
      "pricingQuantityUnit": { "value": 58 }  // 升贴水单位
    }
  }
]
```

**解析工具**：`RiskUtil.parseBasicPriceParam(json)` 将上述 JSON 解析为 `Map<String, String>`，提取出 `abbreviation`、`fixedPrice`、`spreadValue`、`spreadIsPercentage` 等关键参数。

---

## 二、订单创建 → 公式选择

### 2.1 入口

| 路径 | 说明 |
|---|---|
| **UI 手动创建** | `DealController.addOrUpdatePhysicalDealLine()` → 前端传入 `pricingFormulaIdParameters` JSON |
| **批量创建** | `DealController.addOrUpdateAllPhysicalDeal()` → 批量设置 |
| **外部集成** | `FundPathServiceImpl` → 程序化构造 JSON（通常固定为 BasicFixedPrice） |

### 2.2 保存位置

公式选择后存储在两个地方：

| 表 | 字段 | 说明 |
|---|---|---|
| `physical_deal_line` | `pricing_formula_id_parameters` | 完整 JSON 数组（主存储） |
| `phy_deal_line_pricing_formula` | 每行一个公式组件 | 拆分存储（关联表，含 `sortIndex` 排序） |

---

## 三、合同审批 → MovementPrice 生成

### 3.1 什么是 MovementPrice

`MovementPrice`（定价明细）是系统的**核心定价记录**。每条记录代表一次"定价事件"，包含完整的价格和量信息。

关键字段：

| 字段 | 含义 |
|---|---|
| `physicalDealLineId` | 关联的合同行 |
| `basePrice` | 基础价格 |
| `spread` | 升贴水 |
| `otherCostPrice` | 其他费用 |
| `settlementNetPrice` | **净价 = basePrice + spread + otherCostPrice** |
| `scorporoPrice` | 金属拆价（父产品单位） |
| `quantity` | 定价量（采购方向为负） |
| `parentProductQuantity` | 父产品量 |
| `priced` | 1=已定价, 0=未定价 |
| `valid` | 1=有效, 0=已冲销, -1=初始未激活 |
| `movementActionType` | 创建原因：FID=初始定价, FIX=待结算, RI+/RI-=日结滚动 |

### 3.2 三种基础价的生成逻辑

#### 固定价 `BasicFixedPrice`

**触发时机**：合同审批（commit）时**立即生成**

```
生成 1 条 MovementPrice:
  valid = 1, priced = 1, onSpotPrice = 1
  movementActionType = FID
  priceDate = 合同日期
  basePrice = 公式参数中的 fixedPrice
  quantity = 合同行量（采购取负）
```

**特点**：一次性完成，价格确定，后续日结不需要滚动。

---

#### 点价 `BasicTriggeredPrice`

**触发时机**：点价单（PriceTriggering）审批时生成

```
每次点价生成 1 条 MovementPrice:
  valid = 1
  refDocumentType = 4（点价记录）
  refContractNumber = 点价单 ID

  如果价格日 ≤ 日结日:
    priced = 1, movementActionType = FID（价格已确定）
  如果价格日 > 日结日:
    priced = 0, movementActionType = FIX（待日结激活）
```

**basePrice 取值**：
- 现货点价（onSpotPrice=1）：直接取点价单上的 `basePrice`
- 远期点价（onSpotPrice=0）：从远期曲线（ForwardPrice）按商品成分计算

**日结滚动**：未定价的 FIX 记录在每日 EOD 中被 RI-（冲销）+ RI+（新建）滚动到下一个结算日。

---

#### 均价 `BasicAveragePrice`

**触发时机**：合同审批时**预生成**多条，覆盖整个均价期间

```
解析公式参数中的 beginDate 和 endDate
获取该日期范围内的所有定价日（pricingDates）
总量平均分配到每个定价日:
  quantity = 合同行量 / 定价日数量

对每个定价日生成 1 条 MovementPrice:
  如果定价日 < 曲线日:
    valid = 1, priced = 1, movementActionType = FID（已确定）
  如果定价日 = 曲线日:
    valid = 1, priced = 0, movementActionType = FIX（待激活）
  如果定价日 > 曲线日:
    valid = -1, priced = 0, movementActionType = FIX（未激活预备）
```

**日结激活**：每日 EOD 检查 FIX 记录，当定价日到达时，生成 RI-（冲销）+ RI+（已定价），`priced` 从 0 变为 1。

---

### 3.3 升贴水计算

升贴水在 `fillPriceInfo()` 中计算，与基础价类型无关，独立叠加：

```
如果 BasicFixedPremium 的 percentage = "n"（固定值模式）:
  spread = basicSpread
  → 币种转换（从升贴水币种到结算币种）
  → 单位转换（从升贴水单位到合同量单位）

如果 BasicFixedPremium 的 percentage = "y"（百分比模式）:
  spread = spreadValue × basePrice
  → 升贴水 = 基础价的百分比
```

> **注意**：`PercentPremium` 不是一个独立的公式类型，它是 `BasicFixedPremium` 的百分比模式。

### 3.4 统一价格公式

无论哪种基础价类型，最终价格结构始终一致：

```
settlementNetPrice = basePrice + spread + otherCostPrice
scorporoPrice      = 金属拆价（查表或推导）
additionalPrice    = settlementNetPrice / unitConversion - scorporoPrice

totalValue         = settlementNetPrice × quantity
metalValue         = scorporoPrice × parentProductQuantity
addedValue         = additionalPrice × parentProductQuantity
```

---

## 四、日结处理（EOD）

### 4.1 触发

由 `EODServiceImp.UpdateContractHMEEOD()` 在每日批处理中调用 `MovementPriceServiceImpl.updateByDailySettlement()`。

### 4.2 点价的日结滚动

对于 `BasicTriggeredPrice` 的未定价 FIX 记录：

```
1. 创建 RI- 记录: valid=0, quantity取反（冲销旧记录）
2. 创建 RI+ 记录: valid=1, priced=0, 日结日=下一结算日（新记录）
→ 效果：未定价头寸被"滚动"到下一天
```

### 4.3 均价的日结激活

对于 `BasicAveragePrice` 的 FIX 记录，当定价日到达时：

```
1. 创建 RI- 记录: valid=0（冲销旧的未定价记录）
2. 创建 RI+ 记录: valid=1, priced=1, onSpotPrice=1（已定价）
   basePrice = 该定价日的远期曲线价格
→ 效果：预备记录被"激活"为已定价记录
```

---

## 五、现金流生成

### 5.1 触发时机

| 事件 | 入口 |
|---|---|
| 收发货处理 | `ReceiptDeliveryDetailsServiceImpl` → `cashFlowProjectionService.generateCashFlowModel()` |
| UI 手动触发 | `DealController.generateCashFlowModel()` |
| EOD 批处理 | `EODServiceImp` → 对所有有效合同重新计算现金流 |
| 结算审批 | `SettlementServiceImpl.processDone()` |

### 5.2 引擎流水线

```
CashFlowProjectionServiceImpl.generateCashFlowModel()
  │
  ▼
a155.a1208()  ── 引擎调度器（策略模式）
  │
  ├── headerType = PO/SO → a10 (PhysicalFactory)
  │     │
  │     ├── 1. a66 HeaderValuesEngine  → 创建 CashflowModelHeaderValues
  │     │      每个收发行创建两条: SETTLEMENT(现金) + PHYSICAL_AMOUNT(MTM估值)
  │     │
  │     ├── 2. a67 ModelValuesEngine   → 创建 CashflowModelValues
  │     │      设置 quantity(带符号), spread, 币种, 税率
  │     │
  │     ├── 3. a65 PricingEngine       → 计算结算价格
  │     │      FIXED:   settlementPrice = 合同固定价
  │     │      AVERAGE: settlementPrice = 期间均价（从曲线数据）
  │     │      TRIGGER: settlementPrice = 点价触发价
  │     │      FORMULA: settlementPrice = Python公式引擎计算
  │     │
  │     ├── 4. a68/a69 TaxEngines      → 创建税费现金流行
  │     │
  │     └── 5. a63 ClearEngine         → 清理过期记录
  │
  └── 其他 headerType → 其他 Factory（信用证、衍生品、外汇等）
```

### 5.3 现金流金额计算

```
settlementAmount = settlementNetPrice × quantity × settlementAmountRate × fxRate × sign

其中:
  settlementNetPrice = round(basePrice + spread + otherCostPrice, pricingRoundingDigits)
  settlementAmountRate = 1 / (1 + taxRate)     -- 去税因子
  fxRate = 计价币种 → 结算币种汇率
  sign = +1(采购) / -1(销售)
```

### 5.4 现金流类型

| 类型                 | 代码                  | 说明            |
| ------------------ | ------------------- | ------------- |
| **SETTLEMENT**     | `CashflowType_0001` | 主结算现金流（合同收付款） |
| COST               | `CashflowType_0003` | 费用现金流（运费、保险等） |
| MARGIN             | `CashflowType_0004` | 保证金           |
| TAX                | `CashflowType_0006` | 税费            |
| PHYSICAL_AMOUNT    | `CashflowType_0019` | 实物 MTM 估值     |
| SETTLEMENT_TRIGGER | `CashflowType_0033` | 点价触发的结算       |

### 5.5 临时结算 vs 最终结算

| 字段                          | 含义     | 写入时机                          |
| --------------------------- | ------ | ----------------------------- |
| `settlementAmount`          | 当前估算金额 | 现金流生成/日结重估时                   |
| `temporarySettlementAmount` | 临时结算金额 | 临时结算审批时（`settlementStatus=2`） |
| `finalSettlementAmount`     | 最终结算金额 | 最终结算审批时（`settlementStatus=3`） |

最终结算金额公式：
```
finalSettlementAmount = settlementPrice × quantity × unitConversion / (1 + taxRate)
```

---

## 六、全景数据流

```
┌─────────────────────────────────────────────────────────────────────┐
│                        订单创建                                      │
│  选择计价公式 → 存入 pricing_formula_id_parameters (JSON)            │
│  Level 1: BasicFixedPrice / BasicTriggeredPrice / BasicAveragePrice │
│  Level 2: BasicFixedPremium (固定/百分比)                            │
│  Level 3: ProcessingFee                                             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        合同审批 (commit)                             │
│  MovementPriceServiceImpl.updateByContractCommit()                  │
│                                                                     │
│  ┌─ 固定价 ──────────┐  ┌─ 均价 ──────────────────────────────┐    │
│  │ 生成 1 条 MP       │  │ 生成 N 条 MP (每个定价日 1 条)        │    │
│  │ priced=1, FID      │  │ 过去的: priced=1, FID               │    │
│  │ basePrice=固定值    │  │ 当天的: priced=0, FIX               │    │
│  └───────────────────┘  │ 未来的: valid=-1, FIX               │    │
│                          └─────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   点价单审批 (仅 BasicTriggeredPrice)                │
│  MovementPriceServiceImpl.updateByPricingCommit()                   │
│  每次点价 → 生成 1 条 MP (priced=1 或 0, FID 或 FIX)                │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        日结 EOD (每日)                               │
│  MovementPriceServiceImpl.updateByDailySettlement()                 │
│                                                                     │
│  点价 FIX: RI- 冲销 + RI+ 滚动到下一天                              │
│  均价 FIX: RI- 冲销 + RI+ 激活为已定价 (到期日)                      │
│                                                                     │
│  fillPriceInfo() 统一计算:                                          │
│    basePrice (按公式类型取值)                                        │
│    spread (固定值 或 basePrice × 百分比)                             │
│    settlementNetPrice = base + spread + other                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     现金流生成 (收发货/手动/EOD)                      │
│  CashFlowProjectionServiceImpl.generateCashFlowModel()              │
│                                                                     │
│  a66: 创建 HeaderValues (SETTLEMENT + MTM)                          │
│  a67: 创建 ModelValues (量、spread、币种、税率)                      │
│  a65: 计算 settlementPrice (FIXED/AVERAGE/TRIGGER/FORMULA)          │
│                                                                     │
│  settlementAmount = netPrice × qty × (1/(1+tax)) × fxRate × sign   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        结算审批                                      │
│  SettlementServiceImpl.processDone()                                │
│                                                                     │
│  临时结算: temporarySettlementAmount (status=2)                      │
│  最终结算: finalSettlementAmount (status=3)                          │
│  税费行: taxAmount = grossAmount - netAmount                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 七、关键代码入口

| 类 | 路径 | 职责 |
|---|---|---|
| `MovementPriceServiceImpl` | `bcadmin-system/.../service/impl/` | MP 生成、填充、日结滚动 |
| `CashFlowProjectionServiceImpl` | 同上 | 现金流引擎调度 |
| `EODServiceImp` | `bcadmin-system/.../eod/` | 日结批处理 |
| `PricingServiceImpl` | `bcadmin-system/.../service/impl/` | 点价单业务 |
| `SettlementServiceImpl` | 同上 | 结算审批 |
| `RiskUtil` | `bcadmin-cashflowmodel/.../utils/` | 公式参数解析 |
| `PricingFormulaUtils` | `bcadmin-common/.../utils/` | JSON 参数提取 |
| `a65` (PricingEngine) | `bcadmin-cashflowmodel/.../cash/d/` | 现金流定价计算 |
| `a10` (PhysicalFactory) | `bcadmin-cashflowmodel/.../cash/b/` | 实货现金流引擎 |

---

## 八、MovementActionType 速查

| 代码 | 含义 | 触发场景 |
|---|---|---|
| `FID` | 初始固定定价 | 合同审批（固定价/已到期均价） |
| `FIX` | 待结算定价 | 合同审批（未到期均价/远期点价） |
| `CC+` | 补充协议新增 | 补充协议审批 |
| `CC-` | 合同取消冲销 | 合同撤回审批 |
| `RI+` | 日结新建 | EOD 滚动（新记录） |
| `RI-` | 日结冲销 | EOD 滚动（旧记录取反） |
| `ADD` | 价格调增 | 价格变更 |
| `DEC` | 价格调减 | 价格变更 |
| `CAN` | 取消 | 定价取消 |

---

## 九、常见问题

### Q1: 为什么 MovementPrice 的 quantity 是负数？
采购方向（`ps_flag='P'`）的 MP 记录 quantity 为负。这是符号约定，表示"买入"方向。代码中多处用 `× -1` 翻转。

### Q2: `parentProductQuantity` 和 `quantity` 有什么区别？
- `quantity`：合同行的计价量（合同单位）
- `parentProductQuantity`：换算到父产品（如铜精矿→铜金属）的实际量
- 金额计算用 `parentProductQuantity`，量判断用 `quantity`

### Q3: `PercentPremium` 是独立公式吗？
不是。百分比升贴水是 `BasicFixedPremium` 的一个模式，由参数 `percentage = "y"` 控制。
当 `percentage = "y"` 时：`spread = spreadValue × basePrice`。

### Q4: 日结 EOD 做了什么？
1. 对未定价的点价 FIX 记录：RI- 冲销 + RI+ 滚动到下一天
2. 对到期的均价 FIX 记录：RI- 冲销 + RI+ 激活为已定价
3. 重新计算所有 MP 的 `basePrice`、`spread`、`settlementNetPrice`
4. 触发现金流重估

### Q5: 现金流中 `settlement_amount` 和 `final_settlement_amount` 的区别？
- `settlement_amount`：当前估算值，随日结和价格变动而更新
- `final_settlement_amount`：最终结算审批后写入的确定值，不再变动
- 报表中优先取 `final_settlement_amount`，为 null 时回退到 `settlement_amount`
