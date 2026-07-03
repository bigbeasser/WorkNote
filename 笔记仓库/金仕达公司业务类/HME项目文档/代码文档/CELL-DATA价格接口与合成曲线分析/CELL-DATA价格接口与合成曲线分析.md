# CELL-DATA 价格接口与合成曲线计算分析

> [!info] 文档信息
> - **源文件**：`CellDataServiceImpl.java`（价格拉取）、`ForwardPriceServiceImpl.java`（合成曲线计算）
> - **分析日期**：2026/07/02

---

## 一、六大价格接口总览

| 编号 | 接口名 | 数据来源 | 价格类型 | 存储目标 | 币种 | 金属 |
|------|--------|---------|---------|---------|------|------|
| 74 | **GetWmnoteaci** | CELL-DATA ACI | LME 晚间收盘价 | ForwardPrice（日结） | EUR | ACI 相关 |
| 75 | **GetLowest** | CELL-DATA 最低价 | LME/Bloomberg 最低价 | ForwardPrice + IntradayPrice | USD/EUR/GBP | CU/AL/ZN/PB/SN/NI |
| 76 | **GetEveneval** | CELL-DATA 晚间价 | LME 晚间 Bid/Ask | ForwardPrice（日结） | USD | 所有基本金属 |
| 77 | **GetPreciousMet** | CELL-DATA 贵金属 | AG 官方/实时价格 | ForwardPrice + IntradayPrice | USD/EUR | AG（白银） |
| 78 | **GetCurrency** | CELL-DATA 汇率 | ECB/LME/Bloomberg/ICE 汇率 | ForwardPrice + IntradayPrice | 多币种对 | — |
| 79 | **GetMetals** | CELL-DATA 金属价 | LME/Bloomberg 金属远期价 | ForwardPrice + IntradayPrice | USD/EUR/GBP | 所有基本金属 |

---

## 二、各接口详细分析

### 2.1 GetWmnoteaci (74) — ACI 价格

**调用参数**：`request.getParameter()` 传入 SOAP 接口

**返回数据结构**：`MethodGetWmnoteaciResponseItem`
- `aciwmnote` — ACI 加权均价
- `lowwmnote` — ACI 最低价
- `highwmnote` — ACI 最高价
- `datequote` — 报价日期

**价格处理**：
```
① 拉取数据 → 判断是否 LME 节假日（是则跳过）
② 价格 × 10（单位换算）
③ 按 symbol 分别写入三个合约文本：
   ├── "aciwmnote" → ACI加权均价合约
   ├── "lowwmnote" → ACI最低价合约
   └── "highwmnote" → ACI最高价合约
④ 币种固定为 EUR
⑤ 价格类型固定为 SETTLEMENT_PRICE（结算价）
⑥ 存储目标：ForwardPrice（日结价格表）
```

**存储逻辑**（所有接口通用）：
```
查询 forward_contract 表 → 按 symbol + currencyCode 匹配合约文本
  ↓
查询 forward_price 表 → 是否已有同日期+同合约+同价格类型的记录
  ├── 有 → UPDATE market_price_value
  └── 无 → INSERT 新记录
```

---

### 2.2 GetLowest (75) — 最低价

**调用参数**：多种参数，决定拉取哪种市场数据

| 参数 | 市场 | 存储类型 | 币种 |
|------|------|---------|------|
| `CU/AL/ZN/PB/SN/NI` | LME 日内 | **IntradayPrice**（实时） | USD + EUR |
| `OFFCUBLOOM/OFFZNBLOOM/...` | Bloomberg | **ForwardPrice**（日结） | USD + EUR |
| `OFFCUGBPLME/OFFZNG BPLME/...` | LME 官方 | **ForwardPrice**（日结） | USD + GBP |

**价格处理**：
```
① 拉取数据 → 判断 LME 节假日
② 根据参数类型分流：
   ├── 日内参数(CU/AL等) → IntradayPrice（实时价格表）
   │   ├── USD: response.lowest
   │   └── EUR: response.loweste
   │
   ├── Bloomberg参数(OFFCUBLOOM等) → ForwardPrice
   │   ├── USD: response.lowest → publication="Bloomberg"
   │   ├── EUR: response.loweste → publication="Bloomberg"
   │   └── EUR: response.loweste → publication="LME"（额外转存至LME合约）
   │
   └── LME官方参数(OFFCUGBPLME等) → ForwardPrice
       ├── USD: response.lowest → publication="LME"
       └── GBP: response.loweste → publication="LME"
③ marker 固定为 "Lowest"
④ 价格类型固定为 SETTLEMENT_PRICE
```

**特殊逻辑**：Bloomberg 的欧元价格会**同时写入 LME 合约**（代码注释了部分限制条件）

---

### 2.3 GetEveneval (76) — 晚间价

**调用参数**：`request.getParameter()` 传入金属代码

**返回数据结构**：`List<MethodGetEvenevalResponseItem>`（多条记录）
- `metalcode` — 金属代码
- `datequote` — 报价日期
- `quotebid` — Bid 价（买入价）
- `quoteask` — Ask 价（卖出价/结算价）

**价格处理**：
```
① 拉取数据 → 遍历每条记录 → 判断 LME 节假日
② 每条记录写入两种价格类型：
   ├── BID_PRICE = quotebid（买入价）
   └── SETTLEMENT_PRICE = quoteask（结算价）
③ publication 固定为 "EVE"
④ 币种固定为 USD
⑤ 存储目标：ForwardPrice（日结价格表）
```

---

### 2.4 GetPreciousMet (77) — AG 实时价格

**调用参数**：三种模式

| 参数 | 模式 | 存储类型 | 币种 | 价格类型 |
|------|------|---------|------|---------|
| `officials` | 官方日结 | ForwardPrice | USD | SETTLEMENT_PRICE（quote1） |
| `rteuro` | 实时欧元 | IntradayPrice | EUR | BID_PRICE(quote1) + SETTLEMENT_PRICE(quote2) |
| `rtdollar` | 实时美元 | IntradayPrice | USD | BID_PRICE(quote1) + SETTLEMENT_PRICE(quote2) |

**价格处理**：
```
① 根据参数判断模式
② officials 模式：
   ├── 遍历 responseItems
   ├── 判断 LME 节假日
   └── 写入 ForwardPrice（SETTLEMENT_PRICE）
③ rteuro/rtdollar 模式：
   ├── 遍历 realTimeResponseItems
   ├── 判断 LME 节假日
   ├── 写入 IntradayPrice（BID_PRICE = quote1）
   └── 写入 IntradayPrice（SETTLEMENT_PRICE = quote2）
```

---

### 2.5 GetCurrency (78) — 汇率

**调用参数**：四种模式

| 参数 | 来源 | 存储类型 | publication |
|------|------|---------|-------------|
| `ecboff` | ECB 官方汇率 | ForwardPrice | ECB |
| `lmeoff` | LME 官方汇率 | ForwardPrice | LME |
| `bloomboff` | Bloomberg 汇率 | ForwardPrice | Bloomberg |
| `rtcurr` | ICE 实时汇率 | IntradayPrice | ICE |

**价格处理**：
```
① 根据参数判断模式
② 解析 currcode（如 "USD-EUR"）→ 拆分为 currencyCode
③ 每种模式写入两种价格：
   ├── BID_PRICE = bid（买入价）
   └── SETTLEMENT_PRICE = ask（卖出价）
④ 查询合约文本时使用 selectCurrencyBySymbolAndMarkerAndCurve（专用查询）
```

**特殊逻辑**：`currcode` 格式为 `"USD-EUR"`，拆分后取第一段作为 currencyCode 用于匹配合约

---

### 2.6 GetMetals (79) — 金属价

**调用参数**：六种模式

| 参数 | 模式 | 存储类型 | publication | 币种 |
|------|------|---------|-------------|------|
| `offdoll` | LME美元官方 | ForwardPrice | LME | USD |
| `offeurobloomb` | Bloomberg欧元 | ForwardPrice | Bloomberg | EUR |
| `offeurolme` | LME欧元官方 | ForwardPrice | LME | EUR |
| `offeurolmegbpusd` | LME英镑 | ForwardPrice | LME | GBP |
| `rtmet` | 实时Cash | IntradayPrice | LME | USD + EUR |
| `rtmet3M` | 实时3M | IntradayPrice | LME | USD + EUR |

**价格处理**：
```
① 根据参数分流到不同处理方法
② offdoll：
   ├── 解析 metalcode（如 "CU-3M"）→ 判断 Cash/3M marker
   ├── BID_PRICE = bid
   └── SETTLEMENT_PRICE = ask
③ offeurobloomb：
   ├── publication = "Bloomberg"
   ├── BID_PRICE = bide
   └── SETTLEMENT_PRICE = aske
④ offeurolme：
   ├── publication = "LME"
   ├── BID_PRICE = bide
   └── SETTLEMENT_PRICE = aske
⑤ offeurolmegbpusd：
   ├── publication = "LME", 币种 = GBP
   └── 仅写入 SETTLEMENT_PRICE = aske（bid 总是0，跳过）
⑥ rtmet/rtmet3M：
   ├── marker = "Cash" 或 "3M"
   ├── USD: BID=bid, SETTLEMENT=ask
   └── EUR: BID=bide, SETTLEMENT=aske
```

---

## 三、通用存储机制

### 3.1 合约文本匹配

所有接口拉取价格后，都通过 `forwardContractMapper.selectBySymbolAndMarkerAndCurve()` 查找匹配的合约文本：

```sql
-- 查询条件
SELECT * FROM forward_contract
WHERE symbol = #{symbol}            -- 金属代码/汇率代码
  AND marker = #{marker}            -- 标记（Cash/3M/Lowest/All）
  AND publication_name = #{publicationName}  -- 数据源（LME/Bloomberg/ECB等）
  AND currency_code = #{currencyCode}        -- 币种
  AND inactive_flag = false
```

### 3.2 价格存储（二选一）

| 存储表 | 适用场景 | 唯一键 |
|--------|---------|--------|
| **forward_price** | 日结价格（每日一条） | contract_id + curve_id + date + price_type |
| **intraday_price** | 实时价格（每日多条） | contract_id + curve_id + date + time + price_type |

### 3.3 写入逻辑（所有接口统一）

```
查询是否已有记录：
  ├── 已有 → UPDATE market_price_value（价格值）
  └── 没有 → INSERT 新记录
              ├── id = SnowFlake 雪花ID
              ├── session = "0"
              ├── status = 1
              └── market_price_type = SETTLEMENT_PRICE / BID_PRICE
```

### 3.4 LME 节假日过滤

所有接口在写入价格前都会检查：
```java
Set<String> holidays = riskUtil.getLmeHolidays("LME");
if (holidays.contains(datequote)) return;  // 节假日不写入
```

---

## 四、合成曲线（Composite Curve）计算

### 4.1 什么是合成曲线

某些合约文本（ForwardCurve）不是直接从 CELL-DATA 拉取价格，而是**引用其他合约文本的价格，通过公式计算得出**。这类合约文本的 `composite_flag = 'Y'`。

```
┌──────────────────────────────────────────────────────────────┐
│                    合约文本层级关系                            │
│                                                              │
│  基础合约文本（composite_flag = 'N'）                         │
│  ├── LME-CU-Cash     ← GetMetals 直接写入价格                │
│  ├── LME-CU-3M       ← GetMetals 直接写入价格                │
│  ├── Bloomberg-CU-EUR ← GetLowest 直接写入价格               │
│  └── ECB-USD-EUR     ← GetCurrency 直接写入价格              │
│                                                              │
│  合成合约文本（composite_flag = 'Y'）                         │
│  └── 铜欧元综合价     ← 公式: Curve(LME-CU-Cash) ×           │
│                         Curve(ECB-USD-EUR) + spread          │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 forward_composite_curve 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 主键 |
| name | varchar | 名称 |
| **forward_curve_id** | **bigint** | **所属合约文本ID**（合成曲线本身） |
| **composite_forward_curve_id** | **bigint** | **引用的基础合约文本ID** |
| curve_formula_range_id | bigint | 关联的公式区间ID |
| seq | varchar | 序号（同一公式内多个引用项的排序） |
| composite_seq | varchar | 合成序号 |
| **formula_type** | **varchar** | **公式类型：`Curve` 或 `compositeCurve`** |
| **marker** | **varchar** | **引用合约的标记（Cash/3M/All/Lowest）** |
| **last_trading_day** | **varchar** | **最后交易日** |
| weighted | double | 权重 |
| spread | double | 价差/升贴水 |
| unit_id | bigint | 单位 |
| currency_id | bigint | 币种 |
| risk_flag | varchar | 风险标记 |
| status | int | 状态 |

### 4.3 formula_type 的两种类型

| formulaType | 含义 | 公式占位符格式 |
|-------------|------|-------------|
| **`Curve`** | 直接引用基础合约文本的价格 | `Curve(合约文本ID, marker, lastTradingDay)` |
| **`compositeCurve`** | 引用另一个合成合约文本的价格（递归） | `compositeCurve(合约文本ID, marker, lastTradingDay, compositeSeq)` |

### 4.4 触发时机

合成曲线计算在两个场景触发：

```
场景一：日结计算（endOfDay）
  ForwardPriceServiceImpl.calculateCurvePrice()
  ├── 定时任务触发（每日收盘后）
  └── calculateFrequency = "endOfDay"
  → 从 forward_price 表取当日结算价作为输入

场景二：实时计算（realTime）
  ForwardPriceServiceImpl.calculateCurvePrice()
  ├── 价格拉取后触发
  └── calculateFrequency = "realTime"
  → 从 intraday_price 表取最新实时价作为输入
```

### 4.5 完整计算流程

```
═══════════════════════════════════════════════════════════════
  Step 1：查找需要计算的合成曲线合约
═══════════════════════════════════════════════════════════════

  SQL: selectMixedCurve(contractIds, calculateFrequency)

  查询条件：
    forward_curve.composite_flag = 'Y'      ← 只查合成曲线
    forward_contract.calculate_frequency LIKE '%{calculateFrequency}%'
    forward_contract.inactive_flag = false

  结果：List<ForwardContract> contracts
  每个 contract 带有 priority（优先级）和 rangeFormula（公式）


═══════════════════════════════════════════════════════════════
  Step 2：加载公式区间配置
═══════════════════════════════════════════════════════════════

  SQL: curve_formula_ranges
  WHERE forward_curve_id IN (forwardCurveIds)
    AND calculate_frequency LIKE '%{calculateFrequency}%'

  结果：Map<forwardCurveId, CurveFormulaRanges>
  CurveFormulaRanges 包含：
    - calculateFrequency: "endOfDay" 或 "realTime"
    - marker: 标记
    - rangeFormula: 计算公式（如 "Curve(123,Cash,2024-04-20) * Curve(456,Cash,2024-04-20)"）


═══════════════════════════════════════════════════════════════
  Step 3：加载合成曲线引用关系
═══════════════════════════════════════════════════════════════

  SQL: forward_composite_curve
  WHERE forward_curve_id IN (forwardCurveIds)
    AND marker IS NOT NULL
    AND inactive_flag = false

  结果：List<ForwardCompositeCurve>
  每条记录描述一个引用关系：
    forwardCurveId → compositeForwardCurveId（引用哪个基础合约）
    marker → 基础合约的标记（Cash/3M/All/Lowest）
    formulaType → Curve 或 compositeCurve


═══════════════════════════════════════════════════════════════
  Step 4：加载所有基础合约信息
═══════════════════════════════════════════════════════════════

  SQL: forward_contract
  WHERE marker IN ('All', '3M', 'Cash', 'Lowest')
    AND inactive_flag = false

  结果：所有基础合约文本，用于按 marker 查找 contractId


═══════════════════════════════════════════════════════════════
  Step 5：加载当日/当前价格
═══════════════════════════════════════════════════════════════

  日结模式（endOfDay）：
    SQL: getForwardPriceInCurvePrice(queryDate)
    → Map<contractId, marketPriceValue>（结算价）

  实时模式（realTime）：
    SQL: getRealTimePriceInCurvePrice(queryDate)
    → Map<contractId, marketPriceValue>（最新实时价）


═══════════════════════════════════════════════════════════════
  Step 6：按优先级计算（核心步骤）
═══════════════════════════════════════════════════════════════

  calculateByPriority(contractPrice, contracts, compositeList, oldContracts)

  ┌─────────────────────────────────────────────────────────┐
  │ 6a. 按 priority 分组并排序（从小到大）                    │
  │     SortedMap<priority, List<ForwardContract>>          │
  │                                                         │
  │ 6b. 按优先级逐级计算：                                    │
  │     for (priority : 从小到大) {                          │
  │       for (每个合成合约 contract) {                       │
  │                                                         │
  │         ① 查找该合约的 composite 引用列表                  │
  │            compositeMap[forwardCurveId + "-" + seq]      │
  │                                                         │
  │         ② 对每个引用项：                                   │
  │            按 marker 找到基础合约的 contractId             │
  │            从 contractPrice 中取出基础价格                  │
  │                                                         │
  │         ③ 构建公式变量映射：                               │
  │            if formulaType == "Curve":                    │
  │              key = "Curve(合约ID,marker,lastTradingDay)" │
  │            else:                                         │
  │              key = "compositeCurve(合约ID,marker,        │
  │                     lastTradingDay,compositeSeq)"        │
  │            value = 基础合约的价格                          │
  │                                                         │
  │         ④ 公式替换 + JEXL 表达式求值：                     │
  │            formula = contract.rangeFormula               │
  │            将公式中的占位符替换为实际价格值                  │
  │            JexlEngine 计算表达式                           │
  │            结果 → BigDecimal（精度5位）                    │
  │                                                         │
  │         ⑤ 结果写回 contractPrice Map                     │
  │            contractPrice.put(contract.id, price)         │
  │            → 低优先级的结果可供高优先级引用                 │
  │       }                                                 │
  │     }                                                   │
  └─────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
  Step 7：落库
═══════════════════════════════════════════════════════════════

  日结：saveCurveForwardPriceData()
    → 写入 forward_price 表

  实时：saveCurveTimePriceData()
    → 写入 intraday_price 表
```

### 4.6 公式计算示例

假设合约文本 A（合成曲线）的 `rangeFormula` 为：

```
Curve(100,Cash,2024-04-20) * Curve(200,Cash,2024-04-20) + 15.5
```

其中：
- `Curve(100,Cash,...)` → 引用合约文本100（LME铜Cash美元价）= 9500
- `Curve(200,Cash,...)` → 引用合约文本200（USD/EUR汇率）= 0.92
- `15.5` → 固定升贴水（spread）

计算过程：
```java
// Step 1: 替换占位符
formula = "Curve(100,Cash,2024-04-20) * Curve(200,Cash,2024-04-20) + 15.5"
       → "9500 * 0.92 + 15.5"

// Step 2: JEXL 表达式求值
JexlEngine jexl = new JexlBuilder().create();
JexlExpression expression = jexl.createExpression("9500 * 0.92 + 15.5");
Object result = expression.evaluate(context);
// result = 8755.5

// Step 3: 精度处理
BigDecimal price = new BigDecimal("8755.5").setScale(5, RoundingMode.HALF_UP);
// price = 8755.50000
```

### 4.7 优先级（Priority）机制

```
  Priority 1（最先计算）：只引用基础合约的合成曲线
    例：铜欧元价 = LME铜美元价 × USD/EUR汇率

  Priority 2（后计算）：引用 Priority 1 结果的合成曲线
    例：铜欧元综合价 = 铜欧元价 + spread

  Priority N：引用前面所有优先级的结果
    → 保证计算顺序正确，不会出现引用尚未计算的价格
```

**关键点**：低优先级计算完成后，结果写回 `contractPrice` Map，高优先级可以直接引用。

### 4.8 哪些合约文本会触发合成计算？

```sql
-- 查询条件（selectMixedCurve）
SELECT fc.* FROM forward_contract fc
INNER JOIN forward_curve fcv ON fc.forward_curve_id = fcv.id
WHERE fcv.composite_flag = 'Y'                    -- 合约文本标记为合成曲线
  AND fc.calculate_frequency LIKE '%{频率}%'        -- 计算频率匹配
  AND fc.inactive_flag = false                     -- 未停用
  AND fc.marker IN ('All', '3M', 'Cash', 'Lowest') -- 有效标记
```

**总结**：只有同时满足以下条件的合约文本才会参与合成计算：
1. 所属的合约文本（ForwardCurve）`composite_flag = 'Y'`
2. 合约（ForwardContract）的 `calculate_frequency` 包含当前计算频率
3. 合约未停用
4. 合约的 marker 为 All/3M/Cash/Lowest 之一

---

## 五、完整数据流全景图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CELL-DATA 价格拉取 → 合成曲线计算                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ① 定时任务 / 手动触发                                               │
│     │                                                               │
│     ▼                                                               │
│  ② 拉取 CELL-DATA 价格（6个接口）                                    │
│     ┌──────────────────────────────────────────────────────────┐    │
│     │ GetWmnoteaci(74) → ACI价格 × 10 → ForwardPrice          │    │
│     │ GetLowest(75)    → 最低价 → ForwardPrice/IntradayPrice  │    │
│     │ GetEveneval(76)  → 晚间Bid/Ask → ForwardPrice           │    │
│     │ GetPreciousMet(77) → AG价格 → ForwardPrice/IntradayPrice│    │
│     │ GetCurrency(78)  → 汇率Bid/Ask → ForwardPrice/Intraday  │    │
│     │ GetMetals(79)    → 金属Bid/Ask → ForwardPrice/Intraday  │    │
│     └──────────────────────────────────────────────────────────┘    │
│                    │                                                │
│                    ▼                                                │
│  ③ 写入基础合约文本的价格                                             │
│     forward_price 表（日结） / intraday_price 表（实时）              │
│                    │                                                │
│                    ▼                                                │
│  ④ 触发合成曲线计算 calculateCurvePrice()                            │
│     ┌──────────────────────────────────────────────────────────┐    │
│     │ 查找 composite_flag='Y' 的合约文本                        │    │
│     │ 加载 forward_composite_curve 引用关系                     │    │
│     │ 加载 curve_formula_ranges 公式配置                        │    │
│     │ 按 priority 从小到大逐级计算                               │    │
│     │   ├── 替换公式占位符 Curve(...) / compositeCurve(...)      │    │
│     │   ├── JEXL 表达式求值                                     │    │
│     │   └── 结果写回 contractPrice Map（供下级引用）             │    │
│     │ 落库 → forward_price / intraday_price                     │    │
│     └──────────────────────────────────────────────────────────┘    │
│                    │                                                │
│                    ▼                                                │
│  ⑤ 最终结果                                                         │
│     所有合约文本（基础 + 合成）都有当日/当前价格                       │
│     → 供月结、估值、风控等下游使用                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 六、关键文件索引

| 层级 | 文件路径 | 说明 |
|------|---------|------|
| **SOAP接口** | `bcadmin-docking/.../celldata/soap/java/WsCellDataSoap.java` | CELL-DATA SOAP 客户端 |
| **接口实现** | `bcadmin-docking/.../service/impl/CellDataServiceImpl.java` | 6个价格接口的拉取+存储逻辑 |
| **合成曲线计算** | `bcadmin-system/.../service/impl/ForwardPriceServiceImpl.java` | `calculateCurvePrice()` + `calculateByPriority()` |
| **合成曲线CRUD** | `bcadmin-system/.../service/impl/ForwardCompositeCurveServiceImpl.java` | 合成曲线配置管理 |
| **合约文本查询** | `bcadmin-db/.../dao/ForwardContractMapper.java` | `selectBySymbolAndMarkerAndCurve()` / `selectMixedCurve()` |
| **Entity** | `bcadmin-db/.../domain/ForwardCompositeCurve.java` | 合成曲线引用关系实体 |
| **Entity** | `bcadmin-db/.../domain/ForwardPrice.java` | 日结价格实体 |
| **Entity** | `bcadmin-db/.../domain/IntradayPrice.java` | 实时价格实体 |
| **枚举** | `bcadmin-docking/.../common/DockingBusinessType.java` | 接口编号定义（74-79） |
| **Controller** | `bcadmin-docking/.../rest/CellDataController.java` | 价格接口 REST 入口 |
| **Controller** | `bcadmin-system/.../rest/CurveController.java` | 曲线管理 REST 入口 |
