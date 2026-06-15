# `api/document/generateDetailsByDocuments` 接口物资明细计算拆解（基于代码）

## 1. 分析范围与原则

> [!abstract] 分析说明
> - **目标接口**：`POST /api/document/generateDetailsByDocuments`
> - **分析重点**：**物资明细（ReceiptDeliveryDetails）如何计算、如何更新、如何删除、何时联动现金流**
> - **追踪范围**：
>   - `DocumentController.generateDetailsByDocuments(...)`
>   - `ReceiptDeliveryDetailsServiceImpl.generateDetailsByDocuments(Long id, Integer modify)`
>   - `b47 -> b36 -> b34 -> b24` 处理器链
> - **原则**：只写代码中能直接验证的行为，不做自由发挥

---

## 2. 接口入口与参数

源文件：`bcadmin-system/src/main/java/com/resrun/modules/business/rest/DocumentController.java`

```java
@RequestMapping("/api/document/")
@PostMapping("generateDetailsByDocuments")
public void generateDetailsByDocuments(@RequestParam Long id, @RequestParam Integer dataState) {
    receiptDeliveryDetailsService.generateDetailsByDocuments(id, dataState);
}
```

### 2.1 入参含义

- `id`：单据 ID（`documents.id`）
- `dataState`：数据状态，来自 `DataState`
  - `ADD = 0`
  - `MODIFY = 1`
  - `DELETE = 2`

说明：Controller 只转发，不做任何业务计算。

---

## 3. 服务层主流程（`generateDetailsByDocuments`）

源文件：`bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/ReceiptDeliveryDetailsServiceImpl.java`

## 3.1 入口保护与基础查询

1. `id == null` 直接返回。  
2. 查询当前单据头：`iDocumentsService.getDocumentsResById(id)`。  
3. 先查本单据下已删除的明细行（`inactive_flag = true`），用于后续分支判断和删除补偿。

## 3.2 特殊分支：`actionId = 40`（出库通知）+ 删除/失配场景

触发条件：

- 当前单据 `actionId == 40`（出库通知），且满足以下之一：
  - 当前单据下存在删除行；
  - 或本次为整单删除（`modify == DELETE`）且上级单据未拣配。

触发后执行步骤：

1. 组装删除条件（按单据号或按删除行 headerId）。  
2. 调 `deleteRddAndCashflow(...)`：
   - 逻辑删除 `receipt_delivery_details`；
   - 删除关联 `cashflow_model_header_values`；
   - 删除关联 `cashflow_model_values`；
   - 删除关联 `cashflow_model_pricing_detail_values`。
3. 递归重算上级单据物资明细：  
   `generateDetailsByDocuments(parentDocumentId, MODIFY)`。
4. 如果删除结果中命中某些库存单据（`IW/PW/SR` 且动作是出库通知），继续递归重算这些上级库存单据。
5. 构造 `CashModelQueryCriteria(linkId=physicalDealId, headerType=SO)`，调用  
   `cashFlowProjectionService.generateCashFlowModel(...)` 重算现金流。
6. 调 `physicalDealsService.createReceiptDeliveryDetails(...)` 补建合同维度的收发货明细。
7. `return`，结束当前分支。

结论：该分支是“**先删旧链路（含现金流）再递归重建**”的修复型流程。

## 3.3 常规分支：准备输入模型并进入处理器

如果没有走 3.2 分支，继续走标准计算流程。

### 3.3.1 构造头模型 `b5`

- `b5` 继承 `DocumentsRes`，额外带一个状态字段 `a`。
- `b5.a = modify`，并把 `documentsRes` 属性复制进去。

### 3.3.2 构造明细模型列表 `b6List`

`b6` 继承 `DocumentItems`，并扩展：

- `d`：行级 DataState
- `b/c/e/f/g/h`：费用、化验、规格、属性、事件、数量

当前方法先按单据动作类型选择明细来源：

1. `ADD + InitialInventory(13)`：直接查该单据全部行。  
2. `WarehouseOutPlan(39)`：直接从 mapper 查该单据行。  
3. `WarehouseOutRegister(41)`：
   - 若上级未拣配：取全部行；
   - 若上级已拣配：只取未删除行。  
4. 其他场景：`listByDocumentsId(id, null)`。

然后统一转换为 `b6`：

- 行 `inactiveFlag=true` 会强制置 `d=DELETE`。

### 3.3.3 追加“删除但必须参与重算”的行

代码额外把以下删除行补入 `b6List`：

- `rdFlag = W` 的删除拣配行；
- `actionId=39 且 modify=DELETE 且父级未拣配` 时，再补 `rdFlag=D` 删除行；
- `actionId=42`（入库登记）时，补该单据所有删除行；
- `actionId` 在 `50/51/54/55/18/21` 时，再补 `rdFlag=D` 删除行。

这些补入行都强制 `d=DELETE`。

### 3.3.4 数据准备（为每个 `b6` 挂扩展信息）

以 `documentItemId` 批量查询并挂载：

- 数量：`DocumentQuantities`
- 化验：`DocumentAssays`
- 事件：`DocumentEvents`
- 规格：`DocumentSpecifications`
- 属性：`DocumentProperties`（含已删除）
- 费用：`ChargeType.document` 且过滤 `ChargeLevel.ReceiptDelivery`

此外，按 `ProductProperties.code` 做两类属性提取：

- `"0001"` -> `brandId`
- `"0064"` -> `specId`

最后：

- 若行级 `d` 为空，则继承方法入参 `modify`
- 设置 `a = id` 用于后续 `distinct`
- `b6List.distinct()` 去重

### 3.3.5 进入处理器

构造：

- `b7`：承载 `b5 + b6List`
- `b18<b7>`：处理器输入包装
  - `a78 = HeaderTypes.DOCUMENT`
  - `a76 = modify`

执行：

```java
b47.a728(inputModel);
```

---

## 4. 处理器链：物资明细真实“计算+落库”发生点

## 4.1 `b47.a728`：驱动“先物资明细，再现金流”

源文件：`bcadmin-ReceiptDeliveryProcessor/.../b47.java`

执行顺序：

1. `synchronized (b47.class)`，串行化执行。  
2. 调 `b36.a522.get(a78).a409(context)` 进入明细处理链。  
3. 把 `context.a528`（处理后的 `ReceiptDeliveryDetails` 列表）映射成 `a122.a1181`。  
4. 设置 `a122.a1179 = modify`，`a122.a1175 = riskUtil.calculateModelCategory(a78)`。  
5. 调 `_a155.a1208(a122)` 触发现金流计算。

关键点：**现金流输入不是原始 DocumentItems，而是处理链产出的 `a528`。**

## 4.2 `b36` 路由：`HeaderTypes.DOCUMENT -> b34`

`b36` 中固定映射：

- `RECEIPT_DELIVERY_PURCHASE_CONTRACT` -> `b38`
- `RECEIPT_DELIVERY_SALES_FROM_CONTRACT` -> `b38`
- `DOCUMENT` -> `b34`

本接口固定走 `b34`。

## 4.3 `b32.a409` 的流水线顺序

`b34` 继承 `b32`，统一入口按以下顺序调用：

1. `a412`
2. `a410`
3. `a411`
4. `a416`
5. `a452`
6. `a417`
7. `a414`
8. `a415`
9. `a419`
10. `a420`
11. `a418`
12. `a421`
13. `a422`

在 `b34` 中真正重写了：`a410/a416/a417/a419/a420/a421/a422/a452`。

## 4.4 `b34` 的关键步骤

### (1) `a410`：加载上下文“旧数据池”

加载并汇总到 `context.a531`（旧 RDD 候选池）：

- 合同相关历史明细
- PO 合同相关明细
- 库存/单据相关明细
- 按 `headerId/sourceHeaderId` 反查明细

并加载：

- 旧事件、旧数量
- 计量类型、事件类型
- 仓储配置、收发汇总等

用途：后续比对“是新增/更新/删除/拆分/合并”时作为参照。

### (2) `a416`：先做净量化

对输入 `b6` 行先统一做：

- `quantity = quantity - offsetQuantity`
- `auxiliaryQuantity = auxiliaryQuantity - offsetAuxiliaryQuantity`
- 若该行是 `DELETE`，两者直接置 0

这是后续生成 RDD 数量的基础输入。

### (3) `a416` 里顺带重写 `a78`

根据 `DocumentActions.actionType` 动态改写 `a535.a78`：

- 有 actionType 用 actionType
- 否则保持 `DOCUMENT`

影响：后续现金流模型类别可能不是固定 DOCUMENT，而会被动作配置改写。

### (4) `a417`：按 `rdFlag` 选处理器执行行级规则

流程：

1. 取当前 `actionId` 的 `DocumentActionItems` 配置；
2. 对每个 `b6` 行，按 `rdFlag` 匹配配置；
3. 根据配置里的 `action` 字符串，从静态表 `a469` 取 handler：
   - `SplitContractOrDocumentHandler` (`b27`)
   - `SplitDocumentInDistributionHandler` (`b29`)
   - `SplitDocumentWithoutGenerateContractHandler` (`b31`)
   - `SplitDocumentOnTwHandler` (`b30`)
   - `InitialDocumentHandler` (`b26`)
   - `SplitContractSoAndPoHandler` (`b28`)
4. 调用 handler 的 `a375 -> a373 -> a374`。

> 这些 handler 内最终会调用 `b24` 的方法（如 `a233/a258/a305`），并在其中直接做 `receipt_delivery_details` 的 `insert/update`，同时把结果加入 `a528/a529/a530`。

### (5) `a419/a420/a418/a421/a422`：同步从表与衍生数据

- `a419`：重建 `receipt_delivery_events`（官方 assayType）
- `a420`：重建 `receipt_delivery_specifications`
- `a418`：重建 `receipt_delivery_quantities`（按 Python 公式算 quantityValue）
- `a421`：同步 `Charge`（document -> receiptDeliveryDetail）
- `a422`：对 `a530`（删除集）相关数量重算/回填

结论：`b34` 不只是生成主表，还会重建关联从表。

---

## 5. 真正“计算物资明细”的核心实现：`b24`

源文件：`bcadmin-ReceiptDeliveryProcessor/.../c/a/b/b24.java`

在 handler 链路中，`b24` 是实际落库执行器。核心方法：

- `a233(...)`
- `a258(...)`
- `a305(...)`

可见行为（代码事实）：

1. 通过 `_b23.a134(...)` 把 `b5/b6` 组装成 `ReceiptDeliveryDetails` 基础对象。  
2. 在旧池中查重：
   - 命中则 `updateByPrimaryKey`
   - 未命中则生成新 `receiptDeliveryId` 后 `insert`
3. 根据仓储统计配置、品牌规格、仓库、货位等条件，决定：
   - 是否走“汇总型库存统计（storageStatisticsType=1）”
   - 是否合并数量、拆分记录、回冲历史记录
4. 在各种分支中同步维护 `ReceiptDeliverySummary`。
5. 每次插入/更新后，通过 `_b23.a107/a108/a109` 维护上下文集合：
   - `a528`：用于现金流输入的结果集合（最终）
   - `a529`：用于事件/规格/数量重建的更新集合
   - `a530`：用于删除/回冲相关重算集合

因此，“物资明细计算”的核心不在 `generateDetailsByDocuments` 本身，而在 **`b34 + 各 handler + b24`** 的组合。

---

## 6. 与现金流的衔接关系

本接口路径下有两层现金流联动：

1. **特殊删除分支（3.2）**：直接调用  
   `cashFlowProjectionService.generateCashFlowModel(linkId=physicalDealId, headerType=SO)`。
2. **常规处理链**：`b47.a728` 在 RDD 处理完成后，把 `a528` 映射为 `a122.a1181` 并调用 `_a155.a1208(a122)`。

即：该接口默认是“**物资明细先行，现金流随后**”。

---

## 7. 疑难点解释（重点）

> [!question]- 疑难点 1：为什么方法里没有明显 `insert/update`，却能生成物资明细？
> `ReceiptDeliveryDetailsServiceImpl.generateDetailsByDocuments` 只做”模型准备 + 调处理器”。实际 `insert/update` 在处理器链下游 `b24` 内完成（多处 `a226.insert/updateByPrimaryKey`）。

> [!question]- 疑难点 2：`dataState` 是方法级参数，为什么还要行级 `d`？
> 方法级 `modify` 是默认状态；行级 `d` 会因 `inactiveFlag=true` 或补删逻辑被强制改成 `DELETE`。最终每条行按自己的 `d` 参与计算，避免整单状态覆盖行级真实删除状态。

> [!question]- 疑难点 3：为什么要把已删除行再查出来参与计算？
> 这是为了解决拣配链、上下游单据、库存统计与汇总记录的一致性问题。删除行不参与会导致旧 RDD/汇总残留，进而造成数量不平。

> [!question]- 疑难点 4：`actionId=40` 分支为什么会递归调用本方法？
> 该分支属于”修复型重建”：当前单据删改后，上级单据和特定库存单据的明细必须联动重算，否则树状链路会断层。

> [!question]- 疑难点 5：`b47` 中 `a78` 会变化吗？影响什么？
> 会。`b34.a416` 会按 `DocumentActions.actionType` 重写 `a78`。这会影响后续 `RiskUtil.calculateModelCategory(a78)` 结果，从而改变现金流引擎分发。

> [!question]- 疑难点 6：数量值是直接取 `DocumentQuantities` 吗？
> 不是。`a418` 会调用 `b32.a438`，通过 `QuantityType` 对应 Python 脚本公式计算 `quantityValue` 后写入 `receipt_delivery_quantities`。

---

## 8. 时序化流程（简版）

1. Controller 收到 `id + dataState`。  
2. Service 加载单据与明细，判断是否走出库通知删除修复分支。  
3. 常规路径下组装 `b5 + b6List`，补齐删除行与扩展数据。  
4. `b47.a728` 启动处理器。  
5. `b34` 加载旧池、净量化、按 `rdFlag` 分发 handler。  
6. handler -> `b24` 执行 RDD 插入/更新/回冲，并维护 `a528/a529/a530`。  
7. `b34` 同步事件/规格/数量/费用。  
8. `b47` 将 `a528` 转为现金流输入，触发 `_a155.a1208`。  

---

## 9. 关键代码位置索引

- 接口入口  
  - `bcadmin-system/.../rest/DocumentController.java` -> `generateDetailsByDocuments`
- 服务主方法  
  - `bcadmin-system/.../service/impl/ReceiptDeliveryDetailsServiceImpl.java` -> `generateDetailsByDocuments(Long, Integer)`
- 删除联动  
  - 同文件 `deleteRddAndCashflow(...)`
- 处理器入口  
  - `bcadmin-ReceiptDeliveryProcessor/.../b47.java` -> `a728`
- 路由与流水线  
  - `.../c/b36.java`、`.../c/b32.java`
- DOCUMENT 分支  
  - `.../c/b34.java`
- 实际 RDD 落库执行器  
  - `.../c/a/b/b24.java`
- 辅助上下文维护  
  - `.../c/a/b/b23.java`

