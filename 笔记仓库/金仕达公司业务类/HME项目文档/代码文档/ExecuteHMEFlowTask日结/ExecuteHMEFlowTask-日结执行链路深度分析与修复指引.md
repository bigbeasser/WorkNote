# ExecuteHMEFlowTask 日结执行链路深度分析与修复指引

## 1. 文档目的

> [!abstract] 本文目标
> 本文用于紧急修复 `ExecuteHMEFlowTask.execute(String args)` 相关日结缺陷，重点回答：
> - 日结入口方法每一步在做什么
> - 哪些是核心业务方法，哪些是工具方法
> - 下游真实业务处理（价格、计价量、现金流、Session、系统日期推进）分别在哪
> - 建议修复时应采用的调用流程（附流程图）

***

## 2. 入口与总体定位

### 2.1 前端触发到本方法的链路

1. 前端调用 `PUT /api/jobs/execByTaskName/{name}`，且 `name=EOD-hme`。
2. `QuartzJobController.executionEODHme(...)` 做价格校验 `eodService.checkEODPrice(...)`。
3. 校验通过后执行 Quartz 任务（当前代码固定 `jobId=16`），并传入 `key=inside_1ilb`。
4. Quartz 反射调用任务 Bean，进入 `ExecuteHMEFlowTask.execute(String args)`。
5. `ExecuteHMEFlowTask` 基于 Activiti `processDefinitionKey` 启动 EOD 流程。
6. 流程节点由各 Delegate 调用 `EODServiceImp` 的业务方法。

***

## 3. execute 方法逐步骤深度说明（核心）

目标代码：`bcadmin-system/src/main/java/com/resrun/modules/quartz/task/ExecuteHMEFlowTask.java`

### Step A：设置全局日结状态为运行中

- 代码：`_redisUtils.set("EOD:Status", EODStatusEnum.RUNNING.getValue())`
- 作用：作为全局“正在日结”标记，供界面、对接、二次触发判断使用。
- 业务价值：避免并发重复启动，提供状态可观测性。

### Step B：解析请求参数并兼容 systemContext 二次封装

- 代码：`JSON.parseObject(args, HMEProcessDefinitionParameter.class)` + `systemContext` 再反序列化。
- 作用：兼容两种入参结构（直接参数 / 包裹在 `systemContext`）。
- 业务价值：兼容历史/不同调用方参数格式。
- 高风险点：如果 `systemContext` 与外层参数不一致，最终以 `systemContext` 覆盖，可能导致日期/机构偏差。

### Step C：初始化 EOD 上下文到 Redis（工具承载业务上下文）

- 调用：`initEODRedis(parameter)`
- 写入键：`EOD:SystemContext`、`EOD:CurveDate`、`EOD:NextDate`、`EOD:UserId`、`EOD:JobId` 等。
- 作用：为后续各节点（`EODServiceImp` 内 `initEodContext`）提供统一上下文来源。
- 说明：该方法本身偏工具，但它是后续业务方法能正确执行的前提。

### Step D：初始化控制开关默认值（工具）

- 调用：`initEODControl()`
- 作用：补齐 `EOD:control:*` 键的默认值 `0`。
- 注意：`EODServiceImp` 中目前主要改为从 `abutmentConfigService` 读取开关，此处 Redis 默认值对部分逻辑已是“兜底历史行为”。

### Step E：处理批量业务机构（legalEntityIds）

- 分支 1：`legalEntityIds[0] == "ALL"`
  - 从 `sys_company` 取启用且有效机构；
  - 全量写入 Redis 集合 `EOD:LegalEntityIds`。
- 分支 2：指定机构列表
  - 逐个 `sSet` 到 `EOD:LegalEntityIds`；
  - 清空 `parameter.legalEntityId / legalEntityIds`，准备后续逐个弹出处理。

业务意义：

- 把“单次触发日结”扩展成“机构队列串行处理”。

### Step F：从 Redis 机构队列弹出当前机构并确定结算日期上下文

- 条件：`if(_redisUtils.hasKey("EOD:LegalEntityIds"))`
- 动作：
  1. `setPop("EOD:LegalEntityIds")` 取当前机构；
  2. 若为空，判定全部处理完成，置 `EOD:Status=SUCCEED` 并返回；
  3. 若有机构：
     - 写入 `parameter.legalEntityId`；
     - 如果调用方未传 `curveDate`，则根据该机构当前 `session=1` 的 `CurvedateSession` 推导：
       - `curveDate = prevDate`
       - `nextDate = date`
       - 并重新 `initEODRedis(parameter)`；
     - 生成完成标记键 `EOD:Finished:{date}-{legalEntityId}`，未完成则设置当前运行机构 `EOD:LegalEntityId`。

业务意义：

- 这一步是“多机构日结循环”的关键调度逻辑。
- `EOD:Finished:*` 是幂等与重入保护关键机制。

### Step G：启动 Activiti 流程实例

- 查流程定义：`repositoryService.createProcessDefinitionQuery().processDefinitionKey(parameter.key)...`
- 构建变量：`userId / key / taskProcessId / systemContext / legalEntityId / curveDate(...)`
- 记录任务：`addProcessingInfo(...)`
- 启动流程：`runtimeService.startProcessInstanceById(...)`

业务意义：

- `execute` 自己不做重计算，主要负责“上下文准备 + 流程启动 + 状态追踪”。
- 真正价格、计价量、现金流等在 Delegate -> `EODServiceImp` 中。

### Step H：异常与任务状态落库

- 异常时：`TaskProcessingStatus.Error` + 记录 `TaskProcessingInfoLogsModel` + 抛出异常。
- 成功时：`TaskProcessingStatus.Success`。

***

## 4. 下游核心业务方法（排除纯工具方法）

以下为 EOD 流程节点最终调用的核心业务方法，位于 `EODServiceImp`。\
\
（`initEodContext`、`saveLog`、`addProcessingInfo`、`initEODControl` 等不作为核心业务方法）

### 4.1 `UpdateMovementEOD(BaseActivityContext)`（价格/计价量核心）

业务目标：

- 更新“日结口径”的 Movement 定价明细与计价量，并补齐缺失价格。

关键业务动作：

1. 按对接配置 `EOD:control:movement` 判定是否执行。
2. 查询当前机构有效合同（`PhysicalDeals`）。
3. 取合同号集合后并行执行：
   - `_movementPriceService.updateByDailySettlement(contractNumbers, curveDate)`
   - `_movementQuantityService.updateByDailySettlement(contractNumbers, curveDate)`
4. 汇总失败合同号并记日志。
5. 执行 `_movementQuantityService.updateMissingPriceByDailySettlement(curveDate)` 做回填。

典型故障面：

- 合同筛选条件漏/错导致未更新；
- `curveDate` 错误导致更新错日；
- 下游 service 返回错误列表但主流程仍“完成”。

### 4.2 `RollForwardPrice(BaseActivityContext)`（行情跨日复制）

业务目标：

- 将上一交易日 `ForwardPrice` 复制到新交易日，作为新日初始行情。

关键业务动作：

1. 根据 `curveDateId` 找当前 `Curvedate`（含 `prevDate/date`）。
2. 查 `prevDate` 的前值价格；
3. 先删除 `date` 当天同曲线旧数据；
4. 再插入一份拷贝（日期改成 `date`，主键置空）。

典型故障面：

- `curveDateId` 为空或不正确；
- 删除条件过宽/过窄导致重复或误删；
- 并发执行导致同日重复插入。

### 4.3 `ComputeBrassScorporoHMEEOD(BaseActivityContext)`（EOD 价格计算关键）

业务目标：

- 计算并复制黄铜 Scorporo 相关价格，是“日结价格计算”关键环节之一。

关键业务动作：

1. 读开关 `EOD:control:ComputeBrassScorporo`；
2. `_forwardPriceService.calculateCurvePrice(curveDate, null, "endOfDay")`；
3. `_forwardPriceService.copyComplicatePrice(curveDate, nextDate, 0, 1)`；
4. 根据成功标记写完成/失败日志。

典型故障面：

- `curveDate/nextDate` 任一为空；
- 计算成功但复制失败，最终状态不一致；
- 异常被吞（仅 `succeedFlag=false`）导致排障信息不足。

### 4.4 `UpdateContractHMEEOD(BaseActivityContext)`（现金流更新）

业务目标：

- 对应 HME 场景更新合约现金流结果。

关键业务动作：

1. 开关校验 `EOD:control:cashflow`；
2. 获取待处理合约明细；
3. 按定价公式类型与时间窗过滤不需重算的记录；
4. 按 `physicalDealId` 分组，逐合同调用风险引擎 `_a157.a1208(...)`；
5. 汇总失败合同并记录日志。

典型故障面：

- 过滤策略误杀导致漏算；
- 风险引擎异常仅记录，不中断全流程，可能掩盖严重问题。

### 4.5 `UpdateSecondSessionEOD(BaseActivityContext)`（日结推进到 Session2）

业务目标：

- 将机构推进到下一交易日 Session=2，并复制复杂价格到新 Session。

关键业务动作：

1. 失效已有 `session>=2` 记录；
2. 将 `nextDate` 的 `session=1` 标记为非 latest；
3. 插入新 `session=2`（latest=1）；
4. 调用 `_forwardPriceService.copyComplicatePrice(nextDate, nextDate, 1, 2)`。

典型故障面：

- Session 状态更新与插入非事务一致性问题；
- `nextDate` 缺失导致推进失败。

### 4.6 `FixationLockEOD / FixationUnlockEOD`

业务目标：

- 在日结前后同步 CRM/SAP 的 EOD 与 Session 状态（锁定/解锁）。

关键业务动作：

- 分别推送 `sessionStatus/eodStatus/session` 组合到 CRM 与 SAP。

业务价值：

- 保证外围系统与 CTRM 日结状态一致。

### 4.7 `UpdateInventoryReportEOD / UpdatePositionMonitorEOD / updateCurveDate`

- `UpdateInventoryReportEOD`：触发 SAP 库存增量入库；
- `UpdatePositionMonitorEOD`：生成持仓监控日结历史；
- `updateCurveDate`：当所有机构完成日结后推进系统曲线日期（全局日期推进关口）。

***

## 5. Delegate -> 业务方法映射（用于定位具体节点）

- `HMEMovementEODDelegate` -> `UpdateMovementEOD`
- `RollForwardPriceEODDelegate` -> `RollForwardPrice`
- `HMEBrassScorporoEODDelegate` -> `ComputeBrassScorporoHMEEOD`
- `HMEContractCashflowEODDelegate` -> `UpdateContractHMEEOD`
- `HMESessionEODDelegate` -> `UpdateSecondSessionEOD`
- `HMEFixationLockEODDelegate` -> `FixationLockEOD`
- `HMEFixationUnlockEODDelegate` -> `FixationUnlockEOD`
- `HMECurvedateEODDelegate` -> `updateCurveDate`
- `HMEFinishEODDelegate` -> `FinishProcessEOD`

***

## 6. 建议的“可修复”调用流程图

> 说明：仓库内未包含 `inside_1ilb` 的 BPMN 文件，以下是按现有 Delegate 与业务语义给出的建议顺序，用于修复方案设计与回归验证。

```mermaid
flowchart TD
    A[前端: 日结开始] --> B[/api/jobs/execByTaskName/EOD-hme]
    B --> C[QuartzJobController.executionEODHme]
    C --> C1[checkEODPrice]
    C1 -->|通过| D[Quartz执行 ExecuteHMEFlowTask.execute]
    D --> D1[初始化EOD上下文/机构队列]
    D1 --> E[启动Activiti流程 key=inside_1ilb]

    E --> F[HMEBrassScorporoEODDelegate]
    F --> F1[ComputeBrassScorporoHMEEOD: 计算EOD价格]
    F1 --> G[HMEMovementEODDelegate]
    G --> G1[UpdateMovementEOD: 更新计价量/定价明细]
    G1 --> H[HMEContractCashflowEODDelegate]
    H --> H1[UpdateContractHMEEOD: 现金流重算]
    H1 --> I[HMESessionEODDelegate]
    I --> I1[UpdateSecondSessionEOD: 推进到Session2]
    I1 --> J[HMEFixationUnlockEODDelegate]
    J --> J1[FixationUnlockEOD: 对外解锁推送]
    J1 --> K[HMECurvedateEODDelegate]
    K --> K1[updateCurveDate: 推进系统日期]
    K1 --> L[HMEFinishEODDelegate]
    L --> L1[FinishProcessEOD: 标记机构完成并触发下一机构]
```

***

## 7. 紧急修复建议（针对 execute 区域）

> [!warning]- 建议 1：修复/确认流程变量 `curveDate` 的来源一致性
> 当前代码固定：`variables.put(“curveDate”, LocalDate.now())`。
>
> 建议优先改为业务上下文日期（例如 `parameter.curveDate` 或 Redis 中 `EOD:CurveDate`），避免流程节点使用”系统当前日”导致错日结算。

> [!warning]- 建议 2：对 `parameter.key`、`legalEntityId`、`date` 增强前置校验
> - `parameter.key` 为空时，流程定义查询直接失败
> - `legalEntityId` 非数字会在 `Long.parseLong` 失败
> - `date` 可能为空导致 `EOD:Finished:null-xxx`
>
> 建议在启动流程前集中校验并记录结构化错误日志。

> [!warning]- 建议 3：把”机构弹出 + 启动流程”变为可观测事务边界
> 当前 `setPop` 后如果流程启动失败，机构可能丢失重试机会。
>
> 建议增加失败回补机制（例如失败时重新 `sSet` 当前机构）或持久化待处理列表。

> [!warning] 建议 4：将 `EOD:Status` 更新策略细化
> 目前在多个位置直接设置 RUNNING/SUCCEED/TEMP_COMPLETE。
>
> 建议补充”机构级状态 + 全局状态”双层状态，避免多机构串行时误判全局已完成。

***

## 8. 修复后最小回归清单

> [!check] 回归测试要点
> | 序号 | 测试场景 | 验证点 |
> | :---: | :--- | :--- |
> | 1 | 单机构日结 | 价格计算、movement 更新、session 推进、状态落库均成功 |
> | 2 | 多机构日结 | 前一个机构完成后自动触发下一机构 |
> | 3 | 缺失 `curveDate` | 可从 `CurvedateSession` 正确推导 |
> | 4 | 故障注入 | Activiti 启动失败时，机构不丢失、状态可恢复 |
> | 5 | 对外推送 | CRM/SAP 的 session/eod 状态与 CTRM 一致 |

***

## 9. 修复时建议优先关注的方法（按优先级）

> [!tip] 优先级排序
> | 优先级 | 方法 | 关注点 |
> | :---: | :--- | :--- |
> | 🔴 P0 | `ExecuteHMEFlowTask.execute` | 上下文与流程启动 |
> | 🟠 P1 | `EODServiceImp.ComputeBrassScorporoHMEEOD` | EOD价格计算 |
> | 🟡 P2 | `EODServiceImp.UpdateMovementEOD` | 价格/计价量落库 |
> | 🟢 P3 | `EODServiceImp.FinishProcessEOD` | 多机构续跑 |
> | 🔵 P4 | `EODServiceImp.updateCurveDate` | 全局日期推进 |
