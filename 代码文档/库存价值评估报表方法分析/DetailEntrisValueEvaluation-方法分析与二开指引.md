# DetailEntrisValueEvaluation 方法分析与二开指引

## 1. 方法定位

- 方法：`EomStorageServiceImpl.listDetailEntrisValueEvaluation(DetailEntrisValueEvaluationQuery query)`
- 目标：生成“库存价值评估明细”报表数据（行级），并返回给前端/导出模块使用。
- 核心流程：**底稿查询** -> **补充冲销来源行** -> **计算估值与金额指标** -> **冲销行负号化** -> 返回。

---

## 2. 报表查询的是哪类数据

该方法查询的是**入库登记类单据明细（document action=42）在会计日之前的库存价值评估数据**，并按单据行维度输出估值、开票、点价关联、金属/附加价、待收 CD 金额等指标。

在 SQL 层（`EomStorageMapper.xml` -> `listDetailEntrisValueEvaluationFrame`）有以下硬条件：

- `doc.action_id = 42`（只取指定单据动作）
- `doc.sap_push_status = 2`（仅取已推 SAP 的单据）
- `doc.post_date <= accountingDate`（会计日截断）
- `di/doc/pdl/pd` 均要求未失效（`inactive_flag` / `inative_flag`）

因此这是一个**“截至会计日”的库存估值快照明细报表**。

---

## 3. 从哪里收集数据（数据来源地图）

## 3.1 底稿主查询（Frame）

来源 SQL：`EomStorageMapper.listDetailEntrisValueEvaluationFrame(query)`

主要来源表（按职责分组）：

- 单据主线：`systemdb.document_items di`、`systemdb.documents doc`
- 合同主线：`systemdb.physical_deal_line pdl`、`systemdb.physical_deals pd`、`systemdb_ext.physical_deal_line_ext pdl_ext`
- 组织与主数据：`admindb.sys_company`、`sys_business_segment`、`sys_department`、`counterparty`
- 基础档案：`product`（含父商品）、`unit`、`storage_facility`、`currency`
- 控制信息：`contract_execution_monitor`（合同关闭状态）

输出的是报表的“初始行”，包含：单据号、行号、合同号、商品、币种、数量、暂估价等原始字段。

## 3.2 二次补数来源（fillEvaluationInfo）

`fillEvaluationInfo(accountingDate, results)` 会再次从多个来源聚合：

- 定价明细：`movement_price`（`priced=1`，结算日 <= 会计日）
- 点价明细：`price_triggering`（`selectListForEom`）
- 点价关联：`price_triggering_warehouse_rela`（按点价 ID、单据行 ID 分组）
- 发票：`invoiceMapper.selectListForEom(documentItemIds, accountingDate)`（含普通票与 Added Value 的 CD 票）
- 商品财务属性：`product_financial_attributes`（识别 `Z001` 原材料逻辑）
- 商品行基础：`physical_deal_line`（解析计价参数）
- 工厂映射：`abutment_config` + `abutment_config_details`（`dockingMark=Factory`）
- 单位与汇率工具：`riskUnitConversionUtil`、`riskCurveUtil`、`riskUtil`

## 3.3 冲销数量来源

来源 SQL：`EomStorageMapper.selectDocItemOffsetQuantity(documentItemIdList, postDate)`：

- 取 `doc.offset_flag='Y'` 的冲销单据
- 按 `source_document_item_id` 聚合冲销数量
- 回填到被冲销原始行的 `offsetQuantity`

---

## 4. 组装逻辑（怎么拼成报表）

## 4.1 主流程

1. 会计日默认值处理：若未传 `accountingDate`，取 `riskUtil.getCurveDate()`
2. 分页：`size != -1` 时启用 `PageHelper`
3. 先查 frame 数据：`results`
4. 拆分两组：
   - `offsetResults`：冲销行（`offsetFlag=Y`）
   - `normalResults`：正常行 + 冲销来源行（通过 `sourceDocumentItemId` 再查一次补入）
5. 对 `normalResults` 执行 `fillEvaluationInfo` 全量计算
6. 计算并回填冲销数量（`selectDocItemOffsetQuantity`）
7. 对 `offsetResults` 做“镜像负号”处理（多数金额/数量取来源行负值）
8. 返回原始 `results`（其中冲销行在最后被改写）

## 4.2 fillEvaluationInfo 的核心口径

### A. 基础初始化

- 默认数量空值补零
- 初始开票口径：
  - `invoicedQuantity = 0`
  - `uninvoicedQuantity = quantity - offsetQuantity`
- 父商品字段兜底（为空则回退商品字段）

### B. 计价类型识别

从 `pricing_formula_id_parameters` 解析 `abbreviation`：

- `BasicFixedPrice`
- `BasicAveragePrice`
- `BasicTriggeredPrice`

这会决定后续 final price、关联量、待收 CD 的计算分支。

### C. 开票数量/开票金额

来自 `invoiceMap`（普通票）：

- 开票数量：`invoicedQuantity`
- 未开票数量：`deliveryInQuantity - offsetQuantity - invoicedQuantity`
- 开票金额字段：
  - `taxIncInvoiceAmount`（代码实际采用 `exclTaxAmount`）
  - `baseCurTaxIncInvoiceAmount`
- 若存在 final 票据，`invoiceStage = Final`

### D. 最终价（finalPrice）

- Fixed / Average：基于 `movement_price` 按数量加权平均
- Triggered：
  - 关联部分：按点价关联关系取已关联金额
  - 未关联部分：按点价剩余量与价格计算未关联均价
  - 再合成整行最终价
- 若无法取到有效定价，回退暂估价 `estimatedPrice`

### E. 记账金额（Accounting Total Value）

- 全开票或 Final：记账金额=开票金额
- 非全开票：
  - Fixed/Average：未开票量 * finalPrice + 已开票金额
  - Triggered：关联段与未关联段分别估值后 + 已开票金额

### F. 附加价/金属价拆分

- 财务属性 `Z001`：附加价=0，金属价=记账金额
- 其他：
  - 优先用 movement price / 点价关联计算附加价
  - 金属价=记账金额-附加价
  - 若未定价，使用合同日 SCo 价格估算金属价，再反推附加价
- 若有 Added Value CD 票据，再次重分配附加价与金属价

### G. 关联/未关联口径

- `relatedQuantity`、`unrelatedQuantity`
- `relatedAvgPrice`、`unrelatedAvgPrice`
- 点价下按关联关系/未关联余量分别计算

### H. 待收 Credit/Debit 金额

拆分为：

- `relatedReceivableCDAmount`
- `unrelatedReceivableCDAmount`
- 合计 `receivableCDAmount`

并同步计算本位币版本。

### I. 单位、币种、符号、精度

- 数量/价格统一做单位换算（含 KG 和父商品主计量单位）
- 冲销量处理为负号口径
- 最终统一精度：数量/金额/价格均四舍五入到 2 位

---

## 5. 报表维度（你可用于二开筛选/分组）

## 5.1 业务维度

- 单据维度：单据类型、单据号、单据行、过账日、货权转移日
- 合同维度：合同号、合同行、合同日期、合同关闭状态
- 组织维度：业务机构、业务部门、业务板块、公司编码
- 交易维度：交易对家、仓库、工厂
- 商品维度：商品/父商品、批次、单位
- 计价维度：计价类型（固定/均价/点价）、币种/本位币

## 5.2 指标维度

- 数量类：入库登记、冲销量、已入库、已开票、待开票、关联量、未关联量
- 价格类：暂估价、最终价、已关联均价、未关联均价
- 金额类：记账金额、附加价、金属价、开票金额、待收 CD（含本币）

---

## 6. 与冲销相关的关键处理

- 主查询已包含冲销单（`offset_flag`）
- 冲销单会尝试通过 `source_document_item_id` 找到来源行
- 来源行先参与完整估值计算
- 冲销行最后直接复制来源行指标后取负（用于展示“冲回”效果）
- `actionName` 会被追加 `" reverse"`

---

## 7. 二次开发重点风险（改 bug 优先看）

## 7.1 高风险逻辑点

1. **空集合 IN 风险**
   - `fillEvaluationInfo` 内 `movementPriceWrapper.in(... physicalDealLineIds)` 等语句，若集合为空可能在部分 ORM/SQL 配置下生成异常 SQL。

2. **除零风险**
   - Added Value CD 处理处：
     - `baseCurAddedValue = (added+cd)/added * baseCurAdded`
     - `baseCurMetalValue = (metal-cd)/metal * baseCurMetal`
   - 当 `added` 或 `metal` 为 0 时可能抛异常或出现 Infinity 风险。

3. **冲销行字段来源不一致**
   - 冲销镜像时 `deliveryInStockQuantity` 用的是 `deliveryInQuantity` 的负值，若两者口径未来分离会导致误差。

4. **单位换算与精度顺序耦合**
   - 先计算再换算再统一保留两位，可能导致汇总与明细对不上（典型财务口径争议点）。

5. **offsetQuantity 符号前后多次处理**
   - `fillEvaluationInfo` 已对 `offsetQuantity` 统一乘 `-1`，外层冲销逻辑又有补数，排查 bug 时需先确认“入参符号口径”。

## 7.2 建议的最小化改造策略

- 新增逻辑尽量放在 `fillEvaluationInfo` 末尾统一处理，避免破坏现有分支；
- 涉及金额公式修改时，先锁定计价类型分支（Fixed/Average/Triggered）再改；
- 对“除法”统一加保护：
  - 分母为 0 时返回 0 或回退到旧值；
- 对冲销单新增单元测试：
  - 有来源行 / 无来源行
  - 全开票 / 部分开票
  - Added Value CD 存在 / 不存在

---

## 8. 建议你下一步排 bug 的排查顺序

1. 先确定问题是“查询少数据”还是“公式算错”
2. 若少数据：优先看 `listDetailEntrisValueEvaluationFrame` 的 where 条件（尤其 `action_id=42`、`sap_push_status=2`、`post_date<=accountingDate`）
3. 若金额错：先看 `invoiceStage`、`pricingType`、`financialAttr(Z001)` 三个分支命中情况
4. 若冲销错：核对 `source_document_item_id` 是否能查到来源行
5. 若本币错：核对 `publicationId`、汇率日期（合同日 vs 会计日）和单位换算链路

---

## 9. 关键代码入口清单

- 服务入口：`EomStorageServiceImpl.listDetailEntrisValueEvaluation`
- 核心计算：`EomStorageServiceImpl.fillEvaluationInfo`
- 主查询 SQL：`EomStorageMapper.xml` -> `listDetailEntrisValueEvaluationFrame`
- 冲销数量 SQL：`EomStorageMapper.xml` -> `selectDocItemOffsetQuantity`
- DTO：
  - `DetailEntrisValueEvaluationQuery`
  - `DetailEntrisValueEvaluation`

