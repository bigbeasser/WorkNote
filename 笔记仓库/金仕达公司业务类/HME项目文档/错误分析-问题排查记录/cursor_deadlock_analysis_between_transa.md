# Deadlock analysis between transactions
_Exported on 2026/3/18 at GMT+8 13:47:58 from Cursor (2.6.12)_

---

**User**

事务 1（TRX 921587406）	事务 2（TRX 921587226）
执行 SQL：批量更新 cashflow_model_values 表，修改多个字段（cashflow_model_header_vaule_id、quantity、settlement_price 等）	执行 SQL：更新 cashflow_model_values 表，仅修改 invoice_complete_flag 字段，条件是 cashflow_model_value_id in (8876643696115725)
持有锁：表中 heap no 25/26/27/28 等行的排他锁（X 锁）	持有锁：表中 heap no 50/51/52/53/54/55/56 等行的排他锁（X 锁）
等待锁：heap no 50 行的排他锁	等待锁：heap no 25 行的排他锁
最终结果：事务 1 被 MySQL 回滚	最终结果：事务 2 继续执行    分析代码发生死锁的代码和给出建议

---

**Cursor**

### 一、根据你给的信息先还原一次死锁场景

你描述的两条事务状态，本质是典型的「相互持有部分行锁，再去请求对方已经持有的行锁」的死锁：

- **事务 1**
  - 批量更新 `cashflow_model_values`，一次性更新多列（`cashflow_model_header_value_id、quantity、settlement_price...`）。
  - 先锁住了 `heap no 25/26/27/28...` 等几行的 X 锁。
  - 之后又想更新（或扫描到）`heap no 50`，但 `heap no 50` 已经被事务 2 用 X 锁锁住，于是 **等待** 事务 2 释放。

- **事务 2**
  - 更新 `cashflow_model_values`，只改 `invoice_complete_flag`，条件是 `cashflow_model_value_id in (8876643696115725)`。
  - 先锁住了 `heap no 50/51/52/53/54/55/56...` 等几行的 X 锁。
  - 之后又因为执行计划/扫描顺序，尝试访问到 `heap no 25`，但这行已被事务 1 锁住，于是 **等待** 事务 1 释放。

结果是：
- 事务 1 等待事务 2 的 `heap no 50` 行锁；
- 事务 2 等待事务 1 的 `heap no 25` 行锁；
- 构成环路，InnoDB 检测到死锁，选择回滚其中一个（你这里是事务 1 被回滚）。

### 二、可能的 3–5 个具体原因假设（从代码层面推）

结合业务描述，给出几个更贴近「代码」层面的假设，方便你去对应定位：

1. **假设 A：两段更新 SQL 对同一批业务数据行，访问顺序不一致**
   - 事务 1 的批量更新语句：可能是 `UPDATE ... WHERE header_id = ?`，导致涉及很多行（含 heap 25–28、50–56）。
   - 事务 2 的更新只针对特定的 `cashflow_model_value_id in (...)`，执行计划可能按某个索引顺序（如 PK 顺序）访问。
   - 如果：
     - 事务 1 按「条件扫描顺序」先锁到 heap 25–28 再扫到 50–56；
     - 事务 2 按「PK 顺序」先锁到 50–56 再扫到 25–28；
     - 就很容易在中间某个点出现「A 持有 25，等 50；B 持有 50，等 25」。

2. **假设 B：使用了不同索引/条件，导致 MySQL 对同一表同一批行的访问路径不一致**
   - 事务 1 的 `UPDATE` 使用条件比如：`WHERE cashflow_model_header_id = ? AND trade_date BETWEEN ...`，走复合索引。
   - 事务 2 的 `UPDATE` 使用条件：`WHERE cashflow_model_value_id IN (...)`，走主键索引。
   - 不同索引 + 不同扫描方向，会导致锁行顺序看起来是「随机的」，从而和另一条 SQL 的扫描顺序交错，制造死锁。

3. **假设 C：事务粒度过大，批量更新覆盖了很多与开票标记相关的行**
   - 事务 1 的批量更新覆盖了大量行，持续时间较长。
   - 同时并发有很多事务 2（不同 invoice 操作）更新 `invoice_complete_flag`，分别锁住不同行。
   - 行锁持有时间长 + 交叉访问不同行，更容易形成环路。

4. **假设 D：业务代码中，两种操作路径使用了不同的「前置查询顺序」**
   - 例如：
     - 「模型计算保存」路径：先按某个 header、期数等，查询/更新所有 `cashflow_model_values`。
     - 「发票完成标记」路径：先根据 valueId 列表进行更新。
   - 如果这两条路径在一个业务流程内还混合使用（甚至互相调用），就会更频繁产生该死锁模式。

5. **假设 E：隔离级别（如 REPEATABLE READ）+ 范围条件，导致额外 gap 锁/next-key 锁**
   - 如果事务 1 的 SQL 是范围更新（`BETWEEN`，`<`、`>` 等），在 RR 下会产生 gap/next-key 锁。
   - 事务 2 某些情况下也会触发范围扫描，导致锁的粒度和边界不一致，诱发死锁。

### 三、从代码层面，你应该重点排查的地方

在你的 Java / MyBatis / JPA / 自己写的 JDBC 代码中，大概率会有类似结构：

- **模型计算保存 / 批量更新路径（事务 1）**
  - 某个 `Service` 方法（比如 `CashflowModelService.saveOrUpdateValues(...)`）：
    - 开启事务；
    - 查询一批 `cashflow_model_values`；
    - 批量更新多个字段；
    - 提交事务。

- **发票完成 / 标记路径（事务 2）**
  - 某个 `InvoiceService.markComplete(...)` 或类似方法：
    - 开启事务；
    - 根据 `cashflow_model_value_id` 列表更新 `invoice_complete_flag`；
    - 可能还有其他检查/更新；
    - 提交事务。

你可以重点去找：

- `UPDATE cashflow_model_values` 相关的 DAO/Mapper：
  - 是否有：
    - 一种是 `UPDATE cashflow_model_values SET ... WHERE cashflow_model_value_id IN (...)`；
    - 另一种是 `UPDATE cashflow_model_values SET ... WHERE cashflow_model_header_id = ?` 或其他条件。
- 这两类操作是否都在 `@Transactional` 方法中，并且会对同一批业务数据并发执行。

### 四、优化与改进建议（从易到难）

#### 1. **统一行锁顺序（强烈推荐）**

**目标：所有对 `cashflow_model_values` 更新的代码，对同一批业务行的锁定顺序要一致（通常按主键升序）。**

可落地方式：

- **SQL 级别统一顺序**
  - 对批量更新，总是通过一个「先查后改」的流程：
    1. `SELECT cashflow_model_value_id FROM cashflow_model_values WHERE ... ORDER BY cashflow_model_value_id FOR UPDATE;`
    2. 然后在同一个事务中按照查询结果顺序逐条或批量更新。
  - 对单独的发票标记更新：
    - 把 `IN (...)` 的参数列表在代码中按 `cashflow_model_value_id` 排序后再传给 SQL，保证也是按 PK 顺序锁行。

- **示例思路（伪代码）：**

```java
// 事务 1 路径：统一按 PK 顺序锁行
List<Long> ids = cashflowModelValuesMapper.selectIdsForUpdate(headerId);
// mapper 内部 SQL：SELECT cashflow_model_value_id FROM cashflow_model_values WHERE header_id = ? ORDER BY cashflow_model_value_id FOR UPDATE

for (Long id : ids) {
    cashflowModelValuesMapper.updateMainFieldsById(id, ...);
}

// 事务 2 路径：也按 PK 排序传入
List<Long> valueIds = getValueIdsFromInvoice(...);
Collections.sort(valueIds);
cashflowModelValuesMapper.updateInvoiceCompleteFlag(valueIds, completeFlag);
```

- 原理：所有更新最终都是按 `cashflow_model_value_id` 升序锁行，InnoDB 不会出现「A 占前半段锁，B 占后半段锁再反向请求」的环路。

#### 2. **把「只改发票标记」的更新，尽量合并到主事务里**

如果业务允许：

- 在执行模型计算 / 保存时，就直接对 `invoice_complete_flag` 做好最终状态更新，而不是另开一个事务在后面再单独更新。
- 或者：
  - 用「事件驱动/异步队列」的方式，在主事务提交后，由单独的后台任务串行处理发票标记，使得同一行不会被两个事务同时碰。

好处：

- 减少并行写同一张表同一批行的事务数量，自然降低死锁概率。

#### 3. **缩小批量更新范围 & 控制事务时长**

- 把特别大的批量更新拆分成小批量：
  - 例如一次更新几百/几千行，而不是几万行。
- 不要在事务中做长时间业务逻辑、远程调用、人工等待等。
  - 保证从事务开始到提交尽可能短。

#### 4. **显式使用 `SELECT ... FOR UPDATE` 对关键行加锁，提前锁定**

- 对某些必须一致读取+更新的场景，可以先显式：
  - `SELECT ... FROM cashflow_model_values WHERE ... ORDER BY cashflow_model_value_id FOR UPDATE;`
- 让所有路径都先通过这一「加锁统一口」，保证锁顺序统一。

#### 5. **从框架层增加重试机制**

即使代码做了大量优化，在高并发写同一批数据时，MySQL 死锁依然有可能偶发：

- 建议在数据访问层/事务拦截器层，对 `Deadlock found when trying to get lock` / `Lock wait timeout exceeded` 等错误，增加 **有限次自动重试**（例如 1–3 次）。
- 这不能解决根因，但可以让偶发死锁对用户透明。

### 五、如果你能提供相关代码，我可以帮你精确标出风险点

你可以把：

- 负责批量更新 `cashflow_model_values` 的 `Service/Mapper` 方法；
- 负责更新 `invoice_complete_flag` 的 `Service/Mapper` 方法；

贴出来（或用 @ 文件路径），我可以：

- 明确指出哪两段代码之间存在不一致的锁顺序；
- 给你具体的 SQL/Java 重构方案，做到「这两条路径一定按相同顺序锁行」。

---

### 六、给你一份建议的复现/验证步骤

你后面调整代码/SQL 之后，可以按类似步骤在测试环境验证死锁是否消失或显著下降。

<reproduction_steps>
1. 在测试库中准备一批满足两个业务场景的相同 cashflow_model_values 行数据（确保两种 SQL 会命中同一批主键行）。
2. 启动应用，使批量更新模型数据的功能（事务 1 路径）和更新 invoice_complete_flag 的功能（事务 2 路径）都可被调用。
3. 使用压力脚本或并发工具（如 JMeter、自写多线程程序）同时高并发触发这两类操作，观察 MySQL 的死锁日志与应用异常日志。
4. 应用你选择的改动方案（统一行锁顺序/合并更新/拆分批次等），重新部署应用，保持同样的测试数据和压力脚本再跑一轮。
5. 对比两轮测试中 MySQL 的死锁日志和应用侧的异常情况，确认死锁是否消失或显著降低，确认后在工具中按 Proceed/Mark as fixed 完成本轮验证。
</reproduction_steps>

