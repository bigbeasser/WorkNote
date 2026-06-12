# CurveFormulaRanges表的rangeFormula逻辑
_Exported on 2026/3/13 at GMT+8 17:56:16 from Cursor (2.6.12)_

---

**User**

帮我找系统里从CurveFormulaRanges这个表里取出字段rangeFormula数据里面是计算公式,会用在系统哪里进行计算价格,有什么逻辑,帮我梳理下来,我要对此进行思考

---

**Cursor**

我先在代码里全局搜索 `CurveFormulaRanges` 和 `rangeFormula`，找出对应的实体/Mapper/Service 以及调用点，然后梳理：1）这些公式是怎么加载的；2）在哪些服务或定价流程里参与计算；3）有无特殊逻辑（如校验、回退、拆分等）。整理完会用中文给你做一个清晰的小结，方便你后续思考。

我先把跟 `CurveFormulaRanges` 和 `rangeFormula` 相关的几个核心类打开看看实现，然后给你梳理这个公式在价格计算中的整个流转和逻辑。

### 整体结论先说在前面

**`CurveFormulaRanges.rangeFormula` 本身并不直接参与“算数字”的价格计算，它主要有两个作用：**

- **定义合成曲线的“引用结构”**（这个衍生区间里到底引用了哪些基础曲线/合成曲线、marker、到期日等），然后由后台解析成 `ForwardCompositeCurve` 表的数据。
- **控制哪些合约文本在什么频率下需要被计算并入库**（日结 `endOfDay` / 实时 `realTime`，以及对哪些 `marker` 生效），从而影响后续价格写入 `ForwardPrice` / `IntradayPrice`。

**真正做算术运算的公式是在 `ForwardContract.rangeFormula` 上（合约层面），由 `ForwardPriceServiceImpl.calculateByPriority` 用 JEXL 引擎执行。**

下面我按“哪里用到、怎么用”的逻辑帮你梳理。

---

### 1. `CurveFormulaRanges.rangeFormula` 的存储位置

实体定义在：

```1:186:bcadmin-db/src/main/java/com/resrun/db/domain/CurveFormulaRanges.java
private String rangeFormula;
...
public String getRangeFormula() { ... }
public void setRangeFormula(String rangeFormula) { ... }
```

控制层增删改查在 `CurveController` 里就是“远期曲线衍生区间”这一块接口：

```641:699:bcadmin-system/src/main/java/com/resrun/modules/business/rest/CurveController.java
// 删除 / 查询 / 新增修改 / 列表
@DeleteMapping("fowardcurveranges")
@GetMapping("fowardcurveranges/info")
@PostMapping("fowardcurveranges")
@GetMapping("fowardcurveranges")
```

新增/修改时，会把前端传入的 `rangeFormula` 存到 `curve_formula_ranges.range_formula` 字段，并调用 `revalueDerivativeCurves` 做后处理（见下面第 2 点）。

---

### 2. 保存/修改衍生区间时：`rangeFormula` 如何被用来维护“合成关系”

对应 Service 是 `ForwardCurveRangesServiceImpl`：

```24:331:bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/ForwardCurveRangesServiceImpl.java
@Override
public int addAndUpdate(CurveFormulaRanges curveFormulaRanges) { ... }

@Override
public void revalueDerivativeCurves(CurveFormulaRanges curveFormulaRanges) {
    if (curveFormulaRanges.getForwardSettleFlag().equals("F")) {
        relation4Forward(curveFormulaRanges);
    } else {
        relation4Settle(curveFormulaRanges);
    }
}
```

#### 2.1 Forward（远期）场景：`relation4Forward`

核心代码：

```271:329:bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/ForwardCurveRangesServiceImpl.java
private void relation4Forward(CurveFormulaRanges curveFormulaRanges) {

    // 先删除这个 forwardCurveId + seq 下面旧的合成关系
    ForwardCompositeCurveExample forwardCompositeCurveExample = new ForwardCompositeCurveExample();
    forwardCompositeCurveExample.createCriteria()
        .andForwardCurveIdEqualTo(curveFormulaRanges.getForwardCurveId())
        .andSeqEqualTo(curveFormulaRanges.getSeq());
    forwardCompositeCurveMapper.deleteByExample(forwardCompositeCurveExample);

    // 1）从 rangeFormula 里面用正则提取出所有 Curve(...) 或 compositeCurve(...)
    Set<String> uniqueCurves = new HashSet<>();
    Pattern pattern1 = Pattern.compile("(Curve|compositeCurve)\\([^)]+\\)");
    Matcher matcher1 = pattern1.matcher(curveFormulaRanges.getRangeFormula());
    while (matcher1.find()) {
        uniqueCurves.add(matcher1.group());
    }
    List<String> curves = new ArrayList<>(uniqueCurves);

    // 2）把括号里的东西拆成 [curveId, marker, lastTradingDay, (可选)seq, 函数名] 这样的列表
    List<List<String>> valuesList = new ArrayList<>();
    for (String input : curves) {
        List<String> values = new ArrayList<>();
        Pattern pattern = Pattern.compile("\\(([^)]+)\\)");
        Matcher matcher = pattern.matcher(input);
        while (matcher.find()) {
            String[] parts = matcher.group(1).split(",");
            values.addAll(Arrays.asList(parts));
        }
        values.add(input.replaceAll("\\(.*?\\)", ""));
        valuesList.add(values);
    }

    // 3）组装成 ForwardCompositeCurve 记录
    List<ForwardCompositeCurve> newFormulaRanges = new ArrayList<>();
    for(List<String> matcher : valuesList){
        ForwardCompositeCurve ranges = new ForwardCompositeCurve();
        ranges.setCompositeForwardCurveId(Long.valueOf(matcher.get(0)));
        ranges.setMarker(matcher.get(1));
        ranges.setLastTradingDay(matcher.get(2));
        ranges.setFormulaType(matcher.get(3));
        if (matcher.size() > 4) {
            ranges.setCompositeSeq(matcher.get(3));
            ranges.setFormulaType(matcher.get(4));
        }
        newFormulaRanges.add(ranges);
    }

    // 4）插入 ForwardCompositeCurve 表
    for (ForwardCompositeCurve curveInsert : newFormulaRanges) {
        curveInsert.setForwardCurveId(curveFormulaRanges.getForwardCurveId());
        curveInsert.setCurveFormulaRangeId(curveFormulaRanges.getId());
        curveInsert.setSeq(curveFormulaRanges.getSeq());
        curveInsert.setCreatedBy(SecurityUtils.getCurrentUsername());
        curveInsert.setCreatedTime(LocalDateTime.now());
        curveInsert.setInactiveFlag(false);
        curveInsert.setRiskFlag("N");
        curveInsert.setWeighted(1.0d);
        curveInsert.setSpread(0.0d);

        compositeCurveService.addAndUpdate(curveInsert);
    }
}
```

**也就是说：**

- `CurveFormulaRanges.rangeFormula` 中的 **结构型公式**（比如 `Curve(353762008891393,Cash,2024-04-20)`、`compositeCurve(353762008891393,Cash,2024-04-20,1)`）被解析出来。
- 每个这样的片段，都会生成一条 `ForwardCompositeCurve` 记录，表示“本合成曲线（forwardCurveId + seq）引用了哪个基础/合成曲线、哪个 marker、哪个 lastTradingDay、哪个子序号（compositeSeq）”。
- **这个阶段不算价格，只是把“引用关系”从公式文本同步到结构化表。**

#### 2.2 Settle 场景：`relation4Settle`

`relation4Settle` 里也有对 `rangeFormula` 的解析（查找 `curve(` / `settlecurve(`，抽取 ID），但后面对 `SettlementCompositeCurve` 的维护代码都被注释掉了，当前版本等于只是在解析，没有实际改数据库。

---

### 3. 计算价格时：如何利用 `CurveFormulaRanges` 和其它表

核心计算在 `ForwardPriceServiceImpl.calculateCurvePrice`：

```java
public void calculateCurvePrice(LocalDate queryDate, List<Long> contractIds, String calculateFrequency) {
    ...
    // 1. 找要算的合约文本
    List<ForwardContract> contracts = forwardContractMapper.selectMixedCurve(contractIds, calculateFrequency);
    List<Long> forwardCurveIds = contracts.stream().map(ForwardContract::getForwardCurveId).collect(Collectors.toList());
    if (forwardCurveIds.isEmpty()) return;

    // 2. 根据 forwardCurveIds + 计算频率，查 curve_formula_ranges 里的公式配置
    CurveFormulaRangesExample curveFormulaRangesExample = new CurveFormulaRangesExample();
    curveFormulaRangesExample.or().andForwardCurveIdIn(forwardCurveIds).andInactiveFlagEqualTo(false)
            .andCalculateFrequencyLike(String.format("%%%s%%", calculateFrequency));
    List<CurveFormulaRanges> ranges = curveFormulaRangesMapper.selectByExampleWithBLOBs(curveFormulaRangesExample);
    Map<Long, CurveFormulaRanges> rangesMap = ranges.stream()
            .collect(Collectors.toMap(CurveFormulaRanges::getForwardCurveId, o -> o));

    // 3. 再查 ForwardCompositeCurve（这些是第 2 点里由 rangeFormula 推出来的）
    ForwardCompositeCurveExample forwardCompositeCurveExample = new ForwardCompositeCurveExample();
    forwardCompositeCurveExample.or().andForwardCurveIdIn(forwardCurveIds)
            .andInactiveFlagEqualTo(false).andMarkerIsNotNull();
    List<ForwardCompositeCurve> forwardCompositeCurveList = forwardCompositeCurveMapper.selectByExample(forwardCompositeCurveExample);

    // 4. 查所有合约 oldContractInfo（用来找被引用合约）
    ...

    if ("endOfDay".equals(calculateFrequency)) {
        // 5. 查当天的基础日结价格
        List<ForwardPriceRes> forwardPriceRes = forwardPriceMapper.getForwardPriceInCurvePrice(queryDate);
        ...
        Map<Long, BigDecimal> contractDayPrice = ... // 合约 -> 基础价格

        // 6. 按 Priority 用公式算出合成合约的价格
        calculateByPriority(contractDayPrice, contracts, forwardCompositeCurveList, oldContractInfo);

        // 7. 根据 rangesMap 的频率+marker 配置，看看哪些需要入库到 forward_price
        saveCurveForwardPriceData(marketPriceType, contracts, rangesMap, contractDayPrice, queryDate);

    } else if ("realTime".equals(calculateFrequency)) {
        // 同理，算实时价格，最后走 saveCurveTimePriceData
    }
}
```

#### 3.1 真正“算价格”的地方：`calculateByPriority`

**这里用到的公式不是 `CurveFormulaRanges.rangeFormula`，而是 `ForwardContract.rangeFormula`。**

```375:447:bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/ForwardPriceServiceImpl.java
public void calculateByPriority(Map<Long, BigDecimal> contractPrice,
                                List<ForwardContract> contracts,
                                List<ForwardCompositeCurve> forwardCompositeCurveList,
                                List<ForwardContract> oldContractInfo) {

    // 按 forwardCurveId + seq 分组，把前面（由 rangeFormula 推来的）ForwardCompositeCurve 生成为 map
    Map<String, List<ForwardCompositeCurve>> forwardCompositeCurveMap = forwardCompositeCurveList.stream()
            .collect(Collectors.groupingBy(o -> o.getForwardCurveId() + "-" + o.getSeq()));
    ...

    // 合约按 priority（优先级）从小到大，逐级算
    SortedMap<Integer, List<ForwardContract>> contractsByPriority = new TreeMap<>(contracts.stream()
            .collect(Collectors.groupingBy(ForwardContract::getPriority)));
    for (Integer priority : contractsByPriority.keySet()) {

        Map<String, ForwardContract> contractsInPriority = contractsByPriority.get(priority).stream()
                .collect(Collectors.toMap(record -> record.getForwardCurveId() + "-" + record.getSeq(), record -> record));

        for (String forwardCurveIdAndSeq : contractsInPriority.keySet()) {
            ForwardContract contractValue = contractsInPriority.get(forwardCurveIdAndSeq);

            Map<String, BigDecimal> map = new HashMap<>();
            boolean flag = false;

            // 1）通过 forwardCompositeCurveMap 找到“这个合约公式里引用了哪些别的合约”
            if (!CollectionUtils.isEmpty(forwardCompositeCurveMap.get(forwardCurveIdAndSeq))) {
                for (ForwardCompositeCurve item : forwardCompositeCurveMap.get(forwardCurveIdAndSeq)) {
                    // 根据 marker 和 compositeForwardCurveId 找到被引用的 old 合约
                    Long contractId = ...;
                    BigDecimal oldPrice = contractPrice.get(contractId);
                    ...

                    // 拼出跟 rangeFormula 里一样的 key：Curve(...) 或 compositeCurve(...)
                    if ("Curve".equals(item.getFormulaType())) {
                        String quotedContent = "Curve(" + item.getCompositeForwardCurveId() + "," +
                            item.getMarker() + "," + item.getLastTradingDay() + ")";
                        map.put(quotedContent, oldPrice);
                    } else {
                        String quotedContent = "compositeCurve(" + item.getCompositeForwardCurveId() + "," +
                            item.getMarker() + "," + item.getLastTradingDay() + "," + item.getCompositeSeq() + ")";
                        map.put(quotedContent, oldPrice);
                    }
                }
                if (flag) continue;
            }

            // 2）这里才取的是合约自身的 rangeFormula（ForwardContract.rangeFormula）
            final String[] formula = {contractValue.getRangeFormula()};
            // 把公式里的 Curve(...) 或 compositeCurve(...) 替换成具体数字
            map.forEach((key, value) -> {
                formula[0] = formula[0].replaceAll(Pattern.quote(key), value.toString());
            });

            // 3）用 JEXL 执行算术表达式，得到价格
            JexlEngine jexl = new JexlBuilder().create();
            JexlExpression expression = jexl.createExpression(formula[0]);
            JexlContext context = new MapContext();
            Object result = expression.evaluate(context);
            BigDecimal price = new BigDecimal(result.toString()).setScale(5, RoundingMode.HALF_UP);

            // 4）回写到 contractPrice（供更高优先级使用）
            contractPrice.put(contractValue.getId(), price);
        }
    }
}
```

**关键点：**

- `ForwardCompositeCurve` 的数据（即哪些 Curve(...)、compositeCurve(...)）是**从 `CurveFormulaRanges.rangeFormula` 解析出来的**。
- 合约层面真正的计算表达式（如 `0.4*Curve(...) + 0.6*Curve(...) - 10`）保存在 `ForwardContract.rangeFormula`。
- `calculateByPriority` 把 `ForwardCompositeCurve` 中的结构信息，和当前已有价格 map 拼在一起，把 `ForwardContract.rangeFormula` 里的“占位符调用”替换成数字，再用 JEXL 算。

#### 3.2 `CurveFormulaRanges` 对入库节奏的控制

`saveCurveForwardPriceData` / `saveCurveTimePriceData` 里，会拿 `rangesMap`（即按 forwardCurveId 取到的 `CurveFormulaRanges`）来判断哪些合约需要写入价格：

```461:515:bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/ForwardPriceServiceImpl.java
public void saveCurveForwardPriceData(String marketPriceType,
                                      List<ForwardContract> contracts,
                                      Map<Long, CurveFormulaRanges> rangesMap,
                                      Map<Long, BigDecimal> contractDayPrice,
                                      LocalDate queryDate) {
    ...
    // 按合约文本 分类合约
    Map<Long, List<ForwardContract>> forwardContractMap = contracts.stream()
        .collect(Collectors.groupingBy(ForwardContract::getForwardCurveId));
    for (Long id : forwardContractMap.keySet()) {
        CurveFormulaRanges formula = rangesMap.get(id);
        // 只对需要 endOfDay 的 forwardCurveId 写库
        if (formula == null || !formula.getCalculateFrequency().contains("endOfDay")) {
            continue;
        }
        for (ForwardContract contract : forwardContractMap.get(id)) {
            // marker 也要匹配：All 或相同 marker
            if ("All".equals(formula.getMarker()) || contract.getMarker().equals(formula.getMarker())) {
                ...
                // 在 forward_price 中插入或更新对应价格
            }
        }
    }
}
```

实时价格 `saveCurveTimePriceData` 同理，只是判断 `calculateFrequency` 是否包含 `realTime`。

所以：**`CurveFormulaRanges` 决定了“这个 forwardCurveId + marker 在某种频率下要不要参与“合成曲线价格”的入库动作”。**

---

### 4. 你可以怎么理解 / 思考这个设计

- **区间/曲线维度的公式（结构）**：`CurveFormulaRanges.rangeFormula`
  - 用“函数调用”的形式（`Curve(...)` / `compositeCurve(...)` / `settlecurve(...)` 等）声明“这个衍生区间引用了哪些其他曲线、marker、lastTradingDay、子区间 seq”。
  - 保存/修改时，系统解析它，维护 `ForwardCompositeCurve`（以及将来可能的 `SettlementCompositeCurve`）表中的合成关系。
  - 另外还带 `calculateFrequency`、`marker` 等字段，控制**哪些 forwardCurveId + marker + 频率**需要被计算和入库。

- **合约维度的公式（算术表达式）**：`ForwardContract.rangeFormula`
  - 真正的价格计算公式，类似：  
    `0.4 * Curve(A, Cash, 2024-04-20) + 0.6 * compositeCurve(B, Cash, 2024-04-20,1) - 5`
  - 在计算时，`calculateByPriority` 把这些 `Curve(...)` 占位符替换成真实数字，然后用 JEXL 执行。

- **计算流程上与价格的关系：**
  1. 你在界面上配置/修改衍生区间的 `rangeFormula` → `ForwardCurveRangesServiceImpl.relation4Forward` 解析，生成/更新 `ForwardCompositeCurve`。
  2. 定时任务或接口触发 `calculateCurvePrice`：
     - 先根据 `CurveFormulaRanges` 的 `calculateFrequency` / `marker` 筛出要算、要入库的 forwardCurve。
     - 再根据 `ForwardCompositeCurve`（来源于第 1 步）知道每个合约公式里引用哪些基础价格。
     - 最终在 `calculateByPriority` 中用 `ForwardContract.rangeFormula` 做算术运算，结果写入 `ForwardPrice` / `IntradayPrice`。

---

### 5. 如果你要“思考/调整”这一块，可以着重考虑：

- **结构公式 vs 算术公式的职责划分合不合理**  
  现在结构信息放在 `CurveFormulaRanges.rangeFormula`，算术放在 `ForwardContract.rangeFormula`，是否会给业务人员带来理解成本（要在两个地方看公式）？

- **`rangeFormula` 的语法设计**  
  - 是否需要更清晰的 DSL（比如强约束的 JSON / 配置表），而不是靠正则去拆 `Curve(...)` 字符串。
  - `relation4Forward` 里 `matcher.size() > 4` 时把 `matcher.get(3)` 既当 `compositeSeq` 又当 `formulaType` 的逻辑，看起来有歧义，值得你再审查一下。

- **频率与 marker 控制**  
  - 现在 `calculateFrequency` 存在 `CurveFormulaRanges` 上，`ForwardContract` 只管自己的算术公式，这个中间层的存在是否满足你对“日结/实时/不同 marker 是否参与合成”的需求。

如果你希望，我可以针对某一条你关心的 `CurveFormulaRanges.rangeFormula` 示例，帮你逐步“从文本 → ForwardCompositeCurve → 计算价格”的具体案例走一遍。

