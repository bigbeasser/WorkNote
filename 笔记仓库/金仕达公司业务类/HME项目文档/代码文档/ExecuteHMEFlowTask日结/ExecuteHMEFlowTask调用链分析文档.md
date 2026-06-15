# ExecuteHMEFlowTask.execute() 调用链分析文档

> [!info] 文档信息
> - **生成日期**: 2026-06-01
> - **源文件**: `bcadmin-system/src/main/java/com/resrun/modules/quartz/task/ExecuteHMEFlowTask.java`
> - **系统定位**: **CTRM (Commodity Trading and Risk Management) 大宗商品贸易 ERP 系统**，涉及合金、半成品、产成品等商品的贸易与风险管理

---

## 一、总体概述

> [!abstract] 功能概述
> `ExecuteHMEFlowTask.execute()` 是 HME 系统 **日结 (End-of-Day, EOD)** 流程的入口方法。它由 Quartz 定时任务调度触发，负责：
> 1. 解析任务参数，初始化 Redis 中的日结状态和控制标志
> 2. 按 **业务机构** (`legalEntityId`) 逐个启动 **Activiti 工作流**
> 3. 工作流内按顺序执行多个业务步骤
> 4. 每个业务机构完成后自动触发下一个机构的处理

---

## 二、完整调用链总览

```
Quartz Scheduler 触发定时任务
  └─> ExecutionJob.executeInternal()
       └─> QuartzRunnable.call()  (反射调用)
            └─> ExecuteHMEFlowTask.execute(args)
                 │
                 ├─ 1. 设置 EOD:Status = RUNNING
                 ├─ 2. 解析 JSON 参数 → HMEProcessDefinitionParameter
                 ├─ 3. initEODRedis(parameter)        → 写入 Redis 上下文
                 ├─ 4. initEODControl()                → 初始化控制开关
                 ├─ 5. 处理业务机构列表                  → 写入 Redis Set
                 ├─ 6. 弹出一个业务机构 ID
                 ├─ 7. 查询交易时段(CurvedateSession)确定日期
                 ├─ 8. addProcessingInfo()             → 创建任务处理记录
                 ├─ 9. 查询 Activiti ProcessDefinition
                 └─ 10. runtimeService.startProcessInstanceById()
                          │
                          └─> Activiti BPMN 工作流执行
                               │
                               ├─ HMEFixationLockEODDelegate       → 定价锁定：通知 CRM/SAP
                               ├─ HMEBrassScorporoEODDelegate      → 计算 Brass 升贴水曲线价格
                               ├─ HMEContractCashflowEODDelegate   → 更新合同现金流
                               ├─ HMEMovementEODDelegate            → 更新物流定价/数量
                               ├─ HMEPositionMonitorEODDelegate     → 生成持仓监控历史
                               ├─ HMEInventoryReportEODDelegate     → 从 SAP 更新库存报表
                               ├─ HMELMEScorpCheckEODDelegate       → LME 升贴水价格校验
                               ├─ HMESessionEODDelegate             → 创建交易时段 Session 2
                               ├─ HMECurvedateEODDelegate           → 更新估值日期
                               ├─ HMEFixationUnlockEODDelegate      → 定价解锁：通知 CRM/SAP
                               └─ HMEFinishEODDelegate              → 完成 & 触发下一业务机构
```

---

## 三、Quartz 调度层

### 3.1 触发链路

| 层级 | 类 | 方法 | 说明 |
|------|-----|------|------|
| 1 | `QuartzManage` | `addJob()` / `runJobNow()` | 注册/立即触发 Quartz 任务 |
| 2 | `ExecutionJob` | `executeInternal()` | Quartz Job 执行器，创建 `QuartzRunnable` |
| 3 | `QuartzRunnable` | `call()` | 通过 Spring `getBean(beanName)` + 反射调用目标方法 |
| 4 | `ExecuteHMEFlowTask` | `execute(args)` | **日结入口**，beanName = `"executeHMEFlowTask"` |

### 3.2 QuartzJob 配置字段

```
beanName:   "executeHMEFlowTask"
methodName: "execute"
params:     JSON 字符串 (HMEProcessDefinitionParameter)
cronExpression: 定时表达式
subTask:    子任务 ID（逗号分隔）
```

---

## 四、execute() 方法详细流程

### 4.1 参数解析

```java
HMEProcessDefinitionParameter parameter = JSON.parseObject(args, HMEProcessDefinitionParameter.class);
```

**HMEProcessDefinitionParameter 字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `key` | String | Activiti 流程定义 Key（如 `"HME_EOD_Process"`） |
| `systemContext` | Object | 系统上下文（嵌套 JSON 时二次解析） |
| `userId` | Long | 触发用户 ID |
| `jobId` | Long | Quartz 任务 ID |
| `userName` | String | 触发用户名 |
| `legalEntityId` | String | 单个 **业务机构** ID（对应 `SysCompany` 表） |
| `legalEntityIds` | List\<String\> | **业务机构** ID 列表（可为 `"ALL"`） |
| `curveDate` | String | **估值日期**（远期曲线估值基准日） |
| `preDate` | String | 前一交易日 |
| `nextDate` | String | 下一交易日 |
| `name` | String | 任务名称 |

### 4.2 执行步骤

#### Step 1: 设置日结状态为运行中
```java
_redisUtils.set("EOD:Status", EODStatusEnum.RUNNING.getValue());  // 值 = 1
```

#### Step 2: 初始化 Redis 上下文 — `initEODRedis(parameter)`
将参数写入 Redis，供后续工作流各步骤读取：

| Redis Key | 值 | 说明 |
|-----------|-----|------|
| `EOD:SystemContext` | JSON 字符串 | 序列化后的参数上下文 |
| `EOD:CurveDate` | 日期字符串 | 当前 **估值日期** |
| `EOD:PreDate` | 日期字符串 | 前一交易日 |
| `EOD:NextDate` | 日期字符串 | 下一交易日 |
| `EOD:UserId` | 用户 ID | 触发用户 |
| `EOD:UserName` | 用户名 | 触发用户名 |
| `EOD:JobId` | 任务 ID | Quartz Job ID |
| `EOD:Key` | 流程 Key | Activiti 流程定义 Key |

#### Step 3: 初始化控制开关 — `initEODControl()`
在 Redis 中初始化以下控制标志（默认值 `"0"`，表示不执行）：

| Redis Key | 控制目标 |
|-----------|---------|
| `EOD:control:ComputeBrassScorporo` | Brass **升贴水**价格计算 |
| `EOD:control:cashflow` | 合同**现金流**更新 |
| `EOD:control:movement` | **物流**定价/数量更新 |
| `EOD:control:PositionMonitor` | **持仓监控**历史生成 |
| `EOD:control:metalBullitino` | **金属锭**更新 |
| `EOD:control:lock` | CRM/SAP **定价锁定/解锁** |
| `EOD:control:inventoryReport` | **库存报表**更新 |
| `EOD:control:LMEScorpCheck` | LME **升贴水**价格校验 |
| `EOD:control:updateCurveCate` | **估值日期**更新 |

> 控制标志值为 `"1"` 时对应步骤才会执行。实际运行时这些值从 `abutmentConfigService` 读取。

#### Step 4: 处理业务机构列表

```
if legalEntityIds == ["ALL"]:
    查询 SysCompany (业务机构表) 中 enableFlag=true, inactiveFlag=false 的记录
    将所有业务机构 ID 写入 Redis Set "EOD:LegalEntityIds"
else:
    将指定的业务机构 ID 逐个写入 Redis Set "EOD:LegalEntityIds"
```

#### Step 5: 弹出一个业务机构并处理

```
从 Redis Set "EOD:LegalEntityIds" 弹出一个业务机构 ID
  ├─ 若为空 → 设置 EOD:Status = SUCCEED，结束
  └─ 若有值 →
       ├─ 若无 curveDate → 查询 CurvedateSession(交易时段表) 获取最新时段的 prevDate / date
       ├─ 检查 "EOD:Finished:{date}-{业务机构ID}" 是否已完成
       ├─ 设置 "EOD:LegalEntityId" 和 "EOD:Status"
       └─ 启动 Activiti 工作流
```

#### Step 6: 启动 Activiti 工作流

```java
ProcessDefinition pd = repositoryService.createProcessDefinitionQuery()
    .processDefinitionKey(parameter.key)
    .latestVersion()
    .singleResult();

Map<String, Object> variables = new HashMap<>();
variables.put("dateTime", new Date());
variables.put("userId", parameter.userId);
variables.put("key", parameter.key);
variables.put("taskProcessId", UUID.randomUUID().toString());
variables.put("systemContext", parameter.systemContext);
variables.put("userName", parameter.userName);
variables.put("jobId", parameter.jobId);
variables.put("legalEntityId", parameter.legalEntityId);   // 业务机构 ID
variables.put("curveDate", LocalDate.now());                // 估值日期

ProcessInstance pi = runtimeService.startProcessInstanceById(pd.getId(), "001", variables);
```

#### Step 7: 任务处理记录 — `addProcessingInfo()`

在工作流启动前创建任务跟踪记录：
- 创建 `TaskProcessingInfoModel`（状态 = Processing）
- 记录参数 `jobId` 和 `key`
- 工作流成功 → 更新状态为 Success
- 工作流异常 → 更新状态为 Error，记录错误日志

---

## 五、Activiti 工作流层

### 5.1 委托基类继承关系

```
JavaDelegate (Activiti 接口)
  └─ BaseActivityDelegate<T extends BaseActivityContext>   ← 模板方法模式
       └─ BaseEODDelegate                                  ← 日结专用基类
            ├─ HMEFixationLockEODDelegate       (定价锁定)
            ├─ HMEBrassScorporoEODDelegate      (Brass升贴水计算)
            ├─ HMEContractCashflowEODDelegate   (合同现金流)
            ├─ HMEMovementEODDelegate            (物流定价/数量)
            ├─ HMEPositionMonitorEODDelegate     (持仓监控)
            ├─ HMEInventoryReportEODDelegate     (库存报表)
            ├─ HMELMEScorpCheckEODDelegate       (LME升贴水校验)
            ├─ HMESessionEODDelegate             (交易时段)
            ├─ HMECurvedateEODDelegate           (估值日期)
            ├─ HMEFixationUnlockEODDelegate      (定价解锁)
            ├─ HMEMetalBullitinoEODDelegate      (金属锭)
            └─ HMEFinishEODDelegate              (完成)
```

### 5.2 BaseActivityDelegate 执行模板

```
execute(DelegateExecution)
  │
  ├─ 1. initContext(execution)          → 从工作流变量反序列化 Context
  ├─ 2. afterInit(execution, context)   → 子类钩子（设置 mode、processingNode）
  ├─ 3. setProcessBeforeLog(...)        → 记录 "开始执行" 日志
  ├─ 4. internalProcess(...)
  │     └─ process(execution, context)  → 【子类实现具体业务逻辑】
  ├─ 5. setProcessAfterLog(...)         → 记录 "执行结束" 日志
  └─ 6. processAfter(execution, context)→ 将 Context 序列化回工作流变量

异常处理：
  catch (Exception) →
    ├─ 记录 TaskProcessingInfoLogsModel（错误级别 = ENGINE_ERROR）
    ├─ 更新任务状态为 Error
    ├─ 调用 pushErrorMessage() 通知
    └─ 重新抛出异常，终止工作流
```

### 5.3 BaseEODDelegate 增强

- 从 BPMN Field Extension 注入：`mode`、`namedQuery`、`processingNode`、`modelCategory`、`filterId`、`revaluationFilterId`
- 通过 `SpringContextHolder` 获取静态依赖：`EODService`、`RedisUtils`、`EODUtils`

---

## 六、日结工作流步骤详解

### 6.1 步骤总览

| 序号 | Delegate 类 | EODService 方法 | 控制标志 | 说明 |
|------|-------------|----------------|---------|------|
| 1 | `HMEFixationLockEODDelegate` | `FixationLockEOD()` | `EOD:control:lock` | **定价锁定**：通知 CRM/SAP 冻结交易 |
| 2 | `HMEBrassScorporoEODDelegate` | `ComputeBrassScorporoHMEEOD()` | `EOD:control:ComputeBrassScorporo` | 计算 Brass **升贴水**曲线价格 |
| 3 | `HMEContractCashflowEODDelegate` | `UpdateContractHMEEOD()` | `EOD:control:cashflow` | 更新合同**现金流** |
| 4 | `HMEMovementEODDelegate` | `UpdateMovementEOD()` | `EOD:control:movement` | 更新**物流**定价和数量 |
| 5 | `HMEPositionMonitorEODDelegate` | `UpdatePositionMonitorEOD()` | `EOD:control:PositionMonitor` | 生成**持仓监控**历史数据 |
| 6 | `HMEInventoryReportEODDelegate` | `UpdateInventoryReportEOD()` | `EOD:control:inventoryReport` | 从 SAP 更新**库存报表** |
| 7 | `HMELMEScorpCheckEODDelegate` | `LMEScorpCheckEOD()` | `EOD:control:LMEScorpCheck` | LME **升贴水**价格校验 |
| 8 | `HMESessionEODDelegate` | `UpdateSecondSessionEOD()` | 无（始终执行） | 创建 **交易时段 Session 2** |
| 9 | `HMECurvedateEODDelegate` | `updateCurveDate()` | `EOD:control:updateCurveCate` | 更新系统**估值日期** |
| 10 | `HMEFixationUnlockEODDelegate` | `FixationUnlockEOD()` | `EOD:control:lock` | **定价解锁**：通知 CRM/SAP 恢复交易 |
| 11 | `HMEFinishEODDelegate` | `FinishProcessEOD()` | 无（始终执行） | 标记完成，触发下一**业务机构** |

> **注意：** BPMN 中步骤的实际执行顺序由流程定义文件决定，上表为逻辑顺序。BPMN 文件存储在 Activiti 数据库中，不在源码仓库内。

### 6.2 各步骤详细说明

---

#### 步骤 1: FixationLockEOD — 定价锁定（通知 CRM/SAP）

**目的：** 在日结处理期间对外部系统（CRM 和 SAP）发送 **定价锁定(Fixation Lock)** 通知，冻结交易操作，防止数据不一致。

**执行逻辑：**
1. 从 Redis 加载上下文 (`initEodContext`)
2. 查询 `SysCompany`（**业务机构表**）获取公司代码
3. **推送 CRM 锁定通知：**
   - `EodAndSessionRequest`：`sessionStatus="0"`, `eodStatus="0"`, `session="1"`, `curveDate=nextDate`
   - 调用 `_crmDockingService.pushEodAndSession(request)`
4. **推送 SAP 锁定通知：**
   - `SapSessionRequest`：`sessionStatus="0"`, `eodStatus="0"`, `session="1"`, `zxtbs="CTRM"`
   - 调用 `sapDockingService.pushEodAndSessionToSap(request)`

---

#### 步骤 2: ComputeBrassScorporoHMEEOD — 计算 Brass 升贴水曲线价格

**目的：** 计算 Tube/Special Brass **升贴水(Scorporo)** 价格，并将复杂价格从当前日期复制到下一日期的交易时段 Session 1。

**执行逻辑：**
1. 调用 `_forwardPriceService.calculateCurvePrice(curveDate, null, "endOfDay")` — 计算**远期曲线价格**
2. 调用 `_forwardPriceService.copyComplicatePrice(curveDate, nextDate, 0, 1)` — 复制复杂**远期价格**到下一日 Session 1

---

#### 步骤 3: UpdateContractHMEEOD — 更新合同现金流

**目的：** 对有效**实物合同(PhysicalDeals)** 重新计算**现金流(Cashflow)**。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 查询有效合同：`_eodMapper.getAllValidContractDataHME(curveDate, legalEntityId)` — 按**业务机构**和**估值日期**筛选
3. **按定价公式过滤：**
   - `BasicFixedPrice`（固定价定价）：合同日期超过 curveDate 6 天前的移除
   - `BasicAveragePrice`（均价定价）：合同日期和结束日期都超过 6 天前的移除
4. 按 `physicalDealId`（**实物交易 ID**）分组
5. 对每组调用现金流引擎 `_a157.a1208()` 计算
6. 收集并记录出错的 physicalDealId

**涉及 SQL：**
- `_eodMapper.getAllValidContractDataHME(curveDate, legalEntityId)` — 查询有效实物合同数据

---

#### 步骤 4: UpdateMovementEOD — 更新物流定价和数量

**目的：** 更新所有有效实物合同的 **物流(Movement)** 定价和数量信息。物流记录对应商品的发运/交割。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 查询 `PhysicalDeals`（**实物合同表**）：`inactiveFlag=false`, `legalEntityId=当前业务机构`, `status=2`
3. 过滤：排除无长期合同号且非 Spot（**现货**）类型的合同
4. 提取去重的 contractNumber 列表
5. 调用 `_movementPriceService.updateByDailySettlement(contractNumbers, curveDate)` — 更新**物流定价**
6. 调用 `_movementQuantityService.updateByDailySettlement(contractNumbers, curveDate)` — 更新**物流数量**
7. 调用 `_movementQuantityService.updateMissingPriceByDailySettlement(curveDate)` — 回填缺失价格

---

#### 步骤 5: UpdatePositionMonitorEOD — 生成持仓监控历史

**目的：** 生成当日**持仓监控(Position Monitor)** 的历史快照数据，用于跟踪商品头寸变化。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 调用 `positionMonitorHistoryService.generateDailySettlementHistoricalData(curveDate.toString())`

---

#### 步骤 6: UpdateInventoryReportEOD — 更新库存报表

**目的：** 从 SAP 系统拉取合金、半成品、产成品等商品的库存数据并更新。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 调用 `_sapMetalCompositionIncrementalService.inputInventoryBySap(curveDate, curveDate, null, false)` — 增量同步 SAP 金属成分库存

---

#### 步骤 7: LMEScorpCheckEOD — LME 升贴水价格校验

**目的：** 校验 LME（伦敦金属交易所）的金属价汇率和 **升贴水(Scorporo)** 价格。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 记录日志："金属价汇率更新已完成"、"scorporoPrice更新已完成"

---

#### 步骤 8: UpdateSecondSessionEOD — 创建交易时段 Session 2

**目的：** 日结完成后创建第二个**交易时段(Session)**，切换交易时段。一个交易日内可包含多个交易时段（Session 1 为开盘时段，Session 2 为日结后时段）。

**执行逻辑：**
1. 从 Redis 加载上下文
2. **停用已有 Session 2+：**
   - `UPDATE CurvedateSession SET inactiveFlag=true WHERE session >= 2 AND date=nextDate`
3. **标记 Session 1 为非最新：**
   - `UPDATE CurvedateSession SET latest=-1 WHERE session=1 AND date=nextDate`
4. **创建新 Session 2：**
   - `INSERT CurvedateSession`：`session=2`, `sessionType="S"`, `latest=1`, `status=2`, `createdBy="dailySettlement"`
5. 复制**远期价格**：`_forwardPriceService.copyComplicatePrice(nextDate, nextDate, 1, 2)` — Session 1 → Session 2

---

#### 步骤 9: updateCurveDate — 更新系统估值日期

**目的：** 推进系统**估值日期(CurveDate)** 到下一个交易日（需所有业务机构都完成 Session 2 后才执行）。

**执行逻辑：**
1. 设置业务机构级 Redis 缓存：`CurveDate:{业务机构ID}` = `nextDate`
2. 查询所有启用且活跃的业务机构（`SysCompany` 表）
3. 查询已完成 Session 2 且 date > curveDate 的所有业务机构
4. **校验：** 若未全部完成，记录错误并返回（不推进日期）
5. 调用 `_riskUtil.getPreAndNextWorkingDate(curveDate, null)` 获取下一工作日
6. 更新 `Curvedate`（**估值日期表**）：`date=下一工作日`, `prevDate=当前curveDate`
7. 设置 Redis：`CurveDate{当前日期}` = 下一工作日

---

#### 步骤 10: FixationUnlockEOD — 定价解锁（通知 CRM/SAP）

**目的：** 日结完成后对外部系统发送 **定价解锁(Fixation Unlock)** 通知，恢复交易操作，切换到 Session 2。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 查询 `SysCompany`（**业务机构表**）获取公司代码
3. **推送 CRM 解锁通知：** `sessionStatus="1"`, `eodStatus="1"`, `session="2"`, `curveDate=nextDate`
4. **推送 SAP 解锁通知：** 同上参数

---

#### 步骤 11: FinishProcessEOD — 完成并触发下一业务机构

**目的：** 标记当前业务机构的日结为完成，并重新触发 Quartz Job 处理下一个业务机构。

**执行逻辑：**
1. 从 Redis 加载上下文
2. 记录日志："日结操作已完成"
3. 设置 Redis：
   - `EOD:Status` = `TEMP_COMPLETE` (值=3，表示单个业务机构完成但还有待处理机构)
   - `EOD:Finished:{curveDate}-{业务机构ID}` = 1
   - 删除 `EOD:LegalEntityId`
4. **重新触发 Quartz Job：**
   - 从 Redis 读取 `EOD:JobId`
   - 加载 `QuartzJob` 配置
   - 构建新参数（清除 legalEntityId）
   - 调用 `_quartzJobService.execution(quartzJob)` 重新执行

---

## 七、多业务机构处理流程

```
┌──────────────────────────────────────────────────────────┐
│  第一次执行 execute()                                      │
│  ├─ legalEntityIds = ["ALL"] 或 [机构A, 机构B, 机构C]       │
│  ├─ 全部业务机构 ID 写入 Redis Set "EOD:LegalEntityIds"     │
│  ├─ 弹出 机构A → 启动 Activiti 工作流                       │
│  └─ 工作流执行步骤 1~11                                    │
│      └─ FinishProcessEOD: 标记 机构A 完成，重新触发 Job       │
├──────────────────────────────────────────────────────────┤
│  第二次执行 execute()（由 FinishProcessEOD 触发）            │
│  ├─ 从 Redis Set 弹出 机构B                                 │
│  ├─ 检查 EOD:Finished → 机构A 已完成，跳过                   │
│  ├─ 启动 Activiti 工作流处理 机构B                           │
│  └─ FinishProcessEOD: 标记 机构B 完成，重新触发 Job           │
├──────────────────────────────────────────────────────────┤
│  第三次执行 execute()                                      │
│  ├─ 从 Redis Set 弹出 机构C → 处理 → 完成                   │
│  └─ FinishProcessEOD: 重新触发 Job                         │
├──────────────────────────────────────────────────────────┤
│  第四次执行 execute()                                      │
│  ├─ Redis Set 为空                                        │
│  └─ 设置 EOD:Status = SUCCEED (值=2)，全部业务机构日结完成    │
└──────────────────────────────────────────────────────────┘
```

---

## 八、Redis Key 完整清单

### 8.1 状态与上下文

| Key | 类型 | 说明 |
|-----|------|------|
| `EOD:Status` | String | 日结状态 (0=空闲, 1=运行中, 2=全部完成, 3=单机构完成, -1=失败) |
| `EOD:SystemContext` | String | JSON 序列化的系统上下文 |
| `EOD:LegalEntityIds` | Set | 待处理的**业务机构** ID 集合 |
| `EOD:LegalEntityId` | String | 当前正在处理的**业务机构** ID |
| `EOD:Finished:{date}-{id}` | String | 某业务机构某日期的完成标记 |
| `EOD:CurveDate` | String | 当前**估值日期** |
| `EOD:PreDate` | String | 前一交易日 |
| `EOD:NextDate` | String | 下一交易日 |
| `EOD:UserId` | String | 触发用户 ID |
| `EOD:UserName` | String | 触发用户名 |
| `EOD:JobId` | String | Quartz Job ID |
| `EOD:Key` | String | Activiti 流程 Key |
| `CurveDate:{业务机构ID}` | String | 业务机构级估值日期缓存 |

### 8.2 控制标志

| Key | 默认值 | 说明 |
|-----|--------|------|
| `EOD:control:ComputeBrassScorporo` | `"0"` | Brass **升贴水**价格计算开关 |
| `EOD:control:cashflow` | `"0"` | 合同**现金流**更新开关 |
| `EOD:control:movement` | `"0"` | **物流**更新开关 |
| `EOD:control:PositionMonitor` | `"0"` | **持仓监控**开关 |
| `EOD:control:metalBullitino` | `"0"` | **金属锭**开关 |
| `EOD:control:lock` | `"0"` | CRM/SAP **定价锁定**开关 |
| `EOD:control:inventoryReport` | `"0"` | **库存报表**开关 |
| `EOD:control:LMEScorpCheck` | `"0"` | LME **升贴水**校验开关 |
| `EOD:control:updateCurveCate` | `"0"` | **估值日期**更新开关 |

---

## 九、日结状态枚举 (EODStatusEnum)

| 枚举值 | 数值 | 说明 |
|--------|------|------|
| `IDLE` | 0 | 空闲 |
| `RUNNING` | 1 | 日结运行中 |
| `SUCCEED` | 2 | 全部业务机构日结完成 |
| `TEMP_COMPLETE` | 3 | 单个业务机构完成（还有待处理机构） |
| `FAILED` | -1 | 日结失败 |

---

## 十、错误处理机制

### 10.1 execute() 层

```java
try {
    ProcessInstance pi = runtimeService.startProcessInstanceById(pd.getId(), "001", variables);
    taskProcessingUtil.updateTaskStatus(processingKey, TaskProcessingStatus.Success);
} catch (Exception exp) {
    taskProcessingUtil.updateTaskStatus(processingKey, TaskProcessingStatus.Error);
    // 记录错误日志 (ENGINE_ERROR 级别)
    taskProcessingUtil.addTaskProcessingInfoLogs(logsModel);
    throw exp;  // 向上抛出
}
```

### 10.2 BaseActivityDelegate 层

```
process() 抛异常 →
  ├─ 记录 TaskProcessingInfoLogsModel
  │   ├─ processingTaskName = 当前 Delegate 类名
  │   ├─ message = 异常信息 + Context JSON
  │   ├─ messageLevel = ENGINE_ERROR (2)
  │   └─ 完整异常堆栈
  ├─ 更新任务状态为 Error
  ├─ 调用 pushErrorMessage() 发送通知
  └─ 重新抛出异常终止工作流
```

### 10.3 EODService 业务层

- **按实体容错：** `UpdateContractHMEEOD` 等方法对每个 physicalDealId（实物交易）独立 try-catch，单个失败不影响其他
- **控制标志前置检查：** 所有方法首先检查控制标志，未启用则直接返回
- **Redis 上下文加载容错：** `initEodContext()` 对每个 Redis Key 读取独立 try-catch

---

## 十一、关键依赖类文件索引

| 类名 | 路径 | 职责 |
|------|------|------|
| `ExecuteHMEFlowTask` | `bcadmin-system/.../quartz/task/` | 日结入口 Quartz 任务 |
| `HMEProcessDefinitionParameter` | 同上（包级类） | 参数模型 |
| `EODStatusEnum` | `bcadmin-system/.../business/common/` | 日结状态枚举 |
| `ExecutionJob` | `bcadmin-system/.../quartz/utils/` | Quartz Job 执行器 |
| `QuartzRunnable` | `bcadmin-system/.../quartz/utils/` | 反射调用器 |
| `QuartzManage` | `bcadmin-system/.../quartz/utils/` | Quartz 调度管理 |
| `QuartzJob` | `bcadmin-system/.../quartz/domain/` | 任务配置实体 |
| `QuartzJobService` | `bcadmin-system/.../quartz/service/` | 任务服务接口 |
| `BaseActivityDelegate` | `bcadmin-system/.../activiti/` | Activiti 委托基类 |
| `BaseEODDelegate` | `bcadmin-system/.../eod/` | 日结委托基类 |
| `BaseActivityContext` | `bcadmin-system/.../eod/` | 工作流上下文 DTO |
| `EODService` | `bcadmin-system/.../eod/` | 日结业务接口 |
| `EODServiceImp` | `bcadmin-system/.../eod/` | 日结业务实现 |
| `EODUtils` | `bcadmin-system/.../eod/utils/` | 日结工具类（场景表管理） |
| `HME*EODDelegate` | `bcadmin-system/.../eod/delegate/` | 各步骤委托实现 (12个) |
| `TaskProcessingUtil` | `bcadmin-common/.../taskProcessing/` | 任务跟踪工具 |
| `RedisUtils` | `bcadmin-common/.../utils/` | Redis 操作工具 |
| `CurvedateSession` | `bcadmin-db/.../domain/` | **交易时段**实体 |
| `SysCompany` | `bcadmin-db/.../domain/` | **业务机构**（公司）实体 |
| `TaskProcessingStatus` | `bcadmin-common/.../enums/` | 任务状态常量 |
| `EngineCode` | `bcadmin-common/.../enums/Risk/` | 日志级别常量 |

---

## 十二、外部系统集成

| 外部系统 | 集成方式 | 触发步骤 | 说明 |
|---------|---------|---------|------|
| **CRM** | `_crmDockingService.pushEodAndSession()` | 定价锁定 / 定价解锁 | 推送日结状态和**交易时段**信息，控制**定价(Fixation)** 冻结与恢复 |
| **SAP** | `sapDockingService.pushEodAndSessionToSap()` | 定价锁定 / 定价解锁 | 推送**交易时段**状态到 SAP |
| **SAP (库存)** | `_sapMetalCompositionIncrementalService.inputInventoryBySap()` | 库存报表 | 从 SAP 拉取合金/半成品/产成品库存数据 |
| **Activiti** | `runtimeService` / `repositoryService` | execute() | 工作流引擎 |

---

## 十三、数据流向图

```
                    ┌──────────────┐
                    │  Quartz 触发  │
                    └──────┬───────┘
                           │ args (JSON)
                           ▼
                    ┌──────────────┐
                    │   Redis      │ ◄── 写入日结上下文、控制标志、业务机构列表
                    └──────┬───────┘
                           │ 读取参数
                           ▼
                    ┌──────────────┐
                    │  Activiti    │ ◄── 启动流程实例，传入 variables
                    │  工作流引擎   │
                    └──────┬───────┘
                           │ 依次执行 ServiceTask
                           ▼
              ┌────────────────────────┐
              │   BaseEODDelegate      │
              │   ├─ 从 Redis 读上下文  │
              │   ├─ 调用 EODService   │
              │   └─ 写回 Context      │
              └────────────┬───────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ 数据库    │ │  Redis   │ │ 外部系统  │
        │ (Mapper) │ │ (缓存)   │ │ CRM/SAP  │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 十四、CTRM 业务术语速查表

| 术语 | 英文/代码 | 含义 |
|------|----------|------|
| 业务机构 | Legal Entity / `SysCompany` | 系统中的公司/机构，对应 `legalEntityId` |
| 日结 | EOD (End of Day) | 每日交易结束后的结算处理流程 |
| 估值日期 | CurveDate | 远期曲线的估值基准日期 |
| 交易时段 | Session / `CurvedateSession` | 一个交易日内的交易时段划分 |
| 实物合同 | PhysicalDeal | 大宗商品的实物交易记录 |
| 远期合约 | ForwardContract | 远期商品合约 |
| 远期价格 | ForwardPrice | 远期合约的市场价格 |
| 远期曲线 | ForwardCurve | 远期价格曲线 |
| 升贴水 | Scorporo | 金属交易中的升贴水价格调整 |
| 定价锁定 | Fixation Lock | 将浮动价锁定为固定价，日结时冻结交易 |
| 定价解锁 | Fixation Unlock | 解除定价锁定，恢复交易 |
| 物流 | Movement | 商品的发运/交割记录 |
| 现金流 | Cashflow | 合同/交易的现金流计算 |
| 持仓监控 | PositionMonitor | 监控商品持仓头寸 |
| 金属锭 | MetalBullitino | 金属实物形态（合金/半成品/产成品） |
| 现货 | Spot | 即期交易，区别于远期合约 |
| 库存报表 | InventoryReport | 商品库存报告（从 SAP 同步） |
| 银行授信 | BankCredit | 银行信用额度管理 |
| 衍生品 | Derivation | 金融衍生品交易 |
| 航次租船 | Voyage | 商品的航次租船运输 |

---

## 十五、总结

> [!success] 架构设计特点
> `ExecuteHMEFlowTask.execute()` 是 HME CTRM 系统日结流程的核心入口，整体架构设计特点：
>
> | 特点 | 说明 |
> | :---: | :--- |
> | **Quartz + Activiti 双层调度** | Quartz 负责定时触发和多业务机构循环，Activiti 负责编排具体业务步骤 |
> | **Redis 作为状态中枢** | 所有日结状态、控制标志、上下文参数都通过 Redis 传递和持久化 |
> | **多业务机构串行处理** | 通过 Redis Set + FinishProcessEOD 重新触发 Job 实现逐个业务机构处理 |
> | **控制标志灵活开关** | 每个业务步骤都有独立的控制标志，可按需启用/禁用 |
> | **模板方法模式** | BaseActivityDelegate → BaseEODDelegate → 具体 Delegate，统一执行模板和错误处理 |
> | **外部系统集成** | 通过 CRM/SAP 接口实现定价锁定/解锁，保证日结期间数据一致性 |
