---
type: 代码文档
---

# Python 脚本调用机制全链路分析

> [!info] 文档信息
> - **生成日期**：2026-07-01
> - **核心文件**：
>   - `bcadmin-tools/.../PythonUtils.java` — Python 执行器
>   - `bcadmin-tools/.../PythonPyPathServiceImpl.java` — 脚本路径服务
>   - `bcadmin-common/.../MyFileUtil.java` — 文件写入工具
> - **关联文档**：[[Thrift跨语言调用链路说明]] · [[ThriftPricingService分析]] · [[pricing-formula-developer-guide]]

---

## 一、核心结论

> [!summary] 一句话总结
> **Python 脚本的源码以文本形式存储在数据库的 LONGVARCHAR/VARCHAR 字段中**，运行时由 `PythonPyPathServiceImpl` 从数据库读出 → 写入磁盘 `.py` 文件 → 通过 `Runtime.exec()` 以子进程方式调用系统 `python/python3` 执行。

### 整体流程

```
┌──────────────────────────────────────────────────────────────────┐
│                     Python 脚本调用全链路                         │
│                                                                  │
│  ① 业务代码持有某个 ID（如 pricingFormulaId = 42）                │
│       ↓                                                          │
│  ② PythonPyPathServiceImpl.getPricingFormulaPyFilePathById(42)   │
│       ↓                                                          │
│  ③ 查 Redis 缓存 → key = "PythonPath:PricingFormulas:42"         │
│       ↓ (未命中)                                                  │
│  ④ 查数据库 → SELECT pricing_formula FROM pricing_formulas        │
│              WHERE id = 42                                       │
│       ↓ 返回 Python 源码文本（LONGVARCHAR）                       │
│  ⑤ 检查 py_file_path 字段                                        │
│       ├── 为空 或 文件不存在 → 写入磁盘                            │
│       └── 非空 且 文件存在 → 直接使用                              │
│       ↓                                                          │
│  ⑥ MyFileUtil.saveAndGetPathName(basePath, 源码文本)              │
│       → 文件名 = hashCode("python_script_" + 源码) + ".py"       │
│       → 写入磁盘，返回绝对路径                                    │
│       ↓                                                          │
│  ⑦ UPDATE pricing_formulas SET py_file_path = ? WHERE id = 42    │
│       → 回写路径到数据库（下次不用重新写文件）                      │
│       ↓                                                          │
│  ⑧ 写入 Redis 缓存                                               │
│       ↓                                                          │
│  ⑨ PythonUtils.exec_python(pyFilePath, param, context)           │
│       → Runtime.exec(["python", pyFilePath, param, context])     │
│       → 失败则回退到 python3                                      │
│       → 最多等待 20 秒                                            │
│       ↓                                                          │
│  ⑩ 解析 stdout → BaseResultEntity<List<String>>                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 二、Python 脚本存在哪里——6 张数据库表

Python 脚本**不是以文件形式存在的**，而是以**文本形式存储在数据库字段中**。涉及 6 张表：

### 2.1 表清单

| # | 数据库表 | 公式源码字段 | 路径缓存字段 | 业务含义 |
|---|---|---|---|---|
| 1 | `pricing_formulas` | `pricing_formula` (LONGVARCHAR) | `py_file_path` (VARCHAR) | **计价公式**（核心） |
| 2 | `pricing_range_rules` | `pricing_range_formula` (LONGVARCHAR) | `py_file_path` (VARCHAR) | 定价区间规则 |
| 3 | `event_type` | `volume_formula` (VARCHAR) | `py_file_path` (VARCHAR) | 事件类型（日期计算） |
| 4 | `payment_term` | `volume_formula` (VARCHAR) | `py_file_path` (VARCHAR) | 付款条款（日期计算） |
| 5 | `specification_type` | `volume_formula` (VARCHAR) | `py_file_path` (VARCHAR) | 规格类型 |
| 6 | `quantity_type` | `volume_formula` (VARCHAR) | `py_file_path` (VARCHAR) | 数量类型（量计算） |

> [!note] 双字段设计
> 每张表都有两个关键字段：
> - **公式源码字段**（`pricing_formula` / `volume_formula`）：存储 Python 代码的**文本内容**
> - **`py_file_path`**：缓存该代码写到磁盘后的**绝对路径**，避免每次都重新写文件

### 2.2 核心表结构

#### pricing_formulas（计价公式表）

```sql
CREATE TABLE pricing_formulas (
    id                          BIGINT PRIMARY KEY,
    name                        VARCHAR,         -- 公式名称
    description                 VARCHAR,         -- 描述
    price_formula_type          INTEGER,         -- 公式类型
    ref                         VARCHAR,         -- 引用标识（如 BasicFixedPrice）
    formula_description         VARCHAR,         -- 公式说明
    py_file_path                VARCHAR,         -- ★ Python 文件磁盘路径（缓存）
    has_triggered               BIT,             -- 是否已触发
    status                      INTEGER,         -- 状态
    -- ... 审计字段省略 ...
    scopes_cost                 VARCHAR,
    pricing_formula             LONGVARCHAR,     -- ★★ Python 脚本源码（核心）
    pricing_formula_parameter   LONGVARCHAR,     -- 公式参数定义（JSON）
    scopes                      LONGVARCHAR      -- 适用范围
);
```

#### event_type（事件类型表）

```sql
CREATE TABLE event_type (
    id                      BIGINT PRIMARY KEY,
    name                    VARCHAR,         -- 事件名称
    volume_formula          VARCHAR,         -- ★ Python 脚本源码
    volume_formula_parameter VARCHAR,        -- 公式参数（JSON）
    py_file_path            VARCHAR,         -- ★ Python 文件路径（缓存）
    business_module         BIGINT,          -- 所属业务模块
    derive_event_flag       VARCHAR,         -- 派生事件标识
    order_seq               INTEGER          -- 排序号
);
```

#### quantity_type（数量类型表）

```sql
CREATE TABLE quantity_type (
    id                      BIGINT PRIMARY KEY,
    volume_formula          VARCHAR,         -- ★ Python 脚本源码
    volume_formula_parameter VARCHAR,        -- 公式参数（JSON）
    py_file_path            VARCHAR          -- ★ Python 文件路径（缓存）
);
```

---

## 三、怎么找到脚本——PythonPyPathServiceImpl

### 3.1 服务定位

**文件**：`bcadmin-tools/src/main/java/com/resrun/service/impl/PythonPyPathServiceImpl.java`（431 行）

**职责**：根据业务实体 ID → 查数据库获取 Python 源码 → 落盘为 `.py` 文件 → 返回文件路径

### 3.2 提供的 7 个方法

| 方法 | 行号 | 对应表 | 公式字段 |
|---|---|---|---|
| `getPricingFormulaPyFilePathById(Long id)` | 352–384 | `pricing_formulas` | `pricing_formula` |
| `getPricingRangeRulePyFilePathById(Long id)` | 317–349 | `pricing_range_rules` | `pricing_range_formula` |
| `getEventTypePyFilePathById(Long id)` | 82–115 | `event_type` | `volume_formula` |
| `getPaymentTermPyFilePathById(Long id)` | 158–190 | `payment_term` | `volume_formula` |
| `getSpecificationTypePyFilePathById(Long id)` | 213–245 | `specification_type` | `volume_formula` |
| `getQuantityTypePyFilePathById(Long id)` | 268–299 | `quantity_type` | `volume_formula` |
| `getCreditTypePathById(Long id)` | 52–74 | `bankcredit_types` | `formula` |

### 3.3 通用逻辑（所有方法模式一致）

以 `getEventTypePyFilePathById(Long id)` 为例：

```java
@Override
public String getEventTypePyFilePathById(Long id) {

    // ① 查 Redis 缓存
    String key = "PythonPath:EventType:" + id;
    EventType tem = (EventType) redisUtils.get(key);

    // ② 缓存未命中 → 查数据库
    if (tem == null) {
        tem = getEventTypeById(id);
    }
    if (tem == null) return null;

    // ③ 检查公式源码是否非空
    if (MyStringUtils.isNotBlank(tem.getVolumeFormula())) {
        String path = null;

        if (MyStringUtils.isBlank(tem.getPyFilePath())) {
            // ④-a 没有缓存路径 → 写入磁盘
            path = saveEventTypePythonFile(id, tem.getVolumeFormula());
        } else {
            File file = new File(tem.getPyFilePath());
            if (!file.exists()) {
                // ④-b 文件不存在 → 重新写入
                path = saveEventTypePythonFile(id, tem.getVolumeFormula());
            } else {
                // ④-c 文件存在 → 直接使用
                path = tem.getPyFilePath();
            }
        }

        // ⑤ 回写 Redis 缓存
        tem.setPyFilePath(path);
        redisUtils.set(key, tem, -1);  // 永不过期

        return path;
    }
    return null;
}
```

### 3.4 三级缓存策略

```
查找优先级:

Redis 缓存 (key = "PythonPath:{类型}:{id}", 永不过期)
    ↓ 未命中
数据库 py_file_path 字段 (VARCHAR, 持久化)
    ↓ 为空或文件不存在
数据库公式源码字段 (LONGVARCHAR/VARCHAR) → 写入磁盘 → 回写 py_file_path
```

---

## 四、脚本怎么落盘——MyFileUtil

### 4.1 核心方法

**文件**：`bcadmin-common/src/main/java/com/resrun/utils/MyFileUtil.java`

```java
// 第 397 行：按内容哈希生成文件名
public static String saveAndGetPathName(String path, String content) throws IOException {
    File file = new File(path);
    if (!file.exists()) {
        file.mkdirs();
    }
    String filePathName = path + pyFileHashCode(content) + ".py";
    bufferedWriterMethod(filePathName, content);
    return filePathName;
}

// 第 387 行：哈希算法
private static int pyFileHashCode(String content) {
    String finalContent = "python_script_" + content;
    return finalContent.hashCode();
}
```

### 4.2 关键设计

> [!important] 幂等写入
> 文件名 = `hashCode("python_script_" + 源码内容)` + `.py`
>
> **相同内容的公式会生成相同的文件名**，实现幂等写入——内容不变就不会产生新文件。

### 4.3 文件存储位置

由 `FileProperties.path.path` 配置项决定根目录，所有 `.py` 文件写入该目录下。

---

## 五、脚本怎么执行——PythonUtils

### 5.1 核心方法

**文件**：`bcadmin-tools/src/main/java/com/resrun/util/PythonUtils.java`（142 行）

```java
public static BaseResultEntity<List<String>> exec_python(
        String pythonPath,    // .py 文件绝对路径
        String param,         // 公式参数（JSON 字符串）
        String... values      // 上下文对象（JSON 字符串）
) {
    // ① 校验路径
    if (pythonPath == null) return BaseResultEntity.error("python文件路径为null");

    // ② 清理敏感字段（防止参数过大）
    for (int i = 0; i < values.length; i++) {
        JSONObject jo = JSONObject.parseObject(values[i]);
        if (jo.containsKey("line") && jo.getJSONObject("line")
                .containsKey("pricingFormulaIdParameters")) {
            jo.getJSONObject("line").put("pricingFormulaIdParameters", "");
        }
        values[i] = JSONObject.toJSONString(jo);
    }

    // ③ 构造命令行参数
    ArrayList<String> argList = new ArrayList<>();
    argList.add("python");
    argList.add(pythonPath);
    argList.add(param == null ? "{}" : param);
    for (String value : values) argList.add(value);

    // ④ Windows 特殊转义
    if (isWindowsOS) { /* convertJsonInWindows */ }

    // ⑤ 执行：先试 python，失败回退 python3
    String[] args = argList.toArray(new String[0]);
    BaseResultEntity<List<String>> result = execute("python", args);
    if (result.getCode() != SUCCESS) {
        result = execute("python3", args);
    }
    return result;
}
```

### 5.2 底层执行器 execute()

```java
private static BaseResultEntity<List<String>> execute(String cmd, String[] args) {
    Process process = Runtime.getRuntime().exec(args);

    // 线程池异步读取 stdout/stderr（防止缓冲区满导致死锁）
    executor.submit(new PythonResultRunnable(process.getInputStream(), ...));
    executor.submit(new PythonResultRunnable(process.getErrorStream(), ...));

    // 最多等待 20 秒
    boolean finished = process.waitFor(20, TimeUnit.SECONDS);
    if (!finished) {
        process.destroyForcibly();
        return BaseResultEntity.error("Python 执行超时");
    }

    // 解析 stdout → List<String>
    return BaseResultEntity.success(resultLines);
}
```

### 5.3 命令行等价

```bash
python /path/to/{hashCode}.py '{"formulaParam":"value"}' '{"context":"..."}'
```

---

## 六、谁在调用——19 处调用点全景

### 6.1 按业务场景分类

| 场景 | 调用文件 | 行号 | 使用哪个 get*Path 方法 | 计算什么 |
|---|---|---|---|---|
| **计价公式** | RiskValuationUtil | 86 | `getPricingFormulaPyFilePathById` | 组合价格 |
| **计价公式** | PricingServiceImpl | 1333 | `getPricingFormulaPyFilePathById` | 点价保证金 |
| **计价公式** | PhysicalDealLineServiceImpl | 833 | `getPricingFormulaPyFilePathById` | 固定价格 |
| **计价公式** | PhysicalDealLineServiceImpl | 1039 | `getPricingFormulaPyFilePathById` (ID=112) | 月度计划 |
| **数量计算** | PhysicalDealLineServiceImpl | 349, 452 | `getQuantityTypePyFilePathById` | 合同行数量 |
| **数量计算** | DocumentQuantitiesServiceImpl | 186 | `getQuantityTypePyFilePathById` | 单据数量 |
| **数量计算** | WarehouseRelationServiceImpl | 89 | `getQuantityTypePyFilePathById` | 仓库数量 |
| **数量计算** | b32 (收发货处理器) | 228 | `getQuantityTypePyFilePathById` | 收发货数量 |
| **事件日期** | PhysicalDealLineServiceImpl | 379, 497 | `getEventTypePyFilePathById` | 合同行事件日期 |
| **事件日期** | DocumentEventsServiceImpl | 190 | `getEventTypePyFilePathById` | 单据事件日期 |
| **事件日期** | WarehouseRelationServiceImpl | 130 | `getEventTypePyFilePathById` | 仓库事件日期 |
| **事件日期** | a161 (现金流) | 102 | `getEventTypePyFilePathByEventType` | 批量事件日期 |
| **付款条款** | RiskUtil | 333 | `getPaymentTermPyFilePathById` | 需求日期 |
| **付款条款** | PhysicalDealLineServiceImpl | 810 | `getPaymentTermPyFilePathById` | 付款条款日期 |
| **公式模板** | FormulateTemplateUtil | 103 | `deployFinalFormula` | 自定义配方表达式 |
| **通用** | PythonCalculator | 18 | 调用方传入路径 | 通用计算 |

### 6.2 按公式类型分类

```
┌─────────────────────────────────────────────────────────────────┐
│                  Python 脚本调用分类                              │
│                                                                  │
│  ┌─── PricingFormula (计价公式) ─────────────────────────────┐   │
│  │  表: pricing_formulas                                      │   │
│  │  字段: pricing_formula (LONGVARCHAR)                       │   │
│  │  方法: getPricingFormulaPyFilePathById(id)                 │   │
│  │  调用者: RiskValuationUtil, PricingServiceImpl,            │   │
│  │          PhysicalDealLineServiceImpl                       │   │
│  │  计算: 组合价格、保证金、固定价格、月度计划                  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── QuantityType (数量类型) ───────────────────────────────┐   │
│  │  表: quantity_type                                         │   │
│  │  字段: volume_formula (VARCHAR)                            │   │
│  │  方法: getQuantityTypePyFilePathById(id)                   │   │
│  │  调用者: PhysicalDealLineServiceImpl,                      │   │
│  │          DocumentQuantitiesServiceImpl,                    │   │
│  │          WarehouseRelationServiceImpl,                     │   │
│  │          b32 (收发货处理器)                                 │   │
│  │  计算: 合同行数量、单据数量、仓库数量、收发货数量            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── EventType (事件类型) ──────────────────────────────────┐   │
│  │  表: event_type                                            │   │
│  │  字段: volume_formula (VARCHAR)                            │   │
│  │  方法: getEventTypePyFilePathById(id)                      │   │
│  │  调用者: PhysicalDealLineServiceImpl,                      │   │
│  │          DocumentEventsServiceImpl,                        │   │
│  │          WarehouseRelationServiceImpl,                     │   │
│  │          a161 (现金流批量计算)                               │   │
│  │  计算: 交货日期、付款日期、入库/出库日期                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── PaymentTerm (付款条款) ────────────────────────────────┐   │
│  │  表: payment_term                                          │   │
│  │  字段: volume_formula (VARCHAR)                            │   │
│  │  方法: getPaymentTermPyFilePathById(id)                    │   │
│  │  调用者: RiskUtil, PhysicalDealLineServiceImpl             │   │
│  │  计算: 需求日期、付款条款日期                               │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── PricingRangeRules (区间规则) ──────────────────────────┐   │
│  │  表: pricing_range_rules                                   │   │
│  │  字段: pricing_range_formula (LONGVARCHAR)                 │   │
│  │  方法: getPricingRangeRulePyFilePathById(id)               │   │
│  │  调用者: ThriftPricingService (Python 侧通过 RPC 调用)      │   │
│  │  计算: 定价区间规则（valueIndex 函数中使用）                 │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─── SpecificationType (规格类型) ──────────────────────────┐   │
│  │  表: specification_type                                    │   │
│  │  字段: volume_formula (VARCHAR)                            │   │
│  │  方法: getSpecificationTypePyFilePathById(id)              │   │
│  │  调用者: 间接使用                                           │   │
│  │  计算: 规格相关计算                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 七、参数传递与返回值

### 7.1 统一调用签名

```java
PythonUtils.exec_python(
    pyFilePath,     // String: .py 文件绝对路径
    param,          // String: 公式参数 JSON（来自 volume_formula_parameter 等）
    context         // String: 上下文对象 JSON（业务数据）
)
```

### 7.2 不同场景的 context 结构

| 场景 | context 类型 | 包含内容 |
|---|---|---|
| 计价公式 | `a93<Object, Object>` | 空上下文或价格相关数据 |
| 数量计算 | `QuantityFormulaContext<H, L, QuantityType>` | header(头) + line(行) + quantityType |
| 事件日期 | `a92<H, L>` | header(头) + line(行) |
| 付款条款 | 自定义 Object | 条款相关数据 |

### 7.3 返回值解析

```java
BaseResultEntity<List<String>> result = PythonUtils.exec_python(...);

// 数量场景 → double
double qty = Double.parseDouble(result.getData().get(0));

// 日期场景 → LocalDate
LocalDate date = LocalDate.parse(result.getData().get(0), DateTimeFormatter.ofPattern("yyyy-MM-dd"));

// 价格场景 → a119 模型
a119 model = JSONObject.parseObject(result.getData().get(0), a119.class);
// model.getFinalPrice() → 最终价格
// model.getPricingType() → "Fixed" 或 "Percent"
```

---

## 八、缓存策略

### 8.1 两层缓存

| 层级 | 存储位置 | Key 格式 | 过期策略 | 缓存内容 |
|---|---|---|---|---|
| **L1** | Redis | `PythonPath:{类型}:{id}` | 永不过期 (-1) | 实体对象（含 pyFilePath） |
| **L2** | 数据库 | `py_file_path` 字段 | 持久化 | 磁盘文件路径 |

### 8.2 执行结果缓存

部分高频调用还会缓存 Python 执行结果：

| 调用方 | Redis Key 格式 | 缓存时间 | 说明 |
|---|---|---|---|
| RiskValuationUtil | `PriceFormulaGroupKey:{hash}` | 60 秒 | 组合价格计算结果 |
| RiskUtil | `PythonResult:calculateRequirementDate:{id}:{hash}` | 60 秒 | 需求日期计算结果 |
| a161 | `PythonResult:EventType:{id}:{hash}` | 60 秒 | 事件日期计算结果 |
| FormulateTemplateUtil | `FormulaTemplate:{hash}` | 60 秒 | 公式模板计算结果 |

---

## 九、完整调用链示例

### 9.1 示例：合同行保存时计算数量

```
用户操作: 保存合同行（PhysicalDealLine）
    │
    ▼
PhysicalDealLineServiceImpl.save()
    │
    ├── item.getQuantityTypeId() = 5   ← 数量类型 ID
    │
    ▼
pythonPyPathService.getQuantityTypePyFilePathById(5)
    │
    ├── ① Redis: GET "PythonPath:QuantityType:5" → 未命中
    ├── ② DB: SELECT * FROM quantity_type WHERE id = 5
    │         → volume_formula = "import json\nimport sys\n..."
    │         → py_file_path = null（首次）
    ├── ③ MyFileUtil.saveAndGetPathName("/data/py/", 源码)
    │         → 写入 /data/py/-18273645.py
    ├── ④ DB: UPDATE quantity_type SET py_file_path = '/data/py/-18273645.py' WHERE id = 5
    └── ⑤ Redis: SET "PythonPath:QuantityType:5" → 缓存实体
    │
    ▼ 返回 "/data/py/-18273645.py"
    │
PythonUtils.exec_python(
    "/data/py/-18273645.py",
    quantityType.getVolumeFormulaParameter(),   // 公式参数 JSON
    JSON.toJSONString(context)                   // {header: {...}, line: {...}, quantityType: {...}}
)
    │
    ▼ Runtime.exec(["python", "/data/py/-18273645.py", "{...}", "{...}"])
    │
    ▼ Python 脚本执行 → stdout 输出 "150.5"
    │
    ▼ Double.parseDouble("150.5") → item.setQuantityValue(150.5)
```

### 9.2 示例：点价保证金计算

```
用户操作: 点价单提交 → 计算保证金
    │
    ▼
PricingServiceImpl.calculateMargin(PriceTriggering record)
    │
    ├── chargeRes.get().getPricingFormulaId() = 42   ← 计价公式 ID
    │
    ▼
pythonPyPathService.getPricingFormulaPyFilePathById(42)
    │
    ├── ① Redis → DB → 落盘（同上流程）
    └── 返回 "/data/py/98273615.py"
    │
    ▼
PythonUtils.exec_python(
    "/data/py/98273615.py",
    chargeRes.get().getPricingFormulaIdParameters(),  // 公式参数
    JSON.toJSONString(context)                         // 空上下文
)
    │
    ▼ Python 执行 → stdout: '{"finalPrice":2500.00,"pricingType":"Fixed"}'
    │
    ▼ a119 model = parseObject(result) → model.getFinalPrice() = 2500.00
    │
    ▼ margin = record.getQuantity() * model.getFinalPrice()
```

---

## 十、Thrift 反向调用场景

> [!note] 特殊场景：Python 反向调用 Java
> 除了 Java → Python 的正向调用外，还存在 Python → Java 的反向调用（通过 Thrift RPC）。
> 详见 [[Thrift跨语言调用链路说明]]

```
正向: Java → PythonUtils.exec_python → Python 脚本
反向: Python 脚本 → utils.py → ctrm_thrift_client → ThriftServer(9000) → Java
```

在 `utils.py` 中：
- `valueIndex()` / `valueIndexNew()` → 调 `API.Pricing.fetch` → `ThriftPricingService.fetch()`
- `valueSpread()` → 调 `API.MarketingSpread.fetch`

---

## 十一、关键代码入口速查

| 文件 | 方法 | 行号 | 说明 |
|---|---|---|---|
| PythonUtils | `exec_python()` | 70 | Python 执行入口 |
| PythonUtils | `execute()` | 27 | 底层 Runtime.exec |
| PythonPyPathServiceImpl | `getPricingFormulaPyFilePathById()` | 352 | 计价公式路径 |
| PythonPyPathServiceImpl | `getEventTypePyFilePathById()` | 82 | 事件类型路径 |
| PythonPyPathServiceImpl | `getQuantityTypePyFilePathById()` | 268 | 数量类型路径 |
| PythonPyPathServiceImpl | `getPaymentTermPyFilePathById()` | 158 | 付款条款路径 |
| PythonPyPathServiceImpl | `getPricingRangeRulePyFilePathById()` | 317 | 区间规则路径 |
| MyFileUtil | `saveAndGetPathName()` | 397 | 源码落盘 |
| MyFileUtil | `pyFileHashCode()` | 387 | 文件名哈希 |

---

## 十二、总结

> [!summary] 核心设计模式
>
> 1. **脚本存储**：Python 源码以文本形式存在数据库的 `LONGVARCHAR/VARCHAR` 字段中，**不是文件系统中的 .py 文件**
> 2. **懒加载落盘**：首次使用时才写入磁盘，文件名基于内容哈希（幂等）
> 3. **三级查找**：Redis 缓存 → DB `py_file_path` 字段 → DB 源码字段（落盘）
> 4. **进程隔离**：通过 `Runtime.exec()` 启动独立 Python 子进程，20 秒超时保护
> 5. **双版本兼容**：先试 `python`，失败回退 `python3`
> 6. **结果缓存**：高频计算结果额外缓存 60 秒
