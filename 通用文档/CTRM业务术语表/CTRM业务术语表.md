---
type: 通用文档
---
# CTRM 大宗商品贸易系统 — 专有业务术语对照表

> **版本**: v1.0  
> **生成日期**: 2026-06-02  
> **用途**: 团队沟通对齐 & AI 语义识别基准文档  
> **说明**: 本文档从系统前端多语言文件（en.js / zh.js）中提取，按业务模块分类整理。

---

## 目录

1. [实货交易 / Physical Trading](#1)
2. [作价与定价管理 / Fixation & Pricing](#2)
3. [库存管理 / Inventory Management](#3)
4. [应收应付与资金管理 / AR/AP & Capital](#4)
5. [衍生品与风险管理 / Derivatives & Risk](#5)
6. [信用与授信管理 / Credit Management](#6)
7. [业务设置与主数据 / Business Settings & Master Data](#7)
8. [实验室与质检 / Lab & Quality](#8)
9. [流程与审批 / Workflow & Approval](#9)
10. [资金与银行 / Treasury & Banking](#10)
11. [系统对接 / System Integration](#11)
12. [系统管理 / System Administration](#12)

---

## 使用说明

### 术语结构

| 字段 | 说明 |
|------|------|
| **中文术语** | 系统界面上的中文表达 |
| **英文术语** | 系统界面上的英文表达 |
| **AI别名/口语表达** | 用户在日常沟通中可能使用的其他叫法，用于AI语义桥接 |
| **业务含义** | 在CTRM语境下的简要解释 |

### AI 使用指南

当用户用自然语言提问时，请参照本文档的"AI别名/口语表达"列进行语义映射。例如：

- 用户说"帮我查一下这个**业务机构**的信息" → 映射到系统的 **Business Entity（业务机构管理）**
- 用户说"这个**对手方**的授信额度是多少" → 映射到系统的 **Business Partner（客商）+ Credit Limit（授信额度）**
- 用户说"今天的**持仓**情况" → 映射到系统的 **Position Monitor（持仓统计表）**
- 用户说"这笔**入库**的定价" → 映射到系统的 **Good Receipt（入库登记）+ Fixation（点价）**

---

## 1. 实货交易 / Physical Trading

### 实货交易 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| SAP委外销售 | SAP Conversion Sales |  | |
| SAP常规销售 | SAP Full Price Sales |  | |
| 供应商寄售 | Vendor consignment | 寄售, Consignment, Vendor Consignment, VMI | |
| 全价采购 | Full price procurement | Full Price, 全价, 一口价采购, Fixed Price Purchase | |
| 关联采购需求 | Associated Procurement Demand |  | |
| 升贴水明细表 | Premium and Discount Detail | Premium/Discount, 溢价, 贴水, 升水, Premium | |
| 半成品/成品销售开票定价快照 | SF&FG Sales Engagement Snapshot |  | |
| 半成品/成品销售开票定价明细 | SF-FG Sales Engagement Details |  | |
| 卡车信息跟踪表 | Truck Information Tracking Table |  | |
| 原材料到货管理-库管 | Raw material management-warehouse |  | |
| 原材料到货管理-库管详情 | Raw material management-warehouse detail |  | |
| 原材料到货管理-收货 | Raw material management - new entry |  | |
| 原材料到货管理-质检 | Raw material management-quality inspection | Quality Inspection, 检验, 质量检测, 品检 | |
| 原材料到货计划 | Raw Material Arrivals Planning |  | |
| 原材料销售开票定价快照 | RM Sales Engagement Snapshot |  | |
| 原材料销售开票定价明细 | RM Sales Engagement RM Details |  | |
| 原材料销售开票定价表 | Sales Engagement-RM |  | |
| 发货定价 | Delivery Fixation Invoice Report |  | |
| 发货未开票 | Delivered Invoiced Report |  | |
| 合同执行进度表 | Contract execusion status report |  | |
| 合同明细表 | Contract split in detail |  | |
| 合同点价进度表 | Fixation Status Report | 定价, 作价, Fixation, Price Fixation, Pricing | |
| 合同转账登记 | Contract Transaction Registration |  | |
| 固定价现货合同周报 | Fixed Spot Purchase Orders |  | |
| 外仓货物转移 | Conversion(from external warehouse) | 外仓转移, External Warehouse Transfer, 三方库转移 | |
| 委托加工 | Conversion | 加工, Conversion, Subcontracting, 外协加工, 委外加工 | |
| 实货交易 | Physical Trading |  | |
| 收发货明细 | Shipping and Receiving Details |  | |
| 收发货明细-详情 | Shipping and Receiving Details-View |  | |
| 收货定价 | Receipt Fixation Invoice Report |  | |
| 收货明细表 | Detail Entries of Goods Receipt |  | |
| 收货未开票 | Received Invoiced Report |  | |
| 物流信息 | Logistics Information | 物流, Logistics, 运输信息, Shipping Info | |
| 现货合同周报 | Spot Purchase Orders |  | |
| 现货订单 | Spot Order | 现货, Spot, Spot Order, Spot Contract, 即期订单 | |
| 现货订单-采购 | Spot Order - Procurement | 现货, Spot, Spot Order, Spot Contract, 即期订单 | |
| 现货订单-销售 | Spot Order - Sales | 现货, Spot, Spot Order, Spot Contract, 即期订单 | |
| 索赔报告 | Claim Report | 索赔, Claim, Claim Report, 理赔 | |
| 补充协议 | Supplementary Agreement | 补充条款, 合同变更, Supplementary Agreement, Amendment | |
| 补充协议管理 | Supplementary Agreement Management | 补充条款, 合同变更, Supplementary Agreement, Amendment | |
| 采购 | Procurement | 进项发票, Purchase Invoice, 收票 | |
| 采购发票 | Purchase Invoice | 进项发票, Purchase Invoice, 收票 | |
| 采购发票明细表 | Detail Entries of Purchase Invoice | 进项发票, Purchase Invoice, 收票 | |
| 采购定价明细周报 | Purchase Fixation Detail |  | |
| 采购库存定价快照 | Purchase Engagement Snapshot |  | |
| 采购库存定价明细 | Purchase Engagement Details |  | |
| 采购库存定价表 | Purchase Engagement |  | |
| 采购开票未定价 | Purchase No Fixation Invoice Report |  | |
| 采购需求 | Procurement Demand |  | |
| 销售 | Sales | 销项发票, Sales Invoice, 开票 | |
| 销售发票 | Sales Invoice | 销项发票, Sales Invoice, 开票 | |
| 销售发票明细表 | Detail Entries of Sales Invoice | 销项发票, Sales Invoice, 开票 | |
| 销售开票未定价 | Sales No Fixation Invoice Report |  | |
| 长协合同 | Long-term Agreement | 长协, 年度合同, LTA, Long-term Agreement, 框架合同 | |
| 长协合同-采购 | Long-term Agreement - Procurement | 长协, 年度合同, LTA, Long-term Agreement, 框架合同 | |
| 长协合同-销售 | Long-term Agreement - Sales | 长协, 年度合同, LTA, Long-term Agreement, 框架合同 | |
| 长协订单 | LTA Order | 长协执行, LTA Order, 长协下单, 合同项下订单 | |
| 长协订单-采购 | LTA Order - Procurement | 长协执行, LTA Order, 长协下单, 合同项下订单 | |
| 长协订单-销售 | LTA Order - Sales | 长协执行, LTA Order, 长协下单, 合同项下订单 | |
| 预约送货 | Delivery booking |  | |
| 预约送货清单 | Booking list |  | |

### 实货交易 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| LME折扣 |  Discount on LME | 伦敦金属交易所, London Metal Exchange, LME |
| LML折扣 |  Discount on LML |  |
| TQ欧元交易条款折扣 | Discount TQ Eur TM |  |
| 临时升贴水 | Temporary Discount/Premium | Premium/Discount, 溢价, 贴水, 升水, Premium |
| 交货总折扣 | Total Delivered Discount（Eur） |  |
| 交货截止日 | Delivery End Date |  |
| 交货起始日 | Delivery Start Date |  |
| 仓单交易 | Warehouse receipt transaction | Warehouse Receipt, 标准仓单, 提单 |
| 内/外贸 | CN/ Global Trade | 国际贸易, Global Trade, International Trade |
| 升贴水 |  Nominal Premium Discount | Premium/Discount, 溢价, 贴水, 升水, Premium |
| 升贴水单价（欧元/吨） | Unit discount(Eur/TO) | Premium/Discount, 溢价, 贴水, 升水, Premium |
| 原材料销售已定价未交割 | Raw mat | Delivery, 实物交割, Settlement |
| 合同号 | Contract Number |  |
| 合同类型 | Contract Type |  |
| 实货交易 | Physical transaction |  |
| 实际收货日期 | Effective entry date |  |
| 实际收货日期开始 | Effective entry date start |  |
| 实际收货日期结束 | Effective entry date end |  |
| 实际收货物料 | Article |  |
| 实际收货货量 | Actual Received Quantity |  |
| 实际收货量 | Quantity(TO) |  |
| 已收货数量 | Received Quantity |  |
| 应收货款 | Accounts receivable | Goods Payment, 商品货款 |
| 折扣 | Discount |  |
| 收发 | Receipt delivery type |  |
| 收发货明细 | Receipt and delivery details |  |
| 收发货标识 | Receipt delivery identifier |  |
| 收货 | Receive Goods |  |
| 暂估销售炉渣 | prov sales/slag |  |
| 最终升贴水 | Final Discount/Premium | Premium/Discount, 溢价, 贴水, 升水, Premium |
| 月均折扣 | Average Premium/Discount |  |
| 有hu业务，不允许跨订单行选择 | Cross-order line selection prohibited for HU business. |  |
| 标准折扣 | Unitary discount/(Eur/TO) |  |
| 欧元折扣 | EUR Discount |  |
| 溢价 | Premium |  |
| 点价方 | Price setter | 定价, 作价, Fixation, Price Fixation, Pricing |
| 计价类型 | Pricing type |  |
| 资金交易 | Funds transaction |  |
| 部分冲销 | Partial Write-off | Reversal, Write-off, Offset, 红冲, 撤销 |
| 采购 | Purchase | 进项发票, Purchase Invoice, 收票 |
| 采购净库存价值 | Pur Eng Val |  |
| 采购合计 | tot purch |  |
| 采购合计2 | Pur. Eng. |  |
| 采购已定价未交割 | Purchase eng | Delivery, 实物交割, Settlement |
| 采购退款 | Purchase refund |  |
| 采销方向 | Direction |  |
| 销售 | Sales | 销项发票, Sales Invoice, 开票 |
| 销售净库存价值 | Sal Eng Val |  |
| 销售合计 | tot sales |  |
| 销售合计2 | Sale eng. |  |

### 实货交易 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `voyageCharterPricingTypes_1` | WS点 | WS Point |
| `fxPsFlags_1` | 买入 | Buy |
| `receiptDeliveryHeaderTypes_9` | 信用申请 | Credit Application |
| `receiptDeliveryHeaderTypes_10` | 信用登记 | Credit Registration |
| `receiptDeliveryHeaderTypes_8` | 信用计划 | Credit Plan |
| `receiptDeliveryHeaderTypes_4` | 入库登记 | Good Receipt |
| `receiptDeliveryHeaderTypes_2` | 入库登记和采购合同 | Good Receipt and Purchase Contract |
| `priceStatus_2` | 全部确认 | Fully Confirmed |
| `pricingContractTypes_3` | 其他 | Other |
| `receiptDeliveryHeaderTypes_5` | 出库登记 | Good Release |
| `receiptDeliveryHeaderTypes_7` | 初始库存 | Initial Stock |
| `headerStatus_3` | 删除 | Deleted |
| `priceFormulaType_2` | 升贴水 | Premium/Discount |
| `fxPsFlags_2` | 卖出 | Sell |
| `termFlags_1` | 即期 | Spot |
| `receiptDeliverTypes_2` | 发货 | Release |
| `voucherType_4` | 发货 | Delivery |
| `flowStatusTypes_1` | 发起审批 | Initiate Approval  |
| `pricingStatuses_2` | 固定 | Fixed |
| `chargePricingType_1` | 固定价 | Fixed Price |
| `pricingTypes_1` | 均价 | Average Price |
| `pricingTypes_3` | 复杂计价 | Complex Pricing |
| `receiptDeliveryHeaderTypes_15` | 外汇交易 | FX Trading |
| `receiptDeliveryHeaderTypes_11` | 存贷款 | Deposit and Loan |
| `flowStatusTypes_3` | 审批中 | In Approval |
| `flowStatusTypes_4` | 审批通过 | Approved |
| `flowStatusTypes_5` | 审批驳回 | Rejected |
| `pricePointParty_2` | 对方 | To counterparty option |
| `deliveryStatus_2` | 已划款 | Delivered |
| `deliveryTypes_2` | 库存盘点 | Inventory Count |
| `voucherType_5` | 开票 | Invoice Release |
| `pricePointParty_1` | 我方 | To our option |
| `receiptDeliveryHeaderTypes_14` | 掉期 | Swap |
| `voucherType_3` | 收票 | Invoice Received |
| `receiptDeliverTypes_1` | 收货 | Receipt |
| `voucherType_2` | 收货 | Receipt |
| `headerStatus_1` | 新建 | New |
| `flowStatusTypes_2` | 新建 | New |
| `documentStatus_1` | 无 | None |
| `receiptDeliveryHeaderTypes_13` | 期货 | Futures |
| `pricingContractTypes_1` | 期货 | Futures |
| `deliveryStatus_1` | 未划款 | Undelivered |
| `priceStatus_1` | 未确认 | Unconfirmed |
| `documentStatus_2` | 正常 | Normal |
| `pricingStatuses_1` | 浮动 | Floating |
| `pricingTypes_2` | 点价 | Unknown Price |
| `pricingContractTypes_2` | 现货 | Physical |
| `contractTypes_3` | 现货订单 | Spot Order |
| `headerStatus_2` | 生效 | Effective |
| `flowStatusTypes_6` | 生效 | Effective |
| `receiptDeliveryHeaderTypes_12` | 租船合同 | Charter Contract |
| `voucherType_6` | 移仓 | Stock Transfer |
| `receiptDeliveryHeaderTypes_6` | 移库登记 | Stock Transfer Registration |
| `flowStatusTypes_7` | 虚拟合同 | Virtual Contract |
| `voucherType_1` | 订单 | Order |
| `receiptDeliveryHeaderTypes_16` | 质押式回购 | Repurchase Pledge |
| `lcStatus_10` | 贴现 | Discount |
| `warehousePsFlag_1` | 转入 | Transfer In |
| `warehousePsFlag_2` | 转出 | Transfer Out |
| `termFlags_2` | 远期 | Forward |
| `priceStatus_3` | 部分确认 | Partially Confirmed |
| `psFlags_1` | 采购 | Purchase |
| `receiptDeliveryHeaderTypes_1` | 采购合同 | Purchase Contract |
| `deliveryTypes_3` | 采购退货 | Purchase Return |
| `chargePricingType_2` | 金额 | Amount |
| `voyageCharterPricingTypes_2` | 金额 | Amount |
| `psFlags_2` | 销售 | Sale |
| `deliveryTypes_1` | 销售出库 | Sales Outbound |
| `receiptDeliveryHeaderTypes_3` | 销售合同 | Sales Contract |
| `contractTypes_1` | 长协合同 | Long-term Agreement |
| `contractTypes_2` | 长协订单 | LTA Order |

---

## 2. 作价与定价管理 / Fixation & Pricing

### 作价与定价管理 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| Greenlist价格 | Greenlist Price |  | |
| 价格主数据 | Price Master Data |  | |
| 价格因素 | Pricing Factor |  | |
| 作价市场 | Pricing Market | 定价市场, 基准市场, Pricing Market, Benchmark Market | |
| 作价管理 | Fixation Management |  | |
| 定价明细表 | Fixation Detail |  | |
| 常用作价方式 | Common Pricing Formula |  | |
| 月底已定价未交割明细 | EOM Engagement Detail By Base Metal | Delivery, 实物交割, Settlement | |
| 月底金属已定价未交割汇总 | EOM Engagement Summary by Base Metal | Delivery, 实物交割, Settlement | |
| 期货计价量模型 | LME Movement | Futures, 期货合约, 期货交易 | |
| 期间规则 | Period Rule |  | |
| 点价关联 | Link Fixation to GR | 定价, 作价, Fixation, Price Fixation, Pricing | |
| 点价关联明细表 | Fixation Link Detail | 定价, 作价, Fixation, Price Fixation, Pricing | |
| 点价记录 | Fixation Record | 定价, 作价, Fixation, Price Fixation, Pricing | |
| 点价邮件补发 | Fixation Email Re-send | 定价, 作价, Fixation, Price Fixation, Pricing | |
| 现货计价量模型 | Fixation Movement |  | |
| 现货计价量调整 | Fixation Adjustment |  | |
| 计价公式 | Pricing Formula | 定价公式, 价格公式, Pricing Formula, Price Formula | |

### 作价与定价管理 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| Fixation ID | Fixation ID |  |
| Greenlist 价格更新 | Greenlist Price Update |  |
| Greenlist 单价 | Greenlist Price/（Eur/To） |  |
| Greenlist金额（EUR） | tot gl（EUR） |  |
| LME 历史价格 | LME Hist | 伦敦金属交易所, London Metal Exchange, LME |
| MIN 价格 | MIN |  |
| 仅支持对审批完成的单据进行点价关联 | Only supported for pricing association of approved documents | 定价, 作价, Fixation, Price Fixation, Pricing |
| 价格小数点位 | Price rounding digits |  |
| 价格类型 | Price type |  |
| 价格趋势 | Price Trend |  |
| 作价周期类型 | Pricing cycle type |  |
| 作价完成 | Fixation Complete |  |
| 作价市场 | Pricing market | 定价市场, 基准市场, Pricing Market, Benchmark Market |
| 作价期间规则 | Pricing range rule |  |
| 作废失败 | Cancel Failed | Void, Cancel, Invalid, 废弃 |
| 作废成功 | Cancelled | Void, Cancel, Invalid, 废弃 |
| 关联Fixation ID | Link Fixation ID |  |
| 关联交易场景中，基价只能选择BasicTriggeredPrice作价方式 | In the related party transaction scenario, the base price can only choose the Pricing Formula of BasicTriggeredPrice. | Related Party, 关联方交易 |
| 关联失败 | Link Failed |  |
| 关联定价明细ID | Linked Pricing Detail ID |  |
| 关联点价单 | Link Fixation Record | 定价, 作价, Fixation, Price Fixation, Pricing |
| 关联计价量ID | Associated Pricing Quantity ID |  |
| 变更定价日期 | Change Pricing Date |  |
| 变更数量超过新商品行待点价数量 | The quantity change exceeds the quantity of the new product line awaiting pricing | 品种, 产品, 货物, 物料, Article |
| 合约月 | Contract Month | Contract, 期货合约, Contract Name |
| 基价类型 | Basic price type |  |
| 定价日期 | Pricing date |  |
| 定价明细表 | Fixation Detail |  |
| 已关联点价量 | Quantity already associated with pricing | 定价, 作价, Fixation, Price Fixation, Pricing |
| 已定单价 | Fixation Price |  |
| 已点价数量 | Fixeded Quantity | 定价, 作价, Fixation, Price Fixation, Pricing |
| 市场价格 | Market Price |  |
| 总价 | Fixation Value In Settlement Currency |  |
| 成交明细 | Fixation Details |  |
| 成功关联合同 | Link Successful |  |
| 数量 | Quantity |  |
| 数量单位 | Quantity unit |  |
| 有合同的单据无法进行关联合同 | Already linked to contract |  |
| 未点价数量 | Unfixed Quantity | 定价, 作价, Fixation, Price Fixation, Pricing |
| 欧元总价 | Fixation Value In Base Currency |  |
| 点价 | Fixation | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价保证金 | Fixation margin deposit | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价关联 | Pricing association | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价单位 | Pricing unit | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价单号 | Pricing order number | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价变更 | Fixation Change | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价手数 | Unknown Fixation Lots | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价方 | Fixation right | 定价, 作价, Fixation, Price Fixation, Pricing |
| 点价金额 | Pricing Amount | 定价, 作价, Fixation, Price Fixation, Pricing |
| 现货计价量模型 | Fixation Movement |  |

### 作价与定价管理 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `priceType_1` | 均价 | Average Price |
| `priceFormulaType_1` | 基价 | Base Price |
| `priceType_3` | 最低价 | Lowest Price |
| `priceType_2` | 最高价 | Highest Price |

---

## 3. 库存管理 / Inventory Management

### 库存管理 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| EOM Engagement 报表 | EOM Engagement Report  |  | |
| SAP入库单 | SAP Goods Receipt |  | |
| SAP分包商物料移动 | SAP Subcontract Movement |  | |
| SAP废料再生产 | SAP Return Scrap Recycle |  | |
| 仓储设施 | Warehouse |  | |
| 仓库 | Warehouse | 仓储, 库, Warehouse, Storage, Depot | |
| 元素库存报表 | Inventory Report Split by Base Metal |  | |
| 入库报表 | Entry report |  | |
| 入库登记 | Good Receipt | 入库, 收货登记, Good Receipt, GR, Goods Receipt | |
| 出入库配置 | Inbound/ Outbound Configuration |  | |
| 出库明细表 | Detail Entries of Goods Release |  | |
| 出库通知 | Outbound Delivery Note | 发货通知, 出库单, Outbound Delivery, Delivery Note | |
| 初始库存 | Initial Stock |  | |
| 商品库存报表 | Entries report of materials | 品种, 产品, 货物, 物料, Article | |
| 年度商品库存报表 | Yearly entries report of materials | 品种, 产品, 货物, 物料, Article | |
| 年终库存报表 | Year End Inventory Report |  | |
| 库存价值报表 | Detailed Entries Accounting & Added Value |  | |
| 库存价值评估表 | Evaluation of Detaile Entries Value |  | |
| 库存余额表 | Inventory Balance Table |  | |
| 库存总览表 | Inventory Overview Table |  | |
| 库存报表管理 | Inventory Report Management |  | |
| 库存明细对账 | Inventory Detail for Reconcilation |  | |
| 库存明细表 | SAP Year End Inventory by Article |  | |
| 库存月结 | Inventory Monthly Closing | 月末结算, 月度结转, EOM, End of Month, 月结 | |
| 库存管理 | Inventory Management |  | |
| 库存调差 | Inventory Adjustment | 库存调整, 盘盈盘亏, Inventory Adjustment, Stock Adjustment | |
| 废料来料入库 | Residual & Conversion Entry |  | |
| 当月库存附加价 | Added Value of Current Month Entry |  | |
| 月底净库存估值表 | EOM Committed Stock Valuation |  | |
| 月度入库金属价值快照 | Monthly GR Metal Value Snapshot |  | |
| 月度入库金属价值明细 | Monthly GR Metal Value Detail |  | |
| 月结明细 | EOM Details |  | |
| 月结管理 | EOM Management |  | |
| 未开票库存价值 | Accounting Value of Entry without Invoice |  | |
| 移库 | Stock Transfer | 调拨, 库存转移, Stock Transfer, 仓库间转移 | |
| 移库入库 | Stock Transfer Inbound | 调拨, 库存转移, Stock Transfer, 仓库间转移 | |
| 移库出库 | Stock Transfer Outbound | 调拨, 库存转移, Stock Transfer, 仓库间转移 | |
| 移库申请 | Stock Transfer Application | 调拨, 库存转移, Stock Transfer, 仓库间转移 | |
| 金属库存快照 | Inventory of Base Metal Snapshot |  | |
| 金属库存明细 | Inventory of Base Metal Details  |  | |

### 库存管理 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| Begining Stock Ownership | Begining Stock Ownership |  |
| CTRM审批通过、未推送SAP的开票数量 | The number of invoices approved in CTRM but not yet pushed to SAP. | 审核, Approval, Approve, 签批 |
| Diff Stock | Diff Stock |  |
| Ending Stock Ownership | Ending Stock Ownership |  |
| SAP DN行号 | SAP DN Line Number |  |
| SAP 交货单号 | SAP DN |  |
| SAP 物料凭证号 | SAP Article |  |
| SAP 物料凭证年度 | SAP Voucher Fiscal Year |  |
| SAP 物料凭证行号 | SAP Voucher Line Item |  |
| SAP 订单号 | SAP PO |  |
| SAP 订单行号 | SAP PO No.. |  |
| SAP业务场景 | SAP Business Scenario |  |
| SAP会计凭证号 | SAP accounting document number |  |
| SAP会计年 | SAP Document Year |  |
| SAP内向交货单号 | SAP Doc No. |  |
| SAP单位 | SAP UoM |  |
| SAP单据号 | SAP Document No. |  |
| SAP单据行号 | SAP Material Document Line |  |
| SAP发票号 | SAP Inv. No. |  |
| SAP只能关联1行采购需求，请不要多选！ | SAP only can be related to 1 line of purchase request, please do not multi-select! |  |
| SAP基本计量单位 | SAP basic UoM | UOM, Unit of Measure, 计量, 单位 |
| SAP外向交货单行号 | SAP Outbound Delivery Line Number |  |
| SAP批次行号 | SAP Batch Line Number |  |
| SAP数据拉取 | Retrieve SAP Data |  |
| SAP数量单位 | SAP Uom |  |
| SAP物料凭证号 | SAP Material Document Number |  |
| SAP物料凭证年份 | SAP Doc Year |  |
| SAP物料凭证行号 | SAP material document Line |  |
| SAP生产订单号 | SAP Production Order Number |  |
| SAP行项目 | SAP Line Item |  |
| SAP行项目号 | SAP Item num |  |
| SAP订单号 | SAP order number |  |
| SAP订单行号 | SAP Order Line No. |  |
| SAP销售订单行号 | SAP sales order Line No. |  |
| sap物料号 | SAP material number |  |
| storageIs | 查询0库存数据 |  |
| 上级SAP发票号 | Linked SAP Invoice No. |  |
| 上级SAP发票号存在不一致 | Inconsistent parent SAP invoice number exists. |  |
| 上级SAP发票行号 | Linked SAP invoice Line No. |  |
| 不能选择不同仓库，请重新勾选 | Cannot select different warehouses, please reselect | 仓储, 库, Warehouse, Storage, Depot |
| 交货数量(SAP) | Delivered SAP Quantity  |  |
| 仓单交易平台账户 | Warehouse trading platform account | Warehouse Receipt, 标准仓单, 提单 |
| 仓库 | Warehouse | 仓储, 库, Warehouse, Storage, Depot |
| 仓库地点 | Warehouse location | 仓储, 库, Warehouse, Storage, Depot |
| 仓库未填 | Warehouse not filled | 仓储, 库, Warehouse, Storage, Depot |
| 仓库类型 | 仓库类型 | 仓储, 库, Warehouse, Storage, Depot |
| 入库总量 | Total storage quantity |  |
| 入库数量（TO） | Quantity in Warehouse（TO） |  |
| 入库数量（主计量单位） | Quantity in Warehouse(main uom) | UOM, Unit of Measure, 计量, 单位 |
| 入库日期 | Warehouse in date |  |

### 库存管理 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `storageInsideOutside_1` | 三方库 | Third-party Warehouse |
| `warehousePs_1` | 串入 | Transfer In |
| `warehousePs_2` | 串出 | Transfer Out |
| `warehousePsbuy_1` | 买入 | Buy In |
| `warehouseBusinessType_3` | 二次结算收款登记 | Secondary Settlement Receipt Registration |
| `cooperationType_3` | 仓储 | Warehouse |
| `warehouseType_2` | 仓单 | Warehouse Receipt |
| `cdzxType` | 仓单注销 | Warehouse Receipt Cancellation |
| `warehouseTypes_1` | 仓库 | Warehouse |
| `warehouseBusinessType_4` | 保证金 | Margin |
| `billFlag_1` | 入库库存 | Physical Inventory |
| `warehouseStatus_2` | 冻结 | Frozen |
| `warehouseStatus_4` | 出库 | Outbound |
| `warehousePsbuy_2` | 卖出 | Sell Out |
| `rdFlags_2` | 发货 | Release |
| `actionTypes_4` | 库存盘点 | Inventory Count |
| `sapValidateStatus_2` | 待验真 | Awaiting Verification |
| `rdFlags_3` | 拣配 | Picking |
| `billFlag_2` | 提单库存 | Bill Inventory |
| `rdFlags_1` | 收货 | Receipt |
| `sapValidateStatus_1` | 无需验真 | Verification Waived |
| `sapValidateStatus_6` | 未通过 | Not Verified |
| `warehouseFlag_1` | 正回购(S/B) | Repurchase (S/B) |
| `warehouseStatus_1` | 正常 | Normal |
| `warehouseType_1` | 现货 | Physical |
| `transferapplyType_1` | 移库申请 | Stock Transfer Application |
| `warehouseBusinessType_1` | 货款 | Goods Payment |
| `warehouseStatus_3` | 质押 | Pledged |
| `warehouseTypes_2` | 车船 | Vehicles / Vessels |
| `warehouseFlag_2` | 逆回购(B/S) | Reverse Repurchase (B/S) |
| `sapValidateStatus_5` | 通过 | Verified |
| `warehouseBusinessType_2` | 采购货款退款 | Purchase Goods Payment Refund |
| `sapValidateStatus_4` | 验真中 | Verifying |
| `sapValidateStatus_3` | 验真失败 | Verification Failed |

---

## 4. 应收应付与资金管理 / AR/AP & Capital

### 应收应付与资金管理 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| Debit/Credit Note | Debit/Credit Note | 借贷项通知, DC Note, 借项通知, 贷项通知, Debit Note | |
| 付款条款 | payment terms | Payment Terms, 付款条件, 账期 | |
| 付款申请 | Payment Application | 付款, Payment Application, Payment Request, 请款 | |
| 供应商结算发票检查表 | Supplier Settlement Invoice Checklist |  | |
| 应付管理 | Payables Management |  | |
| 应收应付 | Accounts Receivable and Payable |  | |
| 应收管理 | Receivables Management |  | |
| 开票情况查询 | Invoice Status Inquiry |  | |
| 待开Credit/Debit Note表 | Credit/Debit Note to be received |  | |
| 待收Credit/Debit Note表 | Credit/Debit Note to be received |  | |
| 支付工具 | Payment Method |  | |
| 收票情况查询 | Invoice Receipt Status Inquiry |  | |
| 款项类型 | Payment Type |  | |
| 费用记录 | Expense Record | 费用, 杂费, Expense, Charge, Cost Record | |
| 资金管理 | Capital Management |  | |
| 银行流水 | Bank Transactions |  | |

### 应收应付与资金管理 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| DN码 | Delivery Note (DN) Code |  |
| paymentAmountValid | Detected that the current pending payment amount ({paymentApplicationClaimSettingAmount} RMB) is greater than [application amount (Payment currency) ({paymentCurrencyApplicationAmount} RMB) - paid amount ({paymentAmount} RMB)]; please modify the current pending payment amount? |  |
| paymentApplicationAmountValid | Detected that the current application payment amount ({applicationAmount} RMB) is greater than [paid amount ({receiveAmount} RMB) - application amount ({paymentApplicationAmount} RMB)]; please modify the current payment amount |  |
| revokeApproveTip | Do you want to revoke the approval of the expense record {invoiceNumber} created by {createdBy}? |  |
| 上级发票单据号 | Linked Invoice Doc No. |  |
| 不能选择不同交易对家的流水！ | Cannot select transactions with different counterparties! |  |
| 不能选择不同收付类型的流水！ | Cannot select transactions with different payment methods! |  |
| 业务机构账号不同，不能合并认领，请重新选择 | Different business entity accounts, unable to merge claims, please reselect | 公司, 法人实体, 交易主体, 机构, Company |
| 主单位发票数量 | Invoiced Quantity in Master UoM |  |
| 交易对家不同，不能合并认领，请重新选择 | Different counterparty, unable to merge claims, please reselect |  |
| 交易日期不同，不能合并认领，请重新选择 | Different transaction dates, unable to merge claims, please reselect |  |
| 交易时间 | Transaction Time |  |
| 交易附言 | Transaction Note |  |
| 付款 | Payment | 付款, Payment Application, Payment Request, 请款 |
| 付款摘要 | Payment summary |  |
| 付款时间 | Payment date |  |
| 付款条件 | Payment Condition |  |
| 付款条款 | Payment Term | Payment Terms, 付款条件, 账期 |
| 付款申请单据的支付方式暂只支持一行明细 | Payment application documents support only one line item for payment method details | 付款, Payment Application, Payment Request, 请款 |
| 付款进度 | Payment progress |  |
| 付款金额(支付币种) | Payment amount (Payment currency) | Currency, 货币, 交易币种 |
| 付款金额上下不一致，请调整 | Inconsistent payment amount, please adjust |  |
| 付款金额需要大于0 | Payment amount needs to be greater than 0 |  |
| 供应商退货款、供应商质量赔款 | Supplier return payment, supplier quality compensation | Goods Payment, 商品货款 |
| 信用币种 | Credit Segment Currency | Currency, 货币, 交易币种 |
| 信用敞口 | Credit Exposure | Exposure, 风险敞口, Open Exposure |
| 信用限额 | Credit Limit |  |
| 入库未开票数量 | Received Not Invoiced Quantity |  |
| 全部开票? | All invoiced? |  |
| 全部收付? | All payment? |  |
| 关联发票号码 | Linked Invoice No |  |
| 关联报关发票 | Relate Customs Invoice |  |
| 关联部分待收credit/debit金额 | Linked Pending Credit/Debit Amount |  |
| 冲销发票号 | Reversed Invoice Document Number | Reversal, Write-off, Offset, 红冲, 撤销 |
| 出库未开票数量 | Uninvoiced Outbound Quantity  |  |
| 出库通知 | Outbound Delivery Note | 发货通知, 出库单, Outbound Delivery, Delivery Note |
| 出库通知单据号 | Outbound Delivery Note Number | 发货通知, 出库单, Outbound Delivery, Delivery Note |
| 出库通知明细中，通知数量不能为负数 | Outbound Delivery Note detail, notification quantity cannot be negative | 发货通知, 出库单, Outbound Delivery, Delivery Note |
| 出库通知行号 | Outbound Delivery Note Line Number | 发货通知, 出库单, Outbound Delivery, Delivery Note |
| 分类 | Category |  |
| 列表中已有数据，不可多选 | There is existing data in the list, multiple selection is not allowed |  |
| 创建的报关发票 | Created Invoice |  |
| 剩余可结算数量 | Tobe Invoiced Quantity |  |
| 单据明细 | Doc details |  |
| 发票 | invoice | 销项发票, Sales Invoice, 开票 |
| 发票-物资 | Invoice-Article |  |
| 发票不含税金额 | Invoiced amount excluding tax |  |
| 发票信息 | Invoice information |  |
| 发票单价 | invoice unit price |  |
| 发票号 | Invoice Document Number |  |

### 应收应付与资金管理 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `lcTypes_3` | Back To Back | Back To Back |
| `lcTypes_2` | Cash To Back | Cash To Back |
| `invoiceDirection_2` | Credit | Credit |
| `invoiceTypes_5` | Credit Note | Credit Note |
| `invoiceDirection_1` | Debit | Debit |
| `invoiceTypes_4` | Debit Note | Debit Note |
| `invoiceCategory_4` | Final | Final |
| `invoiceCategory2_2` | Final | Final |
| `lcTypes_4` | Front To Back | Front To Back |
| `lcTypes_6` | N/A | N/A |
| `lcTypes_1` | Open Account | Open Account |
| `invoiceCategory_3` | Provisional | Provisional |
| `invoiceCategory2_1` | Provisional | Provisional |
| `repaymentMethods_1` | 一次性先付 | One-time Prepayment |
| `repaymentMethods_2` | 一次性后付 | One-time Postpayment |
| `customsBondPaymentMethod_1` | 一般贸易 | General Trade |
| `invoiceTypes_1` | 临时发票 | Provisional Invoice |
| `invoiceStage_1` | 临时发票 | Provisional Invoice |
| `adFlags_2` | 交单 | Negotiation |
| `lcStatus_6` | 交单 | Documents Presented |
| `lcStatus_8` | 交单 | Documents Presented |
| `chargeDirections_1` | 付款 | Payment |
| `paymentFlags_1` | 付款 | Payment |
| `paymentProgressStatus_2` | 付款完成 | Payment Completed |
| `creditTableType_3` | 例外授信 | Exceptional Credit |
| `taxPaymentStatus_2` | 保税 | Duty-free |
| `bankCreditHeaderTypes_3` | 信用证 | Letter of Credit |
| `invoiceTypes_8` | 信用证保证金 | Letter of Credit Margin |
| `limitTypes_1` | 信用证额度 | Letter of Credit Limit |
| `limitTypes_4` | 信用风险 | Credit Risk |
| `paymentStatuses_4` | 全部认领 | All Claimed |
| `creditTableType_1` | 关联方 | Related Party |
| `invoiceTypes_10` | 内贸发票-单据 | CN Invoice-Doc |
| `invoiceTypes_11` | 内贸发票-物资 | CN Invoice-Article |
| `adFlags_1` | 到单 | Presentation |
| `settlementSourceList_2` | 前期结算调整 | Previous Settlement Adjustment |
| `invoiceType_1` | 发票-单据 | Invoice Doc |
| `invoiceType_2` | 发票-物资 | Invoice Article |
| `invoiceType2_1` | 发票-物资 | Invoice Article |
| `invoiceType_4` | 发票-物资-冲销 | Invoice Article-Offset |
| `cashReceiveType_1` | 合同 | Contract |
| `bankCreditOcFlags_2` | 场内 | Ex Market |
| `bankCreditOcFlags_1` | 场外 | OTC |
| `invoiceCategory_1` | 增值税专用发票 | Special VAT Invoice |
| `invoiceCategory1_1` | 增值税专用发票 | Special VAT Invoice |
| `invoiceType1_1` | 增值税专用发票 | Special VAT Invoice |
| `invoiceCategory_2` | 增值税普通发票 | General VAT Invoice |
| `invoiceCategory1_2` | 增值税普通发票 | General VAT Invoice |
| `invoiceType1_2` | 增值税普通发票 | General VAT Invoice |
| `invoiceType1_3` | 增值税电子专用发票 | Special VAT E-Invoice |
| `invoiceType1_4` | 增值税电子普通发票 | General VAT E-Invoice |
| `lcCategories_2` | 备用信用证 | Standby Letter of Credit |
| `bankCreditHeaderTypes_6` | 存贷款 | Deposit and Loan |
| `taxPaymentStatus_1` | 完税 | Duty Paid |
| `bankCreditHeaderTypes_1` | 实货合同 | Physical Contract |
| `cashReceiveType_2` | 实际 | Actual |
| `creditTableType_4` | 小额授信 | Small Credit |
| `creditObjectType_4` | 小额特殊 | Small Special |
| `settlementStatus_2` | 已临时结算 | Temporarily Settled |
| `creditDataStatus_1` | 已失效 | Expired |
| `limitValues_13` | 已开票未支付 | Invoiced Unpaid |
| `settlementStatus_3` | 已最终结算 | Finally Settled |
| `settlementStatusList_1` | 已结 | Settled |
| `paymentStatuses_3` | 已认领 | Fully Claimed |
| `creditStatus_5` | 待备案 | To be Recorded |
| `creditDataSource_1` | 手工录入 | Manual Input |
| `lcAcceptanceStatuses_1` | 承兑 | Acceptance |
| `lcStatus_9` | 承兑 | Accepted |
| `lcAcceptanceStatuses_2` | 拒绝 | Refusal |
| `indicatorNature_4` | 授信账期 | Credit Term |
| `indicatorNature_3` | 授信额度 | Credit Limit |
| `bankCreditHeaderTypes_5` | 掉期 | Swap |
| `abutmentPayStatusList_3` | 支付失败 | Payment Failed |
| `abutmentPushStatus_5` | 支付成功 | Payment Success |
| `abutmentPayStatusList_2` | 支付成功 | Payment Success |
| `lcStatus_11` | 收付款 | Payment/ Collection |
| `chargeDirections_2` | 收款 | Receipt |
| `paymentFlags_2` | 收款 | Collection |
| `lcTypes_5` | 敞口授信 | Open Credit |
| `paymentStatuses_5` | 无 | None |
| `creditTableType_2` | 普通授信 | General Credit |
| `creditModel_1` | 普通授信 | General Credit |
| `invoiceTypes_2` | 最终发票 | Final Invoice |
| `invoiceStage_2` | 最终发票 | Final Invoice |
| `bankCreditHeaderTypes_4` | 期货 | Futures |
| `lcStatus_7` | 未交单 | Documents Not Presented |
| `paymentProgressStatus_1` | 未付款 | Unpaid |
| `settlementStatusList_2` | 未结 | Unsettled |
| `settlementStatus_1` | 未结算 | Unsettled |
| `lcStatus_1` | 未计划 | Unplanned |
| `paymentStatuses_1` | 未认领 | Unclaimed |
| `settlementSourceList_1` | 本次结算 | Current Settlement |
| `customsBondPaymentMethod_2` | 来料加工 | Incoming Processing |
| `sourceList_1` | 标准 | Standard |
| `purposeListApplication_1` | 正常 | Normal |
| `invoiceTypes_9` | 海关增值税 | Customs VAT |
| `creditModel_2` | 现货现款 | Spot Cash |
| `creditDataStatus_2` | 生效中 | Effective |
| `lcStatus_3` | 申请 | Applied |
| `invoiceCategory3_3` | 电子普通发票 | General E-Invoice |
| `lcStatus_4` | 登记 | Registered |
| `bankCreditHeaderTypes_2` | 租船合同 | Charter Contract |
| `creditObjectType_3` | 第三方 | Third Party |
| `invoiceCategory3_2` | 纸质专用发票 | Physical Special Invoice |
| `invoiceCategory3_1` | 纸质普通发票 | Physical General Invoice |
| `creditObjectType_1` | 股份内 | Intra-Equity |
| `lcStatus_2` | 计划 | Planned |
| `creditDataSource_2` | 评级申请 | Rating Application |
| `cashflowTypes_1` | 货款 | Goods Payment |
| `invoiceTypes_7` | 货款保证金 | Payment Margin |
| `invoiceTypes_3` | 费用 | Expense |
| `invoiceType_3` | 费用发票 | Expense Invoice |
| `expenseScene_3` | 费用发票 | Expense Invoice |
| `lcCategories_1` | 跟单信用证 | Documentary Credit |
| `PurposeList_3` | 转保证金 | Transfer Margin |
| `PurposeList_6` | 转款-入 | Transfer In |
| `PurposeList_5` | 转款-出 | Transfer Out |
| `sourceList_2` | 转账 | Transfer |
| `PurposeList_4` | 转货款 | Transfer Payment |
| `customsBondPaymentMethod_3` | 进料加工 | Outgoing Processing |
| `purposeListApplication_2` | 退款 | Refund |
| `invoiceType1_5` | 通行费发票 | Toll Invoice |
| `abutmentPayStatusList_6` | 部分支付 | Partial Payment |
| `paymentStatuses_2` | 部分认领 | Partially Claimed |
| `lcStatus_5` | 闭卷 | Closed |
| `creditObjectType_2` | 集团内 | Intra-Group |
| `expenseScene_1` | 预付 | Prepayment |
| `limitValues_14` | 预付款 | Prepayment |
| `cashflowTypes_2` | 预收付 | Prepayment and Payment |
| `invoiceTypes_6` | 预收付 | Advanced Payment and Colllection |

---

## 5. 衍生品与风险管理 / Derivatives & Risk

### 衍生品与风险管理 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| LME Bill Book | LME Bill Book | 伦敦金属交易所, London Metal Exchange, LME | |
| LME Engagement | LME Engagement | 伦敦金属交易所, London Metal Exchange, LME | |
| LME Position | LME Position | 伦敦金属交易所, London Metal Exchange, LME | |
| LME Quantity Summary | LME Quantity Summary | 伦敦金属交易所, London Metal Exchange, LME | |
| LME VM Forcast | LME VM Forcast | 伦敦金属交易所, London Metal Exchange, LME | |
| LME交易日期配置 | LME Trade Date Config | 伦敦金属交易所, London Metal Exchange, LME | |
| LME成交流水 | LME Transaction Records | 伦敦金属交易所, London Metal Exchange, LME | |
| LME持仓变动明细 | ME Engagement Details | 伦敦金属交易所, London Metal Exchange, LME | |
| LME持仓快照 | LME Engagement Snapshot | 伦敦金属交易所, London Metal Exchange, LME | |
| 交易小节 | Session |  | |
| 保证金管理 | Margin Management | Margin, 履约保证金, 交易保证金 | |
| 保证金配置 | Margin Configuration | Margin, 履约保证金, 交易保证金 | |
| 历史持仓统计表 | Position Monitor History | 持仓监控, Position Monitor, 头寸监控 | |
| 夜盘保值头寸统计表 | Night Session Hedging Position | 持仓, 敞口, Position, Exposure, Open Position | |
| 头寸汇总表 | Bollettino Summary | 持仓, 敞口, Position, Exposure, Open Position | |
| 市场风险 | Market Risk | Market Risk, 价格风险, 市价风险 | |
| 市场风险报表 | Market Risk Report | Market Risk, 价格风险, 市价风险 | |
| 持仓统计表 | Position Monitor | 持仓监控, Position Monitor, 头寸监控 | |
| 日内市场行情 | Intraday Market Quotation |  | |
| 日结操作 | End of Day | EOD, End of Day, 日终, 日结 | |
| 日结日志 | EOD Log |  | |
| 每日市场行情 | Market Quotation |  | |
| 现金流模型 | Cash Flow Model | Cash Flow, 现金流, Cash Flow Model | |
| 衍生品管理 | Derivatives Management | Derivatives, 衍生品交易, 金融衍生品 | |
| 追保通知 | Margin Call Notification | 追加保证金, Margin Call, 追保 | |
| 追加保证金监控表 | Margin Monitor | Margin, 履约保证金, 交易保证金 | |
| 金属头寸表 | Metal Bollettino | 持仓, 敞口, Position, Exposure, Open Position | |
| 金属损益 | Metal Result |  | |

### 衍生品与风险管理 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| After Melting Composition | After Melting Composition |  |
| LME AL | LME AL | 伦敦金属交易所, London Metal Exchange, LME |
| LME CU | LME CU | 伦敦金属交易所, London Metal Exchange, LME |
| LME Cash (€/KG) | LME Cash (€/KG) | 伦敦金属交易所, London Metal Exchange, LME |
| LME Cash Price | LME Cash Price | 伦敦金属交易所, London Metal Exchange, LME |
| LME Gross Price | LME Gross Price | 伦敦金属交易所, London Metal Exchange, LME |
| LME NI | LME NI | 伦敦金属交易所, London Metal Exchange, LME |
| LME PB | LME PB | 伦敦金属交易所, London Metal Exchange, LME |
| LME Quantity | LME Quantity | 伦敦金属交易所, London Metal Exchange, LME |
| LME SN | LME SN | 伦敦金属交易所, London Metal Exchange, LME |
| LME ZN | LME ZN | 伦敦金属交易所, London Metal Exchange, LME |
| LME 交易头寸 | LME Movement | 伦敦金属交易所, London Metal Exchange, LME |
| LME 到期头寸 | Exprie LME | 伦敦金属交易所, London Metal Exchange, LME |
| LME 多头 | LME long | 伦敦金属交易所, London Metal Exchange, LME |
| LME 多头头寸（欧元） | LME Long Position (EUR) | 伦敦金属交易所, London Metal Exchange, LME |
| LME 空头 | LME short | 伦敦金属交易所, London Metal Exchange, LME |
| LME 空头头寸（欧元） | LME Short Position (EUR) | 伦敦金属交易所, London Metal Exchange, LME |
| LME 等效价 | LME equivalent | 伦敦金属交易所, London Metal Exchange, LME |
| LME多头价值 | LME Long  Val | 伦敦金属交易所, London Metal Exchange, LME |
| LME成交价 | Unit Price | 伦敦金属交易所, London Metal Exchange, LME |
| LME欧元价值 | LME value | 伦敦金属交易所, London Metal Exchange, LME |
| LME空头价值 | LME short  Val | 伦敦金属交易所, London Metal Exchange, LME |
| LME金额（EUR） | tot lme（EUR） | 伦敦金属交易所, London Metal Exchange, LME |
| LME（Eurkg） | LME（Eurkg） | 伦敦金属交易所, London Metal Exchange, LME |
| Session | Session |  |
| 一键追保 | One-click margin call |  |
| 交易日结束 | Trade Date End |  |
| 保证金分类 | Margin classification | Margin, 履约保证金, 交易保证金 |
| 保证金模板 | Margin template | Margin, 履约保证金, 交易保证金 |
| 保证金类型 | Margin type | Margin, 履约保证金, 交易保证金 |
| 保证金认领 | Margin claim | Margin, 履约保证金, 交易保证金 |
| 元素商品 | Composition Product | 品种, 产品, 货物, 物料, Article |
| 初始头寸 | Initial Position | 持仓, 敞口, Position, Exposure, Open Position |
| 合成类型 | Composition Type |  |
| 品味 | Composition |  |
| 商品质检类型中每个类别计价的默认值加起来应为1 | Summary of metal composition does not equal to 1 | 品种, 产品, 货物, 物料, Article |
| 基础头寸 | Basic | 持仓, 敞口, Position, Exposure, Open Position |
| 复杂分析数据 | Composition analytic data |  |
| 套保比率 | Hedging Ratio | 对冲, Hedging, 套期保值, Hedge |
| 实际应追保金额 | Actual margin amount |  |
| 小额套期保值 | small hedg |  |
| 已收付追保金额 | Received/paid margin amount |  |
| 当日结算价 | LME Cash |  |
| 成交价 | In price |  |
| 成分曲线 | Composition Curve |  |
| 持仓 | Position | 持仓监控, Position Monitor, 头寸监控 |
| 暂估提货已定价-追保金额 | Priced and picked - Margin amount |  |
| 更新交易小节 | Session Update |  |
| 最终头寸 | Final Position | 持仓, 敞口, Position, Exposure, Open Position |
| 服务套期保值 | service hed |  |

### 衍生品与风险管理 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `limitValues_11` | %95单日VaR | %95 Single Day VaR |
| `marginReleaseRules_2` | N/A | N/A |
| `instalmentTypes_1` | 一次性 | One-time |
| `lsFlags_1` | 买 | Buy |
| `riskStatuses_1` | 估计值 | Estimated Value |
| `limitValues_16` | 保证金 | Margin |
| `instalmentTypes_2` | 单月 | Single Month |
| `lsFlags_2` | 卖 | Sell |
| `limitValues_12` | 历史场景压力测试 | Historical Scenario Stress Test |
| `limitTypes_2` | 国资委额度 | SASAC Limit |
| `strategyOcFlags_2` | 场内 | Ex Market |
| `strategyOcFlags_1` | 场外 | OTC |
| `insuranceFlags_2` | 套保 | Hedging |
| `insuranceFlags_3` | 套利 | Arbitrage |
| `riskStatuses_2` | 实际值 | Actual Value |
| `limitValues_9` | 实际盈亏 | Actual P&L |
| `ocFlags_3` | 平今 | Close Today |
| `ocFlags_2` | 平仓 | Closing |
| `ocFlags_4` | 平昨 | Close Yesterday |
| `ocFlags_1` | 开仓 | Opening |
| `insuranceFlags_1` | 投机 | Speculation |
| `limitValues_7` | 持仓头寸 | Position |
| `limitValues_8` | 浮动盈亏 | Floating P&L |
| `limitValues_6` | 经营规模 | Business Scale |
| `limitValues_10` | 资金占用规模 | Capital Occupation |
| `limitValues_15` | 赊销 | Open Sale |
| `marginReleaseRules_1` | 逐笔 | By Transaction |
| `limitTypes_3` | 高级市场风险 | High Market Risk |

---

## 6. 信用与授信管理 / Credit Management

### 信用与授信管理 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| 日度限制 | Daily limit |  | |
| 月度限制 | Monthly limit |  | |

### 信用与授信管理 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| 不含税差异 | Variance Amount Excluding Tax |  |
| 交易品种 | Metal |  |
| 含税差异 | Variance Amount Including Tax |  |
| 开始生成现金流 | Start generating cash flow |  |
| 开票限额 | Invoicing limit |  |
| 敞口明细 | Exposure details | Exposure, 风险敞口, Open Exposure |
| 账实差异量 | Physical-booked variance quantity |  |
| 限额 | Limit amount |  |

### 信用与授信管理 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `indicatorSource_2` | 内部主观 | Internal Subjective |
| `indicatorSource_3` | 内部客观 | Internal Objective |
| `indicatorNature_2` | 减分项 | Deduction Item |
| `indicatorNature_1` | 加分项 | Bonus Item |
| `indicatorType_2` | 区间 | Range |
| `certificationTypes_1` | 国营配额 | State-owned Quota |
| `exposureOrFlags_1` | 授予 | Grant |
| `exposureOrFlags_2` | 接收 | Receive |
| `indicatorClassification_3` | 敞口指标 | Exposure Indicator |
| `templateType_2` | 敞口模型 | Exposure Model |
| `indicatorType_3` | 是非 | Binary |
| `indicatorClassification_1` | 普通指标 | General Indicator |
| `indicatorType_1` | 枚举 | Enum |
| `indicatorSource_1` | 第三方数据 | External Data |
| `templateType_1` | 评级模板 | Rating Template |
| `indicatorClassification_2` | 财务指标 | Financial Indicator |
| `indicatorType_4` | 连续 | Continuous |
| `certificationTypes_2` | 非国营配额 | Non-state-owned Quota |

---

## 7. 业务设置与主数据 / Business Settings & Master Data

### 业务设置与主数据 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| 业务主数据 | Business Master Data |  | |
| 业务机构管理 | Business Entity Management | 公司, 法人实体, 交易主体, 机构, Company | |
| 业务板块管理 | Business Segment Management | 板块, 事业部, Segment, Business Segment, Division | |
| 业务部门管理 | Business Department Management | 部门, 交易部门, Department, Business Department, Trading Desk | |
| 事件类型 | Event Type |  | |
| 交易日历 | Trading Calendar | Trading Calendar, 交易日, 交易日历 | |
| 人员管理 | Personnel Management |  | |
| 免税配额管理 | Exemption Management |  | |
| 功能角色权限管理 | Function Permission Management |  | |
| 包装 | Packaging |  | |
| 单位转换 | Unit Conversion |  | |
| 合约文本 | Contract Name | Contract, 期货合约, Contract Name | |
| 合约管理 | Contract Management | Contract, 期货合约, Contract Name | |
| 商品主数据 | Article Master Data | 品种, 产品, 货物, 物料, Article | |
| 商品定义 | Article Definition | 品种, 产品, 货物, 物料, Article | |
| 商品属性 | Article Attribute | 品种, 产品, 货物, 物料, Article | |
| 地点 | Location |  | |
| 客商主数据 | Business Partner Master Data | 交易对手, 对手方, 客户, 供应商, Business Partner | |
| 客商管理 | Business Partner Management | 交易对手, 对手方, 客户, 供应商, Business Partner | |
| 币种 | Currency | Currency, 货币, 交易币种 | |
| 币种转换 | Currency Conversion | Currency, 货币, 交易币种 | |
| 数据角色权限管理 | Data Permission Management |  | |
| 权限管理 | Permission Management |  | |
| 用户管理 | User Management |  | |
| 税码 | Tax Code |  | |
| 系统日期 | System Date |  | |
| 组织管理 | Organizational Management |  | |
| 结算方式 | Settlement Method | Settlement, 结算, Settlement Method | |
| 结算曲线 | Settlement Curve | Settlement Curve, Pricing Curve, 远期曲线, Forward Curve | |
| 计税规则 | Taxation Rules |  | |
| 计量单位 | Unit of Measure | UOM, Unit of Measure, 计量, 单位 | |
| 贸易术语 | Incoterms | Incoterms, 贸易条件, 交货条件, FOB, CIF | |
| 车船 | Vehicles and Vessels |  | |

### 业务设置与主数据 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| CTRM当前行数 | CTRM Current Line |  |
| LML欧元价值 | LML Value |  |
| verified | Verified article |  |
| 业务机构 | Company | 公司, 法人实体, 交易主体, 机构, Company |
| 业务机构代码 | Business entity code | 公司, 法人实体, 交易主体, 机构, Company |
| 业务机构户名 | Business Entity Account Name | 公司, 法人实体, 交易主体, 机构, Company |
| 业务机构简称 | Company Short Name | 公司, 法人实体, 交易主体, 机构, Company |
| 业务机构联系电话 | Business entity contact number | 公司, 法人实体, 交易主体, 机构, Company |
| 业务机构账号 | Business entity account number | 公司, 法人实体, 交易主体, 机构, Company |
| 业务板块 | Business Segment Name | 板块, 事业部, Segment, Business Segment, Division |
| 临时结算 | Provisional Settlement |  |
| 临时结算价 | Provisional Settlement price |  |
| 临时结算单价 | Provisional Unit Price |  |
| 临时结算数量 | Provisional Settlement Quantity |  |
| 临时结算数量类型 | Provisional Settlement Quantity Type |  |
| 临时结算金额 | Provisional Settlement amount |  |
| 交易币种 | Trading currency | Currency, 货币, 交易币种 |
| 交货地 | Delivery Location |  |
| 交货地点 | Delivery location |  |
| 价格货币 | Price Currency |  |
| 企业性质 | Enterprise nature |  |
| 供应商 | Supplier | 寄售, Consignment, Vendor Consignment, VMI |
| 关联业务机构 | Link business entity | 公司, 法人实体, 交易主体, 机构, Company |
| 关联商品明细行号 | Related Article Details Line Number. | 品种, 产品, 货物, 物料, Article |
| 内外部 | Inside and outside |  |
| 分配到商品 | Assign to article | 品种, 产品, 货物, 物料, Article |
| 分配数量不等于结算重量, 不能关联 | The allocated quantity does not equal the settlement weight and cannot be associated |  |
| 包装数量 | Package Quantity |  |
| 单价（本位币） | Price in Base Currency  |  |
| 单价（结算币） | Price in Settle Currency |  |
| 原商品 | Original Article | 品种, 产品, 货物, 物料, Article |
| 原定物料 | Original article |  |
| 合同币种 | Contract currency | Currency, 货币, 交易币种 |
| 名义本金（结算币种） | Notional Amount | Currency, 货币, 交易币种 |
| 商品 | Article | 品种, 产品, 货物, 物料, Article |
| 商品 VAT 类别 | Article VAT Type | 品种, 产品, 货物, 物料, Article |
| 商品信息 | Article info | 品种, 产品, 货物, 物料, Article |
| 商品别名 | Article alias | 品种, 产品, 货物, 物料, Article |
| 商品名称 | Article description | 品种, 产品, 货物, 物料, Article |
| 商品大类 | Article Category | 品种, 产品, 货物, 物料, Article |
| 商品属性 | Article attribute | 品种, 产品, 货物, 物料, Article |
| 商品数量 | Article quantity | 品种, 产品, 货物, 物料, Article |
| 商品数量单位 | Article UoM | 品种, 产品, 货物, 物料, Article |
| 商品明细 | Article Details | 品种, 产品, 货物, 物料, Article |
| 商品税码 | Article Tax Code | 品种, 产品, 货物, 物料, Article |
| 商品编号 | Article code | 品种, 产品, 货物, 物料, Article |
| 商品编码 | Article Code | 品种, 产品, 货物, 物料, Article |
| 商品行号 | Article Line No. | 品种, 产品, 货物, 物料, Article |
| 固定单价 |  Fixed Unit Price |  |
| 固定单价（欧元） | Fixed unit price in Eur |  |

### 业务设置与主数据 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `settlementType_1` | 临时结算 | Provisional Settlement |
| `cooperationType_4` | 交易所 | Exchange Market |
| `insideOutside_1` | 内部 | Internal |
| `pricechangeType_5` | 变更商品减少 | Decrease in Article |
| `pricechangeType_4` | 变更商品增加 | Increase in Article |
| `enterpriseNature_5` | 合资 | Joint Venture |
| `enterpriseNature_1` | 国企 | State-owned Enterprise |
| `storageInsideOutside_2` | 基地 | Base |
| `enterpriseNature_4` | 外资 | Foreign-funded Enterprise |
| `insideOutside_2` | 外部 | External |
| `enterpriseNature_2` | 央企 | National Enterprise |
| `settlementDirection_1` | 无 | None |
| `settlementType_2` | 最终结算 | Final Settlement |
| `cooperationType_5` | 期货公司 | Futures Brokers |
| `enterpriseNature_3` | 民企 | Private Enterprise |
| `sectionList_2` | 氧化铝 | Alumina |
| `sectionList_1` | 电解铝 | Electrolytic Aluminum |
| `sfFlags_1` | 结算价格 | Settlement Price |
| `quantityType_1` | 货币 | Currency |
| `cooperationType_6` | 车船 | Vehicles/ Vessels |
| `cooperationType_9` | 运输商 | Transportation Provider |
| `sectionList_3` | 非铝金属 | Non-ferrous Metal |

---

## 8. 实验室与质检 / Lab & Quality

### 实验室与质检 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| LAB+SPE-414 | LAB+SPE-414 |  | |
| 公式扣减属性 | Reduction function |  | |
| 完成检测列表 | Completed list | Testing, Inspection, 化验 | |
| 实验室模块 | Lab |  | |
| 待检/检测中列表 | List to be checked/tested | Testing, Inspection, 化验 | |
| 新增质检规则 | Standard rule create | Quality Inspection, 检验, 质量检测, 品检 | |
| 检测结果统计 | Inspection statistic | Testing, Inspection, 化验 | |
| 计算规则 | Calculation method per elements |  | |
| 质检 | quality inspection | Quality Inspection, 检验, 质量检测, 品检 | |
| 质检规则配置 | Standard rule configuration | Quality Inspection, 检验, 质量检测, 品检 | |
| 配置元素 | Standard rules & Elements per rule |  | |

### 实验室与质检 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| 人工结果 | Inspection result(manually) |  |
| 可引用数量 | Available Quantity |  |
| 实验室单据ID | Lab ID |  |
| 最新可用? | Latest available? |  |
| 未开始/不可用 | not started/unavailable |  |
| 机器结果 | Inspection result(machine) |  |
| 核实的质量 | Verified quality |  |
| 没有可以{setName}的记录！ | There are no records available for {setName}! |  |
| 申报的质量 | Declared quality |  |
| 结算数量 | Available quantity |  |
| 质检方法 | Analysis type | Quality Inspection, 检验, 质量检测, 品检 |
| 质检组成求和 | tot | Quality Inspection, 检验, 质量检测, 品检 |
| 质检结果 | Inspection Result | Quality Inspection, 检验, 质量检测, 品检 |
| 质检规则 | Standards rule  | Quality Inspection, 检验, 质量检测, 品检 |
| 转出金额大于可转金额，请检查 | The transferred amount is greater than the available amount for transfer, please check |  |

### 实验室与质检 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `assayTypes_2` | 类型1 | Type 1 |
| `assayTypes_3` | 类型2 | Type 2 |
| `assayTypes_1` | 默认 | Default |

---

## 9. 流程与审批 / Workflow & Approval

### 流程与审批 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| 动态表单配置管理 | Dynamic Form Configuration Management |  | |
| 发布流程管理 | Release process management |  | |
| 已办事项 | Completed Items |  | |
| 待办事项 | To Do Items |  | |
| 我的待办 | My To-Do |  | |
| 我的流程 | My process |  | |
| 流程中心 | Process Center |  | |
| 流程管理器 | Process Manager |  | |
| 流程配置 | Process configuration |  | |

### 流程与审批 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| OA审批完成才可推送 | OA approval is required before push | 审核, Approval, Approve, 签批 |
| 任务名称 | Task name |  |
| 加工贸易手册编号 | Processing Trade Manual Number |  |
| 加工费 | Added Value |  |
| 发起审批 | Initiate approval | 审核, Approval, Approve, 签批 |
| 委托加工费 | Commissioned Added Value | 加工, Conversion, Subcontracting, 外协加工, 委外加工 |
| 审批记录 | Approval history | 审核, Approval, Approve, 签批 |
| 审批进度 | Approval progress | 审核, Approval, Approve, 签批 |
| 当前处理日期 | Current processing date |  |
| 撤回审批 | Withdraw approval | 审核, Approval, Approve, 签批 |
| 撤销审批 | Revoke approval | 审核, Approval, Approve, 签批 |
| 进行中 | in progress |  |

### 流程与审批 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `claimReportState_2` | In process | In Process |
| `processingMessageLevel_1` | 信息 | Information |
| `approvalStatus_10` | 冲销 | Reversal |
| `approvalStatus_4` | 初始状态 | Initial |
| `processingTaskStatus_1` | 处理中 | Processing |
| `approvalStatus_21` | 处理中 | In Progress |
| `processingTaskStatus_3` | 失败 | Failure |
| `approvalStatus_2` | 审批中 | In Approval |
| `approvalStatus_9` | 审批完成 | Approval Completed |
| `approvalStatus_20` | 审核中 | In Review |
| `approvalStatus` | 审核状态 | Approval Status |
| `approvalStatus_23` | 已作废 | Void |
| `approvalStatus_12` | 已冲销 | Reversed |
| `approvalStatus_3` | 已审批 | Approved |
| `approvalStatus_19` | 已审核 | Reviewed |
| `approvalStatus_8` | 已提交 | Submitted |
| `approvalStatus_6` | 已撤回 | Revoked |
| `approvalStatus_15` | 已撤销 | Revoked |
| `approvalStatus_22` | 已生效 | Effective |
| `approvalStatus_16` | 已过账 | Posted |
| `approvalStatus_7` | 已驳回 | Rejected |
| `approvalStatus_13` | 待提交 | To Be Submitted |
| `processingTaskStatus_2` | 成功 | Success |
| `approvalStatus_11` | 未冲销 | Not Reversed |
| `noticeStatus_2` | 未处理 | Unprocessed |
| `approvalStatus_1` | 未审批 | Not Approved |
| `approvalStatus_18` | 未审核 | Not Reviewed |
| `approvalStatus_14` | 未提交 | Not Submitted |
| `approvalStatus_17` | 未过账 | Not Posted |
| `approvalStatus_5` | 流程中 | In Process |
| `processingTaskStatus_4` | 等待用户确认 | Waiting for user confirmation |
| `processingMessageLevel_3` | 警告 | Warning |
| `processingMessageLevel_2` | 错误 | Error |

---

## 10. 资金与银行 / Treasury & Banking

### 资金与银行 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| 利息单价（欧元/吨） | Interest（Eur/TO） | Interest, 利率 |
| 利息（欧元） | Interest(Eur) | Interest, 利率 |
| 开户银行 | Depositary bank |  |
| 计息天数 | Days of interest |  |
| 计息天数（新金属） | Interest Days（New metal） |  |

### 资金与银行 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `interestRules_2` | 30 / 360 | 30 / 360 |
| `interestRules_1` | Actual / 360 | Actual / 360 |
| `interestRules_3` | Actual / 365 | Actual / 365 |
| `interestTypes_1` | 固定 | Fixed |
| `dlFlags_1` | 存款 | Deposit |
| `mortgageFlags_1` | 抵押 | Mortgaged |
| `mortgageFlags_2` | 无抵押 | Unmortgaged |
| `interestTypes_2` | 浮动 | Floating |
| `lrFlags_2` | 租入 | Lease In |
| `lrFlags_1` | 租出 | Lease Out |
| `dlFlags_2` | 贷款 | Loan |

---

## 11. 系统对接 / System Integration

### 系统对接 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| 对接凭证 | Integration Credentials |  | |
| 对接日志 | Integration Log |  | |
| 对接配置 | Integration Configuration |  | |
| 系统对接 | System Integration |  | |

### 系统对接 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `groupSharing_2` | 不是集团共享 | Non-Group FSS |
| `source_4` | 共享同步 | FSS Synchronization |
| `groupSharing_1` | 是集团共享 | Group FSS |

---

## 12. 系统管理 / System Administration

### 系统管理 — 功能页面

| 中文术语 | 英文术语 | AI别名/口语表达 | 业务含义 |
|----------|----------|-----------------|----------|
| SQL配置 | SQL Configuration |  | |
| 个人中心 | Personal Center |  | |
| 任务列表 | Task List |  | |
| 任务调度 | Task Scheduling |  | |
| 单号配置 | Serial Configuration |  | |
| 单据模板管理 | Template Management |  | |
| 多语言维护 | Multilingual Maintenance |  | |
| 字典管理 | Dictionary Management |  | |
| 导入模板 | Import Template |  | |
| 执行日志 | Execution Log |  | |
| 报表管理 | Report Management |  | |
| 文件管理 | File Management |  | |
| 日志 | Log |  | |
| 消息中心 | Message Center |  | |
| 消息内容管理 | Message Content Management |  | |
| 消息管理 | Message Management |  | |
| 消息运维管理 | Message Operations Management |  | |
| 消息通知管理 | Message Notification Management |  | |
| 系统设置 | System Settings |  | |
| 系统运维 | System Operations |  | |
| 表单管理 | Form Management |  | |
| 规则引擎 | Rule Engine |  | |
| 规则管理 | Rule Management |  | |
| 透视表 | Pivot Table |  | |

### 系统管理 — 业务字段

| 中文术语 | 英文术语 | AI别名/口语表达 |
|----------|----------|-----------------|
| SQL 名称 | SQL name |  |
| 字典名称 | Dictionary name |  |
| 布局 | Layout |  |
| 所属字典 | Belongs to dictionary |  |

### 系统管理 — 状态/类型枚举值

| 系统Key | 中文值 | 英文值 |
|---------|--------|--------|
| `pivotGridControlTypes_5` | 下拉选择 | Dropdown Select |
| `gridShowTotals_2` | 不显示小计 | Hide Subtotals |
| `gridShowGrandTotals_2` | 不显示总计 | Hide Grand Totals |
| `gridShowTotals_3` | 仅在列显示小计 | Show Subtotals in Columns |
| `gridShowGrandTotals_3` | 仅在列显示总计 | Grand Totals in Columns |
| `gridShowTotals_4` | 仅在行显示小计 | Show Subtotals in Rows |
| `gridShowGrandTotals_4` | 仅在行显示总计 | Grand Totals Only in Rows |
| `dataSorts_1` | 升序 | Ascending |
| `pivotGridDataTypes_2` | 字符串 | String |
| `pivotGridControlTypes_8` | 年份 | Year |
| `gridTypes_2` | 扁平方式 | Flat |
| `pivotGridDataTypes_3` | 数字 | Number |
| `pivotGridControlTypes_1` | 日期 | Date |
| `pivotGridDataTypes_1` | 日期 | Date |
| `pivotGridControlTypes_2` | 日期-月 | Date-Month |
| `pivotGridControlTypes_9` | 日期区间 | Date range |
| `gridShowTotals_1` | 显示小计 | Show Subtotals |
| `gridShowGrandTotals_1` | 显示总计 | Show Grand Totals |
| `dataSorts_3` | 未设置 | Unset |
| `rangeTypes_3` | 相对 | Relative |
| `gridTypes_1` | 简洁方式 | Compact |
| `pivotGridControlTypes_3` | 系统日期 | System Date |
| `pivotGridControlTypes_4` | 级联选择 | Cascading Select |
| `gridTypes_3` | 经典方式 | Classic |
| `rangeTypes_2` | 绝对 | Absolute |
| `pivotGridControlTypes_6` | 输入框 | Input Box |
| `pivotGridControlTypes_7` | 输入框-数字 | Input Box-Number |
| `pivotGridDataTypes_4` | 金额 | Amount |
| `dataSorts_2` | 降序 | Descending |
| `rangeTypes_1` | 默认 | Default |

---

## 附录 A：AI 语义映射速查表

以下是用户在口语/自然语言中最常使用的表达与系统术语的映射关系，按使用频率排列。

| 口语/别名 | 系统中文术语 | 系统英文术语 |
|-----------|-------------|-------------|
| 公司 / 法人实体 / 交易主体 | 业务机构 | Business Entity |
| 部门 / 交易部门 / Trading Desk | 业务部门 | Business Department |
| 事业部 / 板块 / Division | 业务板块 | Business Segment |
| 对手方 / 交易对手 / 客户 / 供应商 | 客商 | Business Partner |
| 品种 / 产品 / 货物 / 物料 | 商品 | Article |
| 品种分类 / 产品类别 | 商品大类 | Article Category |
| 现货 / Spot | 现货订单 | Spot Order |
| 长协 / 年度合同 / LTA | 长协合同 | Long-term Agreement |
| 长协执行 / 长协下单 | 长协订单 | LTA Order |
| 定价 / 作价 / 确定价格 | 点价 | Fixation |
| 定价公式 / 价格公式 | 计价公式 | Pricing Formula |
| 定价市场 / 基准市场 | 作价市场 | Pricing Market |
| 溢价 / 贴水 / 升水 | 升贴水 | Premium/Discount |
| 入库 / 收货 / GR | 入库登记 | Good Receipt |
| 出库 / 发货 | 出库登记 | Good Release |
| 仓储 / 库 / Depot | 仓库 | Warehouse |
| 调拨 / 库存转移 | 移库 | Stock Transfer |
| 盘盈盘亏 / 库存调整 | 库存调差 | Inventory Adjustment |
| 月末结算 / 月结 / EOM | 库存月结 | Inventory Monthly Closing |
| 销项发票 / 开票 | 销售发票 | Sales Invoice |
| 进项发票 / 收票 | 采购发票 | Purchase Invoice |
| 付款 / 请款 | 付款申请 | Payment Application |
| 费用 / 杂费 | 费用记录 | Expense Record |
| DC Note / 借贷项 | Debit/Credit Note | Debit/Credit Note |
| 伦敦金属交易所 | LME | LME |
| 履约保证金 | 保证金 | Margin |
| 追加保证金 / Margin Call | 追保通知 | Margin Call Notification |
| 持仓 / 敞口 / 仓位 | 头寸 | Position |
| 对冲 / 套期保值 / Hedge | 套保 | Hedging |
| Swap / 互换 | 掉期 | Swap |
| L/C / 信用证 | 信用证 | Letter of Credit |
| Incoterms / 贸易条件 | 贸易术语 | Incoterms |
| 货币 / 交易币种 | 币种 | Currency |
| UOM / 计量 / 单位 | 计量单位 | Unit of Measure |
| 账期 / 付款条件 | 付款条款 | Payment Terms |
| 远期曲线 / Forward Curve | 结算曲线 | Settlement Curve |
| EOD / 日终 / 日结 | 日结操作 | End of Day |
| 加工 / 外协 / 委外 | 委托加工 | Conversion |
| 寄售 / Consignment / VMI | 供应商寄售 | Vendor Consignment |
| 索赔 / 理赔 | 索赔报告 | Claim Report |
| 审核 / 签批 | 审批 | Approval |
| 红冲 / 撤销 / Reversal | 冲销 | Write-off/Offset |
| 交割 / Delivery | 交割 | Delivery/Settlement |
| 风险敞口 / Exposure | 敞口 | Exposure |
| 信用额度 / Credit Limit | 授信额度 | Credit Limit |
| 信用评级 / Rating | 评级 | Credit Rating |
| 专票 | 增值税专用发票 | Special VAT Invoice |
| 普票 | 增值税普通发票 | General VAT Invoice |
| 暂估发票 / 预估发票 | 临时发票 | Provisional Invoice |
| 结算发票 | 最终发票 | Final Invoice |
| 预付 / Advance | 预付款 | Prepayment |
| 赊账 / 赊销 | 赊销 | Open Sale |
| OTC / 场外交易 | 场外 | OTC |
| 交易所内 / 场内交易 | 场内 | Ex Market |
| 建仓 / Open | 开仓 | Open Position |
| 了结 / Close | 平仓 | Close Position |
| 在险价值 / Value at Risk | VaR | %95 Single Day VaR |
| 盘点 / Stock Take | 库存盘点 | Inventory Count |
| 退货 / Sales Return | 销售退货 | Sales Return |
| 采购退回 | 采购退货 | Purchase Return |
| 完税 / Duty Paid | 完税 | Duty Paid |
| 保税 / Bonded | 保税 | Duty-free |
| 质押 / Pledge | 质押 | Mortgage/Pledge |
| Repo / 正回购 | 正回购 | Repurchase (S/B) |
| 逆回购 / 买入返售 | 逆回购 | Reverse Repurchase (B/S) |
| 仓单 / Warehouse Receipt | 仓单 | Warehouse Receipt |
| 内贸 / 国内贸易 | 内贸 | CN Trade |
| 外贸 / 国际贸易 | 外贸 | Global Trade |
| 租船 / Charter Party | 租船合同 | Charter Contract |
| 关联方 / 关联交易 | 关联方 | Related Party |
| 现货现款 | 现货现款 | Spot Cash |
| 仓单注销 / 注销仓单 | 仓单注销 | Warehouse Receipt Cancellation |

---

## 附录 B：核心业务状态枚举

### 合同类型 (Contract Types)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `contractTypes_1` | 长协合同 | Long-term Agreement |
| `contractTypes_2` | 长协订单 | LTA Order |
| `contractTypes_3` | 现货订单 | Spot Order |

### 审批状态 (Approval Status)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `approvalStatus_1` | 未审批 | Not Approved |
| `approvalStatus_2` | 审批中 | In Approval |
| `approvalStatus_3` | 已审批 | Approved |
| `approvalStatus_4` | 初始状态 | Initial |
| `approvalStatus_5` | 流程中 | In Process |
| `approvalStatus_6` | 已撤回 | Revoked |
| `approvalStatus_7` | 已驳回 | Rejected |
| `approvalStatus_8` | 已提交 | Submitted |
| `approvalStatus_9` | 审批完成 | Approval Completed |
| `approvalStatus_10` | 冲销 | Reversal |
| `approvalStatus_12` | 已冲销 | Reversed |
| `approvalStatus_13` | 待提交 | To Be Submitted |
| `approvalStatus_16` | 已过账 | Posted |

### 流程状态 (Flow Status)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `flowStatusTypes_1` | 发起审批 | Initiate Approval |
| `flowStatusTypes_2` | 新建 | New |
| `flowStatusTypes_3` | 审批中 | In Approval |
| `flowStatusTypes_4` | 审批通过 | Approved |
| `flowStatusTypes_5` | 审批驳回 | Rejected |
| `flowStatusTypes_6` | 生效 | Effective |
| `flowStatusTypes_7` | 虚拟合同 | Virtual Contract |

### 发票类型 (Invoice Types)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `invoiceTypes_1` | 临时发票 | Provisional Invoice |
| `invoiceTypes_2` | 最终发票 | Final Invoice |
| `invoiceTypes_3` | 费用 | Expense |
| `invoiceTypes_4` | Debit Note | Debit Note |
| `invoiceTypes_5` | Credit Note | Credit Note |
| `invoiceTypes_6` | 预收付 | Advanced Payment and Collection |
| `invoiceTypes_7` | 货款保证金 | Payment Margin |
| `invoiceTypes_8` | 信用证保证金 | Letter of Credit Margin |
| `invoiceTypes_9` | 海关增值税 | Customs VAT |
| `invoiceTypes_10` | 内贸发票-单据 | CN Invoice-Doc |
| `invoiceTypes_11` | 内贸发票-物资 | CN Invoice-Article |

### 客商合作类型 (Business Partner Cooperation Types)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `cooperationType_1` | 客户 | Customer |
| `cooperationType_2` | 供应商 | Supplier |
| `cooperationType_3` | 仓储 | Warehouse |
| `cooperationType_4` | 交易所 | Exchange Market |
| `cooperationType_5` | 期货公司 | Futures Brokers |
| `cooperationType_6` | 车船 | Vehicles/Vessels |
| `cooperationType_9` | 运输商 | Transportation Provider |

### 信用证状态 (Letter of Credit Status)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `lcStatus_1` | 未计划 | Unplanned |
| `lcStatus_2` | 计划 | Planned |
| `lcStatus_3` | 申请 | Applied |
| `lcStatus_4` | 登记 | Registered |
| `lcStatus_5` | 闭卷 | Closed |
| `lcStatus_6` | 交单 | Documents Presented |
| `lcStatus_9` | 承兑 | Accepted |
| `lcStatus_10` | 贴现 | Discount |
| `lcStatus_11` | 收付款 | Payment/Collection |

### 定价状态 (Pricing Status)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `pricingStatuses_1` | 浮动 | Floating |
| `pricingStatuses_2` | 固定 | Fixed |

### 头寸方向 (Position Direction)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `ocFlags_1` | 开仓 | Opening |
| `ocFlags_2` | 平仓 | Closing |
| `ocFlags_3` | 平今 | Close Today |
| `ocFlags_4` | 平昨 | Close Yesterday |

### 交易策略 (Trading Strategy)

| 系统Key | 中文 | 英文 |
|---------|------|------|
| `insuranceFlags_1` | 投机 | Speculation |
| `insuranceFlags_2` | 套保 | Hedging |
| `insuranceFlags_3` | 套利 | Arbitrage |

---

## 附录 C：统计摘要

| 类别 | 数量 |
|------|------|
| 功能页面术语 | 261 |
| 业务字段术语 | 3123 |
| 状态/类型枚举值 | 493 |
| AI语义映射条目 | 72 |
| 业务模块分类 | 12 |
