# Python 定价引擎 · 调用链路全解析

> Java 如何通过 Thrift RPC 调用 Python 脚本计算组合计价公式

---

## 一、为什么需要 Python

系统中计价公式有两种计算路径：

| 路径 | 适用场景 | 实现方式 |
|---|---|---|
| **Java 原生** | 单一公式（纯固定价/纯点价/纯均价） | `a65` PricingEngine 直接在 Java 中计算 |
| **Python 引擎** | 组合公式（基础价 + 升贴水 + 加工费 + 附加价） | `a65` → `a153.executePy()` → Python 脚本 |

当合同行的 `pricingType = FORMULA` 时，走 Python 路径。Python 脚本存储在数据库 `pricing_formulas.pricing_formula` 字段中，运行时写入临时 `.py` 文件执行。

---

## 二、完整调用链

```
订单保存 / 现金流生成
  │
  ▼
a65 PricingEngine (Java)
  │  pricingType == FORMULA
  │
  ▼
a65.a724() → a153.a1485(pricingFormulaId, pricingFormulaIdParameters)
  │
  ▼
a153.executePy()                                    [a153.java L57-168]
  │
  ├── 1. 构建 a104 请求对象
  │     ├── priceFormulaId = 合同行的 pricingFormulaId
  │     ├── priceFormulaParameters = 合同行的 pricingFormulaIdParameters JSON
  │     ├── priceFormulaGroupKey = 缓存 key（合同号+入库信息）
  │     └── context = a93 上下文对象
  │
  ├── 2. 构建 context (a93 对象)
  │     ├── header = PhysicalDeals 合同主表
  │     ├── line = PhysicalDealLine 合同行
  │     ├── headerValues = CashflowModelHeaderValues 现金流头
  │     ├── curveDate = 当前曲线日期
  │     ├── delta = 价格偏移量 Map
  │     ├── events = 收发货事件日期 Map
  │     └── eventTypeList = 事件类型字典
  │
  ▼
RiskValuationUtil.calculateCompositionPrice(a104)   [RiskValuationUtil.java L67-102]
  │
  ├── 3. 查 Redis 缓存
  │     key = "PythonResult:calculateCompositionPrice:" + groupKey
  │     命中 → 直接返回缓存的 a119 结果
  │
  ├── 4. 获取 Python 脚本路径
  │     PythonPyPathServiceImpl.getPricingFormulaPyFilePathById(id)
  │     │
  │     ├── 查 Redis 缓存 → 查 DB pricing_formulas 表
  │     ├── 读取 pricing_formulas.pricing_formula (Python 源码文本)
  │     ├── 检查 pricing_formulas.py_file_path 是否已有文件
  │     │     ├── 有且文件存在 → 直接返回路径
  │     │     └── 无或文件不存在 → 写入临时文件
  │     └── MyFileUtil.saveAndGetPathName()
  │           路径 = fileProperties.path + hash("python_script_" + 源码) + ".py"
  │
  ├── 5. 调用 PythonUtils.exec_python(pyPath, formulaParams, contextJson)
  │
  ▼
PythonUtils.exec_python()                            [PythonUtils.java L70-129]
  │
  ├── 6. 构造命令行参数
  │     argList = ["python", pyPath, formulaParams, contextJson]
  │     │
  │     ├── Windows 特殊处理: convertJsonInWindows() 转义引号
  │     └── 清理 context 中的 pricingFormulaIdParameters（防参数过大）
  │
  ├── 7. Runtime.getRuntime().exec(args)
  │     │
  │     ├── 提交两个线程读取 stdout/stderr（防缓冲区死锁）
  │     │     PythonResultRunnable → BufferedReader.readLine()
  │     │
  │     └── process.waitFor(20, TimeUnit.SECONDS)  ← 最多等 20 秒
  │
  ├── 8. 如果 "python" 失败 → 重试 "python3"
  │
  ▼
Python 脚本执行
  │
  ├── 9. Python 脚本接收两个命令行参数:
  │     sys.argv[1] = pricingFormulaIdParameters JSON
  │     sys.argv[2] = context JSON (a93 序列化)
  │
  ├── 10. Python 脚本通过 Thrift RPC 回调 Java 服务
  │     ctrm_thrift_client.execute("API.Pricing", "fetch", {...})
  │     │
  │     ├── 连接 127.0.0.1:9000 (Thrift Server)
  │     ├── saveArgs(processId, args) → 将参数存入 Java 侧
  │     ├── execute(processId, apiKey, cmd) → Java 执行计算
  │     └── 返回 JSON 结果（远期曲线价格等）
  │
  ├── 11. Python 脚本计算组合价格
  │     ├── 解析 pricingFormulaIdParameters JSON
  │     ├── 按 abbreviation 分支处理每个公式组件
  │     ├── 调用 utils.py 中的 valueIndex/valueSpread 等函数
  │     ├── 通过 Thrift 获取远期曲线价格、汇率、单位转换
  │     └── 输出 JSON 结果到 stdout
  │
  ▼
Java 解析结果                                         [RiskValuationUtil.java L91]
  │
  ├── 12. JSONObject.parseObject(stdout第一行, a119.class)
  │
  ├── 13. 写入 Redis 缓存
  │
  ▼
a153.a1485() 使用 a119 结果                           [a153.java L187-232]
  │
  ├── settlementPrice = finalPrice - spread - otherCostPrice
  ├── settlementNetPrice = round(finalPrice, roundingDigits)
  ├── pricingStatus = FIXED 或 FLOATING（取决于是否有未来定价日）
  └── 写入 CashflowModelValues
```

---

## 三、Python 脚本从哪来

### 3.1 存储位置

Python 脚本**不是**项目中的静态文件，而是存储在数据库 `pricing_formulas` 表中：

| 字段 | 类型 | 说明 |
|---|---|---|
| `pricing_formula` | LONGVARCHAR (TEXT) | Python 源码文本 |
| `py_file_path` | VARCHAR(255) | 运行时生成的临时文件路径 |

### 3.2 文件生成流程

```
PythonPyPathServiceImpl.getPricingFormulaPyFilePathById(id)
  │
  ├── 1. 查 Redis: "PythonPath:PricingFormulas:{id}"
  │     命中 → 返回 pyFilePath
  │
  ├── 2. 查 DB: pricingFormulasMapper.selectByPrimaryKey(id)
  │
  ├── 3. 检查 pricing_formulas.py_file_path
  │     ├── 非空 且 文件存在 → 直接返回
  │     └── 空 或 文件不存在 → 生成文件
  │
  └── 4. MyFileUtil.saveAndGetPathName(basePath, pythonSourceCode)
        │
        ├── 文件名 = hash("python_script_" + 源码) + ".py"
        │     用 hashCode 确保相同源码不会重复生成文件
        │
        ├── 写入文件: basePath + hashCode + ".py"
        │
        └── 更新 DB: pricingFormulasMapper.updateByPrimaryKeySelective(pyFilePath)
```

### 3.3 项目中的 utils.py

`utils.py`（项目根目录）是 Python 脚本的**公共工具库**，被数据库中的动态脚本 `import` 使用：

| 函数 | 用途 |
|---|---|
| `valueIndex(index, context)` | 从远期曲线获取均价/点价价格 |
| `valueIndexNew(index, context)` | 新版指数取值（支持 marker、forwardContract） |
| `valueSpread(spreadObj, ...)` | 计算升贴水（固定/浮动） |
| `getPriceAtTargetCurrency(...)` | 币种+单位转换 |
| `getPriceAtTargetCurrencyByFixingDates(...)` | 按定价日列表做币种转换 |
| `calc(model)` | 调用 Java 侧的组合计算 |

---

## 四、Python ↔ Java 的 Thrift 桥接

### 4.1 架构

```
┌──────────────────┐         ┌──────────────────────┐
│   Python 脚本     │         │   Java Thrift Server  │
│                  │  TCP    │   127.0.0.1:9000      │
│  ctrm_thrift_    │ ──────→ │                       │
│  client.py       │         │  ThriftServiceManager │
│                  │ ←────── │  ├── saveArgs()       │
│  调用:           │         │  └── execute()        │
│  _c.execute(     │         │       │               │
│    "API.Pricing", │         │       ▼               │
│    "fetch",      │         │  路由到对应的 Java      │
│    {...}         │         │  Service 方法          │
│  )               │         │                       │
└──────────────────┘         └──────────────────────┘
```

### 4.2 ctrm_thrift_client.py 调用流程

```python
def execute(apiKey, cmd, args):
    # 1. 建立 TCP 连接到 Thrift Server
    transport = TSocket.TSocket('127.0.0.1', 9000)
    transport = TTransport.TFramedTransport(transport)
    protocol = TCompactProtocol.TCompactProtocol(transport)
    client = ThriftServiceManager.Client(protocol)

    # 2. 生成唯一 processId
    processId = str(uuid.uuid1())

    # 3. 将参数保存到 Java 侧（避免命令行参数过长）
    transport.open()
    client.saveArgs(processId, json.dumps(args))

    # 4. 执行远程调用
    executeArgs = ThriftServiceManager.ExecuteArgs(processId, apiKey, cmd)
    result = client.execute(executeArgs)

    transport.close()
    return json.loads(result)
```

### 4.3 Python 中常用的 Thrift API

| apiKey | cmd | 用途 |
|---|---|---|
| `API.Pricing` | `fetch` | 获取远期曲线价格列表 |
| `API.Pricing` | `getPricingRangeRulePyPath` | 获取定价区间规则的 Python 脚本路径 |
| `API.MarketingSpread` | `fetch` | 获取市场升贴水 |
| `API.MarketingSpread` | `calc` | 组合价格计算 |
| `API.MarketingSpread` | `getPriceAtTargetCurrency` | 币种/单位转换 |

---

## 五、Python 脚本内部逻辑

数据库中的 Python 脚本（`pricing_formulas.pricing_formula`）的典型结构：

```python
import json
import sys
import utils
from utils import valueIndex, valueIndexNew, valueSpread, getPriceAtTargetCurrency

# 1. 接收命令行参数
formulaParams = json.loads(sys.argv[1])  # pricingFormulaIdParameters JSON
context = json.loads(sys.argv[2])        # a93 context JSON

# 2. 解析公式组件
result = {
    "finalPrice": 0.0,
    "basicPrice": 0.0,
    "spread": 0.0,
    "otherCostPrice": 0.0,
    "pricingType": "Fixed",
    "priceDetail": [],
    "fixingDates": []
}

# 3. 遍历公式组件，按 abbreviation 分支处理
for component in formulaParams:
    abbreviation = component.get("abbreviation", "")
    level = component.get("level", 0)
    params = component.get("formula_parameters", {})

    if level == 1:  # 基础价
        if abbreviation == "BasicFixedPrice":
            # 固定价: 直接取 fixedPrice 参数
            result["basicPrice"] = float(params["fixedPrice"]["value"])

        elif abbreviation == "BasicTriggeredPrice":
            # 点价: 通过 Thrift 从远期曲线取价
            indexResult = valueIndexNew({
                "pricingType": "Triggered",
                "value": {
                    "baseIndex": params["pricingIndex"],
                    "beginDate": params["beginDate"],
                    "endDate": params["endDate"],
                    "marker": params.get("marker", {}),
                    "forexMarketId": params.get("forexMarketId", {}),
                    ...
                }
            }, context)
            result["basicPrice"] = indexResult["curvePrice"]

        elif abbreviation == "BasicAveragePrice":
            # 均价: 通过 Thrift 获取期间所有定价日的价格，取平均
            indexResult = valueIndexNew({
                "pricingType": "Average",
                "value": {
                    "baseIndex": params["baseIndex"],
                    "beginDate": params["beginDate"],
                    "endDate": params["endDate"],
                    ...
                }
            }, context)
            result["basicPrice"] = indexResult["curvePrice"]

    elif level == 2:  # 升贴水
        if abbreviation == "BasicFixedPremium":
            spreadValue = float(params["basicSpread"]["value"])
            isPercentage = params.get("percentage", {}).get("value", "n")
            if isPercentage == "y":
                result["spread"] = spreadValue * result["basicPrice"]
            else:
                # 币种+单位转换
                result["spread"] = getPriceAtTargetCurrency(
                    spreadValue,
                    params["forexMarketId"]["value"],
                    params["pricingCurrency"]["value"],
                    targetCurrencyId,
                    params["pricingQuantityUnit"]["value"],
                    targetUnitId,
                    fromDate, toDate
                )

    elif level == 3:  # 加工费
        if abbreviation == "ProcessingFee":
            result["otherCostPrice"] += float(component["value"])

    elif level == 4:  # 附加价
        if abbreviation == "AddedValue":
            result["otherCostPrice"] += float(params["fixedPrice"]["value"])

# 4. 计算最终价格
result["finalPrice"] = result["basicPrice"] + result["spread"] + result["otherCostPrice"]

# 5. 输出 JSON 到 stdout（Java 读取）
print(json.dumps(result))
```

> **注意**：以上是推断的典型结构。实际的 Python 脚本内容存储在数据库中，
> 每个 `pricing_formulas` 记录可以有不同的 Python 实现。

---

## 六、a119 返回结果结构

```java
@Data
public class a119 {
    String pricingType;           // "Fixed" / "Average" / "Triggered"
    Double finalPrice;            // 最终价格 = basicPrice + spread + otherCostPrice
    Double basicPrice;            // 基础价格
    Double spread;                // 升贴水
    Double otherCostPrice;        // 其他费用（加工费 + 附加价）
    Double threshold;             // 阈值
    String thresholdType;         // 阈值类型
    List<a120> priceDetail;       // 按远期合约分组的价格明细
    List<LocalDate> fixingDates;  // 定价日期列表
}
```

### a153 拿到 a119 后的处理

```java
// a153.java L187-232 (a1485 方法)

// 1. 设置定价状态
pricingStatus = FIXED;  // 默认固定
for (priceDetail : a119.priceDetail) {
    if (任何 fixingDate > curveDate) {
        pricingStatus = FLOATING;  // 有未来定价日 → 浮动
    }
}

// 2. 设置升贴水和其他费用
cashflowModel.setSpread(a119.spread);
cashflowModel.setOtherCostPrice(a119.otherCostPrice);

// 3. 计算结算价格
settlementPrice = round(a119.finalPrice - a119.spread - a119.otherCostPrice, roundingDigits);
//                 ^^^^^ 基础价 = 最终价 - 升贴水 - 其他费用

// 4. 计算结算净价格
settlementNetPrice = round(a119.finalPrice, roundingDigits);
```

### executePy 中的 estimated_price 回退逻辑

```java
// a153.java L113-165

// 如果 Python 返回的 finalPrice = 0（远期曲线没有数据）
// 回退到 physical_deal_line_ext.estimated_price（预估价格）

estimatedPrice = ext.get("estimated_price");
if (estimatedPrice != null) {
    // 预估价格需要 币种×单位 转换
    estimatedPrice *= unitConversion * currencyConversion;
}

if (a119.finalPrice == 0) a119.finalPrice = estimatedPrice;
if (a119.basicPrice == 0) a119.basicPrice = estimatedPrice;

// 对 priceDetail 中 marketPriceValue = 0 的也填充 estimatedPrice
```

---

## 七、缓存机制

系统有两层缓存防止重复计算：

### 7.1 Redis 结果缓存

```java
// RiskValuationUtil.java L74-80
String cacheKey = "PythonResult:calculateCompositionPrice:" + groupKey;
a119 cached = (a119) redis.get(cacheKey);
if (cached != null) return cached;  // 命中缓存，跳过 Python 调用
```

`groupKey`（`a118` 对象）包含：合同号、品牌ID、规格ID、货源、收货地址、包装方式、物权转移日期、合同ID。相同条件的重复计算直接返回缓存。

### 7.2 Python 脚本内缓存

```python
# utils.py L9-16
def getAndSetCache(key, f, fArgs):
    if key not in FormulaContext.cache:
        FormulaContext.cache[key] = f(fArgs)
    return FormulaContext.cache[key]
```

Python 脚本内部也有内存缓存，同一个脚本执行期间，相同的 Thrift API 调用不会重复请求。

### 7.3 Python 脚本文件缓存

```java
// PythonPyPathServiceImpl.java L352-384
// 脚本文件路径存入 Redis: "PythonPath:PricingFormulas:{id}"
// 脚本文件写入磁盘后，后续直接使用已有文件，不重复写入
```

---

## 八、异常处理与容错

| 场景 | 处理方式 |
|---|---|
| Python 脚本路径为 null | `exec_python` 返回 error: "python文件路径为null" |
| Python 执行超时 | `process.waitFor(20, SECONDS)` 最多等 20 秒 |
| `python` 命令不存在 | 自动重试 `python3` 命令 |
| Python 输出错误 | 读取 stderr，返回 error 信息 |
| Python 返回 finalPrice = 0 | 回退到 `estimated_price`（预估价格） |
| Thrift 连接失败 | Python 脚本抛出异常 → Java 捕获为 `a154` 异常 |
| Redis 缓存未命中 | 正常执行 Python，结果写入缓存 |

---

## 九、全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Java 侧                                   │
│                                                                  │
│  a65 PricingEngine                                               │
│    │ pricingType == FORMULA                                      │
│    ▼                                                             │
│  a153.executePy()                                                │
│    │                                                             │
│    ├── 构建 a104 (formulaId + formulaParams + context)           │
│    │                                                             │
│    ├── 查 Redis 缓存 → 命中直接返回                               │
│    │                                                             │
│    ├── PythonPyPathService                                       │
│    │   ├── DB: pricing_formulas.pricing_formula (Python源码)     │
│    │   └── 写入临时文件: basePath + hash(源码) + ".py"            │
│    │                                                             │
│    ▼                                                             │
│  PythonUtils.exec_python(pyPath, formulaParams, contextJson)     │
│    │                                                             │
│    ├── Runtime.exec(["python", pyPath, arg1, arg2])              │
│    ├── stdout/stderr 分别用线程读取（防死锁）                      │
│    └── 超时 20s，失败重试 python3                                 │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ 进程间通信
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Python 侧                                 │
│                                                                  │
│  动态脚本 (从 DB 生成)                                            │
│    │                                                             │
│    ├── sys.argv[1] = pricingFormulaIdParameters JSON             │
│    ├── sys.argv[2] = context JSON                                │
│    │                                                             │
│    ├── 遍历 JSON 数组，按 abbreviation 分支:                      │
│    │   ├── BasicFixedPrice → 直接取 fixedPrice                   │
│    │   ├── BasicTriggeredPrice → valueIndexNew() → Thrift 取价   │
│    │   ├── BasicAveragePrice → valueIndexNew() → Thrift 取均价   │
│    │   ├── BasicFixedPremium → 固定值或百分比 × basePrice         │
│    │   ├── ProcessingFee → 直接取 value                          │
│    │   └── AddedValue → 取 fixedPrice                            │
│    │                                                             │
│    ├── 通过 Thrift RPC 回调 Java:                                 │
│    │   ctrm_thrift_client.execute("API.Pricing", "fetch", ...)   │
│    │   → 127.0.0.1:9000 → Java Thrift Server → 返回曲线价格      │
│    │                                                             │
│    ├── utils.py 提供公共函数:                                     │
│    │   valueIndex · valueSpread · getPriceAtTargetCurrency       │
│    │                                                             │
│    └── print(json.dumps(a119结果)) → stdout                      │
│                                                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ stdout
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Java 侧 (结果处理)                        │
│                                                                  │
│  RiskValuationUtil.calculateCompositionPrice()                   │
│    │                                                             │
│    ├── JSONObject.parseObject(stdout[0], a119.class)             │
│    ├── 写入 Redis 缓存                                           │
│    │                                                             │
│    ▼                                                             │
│  a153.a1485()                                                    │
│    │                                                             │
│    ├── finalPrice = 0? → 回退到 estimated_price                  │
│    ├── settlementPrice = finalPrice - spread - otherCost         │
│    ├── settlementNetPrice = round(finalPrice, digits)            │
│    ├── pricingStatus = FIXED 或 FLOATING                         │
│    │                                                             │
│    └── 写入 CashflowModelValues → 持久化到数据库                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 十、关键注意点

1. **Python 脚本在数据库中** — 不在项目源码里。修改计价公式的 Python 逻辑需要直接改数据库 `pricing_formulas.pricing_formula` 字段，或通过后端的计价公式管理界面。

2. **Thrift 双向通信** — Python 不是独立计算，它通过 Thrift RPC 回调 Java 服务获取远期曲线价格、汇率、单位转换等数据。Python 只负责**编排逻辑**，数据源仍在 Java 侧。

3. **20 秒超时** — `process.waitFor(20, SECONDS)` 是硬限制。如果 Thrift 回调链过长（多次 fetch），可能超时。

4. **Windows 兼容** — `convertJsonInWindows()` 对 JSON 中的引号做特殊转义，这是因为 Windows 命令行的引号处理与 Linux 不同。

5. **hashCode 作为文件名** — `MyFileUtil.saveAndGetPathName()` 用 `"python_script_" + 源码` 的 hashCode 作为文件名。相同源码不会重复生成文件，但修改源码后会生成新文件，旧文件不会自动清理。

6. **estimated_price 回退** — 当 Python 返回的 finalPrice = 0（远期曲线无数据）时，系统会回退到 `physical_deal_line_ext.estimated_price`，这是一个手动维护的预估价格。
