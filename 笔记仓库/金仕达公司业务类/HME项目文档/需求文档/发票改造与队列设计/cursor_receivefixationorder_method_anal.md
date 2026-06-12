

---

 create table ic_invoice_generate_task(    id            bigint auto_increment        primary key,    business_id   bigint  not null comment '业务ID,入库登记ID,等',    business_numbers varchar(100) DEFAULT NULL COMMENT '业务单号 (冗余字段，方便查询)',    request_params   text null comment '原始请求参数 (JSON)',    action_type  varchar(100) not null comment '发票类型,冲销发票/正向发票',    invoice_type  varchar(100) not null comment '发票种类,采购发票/销售发票/Credit/Debit',    source_type      varchar(500) not null comment '任务来源,crm_接收点价单/crm_接收入库登记',    status      varchar(50) not null comment 'PENDING：待处理;PROCESSING：处理中;SUCCESS：成功;FAILED：失败;',    sap_push_status      varchar(50)  null comment 'SUCCESS：成功;FAILED：失败;init:未推送',    error_message   text  null comment '最近一次失败原因摘要',    start_time datetime DEFAULT NULL COMMENT '开始执行时间',    end_time datetime DEFAULT NULL COMMENT '结束时间',    version int(11) NOT NULL DEFAULT 0 COMMENT '版本号 (乐观锁)',    created_by    varchar(255) not null comment '创建者',    created_time  datetime     not null comment '创建时间',    inactive_flag bit          not null comment '逻辑删除标识(0:未删除、1:已删除)',    KEY idx_business_id (business_id),    KEY idx_status (status)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 comment 'IC发票自动生成队列表';​​create table ic_invoice_generate_task_result(    id            bigint auto_increment        primary key,    ic_invoice_generate_task_id  bigint not null comment 'IC发票自动生成队列表id',    business_id    bigint not null comment '业务ID,例如入库登记ID',    relate_invoice_id     bigint not null comment '关联生成的发票',    relate_invoice_document_id     bigint not null comment '关联生成的发票明细',    created_by    varchar(255) not null comment '创建者',    created_time  datetime     not null comment '创建时间',    KEY idx_ic_invoice_generate_task_id (ic_invoice_generate_task_id),    KEY idx_business_id (business_id),    KEY idx_invoice_document_id (relate_invoice_document_id),    KEY idx_invoice_id (relate_invoice_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 comment 'IC发票自动生成队列关联结果表';sql

仔细分析这个方法nestFixationGenerPayInvoice,详细了解每一步调用,和调用他的地方,现在当有并发出现的时候,会出现一种情况,发票生成重复,现在希望吧生成发票这个功能解耦出来 ,数据库里设计一张表,当个地方进行调用的时候,先存进表里,然后定时任务一个一个再进行实际执行,给出我方案,各种细节的设计

---

**Cursor**

先把你关心的这块理一遍：**现在的 `nestFixationGenerPayInvoice` 是“同步直接调生成发票”的方式**，在并发场景下容易出现同一批入库登记（RegisterIds）被多次传入，从而触发多次 `genInvoiceByCrmPricing` 调用，虽然方法内部有一定去重校验，但在高并发+事务隔离下仍可能产生重复发票。你希望的是：**把“生成发票”变成一个异步任务队列**，入口只负责“写任务表”，由定时任务顺序消费，这个方向是对的。

下面分三块说：  
1）现有方法链路和调用点分析  
2）为什么在并发下仍然可能重复生成发票  
3）设计一个“发票生成任务表 + 定时任务消费”的完整解耦方案（含表结构、状态流转、并发控制、幂等设计等）

---

### 1. `nestFixationGenerPayInvoice` 方法执行逻辑与调用关系

#### 1.1 方法本身逻辑

方法位置（你可以在 IDE 里跳转）：

```3813:3838:bcadmin-system/src/main/java/com/resrun/modules/business/service/impl/PricingServiceImpl.java
    @Override
    public void nestFixationGenerPayInvoice(List<Long> RegisterIds) {
        if (CollectionUtils.isEmpty(RegisterIds)) {
            return;
        }
        LambdaQueryWrapper<Documents> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(Documents::getInactiveFlag, false);
        queryWrapper.eq(Documents::getActionId, 42L);
        queryWrapper.eq(Documents::getOffsetFlag, "n");
        queryWrapper.in(Documents::getIntercompany, Arrays.asList("BTO", "BTS"));

        queryWrapper.in(Documents::getId, RegisterIds);
        List<Documents> documents = documentsMapper.selectList(queryWrapper);
        if (org.springframework.util.CollectionUtils.isEmpty(documents))
            return;

        CrmFixationParams paras = new CrmFixationParams();
        paras.setDocs(documents);
        /* 生成 采购发票 */
        try {
            log.info("点价接口开始生成采购发票 ----  ");
            List<Invoice> invoices = invoiceService.genInvoiceByCrmPricing(paras, null);
        } catch (BizException e) {
            log.error("采购发票生成失败", e);
        }
    }
```

**逐步拆解：**

- **Step 1：入参判空**
  - `RegisterIds` 为空直接返回。

- **Step 2：查询入库登记 `Documents`**
  - 条件：
    - `inactiveFlag = false`
    - `actionId = 42L`
    - `offsetFlag = "n"`（未冲销）
    - `intercompany in ("BTO", "BTS")`
    - `id in RegisterIds`
  - 这一步得到的是一批“满足条件的入库登记单”。

- **Step 3：判空**
  - 如果根据上述条件查不到 `documents`，直接返回。

- **Step 4：组装参数 `CrmFixationParams`**
  - `paras.setDocs(documents);`
  - 这里只填充了 `docs`，`docItems/pdLines/pds` 在 `InvoiceServiceImpl.genInvoiceByCrmPricing` 里会进一步补全。

- **Step 5：调用发票生成服务**
  - `invoiceService.genInvoiceByCrmPricing(paras, null);`
  - `postDate` 传 `null`，意思是过账日期使用默认逻辑（通常取入库登记的过账日期）。

#### 1.2 调用方（谁在调用它）

主要调用点：

```110:130:bcadmin-system/src/main/java/com/resrun/modules/business/rest/DockingCrmController.java
    public CrmFixationOrderRes receiveFixationOrder(@RequestBody CrmFixationOrderReq request) {
        ...
        String key = ICPRICLOCK + crmIdKey;
        contractStatusLockMap.computeIfAbsent(key, k -> new Object());
        synchronized (contractStatusLockMap.get(key)) {
            try {
                if (COLUMN2_VALUE_OFFSET.equalsIgnoreCase(crmFixationOrderReqItem.getColumn2())) {
                    // 冲销逻辑
                    return pricingService.getRevertFixationOrderFromCrm(request);
                }
                CrmFixationOrderRes fixationOrderFromCrm = pricingService.getFixationOrderFromCrm(request);// 新建
                pricingService.nestFixationGenerPayInvoice(fixationOrderFromCrm.getRegisterIdList());  // 生成发票（当前是同步）
                return fixationOrderFromCrm;
            } catch (Exception e) {
                ...
            }
        }
    }
```

调用链概览：

1. CRM 调用 `POST /api/dockingCrm/receiveFixationOrder`（类名略，接口路径按你实际）。
2. `DockingCrmController.receiveFixationOrder` 解析请求，做一个以 `crmId` 为粒度的 `synchronized` 锁。
3. 如果是新建（非冲销）：
   - 调 `pricingService.getFixationOrderFromCrm(request)`：根据 CRM 点价生成本系统点价及相关数据，返回 `CrmFixationOrderRes`，其中包含 `registerIdList`（入库登记 ID 集合）。
   - 立即调用 `pricingService.nestFixationGenerPayInvoice(registerIdList)`：**同步生成采购发票**。
4. 返回给 CRM。

还有其他地方间接走 `genInvoiceByCrmPricing` 的，如 `DockingSapController`、`InvoiceAsyncTask`、`SystemOperationsController`，但你这次问的是 **nestFixationGenerPayInvoice 这条链路**。

---

### 2. 并发下重复发票的原因分析（在现有设计下）

结合上面的链路，以及 `genInvoiceByCrmPricing` 内部逻辑，可以得出几个关键点：

1. **`receiveFixationOrder` 的锁粒度是 `crmId`，不是 “入库登记 ID” 或 “合同+行号”**
   - 如果**不同的 CRM 请求**（不同 `crmId`）逻辑上指向了**相同的一批入库登记（RegisterIds）**，这些请求之间是**没有互斥的**。
   - 这种情况在补单、重发等“上游重复推送”的场景里比较常见。

2. **`genInvoiceByCrmPricing` 的幂等性依赖于“先查已有发票，再决定是否生成”**
   - `InvoiceServiceImpl.genInvoiceByCrmPricing` 中做了不少“避免重复生成”的逻辑（简化一下）：
     - 通过 `myFinanceMapper.selectInvoiceByCriteria` 判断当前入库是否已有发票；
     - 通过 `invoiceDocuments` 和 `Invoice`（gzstatus != 3）过滤出已经被有效发票引用的 `DocumentItems`；
     - 只对 `jsQuantity>0` 的明细生成发票。
   - 但在 **高并发 + 事务隔离（`REQUIRES_NEW`）** 下，会存在这样的竞态：
     - 线程 A 和线程 B 几乎同时进入 `genInvoiceByCrmPricing`；
     - 两者在各自事务里查询 `InvoiceDocuments` 时，看不到对方尚未提交的那批数据；
     - 都认为“还没开这个发票”，于是各自生成了一组发票并提交——这时就产生了重复。

3. **`nestFixationGenerPayInvoice` 是同步串接，发票生成耗时 + CRM 同步等待，放大并发问题**
   - 发票生成逻辑不轻（查询 + 汇率 + 发票行组装 + 插表），在接口同步里做，一旦 CRM 有高峰并发：
     - 一方面请求慢；
     - 另一方面，发票生成这段复杂逻辑在多线程下同时跑，更容易制造上述读/写竞态。

综上：**即便 `genInvoiceByCrmPricing` 做了不少防重复校验，在“多线程近同时进入 + 校验也在事务内”的场景下，仍然可能导致重复生成。**  
你的目标是把这块从“高并发入口”里抽离出来，改成“统一队列 + 单点/小并发消费者”，这是从架构层面减轻竞态的办法。

---

### 3. 解耦设计方案：任务表 + 定时任务 + 幂等与并发控制

下面给一个比较完整、落得下地的方案，按你现在的技术栈（Spring + MyBatis/MyBatis-Plus + Quartz/定时任务）来设计。

#### 3.1 新增一张“发票生成任务表”

可以命名为：`invoice_generate_task`（或按你们命名规范来）。

**建议字段（核心字段 + 建议约束）：**

- **主键**
  - `id` (bigint, PK)

- **业务维度 / 去重维度**
  - `register_id` (bigint)  
    - 对应 `Documents.id`，一条任务通常可以针对 1 个入库登记；如果一次任务要处理多个，可以设计 `task_id + 子表`，但按你现状，每个 `RegisterId` 一个任务更清晰。
  - `invoice_type` (varchar)  
    - 例如固定 `"DomesticInvoiceMaterial"`，也为后续扩展不同类型预留空间。
  - **唯一约束**：`unique(register_id, invoice_type)`  
    - 防止同一个入库登记+发票类型被重复入队。

- **来源信息（便于追踪、排障）**
  - `source_type` (varchar)：如 `"CRM_FIXATION"`, `"SAP_RESEND"`, `"OPS_MANUAL"` 等。
  - `source_key` (varchar)：例如 `crmId`、外部系统单号。
  - `request_payload` (text/json)：可选，用于存储原始请求关键参数（比如 registerIdList、contractNo 等）。

- **执行控制字段**
  - `status` (varchar)：枚举，比如：
    - `PENDING`：待处理
    - `PROCESSING`：处理中
    - `SUCCESS`：成功
    - `FAILED`：失败（可重试）
    - `PERMANENT_FAILED`：多次失败后不再重试
  - `retry_count` (int)：当前重试次数。
  - `next_run_time` (datetime)：下次允许执行时间，用于做退避（比如失败后 5 分钟再试）。
  - `last_error` (varchar/text)：最近一次失败原因摘要（堆栈截断即可）。
  - `last_run_time` (datetime)：最后一次尝试执行时间。
  - `created_time` / `updated_time` / `created_by` 等审计字段。

> 如果你觉得“一条任务就是一组 RegisterIds”更合适，也可以：  
> - 表里用 `register_ids` 存 JSON 数组；  
> - 唯一约束改为业务自定义，比如 `UNIQUE(task_key)`，`task_key` 可由 `crmId` 等组合生成。  
> 下文用“每个 RegisterId 一条任务”的思路讲解，更细粒度，也更自然和幂等。

#### 3.2 入口改造思路：从“直接生成发票”变为“写任务表”

**现状：**

```java
CrmFixationOrderRes fixationOrderFromCrm = pricingService.getFixationOrderFromCrm(request);
pricingService.nestFixationGenerPayInvoice(fixationOrderFromCrm.getRegisterIdList());
```

**目标：**

- 把这段变成：**只负责把 `registerIdList` 写入 `invoice_generate_task`，不直接调发票生成**。
- 对 CRM 的响应仍然是“点价创建成功”，但要明确发票是异步生成。

**伪代码设计（供你后续改造时参考）**：

```java
List<Long> registerIds = fixationOrderFromCrm.getRegisterIdList();
for (Long registerId : registerIds) {
    try {
        invoiceGenerateTaskService.enqueueCrmPricingTask(registerId, "CRM_FIXATION", request.getCrmId(), currentUser);
    } catch (DuplicateKeyException e) {
        // 已经存在同样的任务了，说明已排队/执行过，忽略即可（幂等）
    }
}
```

`invoiceGenerateTaskService.enqueueCrmPricingTask` 内部逻辑建议：

- 插入一条 `invoice_generate_task` 记录：
  - `register_id = registerId`
  - `invoice_type = "DomesticInvoiceMaterial"`
  - `status = PENDING`
  - `retry_count = 0`
  - `next_run_time = now`
  - `source_type = "CRM_FIXATION"`
  - `source_key = crmId`
- 利用前面提到的 `(register_id, invoice_type)` 唯一约束，天然防止同一入库登记被多次入队。

> 这里按你的要求，我**只给方案，不改代码**；你后面可以根据这个思路落代码。

#### 3.3 定时任务：顺序（或限流）消费任务表

新建一个类似 `InvoiceGenerateTaskJob` 的定时任务/Quartz Job：

**核心流程：**

1. **拉取一批待处理任务**
   - SQL 示例（伪代码）：
     - `select * from invoice_generate_task where status = 'PENDING' and next_run_time <= now() order by created_time asc limit 100`
     - 或者再加一层 `FOR UPDATE SKIP LOCKED`（如果底层支持），保证多实例情况下不会抢同一条记录。
   - 对于每条记录，在代码里：
     - 使用乐观/悲观方式把状态从 `PENDING` 更新为 `PROCESSING`：
       - `update invoice_generate_task set status='PROCESSING', last_run_time=now() where id=? and status='PENDING'`
       - 返回影响行数==1 说明抢到了执行权；否则说明别的实例已经抢走了，当前实例跳过。

2. **执行单条任务（建议每条任务一个新事务）**
   - 在 `PROCESSING` 状态下，执行类似当前 `nestFixationGenerPayInvoice` 中的逻辑：
     - 根据 `register_id` 去 `Documents` 查对应入库登记（同现有 where 条件）。
     - 构造 `CrmFixationParams`，设置 `docs`。
     - 调用 `invoiceService.genInvoiceByCrmPricing(paras, null)`。
   - 完全可以把 `nestFixationGenerPayInvoice` 的“查询+组装+调用”逻辑搬到一个私有方法，让任务消费和原来的同步入口共用，减少重复。

3. **根据执行结果更新任务状态**
   - **成功：**
     - `status = SUCCESS`
     - `retry_count` 不变（或设置为最终值）
     - 可选：记录生成的 `invoice_ids`，写到另一个关联表 `invoice_generate_task_result` 里。
   - **失败可重试：**
     - 增加 `retry_count`。
     - 若 `retry_count < maxRetry`（比如 3 或 5），则：
       - `status = FAILED`
       - `next_run_time = now() + retryInterval * retry_count`（简单指数退避）
       - `last_error = 截断后的错误信息`
     - 若达到最大重试次数：
       - `status = PERMANENT_FAILED`
       - 报警/人工介入（邮件、钉钉等）。

4. **并发与幂等控制**
   - 通过：
     - **任务表唯一约束** 防止“入口层面”的重复排队；
     - **任务消费端单条任务 + 事务 + 现有 `genInvoiceByCrmPricing` 中的发票存在性校验**  
       再加上一层“串行或小并发、非高并发入口”的架构，将**生成重复发票的概率极大降低**，即便极端情况下仍有竞态，数据库层面可以再加业务唯一索引（比如某些业务键）兜底。

#### 3.4 业务幂等与数据约束建议

为确保即便入口或任务消费出现异常，也不会产生重复发票，可以再增加一些“硬约束”：

- **在发票明细关系表 `InvoiceDocuments` 上增加业务唯一约束**（如果业务允许）：
  - 例如：`UNIQUE(document_items_id, invoice_type, gzstatus not reversed)` 之类的组合（这需要结合你们现有表结构仔细设计）。
  - 如果插入时违反唯一约束，说明这条明细已经被某个有效发票引用，可以捕获异常视为“已成功/已存在”，从逻辑上将本次任务标记为成功而不是失败。

- **任务表与发票之间建立关联表（可选）**
  - 如 `invoice_generate_task_result(task_id, invoice_id, created_time)`。
  - 方便后续排查：“这条任务到底生成了哪些发票”。

#### 3.5 回到现有接口行为的影响

- **对 CRM 调用方**：
  - 现在：CRM 发起点价 → 接口里“点价 + 同步生成发票” → 成功返回时，发票基本已经在系统中。
  - 未来：CRM 发起点价 → 接口里“点价 + 写任务表” → 立即返回成功（或带上“发票生成中”的状态），发票由后台任务稍后生成。
- 如果 CRM 端对“发票是否已生成”有依赖，需要：
  - 要么增加一个“查询发票生成状态”的接口（通过 `crmId` 或 `registerId` 查询）；
  - 要么通过你们现有对接给 SAP/CRM 的反向推送来通知发票生成结果。

---

### 4. 小结

- **当前问题本质**：发票生成逻辑在高并发入口中被多次触发，依赖“先查再生成”的逻辑去重，在事务并发下不完全可靠，导致偶发重复发票。
- **建议方案**：  
  - 新增 `invoice_generate_task` 任务表；  
  - 所有地方（包括 `nestFixationGenerPayInvoice` 的现有调用点）不再直接调 `genInvoiceByCrmPricing`，而是向任务表写入记录；  
  - 由单实例/限流的定时任务顺序消费任务，在任务消费端执行现有的 `genInvoiceByCrmPricing` 逻辑；  
  - 配合任务状态机（PENDING/PROCESSING/SUCCESS/FAILED/...）、唯一约束和可选的发票明细唯一索引，整体上做到既防重复，又易于监控和重试。

如果你愿意，下一步我可以帮你：  
- 把“任务表字段 + 索引方案”写成完整的建表 SQL；  
- 以及“enqueue 服务接口”和“定时任务消费伪代码”写成接近可直接贴进项目的 Java 代码草案，方便你后续自己落地实现。

---

<reproduction_steps>
1. 在测试库中按上述方案先设计并创建 `invoice_generate_task` 表以及必要的唯一约束（例如 `(register_id, invoice_type)` 唯一）。
2. 在测试环境中，将当前同步调用 `nestFixationGenerPayInvoice` 的逻辑改为“只写任务表、不直接生成发票”，并实现定时任务消费逻辑（单线程或受控并发）。
3. 使用同一组 `RegisterIds` 构造 5～10 个并发的 CRM 点价请求，确认请求返回时只是排队，不会立刻在发票表中出现多组重复数据。
4. 等定时任务运行完成后，检查发票相关表（`Invoice`、`InvoiceDocuments`）和任务表，确认：相同的 `registerId` 只生成了一套有效发票，失败任务有清晰的状态和错误信息。
5. Press Proceed/Mark as fixed when done.
</reproduction_steps>

