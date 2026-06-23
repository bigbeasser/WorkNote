# MovementPrice 定价明细 · 前世今生

> 从合同审批到日结滚动，从点价触发到报表消费，一条定价记录的完整生命旅程

相关文档：[[pricing-order-creation-and-calculation]] · [[pricing-formula-developer-guide]] · [[cashflow-pricing-formula-trace]] · [[python-pricing-engine-trace]] · [[pricing-order-reference-flow]]

---

## 一、MovementPrice 是什么

MovementPrice（定价明细）是系统的**核心定价记录表**。每一条记录代表一次"定价事件"——某个合同行的某批金属在某个日期被确定了一个价格。

它同时承担三个职责：

| 职责 | 说明 |
|---|---|
| **价格载体** | 存储 basePrice、spread、otherCostPrice、settlementNetPrice 等完整价格 |
| **量追踪** | 通过 quantity + priced + valid 追踪"多少量已定价、多少量未定价" |
| **审计链** | 通过 movementActionType + valid 形成完整的变更历史（冲销/新建/滚动） |

---

## 二、表结构核心字段

### 2.1 身份与关联

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Long | 主键（雪花 ID） |
| `code` | String | 业务编码（自动生成） |
| `physicalDealId` | Long | FK → 合同 |
| `physicalDealLineId` | Long | FK → 合同商品行 |
| `physicalDealLineNumber` | String | 合同行号 |
| `supplementId` | Long | FK → 补充协议（如有） |
| `refDocumentType` | Integer | 来源类型：1=现货单 2=长协单 3=补充协议 **4=点价单** |
| `refContractNumber` | String | 关联的点价单 fixationId |
| `refMovementPriceCode` | String | 关联的父/冲销 MP 编码 |

### 2.2 日期

| 字段 | 说明 |
|---|---|
| `priceDate` | 定价日期（价格属于哪一天） |
| `dailySettlementDate` | 日结日期（价格在哪天生效） |
| `session` | 交易场次 |

### 2.3 价格组件

| 字段 | 说明 | 公式关系 |
|---|---|---|
| `basePrice` | 基础价格 | 由公式类型决定取值方式 |
| `spread` | 升贴水 | 固定值 或 basePrice × 百分比 |
| `otherCostPrice` | 其他费用（加工费等） | |
| **`settlementNetPrice`** | **净价** | **= basePrice + spread + otherCostPrice** |
| `scorporoPrice` | 金属拆价（父产品单位） | 查表或推导 |
| `additionalPrice` | 附加价 | = settlementNetPrice / unitConversion - scorporoPrice |

### 2.4 量字段

| 字段 | 说明 |
|---|---|
| `quantity` | 定价量（采购方向为**负**，销售方向为正） |
| `parentProductQuantity` | 父产品量（换算到主金属单位） |
| `unitConversion` | 单位转换系数 |
| `quantityUnitId` | 量单位 ID |
| `parentProductQuantityUnitId` | 父产品量单位 ID |

### 2.5 金额字段

| 字段 | 公式 |
|---|---|
| `totalValue` | = settlementNetPrice × quantity |
| `metalValue` | = scorporoPrice × parentProductQuantity |
| `addedValue` | = additionalPrice × parentProductQuantity |
| `amountBaseCur` | = settlementNetPriceBaseCur × quantity |

### 2.6 状态字段

| 字段 | 值 | 含义 |
|---|---|---|
| `priced` | `1` | 已定价（价格已确定） |
| `priced` | `0` | 未定价（价格待确定） |
| `valid` | `1` | 有效（当前生效） |
| `valid` | `0` | 已冲销（被 RI- 取代） |
| `valid` | `-1` | 初始未激活（均价预备记录） |
| `onSpotPrice` | `0` | 未知价（Unknown） |
| `onSpotPrice` | `1` | 现货价（On Spot） |
| `onSpotPrice` | `2` | 已知价（Known） |

### 2.7 动作类型 movementActionType

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
| `REA` | 重新分配 | 定价重分配 |
| `STO` | 存储 | 定价存储 |

---

## 三、前世 — MovementPrice 的诞生

### 3.1 诞生路径总览

```
┌─────────────────────────────────────────────────────────────┐
│                    MovementPrice 的 5 种诞生方式              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① 合同审批 ──→ 固定价: 1 条 MP (FID, priced=1)             │
│                 均价:   N 条 MP (每个定价日 1 条)             │
│                                                             │
│  ② 点价单提交 ──→ 每次点价: 1 条 MP (FID 或 FIX)             │
│                                                             │
│  ③ 补充协议 ──→ 变更量/价: CC+ 记录                          │
│                                                             │
│  ④ 日结 EOD ──→ 滚动: RI- (冲销) + RI+ (新建)               │
│                                                             │
│  ⑤ 合同撤回 ──→ 冲销: CC- 记录                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 诞生路径 ① — 合同审批

**入口**: `MovementPriceServiceImpl.updateByContractCommit()`

#### 固定价 BasicFixedPrice

```
合同审批
  │
  ▼
generateByContractCommitFixed()
  │
  ├── 创建 1 条 MovementPrice:
  │     valid = 1, priced = 1, onSpotPrice = 1
  │     movementActionType = FID
  │     priceDate = 合同日期
  │     dailySettlementDate = 曲线日期
  │     quantity = 合同行量（采购取负）
  │
  ├── fillBasicInfo() → 设置量/单位/汇率
  │
  └── fillPriceInfo() → 计算价格:
        basePrice = 公式参数中的 fixedPrice
        spread = 固定值 或 basePrice × 百分比
        settlementNetPrice = base + spread + other
```

#### 均价 BasicAveragePrice

```
合同审批
  │
  ▼
generateByContractCommitAverage()
  │
  ├── 解析公式参数: beginDate, endDate
  ├── 获取日期范围内所有定价日 pricingDates
  ├── 总量平均分配: qty = 合同行量 / 定价日数
  │
  └── 对每个定价日创建 1 条 MP:
        │
        ├── 定价日 < 曲线日 (已过期):
        │     valid=1, priced=1, FID, onSpotPrice=1
        │     basePrice 立即计算
        │
        ├── 定价日 = 曲线日 (今天):
        │     valid=1, priced=0, FIX
        │     待日结激活
        │
        └── 定价日 > 曲线日 (未来):
              valid=-1, priced=0, FIX
              预备记录，待日结激活
```

### 3.3 诞生路径 ② — 点价单提交

**入口**: `MovementPriceServiceImpl.updateByPricingCommit()`

```
点价单提交 (priceOrderSubmission)
  │
  ▼
对每条 PriceTriggering:
  │
  ├── 已有 MP → generateByPricingChange() (变更)
  │
  └── 新的 → generateByPricing()
        │
        ├── 创建 MP:
        │     refDocumentType = 4 (点价记录)
        │     refContractNumber = fixationId
        │     quantity = -PriceTriggering.quantity (采购取负)
        │
        ├── 判断 priced 状态:
        │     priceDate ≤ dailySettlementDate:
        │       priced=1, FID (价格已确定)
        │     priceDate > dailySettlementDate:
        │       priced=0, FIX (待日结确定)
        │
        ├── fillBasicInfo()
        │
        └── fillPriceInfo():
              │
              ├── onSpotPrice=1 或 2 (现货/已知):
              │     直接从 PriceTriggering 复制:
              │     basePrice = pt.basePrice
              │     spread = pt.spread
              │     settlementNetPrice = pt.price
              │     scorporoPrice = pt.metalPrice
              │
              └── onSpotPrice=0 (未知/远期):
                    从远期曲线逐成分计算 basePrice
                    应用币种/单位转换 + 规格系数
```

### 3.4 诞生路径 ③ — 补充协议

**入口**: `MovementPriceServiceImpl.updateBySupplementCommit()`

```
补充协议审批
  │
  ├── 量变更 → CC+ 记录 (新增量)
  ├── 价变更 → ADD/DEC 记录
  └── 商品变更 → CAN + CC+ 配对
```

### 3.5 诞生路径 ④ — 日结 EOD 滚动

**入口**: `EODServiceImp.UpdateMovementEOD()` → `updateByDailySettlement()`

这是 MovementPrice 最复杂的生命周期阶段。

#### 点价的日结滚动 (BasicTriggeredPrice)

```
每日 EOD
  │
  ▼
updateByDailySettlementTrigger()
  │
  ├── 找到所有 valid=1, priced=0, FIX 的 MP
  │
  └── 对每条 MP:
        │
        ├── 1. 创建 RI- (冲销):
        │     quantity = 原量 × -1
        │     valid = 0
        │     价格 = 原价格
        │     → 效果: 抵消昨天的未定价记录
        │
        ├── 2. 创建 RI+ (新建):
        │     quantity = 原量
        │     valid = 1
        │     priced = 1 (如果今天可以定价)
        │     dailySettlementDate = 今天
        │     → 从现金流模型读取最新价格
        │     → 回写 PriceTriggering 的价格字段
        │
        └── 3. 原 MP 设为 valid=0
```

#### 均价的日结激活 (BasicAveragePrice)

```
每日 EOD
  │
  ▼
updateByDailySettlementAverage()
  │
  ├── 找到 valid=1, priced=0, FIX 的均价 MP
  │   (定价日已到达的记录)
  │
  └── 对每条 MP:
        │
        ├── 1. 创建 RI- (冲销):
        │     quantity = 原量 × -1
        │     valid = 0, priced = 0
        │
        ├── 2. 创建 RI+ (激活):
        │     quantity = 原量
        │     valid = 1, priced = 1, onSpotPrice = 1
        │     basePrice = 该定价日的远期曲线价格
        │
        └── 3. 处理 valid=-1 的预备记录:
              updateByDailySettlementInitialAverage()
              当定价日临近 → 创建 valid=1, priced=0 的新记录
```

### 3.6 诞生路径 ⑤ — 合同撤回

```
合同撤回审批
  │
  ▼
updateByContractCancle()
  │
  ├── 找到所有 valid=1 的 MP
  │
  └── 对每条 MP 创建 CC- 冲销:
        quantity = 原量 × -1
        valid = 1
        → 效果: 所有定价记录被反向冲销
```

---

## 三-B、实战追踪：点价单提交 → 次日日结

> 以一次真实的点价单提交为例，逐行追踪代码，看 MovementPrice 在 48 小时内经历了什么。

### 场景设定

- 合同行 `pdl.id = 10001`，采购方向（`ps_flag = 'P'`），基础价公式 = `BasicTriggeredPrice`
- 用户在点价单上填写：`onSpotPrice = 0`（未知价），`transactionDate = 2026-06-16`（今天），`quantity = 100`
- 系统曲线日期 `curveDate = 2026-06-16`

---

### 第一天：点价单提交（Day 1 下午）

**入口**: `PricingController.priceOrderSubmission()` → `movementPriceService.updateByPricingCommit(pricingIds, null)`

#### Step 1: generateByPricing() 创建 MP 骨架

**代码**: `MovementPriceServiceImpl.java` L1998-2155

```
generateByPricing(pricing, priceTriggering, null, pd, pdLine, date=null)
  │
  ├── date = null → 取最新 curveDate session
  │     date = 2026-06-16, session = 2
  │
  ├── factor = "P".equals(psFlag) ? -1 : 1  →  factor = -1
  │
  ├── 基础字段:
  │     physicalDealLineId = 10001
  │     priceDate = priceTriggering.transactionDate = 2026-06-16
  │     dailySettlementDate = max(curveDate, transactionDate) = 2026-06-16
  │     quantity = 100 × (-1) = -100  (采购取负)
  │     valid = 1
  │     refDocumentType = 4 (点价记录)
  │     refContractNumber = fixationId (如 "FX30260616_00001")
  │
  └── ★★★ 关键分支判断 (L2079-2146) ★★★
        │
        ├── onSpotPrice = 0, 不是 1 也不是 2, 不是 isSpecialPricing
        │     → 进入 L2101: onSpotPrice == 0 分支
        │
        ├── changeType = null (正常点价，不是变更)
        │     → 进入 L2102
        │
        └── priceDate(06-16).isBefore(dailySettlementDate(06-16))
              → false! (06-16 不 before 06-16)
              → 进入 L2106 else:
                    movementActionType = FIX
                    priced = 0  ← ★ 未定价！
```

**结果**: 创建了 1 条 MP：

| 字段 | 值 |
|---|---|
| `valid` | `1` |
| `priced` | **`0`** (未定价) |
| `movementActionType` | **`FIX`** |
| `onSpotPrice` | `0` |
| `quantity` | `-100` |
| `priceDate` | `2026-06-16` |
| `dailySettlementDate` | `2026-06-16` |

#### Step 2: fillBasicInfo() + fillPriceInfo()

**代码**: L1776-1778

```
fillBasicInfo(addList):
  ├── parentProductQuantity = quantity × unitConversion
  ├── baseCurrencyId = 业务机构本位币
  ├── exchangeRateBaseCur = 结算币种→本位币汇率
  └── taxRate, businessSegmentId ...

fillPriceInfo(addList):
  ├── basePrice:
  │     onSpotPrice=0, 不是 1/2 → 进入远期曲线计算 (L2987-3067)
  │     获取商品成分 (category="Fixation")
  │     对每个成分: 查 ForwardPrice(date=06-16) → 币种/单位转换 → 累加
  │     basePrice = Σ 成分价格
  │
  ├── spread: 从 pricingFormulaIdParameters 解析
  │     BasicFixedPremium → 固定值或百分比 × basePrice
  │
  ├── settlementNetPrice = basePrice + spread + otherCostPrice
  │
  ├── scorporoPrice: 查 scorporo 价格表 或 netPrice/unitConversion
  │
  └── additionalPrice = netPrice/unitConversion - scorporoPrice
```

#### Step 3: 回写 PriceTriggering

**代码**: L1787-1805

```
对每条 PriceTriggering:
  ├── movementDate = MP.dailySettlementDate = 2026-06-16
  │
  └── 因为 priced = 0 (不是 1):
        不更新 metalPrice 和 additionalPrice
        (这两个字段等 priced=1 时才回写)
```

> **Day 1 结束时的状态**：
> - `movement_price` 表：1 条记录，`valid=1, priced=0, FIX`
> - `price_triggering` 表：`movementDate` 被更新，但价格字段保持用户填写的值

---

### 第二天：日结 EOD（Day 2 凌晨）

**入口**: `EODServiceImp.UpdateMovementEOD()` → `movementPriceService.updateByDailySettlement(contractNumbers, curveDate=2026-06-17)`

#### Step 4: 查询待处理的 MP

**代码**: L2402-2404

```sql
SELECT * FROM movement_price
WHERE inactive_flag = false
  AND valid = 1
  AND on_spot_price = 0           -- ★ 只处理未知价
  AND movement_action_type != 'FID'  -- ★ 排除已确定的
  AND physical_deal_id IN (...)
```

我们 Day 1 创建的 MP 满足所有条件：`valid=1, onSpotPrice=0, actionType=FIX` → **被选中**。

#### Step 5: 过滤检查

**代码**: L2432-2448

```
对每条 MP:
  │
  ├── basicPf = pricingFormulas 查到 ref = "BasicTriggeredPrice"
  │     → 进入 L2441 点价分支
  │
  ├── curveDate(06-17).isBefore(dailySettlementDate(06-16))
  │     → false (06-17 不 before 06-16) → 不跳过 ✓
  │
  ├── curveDate(06-17).isBefore(priceDate(06-16))
  │     → false → 不跳过 ✓
  │
  ├── noActions = {RI-, RI+, FID, CAN, ADD}
  │     actionType = FIX → 不在 noActions 中 → 不跳过 ✓
  │
  └── actionType ≠ DEC → 不跳过 ✓
      → 进入 updateByDailySettlementTrigger()
```

#### Step 6: updateByDailySettlementTrigger() — 创建 RI-/RI+

**代码**: L2317-2375

```
updateByDailySettlementTrigger(原MP, cashflowModel, curveDate=2026-06-17)
  │
  ├── 复制原 MP 为 mq1 和 mq2 (BeanUtils.copyProperties)
  │
  ├── === RI- (冲销记录) mq1 ===
  │     id = 新雪花ID
  │     code = 新编码
  │     refMovementPriceCode = 原MP.code  ← 血缘关联
  │     movementActionType = "RI-"
  │     dailySettlementDate = 2026-06-17
  │     valid = 0  ← 已冲销
  │     quantity = 原量 × -1 = -100 × -1 = 100  ← 反向
  │     parentProductQuantity = 原值 × -1
  │     (价格保持原值不变)
  │
  └── === RI+ (新记录) mq2 ===
        id = 新雪花ID
        code = 新编码
        refMovementPriceCode = 原MP.code  ← 血缘关联
        movementActionType = "RI+"
        dailySettlementDate = 2026-06-17
        valid = 1  ← 有效
        priced = 1  ← ★ 已定价！
        quantity = -100 (保持原方向)
        │
        ├── ★★★ 从现金流模型更新价格 ★★★
        │     spread = cashflowModel.spread  (L2353)
        │     otherCostPrice = cashflowModel.otherCostPrice  (L2354)
        │     settlementNetPrice = cashflowModel.settlementNetPrice  (L2355)
        │
        └── (basePrice 不在此处更新，留给 fillPriceInfo)
```

#### Step 7: fillBasicInfo() + fillPriceInfo() 对 addList

**代码**: L2500-2507

```
fillBasicInfo([RI-, RI+]):
  └── 设置 parentProductQuantity, exchangeRate, taxRate 等

fillPriceInfo([RI-, RI+]):
  │
  └── 对 RI+ 记录:
        ├── basePrice: 从远期曲线重新计算 (date=priceDate=06-16)
        │     查询 ForwardPrice(date=06-16, contract, session=0)
        │     逐成分: 市场价 × 汇率 × 单位换算 × 系数 → 累加
        │
        ├── spread: 已被 L2353 从现金流模型覆盖
        │     fillPriceInfo 中会再次根据公式参数计算
        │     如果是百分比: spread = spreadValue × basePrice
        │
        ├── settlementNetPrice = basePrice + spread + otherCostPrice
        │     (覆盖 L2355 的值)
        │
        ├── scorporoPrice: 查 scorporo 价格表
        │     scorporoDate = dailySettlementDate = 2026-06-17
        │
        └── additionalPrice = netPrice/unitConv - scorporoPrice
```

#### Step 8: 原 MP 设为无效

**代码**: L2453-2456

```
原MP:
  valid = 0  ← 已冲销
  updatedTime = now
  updatedBy = "EOD:UserName" 或 "admin"
```

#### Step 9: 持久化

**代码**: L2500-2513

```
saveBatch(addList):     保存 RI- 和 RI+ 两条新记录
updateBatchById(updateList):  更新原 MP (valid=0)
```

#### Step 10: 回写 PriceTriggering

**代码**: L2516-2561

```
找到所有 RI+ 记录 → 提取 refContractNumber (fixationId)
  │
  └── 对每条 PriceTriggering (fixationId 匹配):
        │
        ├── metalPrice = unitConversion × RI+.scorporoPrice  (L2537)
        │
        ├── 如果不是 isSpecialPricing 且不是 onSpotPrice=2 且没有 dnCode:
        │     basePrice = RI+.basePrice  (L2545)
        │     spread = RI+.spread  (L2546)
        │     otherExpenses = RI+.otherCostPrice  (L2547)
        │     price = RI+.settlementNetPrice  (L2548)
        │     additionalPrice = RI+.additionalPrice  (L2549)
        │     dealAmount = quantity × settlementNetPrice  (L2550)
        │
        └── updateBatchById(ptUpdateList)
```

> **Day 2 结束时的状态**：
>
> `movement_price` 表有 **3 条记录**：
>
> | # | actionType | valid | priced | quantity | dailySettlementDate | 说明 |
> |---|---|---|---|---|---|---|
> | 1 | FIX | **0** | 0 | -100 | 06-16 | Day 1 原始记录，已被冲销 |
> | 2 | RI- | 0 | 0 | **+100** | 06-17 | 冲销记录，量取反 |
> | 3 | RI+ | **1** | **1** | -100 | 06-17 | 新记录，已定价，价格已更新 |
>
> `price_triggering` 表：
> - `basePrice`、`spread`、`otherExpenses`、`price`、`additionalPrice`、`dealAmount` 全部被 RI+ 的计算结果覆盖
> - `metalPrice` = unitConversion × scorporoPrice

---

### 两种场景对比

#### 场景 A：onSpotPrice = 1 或 2（现货价/已知价）

```
Day 1 提交:
  generateByPricing() → onSpotPrice=1/2
    → movementActionType = FID, priced = 1
    → fillPriceInfo: 直接从 PriceTriggering 复制价格
    → 回写 PriceTriggering: metalPrice, additionalPrice 立即更新

Day 2 EOD:
  查询条件: on_spot_price = 0
  → FID 记录 onSpotPrice ≠ 0 → 不被选中
  → ★ 什么都不发生
```

#### 场景 B：onSpotPrice = 0（未知价/远期）

```
Day 1 提交:
  generateByPricing() → onSpotPrice=0
    → priceDate < dailySettlementDate:
        movementActionType = FID, priced = 1  (价格已过期，直接确定)
    → priceDate >= dailySettlementDate:
        movementActionType = FIX, priced = 0  (价格待确定)

Day 2 EOD (仅 FIX 记录):
  → 被选中 → 创建 RI-(冲销) + RI+(新记录)
  → RI+ 从现金流模型获取最新 spread/otherCost
  → fillPriceInfo 从远期曲线重新计算 basePrice
  → 回写 PriceTriggering 所有价格字段
```

#### 判断逻辑总结

```
                    onSpotPrice = ?
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          ▼          ▼
            1(现货)    2(已知)    0(未知)
              │          │          │
              ▼          ▼          ▼
           FID         FID     priceDate < dailySettlementDate?
         priced=1    priced=1      │           │
                                   Yes         No
                                    │           │
                                    ▼           ▼
                                  FID         FIX
                                priced=1    priced=0
                                              │
                                         日结 EOD
                                         RI- + RI+
                                         价格更新
```

---

### 第三天及以后：持续滚动

如果 RI+ 记录的 `onSpotPrice` 仍然是 0（远期合约未到期），**每个 EOD 都会重复滚动**：

```
Day 2: FIX(valid=1) → RI-(valid=0) + RI+(valid=1, priced=1)
Day 3: RI+(valid=1, onSpotPrice=0) → 又被选中!
       → 新的 RI-(valid=0) + 新的 RI+(valid=1, priced=1)
Day 4: 同上...
...
Day N: 直到远期合约到期，basePrice 确定
```

> **这就是为什么一个点价记录可能产生几十条 MovementPrice** — 每天一对 RI-/RI+，
> 形成完整的审计链。但任何时刻只有一条 `valid=1` 的记录是有效的。

---

## 四、今生 — MovementPrice 的价格计算

### 4.1 fillPriceInfo() — 核心定价引擎

**文件**: `MovementPriceServiceImpl.java` L2725-3201

这是所有 MP 记录价格的最终计算入口。无论哪种诞生路径，最终都会调用此方法。

```
fillPriceInfo(movementPrice)
  │
  ├── 1. 确定基础价 basePrice ──────────────────────────────┐
  │                                                         │
  │   BasicFixedPrice:                                      │
  │     basePrice = 公式参数 fixedPrice                     │
  │     (或现金流模型的 settlementPrice)                     │
  │                                                         │
  │   BasicTriggeredPrice:                                  │
  │     onSpotPrice=1/2: 从 PriceTriggering 复制            │
  │     onSpotPrice=0:   从远期曲线逐成分计算                │
  │                                                         │
  │   BasicAveragePrice:                                    │
  │     basePrice = 该定价日的远期曲线价格                    │
  │                                                         │
  ├── 2. 计算升贴水 spread ─────────────────────────────────┐
  │                                                         │
  │   BasicFixedPremium (固定模式):                          │
  │     spread = basicSpread                                │
  │     → 币种转换 (spreadCurrency → settlementCurrency)     │
  │     → 单位转换 (spreadUnit → contractUnit)              │
  │                                                         │
  │   BasicFixedPremium (百分比模式):                        │
  │     spread = spreadValue × basePrice                    │
  │                                                         │
  │   PercentPremium:                                       │
  │     spread += percentSpreadValue × basePrice            │
  │                                                         │
  │   最终: totalSpread = newSpread + oldSpread             │
  │                                                         │
  ├── 3. 其他费用 otherCostPrice                            │
  │     从现金流模型或公式参数取值                             │
  │                                                         │
  ├── 4. 计算净价                                           │
  │     settlementNetPrice = basePrice + spread + other     │
  │                                                         │
  ├── 5. 计算金属拆价 scorporoPrice                         │
  │     核算组 Z002/Z003: 查 scorporo 价格表                │
  │     其他: scorporoPrice = netPrice / unitConversion     │
  │                                                         │
  ├── 6. 计算附加价                                         │
  │     additionalPrice = netPrice/unitConv - scorporoPrice │
  │                                                         │
  └── 7. 本位币转换                                         │
        *BaseCur = exchangeRateBaseCur × 原值               │
```

---

## 五、来世 — MovementPrice 的下游消费

### 5.1 消费全景图

```
                        MovementPrice
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐      ┌────────────┐      ┌────────────┐
    │ 报表消费 │      │ 业务校验    │      │ 日结/月结   │
    └────┬────┘      └─────┬──────┘      └─────┬──────┘
         │                 │                   │
    ┌────┴────┐       ┌────┴────┐         ┌────┴────┐
    │         │       │         │         │         │
    ▼         ▼       ▼         ▼         ▼         ▼
  点价明细  采购库存  合同关闭  合同撤回   EOD滚动   EOM估值
  报表     定价报表  校验     校验       RI-/RI+   存货计价
    │         │
    ▼         ▼
  现货采购  发票未定价
  信息报表  检查
    │
    ▼
  信用/借记
  通知单
```

### 5.2 报表消费（10+ 个报表）

| 报表 | SQL/Java | 使用 MP 的哪些字段 | 做什么 |
|---|---|---|---|
| **定价明细列表** | MovementPriceMapper `selectListByCriteria` | 全部字段 + 30 表 JOIN | 主列表页展示 + Excel 导出 |
| **采购库存定价表** | MyReceiptDeliveryDetailsMapper `getProcurementInventoryPricingMainframeTest` | `SUM(quantity)` where priced=1 | 计算已定价量，判断定价量与入库量是否匹配 |
| **合同进度表** | MyReceiptDeliveryDetailsMapper `getContractProgressTable` | `SUM(parent_product_quantity)` | fixedQuantity（已定量）和 unFixedQuantity（未定量） |
| **现货采购信息** | SysReportMapper `spotPurchaseInfo` | `SUM(quantity * -1)` where priced=1 | 按合同/订单汇总已定价量 |
| **现货采购价格明细** | SysReportMapper `spotPurchaseInfoPriceDetail` | 全字段 + 3 路 UNION (Unknown/Fixed/Average) | 按定价方式分类展示价格明细 |
| **采购点价明细** | SysReportMapper `purchaseFixationDetailList` | 全字段 + pricing_formulas JOIN | 点价记录的完整价格信息 |
| **信用/借记通知单** | ReportMapper `Movement_Price` CTE | `ABS(SUM(amount_base_cur))`, `SUM(quantity)` | 定价金额 vs 发票金额的差额 |
| **发票未定价检查** | InvoiceMapper `selectInvoiceNotPriced` | `SUM(quantity)` where priced=1, valid=1 | 判断发票行是否还有未定价量 |
| **发票明细（均价）** | InvoiceMapper `average_price_data` CTE | `SUM(-quantity)`, `SUM(-total_value_base_cur)` | 加权平均价格计算 |
| **销售调差明细** | Java LambdaQueryWrapper | `SUM(quantity)` where priced=1 | 销售engagement的已定价量 |
| **EOM 存货估值** | EomStorageMapper (20+ 子查询) | quantity, settlementNetPrice, scorporoPrice, additionalPrice, basicPriceFormulaId | 月末存货计价、估值明细 |

### 5.3 业务校验

| 校验场景 | 代码位置 | 怎么用 MP |
|---|---|---|
| **合同关闭校验** | `ContractMonitorServiceImpl` L414 | `SUM(|quantity|)` where priced=1, valid=1 → 与入库量、发票量比对，三者必须一致（容差 1） |
| **定价完成度校验** | `ContractMonitorServiceImpl` L790, L845 | `SUM(quantity × -1)` per line → 与合同行量 × (1±溢短率) 比较 |
| **合同撤回校验** | `PhysicalDealsServiceImpl` L1944 | `SUM(quantity)` for deal → 非零时禁止撤回（Unknown 类型） |
| **点价均价计算** | `PricingServiceImpl.getAveragePrice()` L1481 | `SUM(settlementNetPrice × quantity) / SUM(quantity)` → 加权均价 |

### 5.4 日结 / 月结

| 场景 | 怎么用 MP |
|---|---|
| **EOD 日结滚动** | 读取 valid=1, priced=0 的 MP → 创建 RI-/RI+ 对 → 更新价格 |
| **EOD 合同过滤** | `EODMapper.getAllValidContractDataHME` → 找含未定价 MP 的合同行 |
| **EOM 月末估值** | 读取 priced=1, dailySettlementDate ≤ 月末 → 计算 fixedPriceFix / fixedPriceAverage |
| **现金流重生成** | 批量读取 priced=1, valid=1 的 MP → 触发 `generateCashFlowModel()` |

---

## 六、生命周期状态机

```
                    ┌──────────────────────────┐
                    │      合同审批 / 点价提交    │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │  valid=1, priced=0/1      │
                    │  actionType=FID/FIX       │
                    │  (初始记录)                │
                    └──────────┬───────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
    │ priced=1     │  │ priced=0     │  │ valid=-1     │
    │ 已定价       │  │ 未定价       │  │ 预备(均价)    │
    │ 直接消费     │  │ 等待日结     │  │ 等待激活     │
    └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
           │                │                 │
           │         ┌──────▼───────┐         │
           │         │  每日 EOD     │         │
           │         │  RI- 冲销     │         │
           │         │  valid→0     │         │
           │         └──────┬───────┘         │
           │                │                 │
           │         ┌──────▼───────┐  ┌──────▼───────┐
           │         │  RI+ 新建     │  │  日结激活     │
           │         │  valid=1     │  │  valid=1     │
           │         │  priced=1    │  │  priced=0/1  │
           │         │  新价格      │  │  新记录      │
           │         └──────┬───────┘  └──────┬───────┘
           │                │                 │
           └────────────────┼─────────────────┘
                            │
                   ┌────────▼────────┐
                   │  下游报表消费     │
                   │  SUM(quantity)  │
                   │  SUM(amount)    │
                   │  加权均价        │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │  合同关闭校验     │
                   │  MP量 = 入库量   │
                   │  MP量 = 发票量   │
                   └─────────────────┘
```

---

## 七、与 MovementQuantity 的孪生关系

MovementPrice 和 MovementQuantity 是**并行孪生表**：

| 维度 | MovementPrice | MovementQuantity |
|---|---|---|
| 追踪对象 | 价格（多少钱） | 量（多少货） |
| 核心字段 | basePrice, spread, settlementNetPrice | grossWeight, netWeight, blockNumber |
| 量字段 | quantity (定价量) | quantity (移动量) |
| 关联方式 | `movementQuantity.movementPriceId = movementPrice.id` |
| 动作类型 | 共用 MovementActionTypeEnum | 共用 MovementActionTypeEnum |
| 日结滚动 | RI-/RI+ 同步创建 | RI-/RI+ 同步创建 |
| 创建时机 | 合同审批/点价/日结 | 合同审批/点价/收发货/日结 |

**匹配键**: `physicalDealLineId + movementActionType + priceDate + valid + priced`

---

## 八、数据血缘图

```
┌─────────────────────────────────────────────────────────────┐
│                        数据源头                              │
│                                                             │
│  pricing_formulas ──→ 公式定义 (abbreviation, pyFilePath)    │
│  physical_deal_line ──→ 合同行 (quantity, pricingFormulaId)  │
│  price_triggering ──→ 点价单 (basePrice, spread, quantity)   │
│  forward_price ──→ 远期曲线 (marketPriceValue, date)         │
│  cashflow_model_values ──→ 现金流 (settlementPrice, spread)  │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    MovementPrice                             │
│                                                             │
│  价格: basePrice + spread + other = settlementNetPrice       │
│  量:   quantity (采购负/销售正)                               │
│  状态: valid × priced × onSpotPrice                          │
│  血缘: movementActionType + refDocumentType + refContract    │
└───────────────────────────────┬─────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ 报表 (10+)    │    │ 校验 (4)          │    │ 结算/估值         │
│              │    │                  │    │                  │
│ 定价明细列表  │    │ 合同关闭          │    │ EOD 日结滚动      │
│ 采购库存定价  │    │ 定价完成度        │    │ EOM 月末估值      │
│ 现货采购信息  │    │ 合同撤回          │    │ 现金流重生成      │
│ 信用借记通知  │    │ 点价均价          │    │ 发票未定价检查    │
│ 发票明细     │    │                  │    │                  │
│ EOM 存货估值  │    │                  │    │                  │
└──────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 九、关键代码入口速查

| 操作 | 类 | 方法 | 行号 |
|---|---|---|---|
| 合同审批生成 (固定) | MovementPriceServiceImpl | `generateByContractCommitFixed()` | ~L449 |
| 合同审批生成 (均价) | MovementPriceServiceImpl | `generateByContractCommitAverage()` | ~L510 |
| 点价提交生成 | MovementPriceServiceImpl | `generateByPricing()` | ~L1998 |
| 补充协议生成 | MovementPriceServiceImpl | `updateBySupplementCommit()` | - |
| 合同撤回冲销 | MovementPriceServiceImpl | `updateByContractCancle()` | - |
| **价格计算核心** | MovementPriceServiceImpl | **`fillPriceInfo()`** | **L2725** |
| 基础信息填充 | MovementPriceServiceImpl | `fillBasicInfo()` | ~L2640 |
| 日结滚动 (点价) | MovementPriceServiceImpl | `updateByDailySettlementTrigger()` | ~L2317 |
| 日结滚动 (均价) | MovementPriceServiceImpl | `updateByDailySettlementAverage()` | ~L2568 |
| 日结入口 | EODServiceImp | `UpdateMovementEOD()` | L371 |
| 列表查询 | MovementPriceMapper | `selectListByCriteria` | XML |
| Excel 导出 | MovementPriceServiceImpl | `pageExport()` | L3333 |
| 加权均价 | PricingServiceImpl | `getAveragePrice()` | L1481 |
| 合同关闭校验 | ContractMonitorServiceImpl | L414, L790, L845 | - |

---

## 十、常见问题

### Q1: 为什么同一个合同行会有几十条 MovementPrice？

因为日结 EOD 每天创建 RI-/RI+ 对。一个点价记录存在 30 天就会产生约 60 条 MP（30 条 RI- + 30 条 RI+），但只有最后一条 `valid=1` 的是有效的，其余都是历史审计链。

### Q2: `quantity` 为什么是负数？

采购方向（`ps_flag='P'`）的 MP 记录 quantity 为负。这是符号约定：采购 = 买入 = 负（从库存角度）。查询时通常用 `SUM(quantity × -1)` 或 `ABS(SUM(quantity))` 还原为正数。

### Q3: `priced=0` 的记录有什么用？

未定价记录代表"已存在但价格尚未确定"的头寸。它参与日结 EOD 的滚动（RI-/RI+），但不参与报表的已定价量计算（报表通常过滤 `priced=1`）。当价格确定后，`priced` 从 0 变为 1。

### Q4: `valid=-1` 是什么？

仅用于均价（BasicAveragePrice）。合同审批时，未来定价日的 MP 记录以 `valid=-1` 创建（预备状态）。当日期临近时，日结 EOD 将其转为 `valid=1, priced=0`，再在定价日到达时激活为 `priced=1`。

### Q5: RI-/RI+ 为什么不直接更新原记录？

为了**审计追溯**。每次日结滚动都保留完整的变更历史：谁在什么日期以什么价格被冲销，新的价格是什么。这在金属贸易中是合规要求。

### Q6: MovementPrice 和 cashflow_model_values 的关系？

两者是**互相影响**的：
- 合同保存时：现金流引擎 → 生成 cashflow_model_values → MovementPrice 从中读取 spread/otherCost
- 日结时：MovementPrice 的 RI+ 回写 → 更新 PriceTriggering → 触发现金流重生成
- 报表中：两者独立被查询，MovementPrice 提供定价维度，cashflow 提供结算维度
