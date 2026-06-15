# `generateCashFlowModel` 方法数据流梳理（基于代码）

## 1. 文档范围与边界

> [!abstract] 分析范围
> - **分析目标**：`bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/CashFlowProjectionServiceImpl.java` 中的 `generateCashFlowModel(CashModelQueryCriteria criteria)`
> - **向上追踪**：该方法的 REST 入口、典型业务触发点
> - **向下追踪**：`a155.a1208(...)` 的引擎分发逻辑，以及输入模型如何转换为引擎上下文
> - **说明边界**：本文只写”代码中可以直接看到的事实”，不对业务语义做额外假设

---

## 2. 方法签名与入参结构

### 2.1 方法签名

```java
@Override
public void generateCashFlowModel(CashModelQueryCriteria criteria)
```

### 2.2 入参对象（`CashModelQueryCriteria`）中与本方法直接相关的字段

源文件：`bcadmin-system/src/main/java/com/resrun/modules/business/dto/CashModelQueryCriteria.java`

- `linkId`：在本方法中用于
  - 查询 `receipt_delivery_details`（`andLinkIdEqualTo(criteria.getLinkId())`）
  - 构造输入明细中的 `a1174`
  - 无明细兜底时赋值给 `a1173/a1174`
- `headerType`：在本方法中用于
  - 查询 `receipt_delivery_details`（`andHeaderTypeEqualTo(criteria.getHeaderType())`）
  - 调用 `riskUtil.calculateModelCategory(...)` 推导模型类别

---

## 3. 上游入口与触发路径（代码可见）

## 3.1 HTTP 入口

源文件：`bcadmin-system/src/main/java/com/resrun/modules/business/rest/DealController.java`

```java
@PutMapping("cashmodelvalues/generate")
public BaseResultEntity generateCashFlowModel(CashModelQueryCriteria criteria) {
    cashFlowProjectionService.generateCashFlowModel(criteria);
    return BaseResultEntity.success();
}
```

说明：控制层不做业务组装，直接将 `criteria` 透传到服务层。

## 3.2 业务内触发样例（非唯一）

- `PhysicalDealsServiceImpl`：合同提交时构建 `CashModelQueryCriteria(linkId, headerType=PO/SO)` 后调用。
- `ReceiptDeliveryDetailsServiceImpl`：出入库明细重建/删除链路中构建 `criteria` 后调用。

（以上由全局引用 `generateCashFlowModel(` 检索得到）

---

## 4. 方法主流程逐段拆解

源文件：`bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/CashFlowProjectionServiceImpl.java`

## 4.1 参数校验与快速返回

```java
if (MyStringUtils.isEmpty(criteria.getHeaderType()) || criteria.getLinkId() == null) {
    return;
}
```

结论（代码事实）：

- `headerType` 为空 或 `linkId` 为空，方法直接结束。
- 无异常抛出、无日志、无后续调用。

## 4.2 构建出入库明细查询条件

```java
ReceiptDeliveryDetailsExample example = new ReceiptDeliveryDetailsExample();
example.or().andLinkIdEqualTo(criteria.getLinkId())
        .andHeaderTypeEqualTo(criteria.getHeaderType())
        .andBavFlagEqualTo("Y")
        .andMatchNumberIsNull()
        .andInactiveFlagEqualTo(false);
```

随后执行：

```java
List<ReceiptDeliveryDetails> receiptDeliveryDetails = receiptDeliveryDetailsMapper.selectByExample(example);
```

结论（代码事实）：

- 本次参与现金流输入构建的数据来源是 `receipt_delivery_details`。
- 过滤条件固定包含 5 个约束：`linkId`、`headerType`、`bavFlag=Y`、`matchNumber is null`、`inactiveFlag=false`。

## 4.3 创建现金流输入头模型 `a122`

```java
a122 inputModel = new a122();
inputModel.a1175 = riskUtil.calculateModelCategory(criteria.getHeaderType());
inputModel.a1179 = DataState.MODIFY;
```

结合 `a122` 类定义（`bcadmin-cashflowmodel/.../a122.java`）可确认：

- `a1175`：模型类别（由 `headerType` 转换而来）
- `a1179`：数据状态（这里固定为 `MODIFY`）
- `a1181`：明细列表（后续赋值）

## 4.4 逐条组装明细模型 `a121`

```java
receiptDeliveryDetails.forEach(p -> {
    inputDetailModels.add(new a121() {
        {
            a1170 = p.getPhysicalDealId();
            a1171 = p.getLineNumber();
            a1172 = p.getReceiptDeliveryId();
            a1173 = p.getHeaderId();
            a1174 = criteria.getLinkId();
        }
    });
});
```

结论（代码事实）：

- 每条 `ReceiptDeliveryDetails` 映射成一条 `a121`。
- 映射字段关系是固定的一一对应（如上）。
- `a1174` 并非来自 `p`，而是统一使用 `criteria.getLinkId()`。

## 4.5 无明细兜底分支

当 `receiptDeliveryDetails.isEmpty()` 为 `true`：

1) 先尝试查询 `physical_deals` 主表并写日志（仅日志，不改变流程）：

```java
PhysicalDeals physicalDeal = physicalDealsMapper.selectByPrimaryKey(criteria.getLinkId());
```

2) 无论查到与否，都会追加一条兜底 `a121`：

```java
inputDetailModels.add(new a121() {
    {
        a1173 = criteria.getLinkId();
        a1174 = criteria.getLinkId();
    }
});
```

结论（代码事实）：

- 即使没有任何符合条件的 `receipt_delivery_details`，也会强制构造一条最小明细，继续调用计算引擎。
- 该最小明细只赋值 `a1173/a1174`，其余字段为空。

## 4.6 组装完成并调用计算引擎

```java
inputModel.a1181 = inputDetailModels;
a18 a18 = a155.a1208(inputModel);
```

结论（代码事实）：

- 本方法本身不直接落库现金流值。
- 真实计算和可能的持久化行为发生在 `a155.a1208(...)` 及其后续调用链。
- 返回值 `a18` 在本方法内未继续使用。

---

## 5. `headerType -> 模型类别` 的实际映射

源文件：`bcadmin-cashflowmodel/src/main/java/com/resrun/utils/RiskUtil.java`，方法 `calculateModelCategory(...)`

已编码规则：

- `RECEIPT_DELIVERY_SALES_FROM_CONTRACT` / `RECEIPT_DELIVERY_PURCHASE_CONTRACT` -> `EngineModelCategory.PHYSICAL`
- `VOYAGE_CHARTER` -> `EngineModelCategory.VOYAGE_CHARTER`
- `FUTURE` / `SWAP` -> `EngineModelCategory.DERIVATIVE`
- `DEPOSIT_LOAN` -> `EngineModelCategory.DEPOSIT_LOAN`
- `LC_APPLICATION` / `LC_PLAN` / `LC_REGISTRATION` -> `EngineModelCategory.LC_WITH_CHARGE`
- `DOCUMENT` -> `EngineModelCategory.DOCUMENT`
- 其他值 -> 原样返回

说明：该映射决定了后续 `a155.a1208(...)` 会选中哪个计算器。

---

## 6. 下游引擎调用链（直接调用链）

## 6.1 `a155` 对上下文开关的设置

源文件：`bcadmin-cashflowmodel/src/main/java/com/resrun/a155.java`

```java
@Override
protected void a1217(a16 a1209) {
    a1209.a40 = true;
    a1209.a42 = true;
}
```

说明：`a155` 继承 `a156`，只覆写了 `a1217`，用于设置计算上下文两个布尔开关。

## 6.2 `a156.a1208(a122)` 的主流程

源文件：`bcadmin-cashflowmodel/src/main/java/com/resrun/a156.java`

流程按代码顺序：

1. `synchronized (a155.class)`：全局串行执行（同一 JVM 内按类锁）。
2. `a1215(a122)`：把输入模型转换为引擎上下文 `a16`。
3. 调用 `a1217(a16)`：由子类（`a155`）补充开关。
4. 从静态列表 `a1207` 按 `a122.a1175` 查找匹配计算器（`a1` 子类）。
5. 命中则执行 `calculator.a8(a16, null)`。
6. 若未命中：
   - 先尝试按 `a122.a1175` 从 Spring 容器拿 Bean；
   - 再失败则尝试按 `DocumentActions` 的 `actionType` 兜底；
   - 仍失败仅记录错误日志。
7. 返回 `a18` 结果。

## 6.3 `a122 -> a16` 字段转换

源文件：`a156#a1215(...)`

- `a16.a38 = a122.a1176`
- `a16.a37 = a122.a1177`
- `a16.a39 = a122.a1179`
- `a16.a123s = a122.a1181` 映射后的列表（映射字段如下）：
  - `a123.a177 <- a121.a1173`
  - `a123.a180 <- a121.a1170`
  - `a123.a181 <- a121.a1171`
  - `a123.a183 <- a121.a1174`
  - `a123.a178 <- a121.a1172`
  - 同时初始化 `a124/a17` 空集合，`a182=false`
  - 最后 `.distinct()` 去重

---

## 7. 物理合同模型分支（`PHYSICAL`）的可见行为

当 `calculateModelCategory(...)` 返回 `PHYSICAL`，`a156` 会分发到 `a10`（静态映射可见）。

源文件：`bcadmin-cashflowmodel/src/main/java/com/resrun/cash/b/a10.java`

`a10.a4(...)` 中可见的关键行为：

- 重新装载与本次上下文相关的数据集（出入库明细、事件、规格、应收、合同线、旧现金流等）。
- 对旧头值进行过滤（排除 `MARGIN_CALL`）。
- 执行一组按序号排序的引擎链（`a66/a67/.../a63` 等）。
- 末尾还会执行 `_a9.a8(...)`、`_a2.a8(...)`。
- 最终通过 `a11(a116)` 汇总生成 `a18` 返回。

说明：这里可以确认 `generateCashFlowModel` 的下游不是单一步骤，而是“加载数据 + 多引擎流水线”。

---

## 8. 数据流转总图（文字版）

1. 外部调用（Controller/业务服务）传入 `CashModelQueryCriteria`。  
2. `generateCashFlowModel` 校验 `headerType/linkId`。  
3. 用 `linkId + headerType + bav/match/inactive` 查询 `receipt_delivery_details`。  
4. 组装 `a122`（模型类别、状态、明细列表）。  
5. 若查不到明细，补一条最小 `a121` 兜底。  
6. 调 `a155.a1208(a122)`。  
7. `a156` 转 `a16` 上下文并按模型类别分发到对应计算器。  
8. 计算器内部加载关联数据并执行引擎链，返回 `a18`。  

---

## 9. 可直接确认的行为与注意点

> [!warning] 关键注意点
> - 本方法是 `void`，且不抛业务异常；失败感知主要依赖下游日志/异常传播
> - 当没有符合条件的出入库明细时，仍会触发引擎（通过兜底明细）
> - 本方法未读取 `criteria.computeFlag/localDate/...` 等字段；当前代码中只使用 `headerType/linkId`
> - 引擎调用加了 `synchronized (a155.class)`，意味着同进程内该入口具备串行化特征
> - `a18` 返回值在本方法里未消费，仅触发计算过程

---

## 10. 本文依据的核心代码位置

- `bcadmin-system/.../CashFlowProjectionServiceImpl.java`：`generateCashFlowModel(...)`
- `bcadmin-system/.../dto/CashModelQueryCriteria.java`
- `bcadmin-cashflowmodel/.../utils/RiskUtil.java`：`calculateModelCategory(...)`
- `bcadmin-cashflowmodel/.../cash/g/a122.java`
- `bcadmin-cashflowmodel/.../cash/g/a121.java`
- `bcadmin-cashflowmodel/.../a155.java`
- `bcadmin-cashflowmodel/.../a156.java`：`a1208(...)`、`a1215(...)`
- `bcadmin-cashflowmodel/.../cash/b/a10.java`（`PHYSICAL` 分支示例）

