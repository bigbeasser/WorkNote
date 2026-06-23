# 采购库存定价表 · 计算逻辑详解

> `ReceiptDeliveryDetailsServiceImpl#getProcurementInventoryPricingTableNew`
> 源码位置：L2586–L2949

---

## 一、数据源与关键字段

方法在循环外**一次性批量加载** 9 个数据源，全部按 `physicalDealLineId`（商品行 ID）分组为 Map，避免循环内逐条查库。

| # | 数据源 | 变量名 | 关键字段 | 用途 |
|---|---|---|---|---|
| 1 | MovementPrice | `movementPriceMap` | `quantity`, `parentProductQuantity`, `scorporoPrice`, `scorporoPriceBaseCur` | 定价明细，核心计算来源 |
| 2 | DocInQuantity | `docInQuantityMap` | `quantity` | 截至当月的累计入库量 |
| 3 | AdjustDifference | `sumDiiferenceMap` | `sumQuantity` | 调差量（合同执行中的量差调整） |
| 4 | PriceTriggering | `priceTriggeingMap` | `quantity` | 点价记录（每次点价的量） |
| 5 | PriceTriggeringDetail | `priceTriggeringDetailMap` | `relateQuantity` | 点价与入库的关联记录 |
| 6 | Evaluation | `evaluationMap` | `metalValue`, `baseCurMetalValue`, `receivableCDAmount`, `baseCurReceivableCDAmount` | 入库估值（EOM 存储） |
| 7 | PricingParams | `pricingParamMap` | `abbreviation` | 定价方式标识 |
| 8 | ContractType | `contractTypeMap` | `value → label` | 合同类型字典翻译 |
| 9 | ProductAccountingGroup | `productAccountingGroupTypeMap` | `productId → Boolean` | 商品核算组类型 |

### MovementPrice 查询条件（L2640–L2644）

```
inactiveFlag = false          -- 未停用
priced = 1                    -- 已定价
physicalDealLineId IN (...)   -- 在当前页的商品行范围内
dailySettlementDate <= endDay -- 日结日期 ≤ 查询截止日
```

---

## 二、数量计算

### 2.1 基础量（每条商品行）

#### 已入库量 `quantityAlready`

```
quantityAlready = docInQuantityMap.get(pdLineId) ?? 0.0
```

来源：`documentsMapper.getDocInQuantityByLineIdAndDate`，截至查询月份的累计入库量。

#### 调差量 `diffQuantity`

```
diffQuantity   = sumDiiferenceMap.get(pdLineId).sumQuantity ?? 0.0
diffQuantityKg = diffQuantity × DocUnitConversion
```

#### 单位换算系数 `DocUnitConversion`

```
if pdlUnitId == KG(83):
    DocUnitConversion = 1.0
else:
    DocUnitConversion = riskUnitConversionUtil.getUnitConversionNew(pdlUnitId, kgUnitId, productId)
```

含义：将商品行的原始单位转换为 KG 的比率。例如商品行单位是"吨"，则转换率为 1000。

---

### 2.2 MovementPrice 聚合量（循环前 for 循环，L2715–L2733）

对当前商品行的**所有 MovementPrice 记录**逐条累加：

```
quantityCheckBD         = Σ movementPrice.quantity
parentProductQuantityBD = Σ movementPrice.parentProductQuantity

pricedMetalValue        = |Σ (scorporoPrice × parentProductQuantity)|
pricedMetalValueBaseCur = |Σ (scorporoPriceBaseCur × parentProductQuantity)|
```

> **注意**：`pricedMetalValue` 和 `pricedMetalValueBaseCur` 最终取**绝对值**（`.abs()`），
> 因为 MovementPrice 中的量通常以负数记录（表示出库方向），乘积也为负，取绝对值还原为正的金属金额。

四个累加器的含义：

| 变量 | 含义 | 币种 |
|---|---|---|
| `quantityCheckBD` | 定价明细的 quantity 之和（用于判断是否有定价） | 原始单位 |
| `parentProductQuantityBD` | 定价明细的 parentProductQuantity 之和 | 原始单位 |
| `pricedMetalValue` | 已定价金属总金额（结算币种） | 结算币种 |
| `pricedMetalValueBaseCur` | 已定价金属总金额（本位币） | 本位币 |

---

### 2.3 两大情景分支

#### 情景一：未定价（L2779–L2786）

**进入条件**：`movementPrices 为空` 或 `quantityCheck == 0.0`

```
quantityAlreadyPriced    = 0.0
quantityAlreadyPricedKg  = 0.0

quantityAlreadyKg        = quantityAlready × DocUnitConversion

pricedButNotInStock      = 0 − quantityAlready − diffQuantity
pricedButNotInStockKg    = 0 − quantityAlreadyKg − diffQuantityKg
```

> 解读：没有任何定价明细时，已定价量为 0，"已定价未入库量"退化为 **−(已入库量 + 调差量)**，
> 即一个负数，表示"有多少量尚未被定价覆盖"。

#### 情景二：有定价明细（L2786–L2887）

**进入条件**：`movementPrices 非空` 且 `quantityCheck ≠ 0.0`

##### 已定价量（原始单位）

```
quantityAlreadyPriced = −1 × quantityCheck
                      = −1 × Σ movementPrice.quantity
```

> **符号约定**：MovementPrice.quantity 通常为负值（出库方向），乘以 −1 后变为正数，
> 代表"已经定价了多少量"。

##### 已定价未入库量（原始单位）

```
pricedButNotInStock = quantityAlreadyPriced − quantityAlready − diffQuantity
```

含义：**已定价量 − 已入库量 − 调差量**。
- 正值 → 定价量超过入库量（有"已定价但未入库"的部分）
- 负值 → 入库量超过定价量（有"已入库但未定价"的部分）
- 零 → 完全匹配

##### 已定价量（KG）

```
QuantityAlreadyPricedKg = Σ (parentProductQuantity × −1)
                          -- 仅取 parentProductQuantity 不为 null 的记录

-- 如果上述和 ≈ 0（精度 0.00001），则回退到：
if |QuantityAlreadyPricedKg| < 0.00001:
    movUnit = movementPrices 中第一个非空的 quantityUnitId
    MovUnitConversion = getUnitConversionNew(movUnit, kgUnitId, productId)
    QuantityAlreadyPricedKg = quantityAlreadyPriced × MovUnitConversion
```

> **为什么用 `parentProductQuantity` 而不是 `quantity`？**
> `quantity` 是定价明细自身的计价量，`parentProductQuantity` 是关联到父商品行的实际量。
> 当 parentProductQuantity 全为 0 时（可能是子产品行场景），回退用 quantityAlreadyPriced × 单位转换率。

##### 已入库量（KG）

```
quantityAlreadyKg = quantityAlready × DocUnitConversion
```

##### 已定价未入库量（KG）

```
pricedButNotInStockKg = quantityAlreadyPricedKg − quantityAlreadyKg − diffQuantityKg
```

---

### 2.4 点价特殊分支（L2825–L2880）

仅在 `BasicTriggeredPrice == true` 时进入。固定价和均价的分支体为空（沿用上面的通用计算）。

#### 三个比较量

| 变量 | 来源 | 含义 |
|---|---|---|
| `priceTriggerQuantity` | `Σ PriceTriggering.quantity` | 点价总量（所有点价记录的量之和） |
| `dociQuantity` | `docInQuantityMap` | 入库量（同 quantityAlready） |
| `priceTriggeringRealQuantity` | `Σ PriceTriggeringAndMoementPrice.relateQuantity` | 点价已关联入库的量 |

三个量均转为 BigDecimal（精度 5 位）后两两比较：

```
caseA = priceTriggerQuantity  vs  dociQuantity       -- 点价量 vs 入库量
caseB = priceTriggerQuantity  vs  priceTriggeringRealQuantity  -- 点价量 vs 关联量
```

#### 分支逻辑

```
┌─ caseA < 0（点价量 < 入库量）
│   ├─ caseB > 0（点价量 > 关联量）→ 空分支，沿用通用计算
│   └─ caseB = 0（点价量 = 关联量）→ "同没点价"，重新计算 ↓
│
│       quantityAlreadyPriced = −Σ movementPrice.quantity
│       pricedButNotInStock   = quantityAlreadyPriced − quantityAlready − diffQuantity
│       quantityAlreadyKg     = quantityAlready × DocUnitConversion (精度5)
│       quantityAlreadyPricedKg = quantityAlreadyPriced × DocUnitConversion (精度5)
│       pricedButNotInStockKg = quantityAlreadyPricedKg − quantityAlreadyKg − diffQuantityKg
│
└─ caseA ≥ 0（点价量 ≥ 入库量）→ 空分支，沿用通用计算
```

> **解读 caseB = 0 的含义**：点价量完全等于关联量，意味着所有点价都已关联到入库记录，
> 没有"游离"的点价。此时视同"没有有效点价"，用 MovementPrice 的 quantity 重新计算。
>
> **注意**：这个分支和通用计算的区别在于用了 `movementPrice.quantity`（而非 `quantityCheck`）
> 并用 `DocUnitConversion` 做转换（精度 5 位），而不是用 parentProductQuantity。

---

## 三、金额计算

### 3.1 已定价金属金额（来自 MovementPrice 聚合）

```
pricedMetalValue        = |Σ (scorporoPrice × parentProductQuantity)|        -- 结算币种
pricedMetalValueBaseCur = |Σ (scorporoPriceBaseCur × parentProductQuantity)| -- 本位币
```

- `scorporoPrice`：拆价（结算币种单价），即从期货价格中剥离出的金属单价
- `scorporoPriceBaseCur`：同一拆价换算到本位币的值
- 乘以 `parentProductQuantity`（父产品量）得到该条定价明细的金属金额
- 对所有明细求和后取绝对值

### 3.2 入库估值（来自 Evaluation）

```
estMetalValue            = Σ evaluation.metalValue              -- 结算币种
estMetalValueBaseCur     = Σ evaluation.baseCurMetalValue       -- 本位币
receivableCDAmount       = Σ evaluation.receivableCDAmount      -- 结算币种
receivableCDAmountBaseCur= Σ evaluation.baseCurReceivableCDAmount -- 本位币
```

- `estMetalValue`：入库时按当时市价估算的金属价值
- `receivableCDAmount`：应收 CD（Credit/Debit）金额，即信用调整项

### 3.3 已定价未入库金额

```
pricedButNotInAmount1    = pricedMetalValue − estMetalValue − receivableCDAmount        -- 结算币种
pricedButNotInAmountEur1 = pricedMetalValueBaseCur − estMetalValueBaseCur − receivableCDAmountBaseCur -- 本位币
```

> **公式含义**：
>
> `已定价未入库金额 = 已定价金属总额 − 已入库估值 − 应收CD调整`
>
> - 已定价金属总额：所有定价明细覆盖的金属价值
> - 减去入库估值：已经入库的部分按入库时估值扣除
> - 减去应收 CD：信用/借记调整项
> - 剩余部分 = 已定价但尚未入库的金额敞口

---

## 四、单价推导

### 4.1 目标单位转换

```
if targetUnit 存在:
    targetUnitConversion = getUnitConversionNew(kgUnitId, targetUnitId, productId)
    targetUnitPricedButNotInStock = pricedButNotInStockKg × targetUnitConversion
else:
    targetUnitPricedButNotInStock = pricedButNotInStockKg  -- 保持 KG
```

> 注意方向：这里是 KG → 目标单位，与前面的 原始单位 → KG 方向相反。

### 4.2 单价计算

```
pricedButNotInAmount    = pricedButNotInAmount1    ÷ targetUnitPricedButNotInStock  (精度 9 位)
pricedButNotInAmountEur = pricedButNotInAmountEur1 ÷ targetUnitPricedButNotInStock  (精度 9 位)
```

即：**已定价未入库金额 ÷ 已定价未入库重量 = 单价**

精度为 9 位小数（`RoundingMode.HALF_UP`），这是金属贸易中常见的高精度要求。

---

## 五、完成状态判定

循环结束后，第二次遍历所有结果行（L2928–L2946）：

```
son   = quantityAlreadyPriced  (已定价量, 精度 5)
mom   = quantityAlready        (已入库量, 精度 5)

if mom ≠ 0:
    ratio = son ÷ mom  (精度 5)
    if 0.9999 ≤ ratio ≤ 1.0001:
        status = COMPLATE    -- 完成（允许 ±0.01% 的误差）
    else:
        status = UNCOMPLATE  -- 未完成
else:
    status = UNCOMPLATE      -- 入库量为 0，视为未完成
```

> **容差设计**：比值在 [99.99%, 100.01%] 之间视为完成。
> 这个 ±0.01% 的容差是为了处理浮点精度和单位换算带来的微小偏差。

---

## 六、计算全景图

```
输入: date, page, size, unitId
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│  批量预加载 9 个 Map                                      │
│  MovementPrice · DocInQuantity · AdjustDifference        │
│  PriceTriggering · PriceTriggeringDetail · Evaluation    │
│  PricingParams · ContractType · ProductAccountingGroup   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  遍历每行:                                               │
│                                                          │
│  ① quantityAlready = 入库量                              │
│  ② quantityCheck = Σ mov.quantity                        │
│  ③ pricedMetalValue = |Σ (scoPrice × parentQty)|         │
│  ④ diffQuantity = 调差量                                  │
│                                                          │
│  ┌── 无定价 ──────────────────────────────────────────┐  │
│  │ 已定价量 = 0                                        │  │
│  │ 未入库量 = 0 − 入库量 − 调差量                       │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌── 有定价 ──────────────────────────────────────────┐  │
│  │ 已定价量 = −quantityCheck                           │  │
│  │ 未入库量 = 已定价量 − 入库量 − 调差量                │  │
│  │                                                     │  │
│  │ ┌─ 点价 & 点价量<入库量 & 点价量=关联量 ─────────┐  │  │
│  │ │ 重算: 用 mov.quantity + DocUnitConversion      │  │  │
│  │ └────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ⑤ 未入库金额 = 金属金额 − 估值 − 应收CD                 │
│  ⑥ 单价 = 未入库金额 ÷ 未入库重量(KG→目标单位)           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  第二次遍历: 完成率判定                                    │
│  ratio = 已定价量 ÷ 入库量                                │
│  ∈ [0.9999, 1.0001] → 完成, 否则 → 未完成                │
└─────────────────────────────────────────────────────────┘
```

---

## 七、关键注意点

1. **符号约定**：MovementPrice 中 quantity 通常为负（出库方向），代码中多处用 `× −1` 翻转为正。
   `pricedMetalValue` 最终取 `.abs()` 也是同一原因。

2. **两套量字段**：`movementPrice.quantity` 和 `movementPrice.parentProductQuantity` 是两套不同的量。
   - `quantity`：定价明细自身的计价量
   - `parentProductQuantity`：关联到父商品行的实际金属量
   - 金额计算用 `parentProductQuantity`，量判断用 `quantity`

3. **固定价和均价分支为空**：L2882–L2886 的 `BasicFixedPrice` 和 `BasicAveragePrice` 分支体为空。
   说明这两种定价方式在通用计算（情景二）中已覆盖，不需要额外处理。

4. **点价分支 caseB > 0 为空**：点价量 > 关联量 但 点价量 < 入库量时，代码没有特殊处理，
   沿用通用计算。这可能是业务上认为这种情况不需要调整。

5. **精度控制**：
   - 量比较用 BigDecimal（精度 5 位）
   - 单价用 BigDecimal（精度 9 位，HALF_UP）
   - 完成率比值精度 5 位
   - 点价特殊分支的 KG 转换用精度 5 位

6. **`minusMuchParam(a, b, c)` = `a − b − c`**：
   工具方法，将所有后续参数从第一个参数中减去，内部用 BigDecimal 避免浮点误差。
