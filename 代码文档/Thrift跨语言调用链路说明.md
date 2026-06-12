# Thrift 跨语言调用链路说明（点价场景）

## 1. 背景与结论

本文档说明系统在什么前后文下会触发 Thrift 跨语言调用、为什么需要调用、以及 `API.Pricing` 在链路中的计算职责。

核心结论：

- `ThriftApiManager.APIs` 当前基本不参与运行时分发（更偏历史注册表）。
- 当前生效的分发方式是：`ThriftServiceManagerProcessor.execute(...)` 通过 `apiKey` 动态 `getBean` + 反射执行 `cmd`。
- Thrift 跨语言调用通常发生在 **Java 业务执行 Python 公式** 时，Python 侧通过 `utils.py -> ctrm_thrift_client.py` 反向调用 Java 计算能力。

---

## 2. 总调用图（点价场景）

```mermaid
flowchart TD
A[前端调用点价相关接口] --> B[PricingController]
B --> C[PricingServiceImpl]
C --> D[PythonPyPathService 获取公式脚本路径]
D --> E[PythonUtils.exec_python 执行 Python]
E --> F[Python 脚本调用 utils.py]
F --> G[ctrm_thrift_client.execute(apiKey, cmd, args)]
G --> H[ThriftServer(9000) 接收请求]
H --> I[ThriftServiceManagerProcessor.execute]
I --> J[SpringContextHolder.getBean(apiKey)+反射调用cmd]
J --> K[ThriftPricingService / ThriftMarketingSpreadService 等]
K --> L[返回 JSON 给 Python]
L --> M[Python 继续公式计算并返回 Java]
M --> N[Java 业务继续处理并响应前端]
```

---

## 3. 入口与前后文

### 3.1 典型入口（示例）

点价模块里一个清晰入口：

- 控制器：`PricingController`
- 接口：`POST /api/deal/calculateMargin`
- 方法：`calculateMargin(@RequestBody PriceTriggering record)`

该入口将请求交给 `pricingService.calculateMargin(record)`。

### 3.2 调用前文

在 `PricingServiceImpl.calculateMargin(...)` 中，系统会：

1. 找到与业务相关的 `pricingFormulaId`（定价/保证金公式）。
2. 通过 `pythonPyPathService.getPricingFormulaPyFilePathById(...)` 拿到 Python 公式脚本路径。
3. 调用 `PythonUtils.exec_python(...)` 执行 Python。

此时还未必会触发 Thrift；是否触发取决于 Python 脚本内部是否调用 `utils.py` 的跨语言函数。

### 3.3 调用后文

若 Python 内触发了 Thrift：

1. Java Thrift 服务计算完成并返回 JSON 给 Python。
2. Python 脚本继续计算最终结果。
3. Python 输出结果回到 Java（`PythonUtils.exec_python` 返回）。
4. Java 业务层基于结果继续后续流程（保存、提交、返回前端等）。

---

## 4. 为什么会调用 Thrift

设计目的：**让 Python 公式可动态编排，同时复用 Java 已有核心业务能力**。

- Python 负责公式表达和灵活编排（脚本快速变化）。
- Java 负责稳定的核心能力：数据库访问、估值、曲线取价、汇率与单位换算等。
- Thrift 作为跨语言 RPC 桥梁，让 Python 在运行公式时按需调用 Java 能力。

因此，触发条件不是“进入点价模块就调用 Thrift”，而是“公式运行过程中需要 Java 核心能力时才调用”。

---

## 5. 触发 Thrift 的关键代码链

## 5.1 Python 侧客户端调用

`ctrm_thrift_client.py` 中 `execute(apiKey, cmd, args)`：

1. 连接 `127.0.0.1:9000`。
2. 调 `saveArgs(uuid, jsonArgs)` 把参数存入服务端（Redis）。
3. 调 `execute(ExecuteArgs(uuid, apiKey, cmd))` 发起执行。

## 5.2 Java 侧服务端接收

`ThriftServer.Start(...)` 注册 `ThriftServiceManagerProcessor` 处理器并启动服务。

`ThriftServiceManagerProcessor.execute(...)` 处理逻辑：

1. 用 `uuid` 从 Redis 取参数。
2. 用 `apiKey` 获取 Spring Bean（`SpringContextHolder.getBean(executeArgs.apiKey)`）。
3. 通过反射执行 `cmd` 对应方法。
4. 将返回值序列化为 JSON 返回给调用方。

---

## 6. `ThriftApiManager` 的当前角色

`ThriftApiManager` 内维护了 `APIs` 映射（例如 `API.Pricing`、`API.Date` 等）。

但当前代码中几乎未见实际读取该 Map 的运行逻辑，仅在处理器里有一行被注释掉的历史代码：

- `//ThriftBaseService instance = ThriftApiManager.APIs.get(executeArgs.apiKey);`

当前真实生效的是按 Bean 名动态分发，不依赖该 Map。

---

## 7. `API.Pricing` 在计算什么

`API.Pricing` 对应 `ThriftPricingService`（`@Component(value = "API.Pricing")`），典型能力：

- `fetch(String executeArgs)`：定价主入口。
- `getPricingRangeRulePyPath(String executeArgs)`：返回区间规则 Python 路径。
- `getEventTypePyPath(String executeArgs)`：返回事件类型 Python 路径。

`fetch(...)` 的核心处理：

1. 解析传入定价参数（`ThriftPricingModel`）。
2. 按业务维度组装成分数据与规格系数。
3. 根据 `PricingType` 进入不同估值分支（如 `TRIGGER`、`SPECIFICATION_MONTH`、`AVERAGE`）。
4. 调用估值与换算能力（币种、单位、系数等）。
5. 输出价格结果 JSON 给 Python 脚本继续使用。

---

## 8. 哪些 Python 计算最常触发跨语言调用

在 `utils.py` 中，以下函数是典型触发点：

- `valueIndex(...)`
  - 调 `API.Pricing.getPricingRangeRulePyPath`
  - 调 `API.Pricing.fetch`
- `valueSpread(...)`
  - 调 `API.MarketingSpread.fetch`
  - 调 `API.MarketingSpread.calc`
  - 调 `API.MarketingSpread.getPriceAtTargetCurrency`

说明：当业务公式使用这些函数时，运行时会发起 Thrift 调用。

---

## 9. 排查建议（定位“是否触发了 Thrift”）

可按以下顺序排查：

1. 先确认入口是否执行到 `PythonUtils.exec_python(...)`。
2. 确认执行的 Python 脚本是否引用并调用了 `utils.py` 中 `_c.execute(...)` 路径。
3. 确认 Thrift 服务端是否已启动（`ThriftServer.Start(...)`，端口默认 `9000`）。
4. 若有异常，优先看 `ThriftServiceManagerProcessor.execute(...)` 中日志（`API.KEY`、`API.CMD`、`API.UUID`）。

---

## 10. 术语对照

- `apiKey`：Spring Bean 名（例如 `API.Pricing`）。
- `cmd`：要反射调用的方法名（例如 `fetch`）。
- `uuid`：参数暂存与执行关联标识，用于 Redis 中转。

