---
type: Note
---
# 金属损益（Metal Result）及管报重构项目进度汇报及问题沟通

# 一、项目进度

## 1\.1 系统架构设计

金属损益模块整体架构如下：

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzNlZjAyY2IwMzk2ZTk4ZTUzYzg5ZmZhODI0ZmFmNDNfNjMyZTlhMGFkYjg1ZDQ0ODAwNWE5MGI2OWJiYjgzM2NfSUQ6NzY0NjcxMDI2MDU3MzMyNjMwNl8xNzgxMjI5NjEyOjE3ODEzMTYwMTJfVjM)

Metal result 系统结构图

为确保金属损益项目需求实现的准确性与稳定性，项目组采取“业务梳理 → 算例确认 → 基于CTRM系统数据手算验证 → 需求设计 → 开发实现 → 用户验证”的闭环推进思路。以业务数据为驱动、以算例为“标准”，确保每一计算环节均经过业务确认，最大程度降低后期需求变更与返工风险。

## 1\.2 目前Metal result开发进度总览，不包含管报重构

- 总任务数：73项

- 已完成：29项（开发测试\+需求完成14项进行中）

- 未开始：30项

- 总体进度：约 50%

已完成/进行中：

- ✅ 价格主数据管理（LME、Greenlist、Scorporo等）

- ✅ 净库存数量统计

- 🔄 净库存金额统计（需求已完成，开发中）

- 🔄 P\&L金额统计（需求进行中）

- ⏳ 审计版本报表统计（未开始）

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MWFhNDUzOWJjOWZjNzVkODU5ZTdmNjI1Njg4ZDJiZGNfOWQxNjdhNTUxYWZkZTgyNWIwYTZhMzUyNGNiNTcxZWRfSUQ6NzY0NjI5NDE3MjkwMzExNTk5MV8xNzgxMjI5NjEyOjE3ODEzMTYwMTJfVjM)

Metal Result 开发进度（截止2026年6月3日）

[✅任务管理](https://hailiang.feishu.cn/wiki/KKZDwpgkZiJ8lFkO9qWcLHnGnCg?base_hp_from=shared_record&table=blky2YEUcOuOf0ZD)

关键里程碑：



2026年4月EOM BASE DATA 系统数据与线下手算对比：

当前系统数据统计结果核对（以四月份数据为例）：

1、意大利、柏林工厂 未套期保值头寸数据与线下手工计算一致；

2、法国工厂 未套期保值头寸数据比线下数据多 2365\.2KG;（差异源自CRM单据数量增加）

3、门登工厂 数据存在较大出入；（差异源自西班牙头寸数据未参与计算）

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NjgzZDdkZDEzMmE4Yjg2ZDc1MTY5OTlkZTEzNGM1NDhfM2NlYzE1MzE2NjI1NzcxNDI5YzgzYzIyNDhmNjczZGVfSUQ6NzY0NzA0NzI0MTg3NDA2NjQxM18xNzgxMjI5NjEyOjE3ODEzMTYwMTJfVjM)

2026年4月EOM BASE DATA 系统数据与线下手算对比

## 1\.3 管报重构项目进度

- 基础数据（Margin部分）开发：6月30日

- 其余开发项：8月启动

- 系统上线：12月1日

- UAT测试：验证12月\&1月月结数据

- 验收时间：2027年1月31日

# 二、项目计划

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OTA5YmNlODllZDVjMTUzNTU5M2UxOGQzMTQxYmFkMTBfMDc4YWJmNTI0MWYyNGMxZThjZmQxMzA3Yjk2ZWM3OWNfSUQ6NzY0NjMwMDEzMTM1NjIxNjI5MF8xNzgxMjI5NjExOjE3ODEzMTYwMTFfVjM)

Metal Result 开发计划

## 2\.1 金属损益项目

## 2\.2 管报重构项目

审计版可以延后，管报重构提前

# 三、关键问题与建议方案

## 3\.1 Metal Result价格逻辑概览

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzM5MjgzNjM2ZDZmMWUwNGJmNjUxOTIxOTE1MjMyNjJfNDM0YWFhYzI3NDVjNDAyZTgwOTgxOTFkNGE0ZDlhYTlfSUQ6NzY0NjQxMDk5Mjk1MzI0ODcwMF8xNzgxMjI5NjEyOjE3ODEzMTYwMTJfVjM)

Metal Result 价格计算框架

Metal Result 价格逻辑概览

## 3\.2 采购订单升贴水（Premium/Discount）报表

**现有业务逻辑：**

- 升贴水计算公式：`Unit discount + ``Interest`` - Transportation`

    - Unit discount：固定值或百分比（订单签订日 LME × 百分比）。区分金属类型：New metal 取 LME Cash；Scrap 取 LME Lowest。

    - Interest：`4% ÷ 365 × Payment Days × Metal Value`

    - Transportation：根据贸易术语取固定单价

- 升贴水需在采购订单中由业务人员手工录入，系统据此生成升贴水报表。

**需要确认的问题：**

采购人员订单中会有忘记录入升贴水的情况，或者系统不支持复杂升贴水，导致用户录入订单缺失升贴水的情况，报表无法取到某些订单的升贴水。

业务如何管理和核对升贴水缺失？是否需要倒算升贴水的方式（例如根据合同金额与LME价格反推）？

复杂升贴水场景（固定升贴水 \+ 百分比升贴水），正在设计开发中。



## 3\.3 Greenlist 市场公允采购价

**现有业务逻辑：**

- 原材料：`Greenlist = LME + Discount`

    - 月底 LME：New metal 取 LME Cash；Scrap 取 LME Lowest

    - Discount：根据最近一个月收货数量和订单升贴水加权平均计算

- 半成品/成品：月底 `Scorporo Price`（配方成本 \+ 销售加价）

- 支持特殊规则和手动调整。

**需要确认的问题：**

1. 加权平均 Discount 的计算窗口期是否固定为“最近一个月”如何理解？EIRC：如果当月没有则找上个月的收货记录。

手动调整的依据和逻辑是什么。



## 3\.4 LME Equivalent（LME折算价）

**现有业务逻辑：**

- 公式：`LME Equivalent = Σ(Yield × LME × Composition)`

- 取月底的 LME Cash 价格。

**需要确认的问题：**

1. Yield 和 Composition如何取值？Eric:取工厂的质检类型数据。 Yiled:金属回收率/出水率

2. 回料（Recycle）和废料（Residules）如何取值？



## 3\.5 Delta of Greenlist and LME（价差）

**现有业务逻辑：**

- `Delta = Greenlist - LME Equivalent`（Greenlist 与 LME 的价差）

**需要确认的问题：**

1. Delta 是商品的维度，Adder是元素的维度，Adder通过当月的收货拆分得到，两者关系如何定义更简便？



## 3\.6 WAV of Base Metal（采购加权平均成本）

**现有业务逻辑：**

- 累计采购入库成本 = 上月剩余库存成本 \+ 本月采购入库成本 → 得到金属成本单价

- 月底剩余库存成本 = 金属单价 × 月底剩余库存数量

- 支持盘库更新月底剩余库存数量。

**数据示例：**



**需要确认的问题：**

1. 盘库更新是否需要系统自动更新计算的月底库存？Eric:一年2次，系统自动更新更好，但是手动更新也可以接受。



## 3\.7 本月采购成本（入库金属价值拆分）

**现有业务逻辑：**

- 数量：`收货数量 × Yield × 工厂金属组成`。特殊规则：如果金属数量 \> 10,000 吨，则减去 10,000 吨（Eric 公式）。

- 金额：按收货日期估值

    - 主成分：`金属价值 + 待收发票金额 - 非主成分金额`

    - 非主成分：入库日期，金属单价 × 金属组成

        - 原材料：非主成分金额 = 入库日期 `Σ(LME Cash × Yield× 金属组成)`

        - 半成品/成品：非主成分金额 = 入库日期 `Σ(Scorporo_金属 × Yield× 金属组成)`（Scorporo\_Cu、Scorporo\_Zn 等）

![Image](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZmI2YWNjYTUxMzNhMWNiN2EzMTYwNGEwYTNiZGZjZDNfOTJlMjNlZWE1MGU5ZDA2YTM3MWM1YmQ3MzI4MDllYzlfSUQ6NzY0Njc4MDMwMjIwMjkzMjE3M18xNzgxMjI5NjExOjE3ODEzMTYwMTFfVjM)

本月采购成本拆分金属计算逻辑

**数据示例：**

[Wav \& Adder HBF 202603](https://hailiang.feishu.cn/wiki/LReqwB1xTiP0B6kfnrjcWVnAnjR?sheet=7H3V4T)

**需要确认的问题：**

1. “金属数量 \> 10,000 吨减去 10,000 吨”规则是否适用于所有金属？10,000 吨是固定值还是按金属不同？Eric:都按10000吨考虑。目的是什么？

行业中存在长单合同，超过年度协议量后价格另议，故需减除超额部分。

2. 主成分与非主成分的拆分依据是质检含量最高元素

3. 为什么半成品/成品采用了Scorporo\_金属计算非主成分金额

AI解读：因为半成品/成品的非主成分金属（如黄铜中的铅、锌）已包含在配方成本中，若用LME会重复计价，故采用Scorporo\_金属价格更合理。





## 3\.8 ADDER of Base Metal（元素维度精废价差）

**现有业务逻辑：**

- 当月收货：`ADDER = (主成分的 Adder 求和 - 半成品&成品 Margin 金额) / 主成分数量`

- Adder 本质是月底 Greenlist 与 LME 的价差，价差只分配到主成分上：`Σ(Adder × 主成分数量)`

- 只计算本月，不累计。

**数据示例：**

当月收货示例：

Total Adder计算：

||Total ADDER|Total Qty|Adder单价|
|---|---|---|---|
|ZN|3733\.687907||0\.043711886|
|CU|\-187\.0476564|12530\.46701|\-0\.014927429|





**需要确认的问题：**

1. 为什么 Adder 只计算本月而不累计（与 WAV 不同）？业务上如何解释？

AI解读：Adder反映的是当月市场精废价差的真实水平，用于减值测试中的可变现净值（NRV）。若累计计算，会模糊当期市场信号，不利于及时计提减值。WAV是成本概念，需要累计；Adder是市场价格概念，使用当月值更符合谨慎性原则。

2. 半成品\&成品的 Margin 金额是 3\.9 中 Margin 的影响

3. Delta 是商品的维度，Adder是元素的维度，Addert通过当月的收货拆分得到，两者关系如何定义更简便？

4. Adder只计算主成分占的数量，似乎把其他成分的数量影响金额漏掉了，是否正确？

AI解读：精废价差通常由主成分金属驱动（如铜废料按含铜量定价），非主成分金属的价差波动较小，且已通过非主成分金额计算体现。因此只将Adder分配到主成分上是行业惯例。

## 3\.9 Margin（半成品/成品销售加价）的计算

**现有业务逻辑：**

- Margin数据维护：类似于 Scorporo 价格管理。未来只存在一个 Margin 值（不区分固定与变动），不一定每日调整。EOD 时若无新上传，则沿用上一日价格。

- 对 Adder 的影响：仅针对半成品和成品。

    - 手工计算方式：`Σ(月底 Margin × Alloy 本年度所有入库数量) / Σ(Alloy 本年度所有入库数量) × 本月主成分数量` → 得到调减金额。不考虑上年度剩余库存，采用本年度平均 Margin × 本月主成分数量。

    - 系统建议逻辑：与 WAV 和 Adder 类似，每月在入库行层面计算当月月底 Margin，计算 `Margin × 入库数量`。单独出具报表，统计 `Σ(Margin × 入库数量) / Σ入库数量 × 主成分数量` 作为调减金额。若 Margin 变动，每月单独计算后累加。

**数据示例：**

**需要确认的问题：**

1. 系统应采用手工计算方式还是建议逻辑？建议逻辑与 WAV 保持一致（逐月累加），更符合会计连贯性原则。

2. Margin 是否应纳入月底最终库存估值调减？





## 3\.10 待收发票金额（Credit/Debit to be received）的部分开票处理

**现有业务逻辑：**

- 场景一（发生点价，金额部分开票）：
`Credit/Debit to be received = 点价金额 - 已开票金额`

- 场景二（未发生点价，金额部分开票）：
`Credit/Debit to be received = 月底定价公式价格 - 已开票金额`（优先使用点价，否则用月结定价规则，而非暂估价格）

- 订单关闭后，`Credit/Debit to be received = 0`。

**典型场景示例：**

- 铜精矿采购，点价前暂估价$8000/吨，收货100吨，发票开50吨，单价$7900。

    - 已开票金额 = 50×7900 = $395,000

    - 点价后最终价$8200/吨，点价金额 = 100×8200 = $820,000

    - Credit/Debit = 820,000 \- 395,000 = $425,000（待收）

- 若订单关闭（收货完成、发票结清、款项两清），则该金额归零。



**需要确认的问题：**

- 系统计算出 `Credit/Debit ≠ 0` 时，若操作关闭订单，该金额归零。什么情况下会关闭订单？是业务实际完成（如收货完成、发票结清）还是人为强制关闭？为什么要关闭？关闭后是否可逆？

- 如何让采购团队更好地确认这一场景涉及的金额？确认截止时间？未确认时的默认值策略？



## 3\.11 实物库存减值测试

**现有业务逻辑：**

- `库存价值 = Σ月底实物库存金属占比 × MIN(WAV, Comparable Price)`

- 按金属维度（CU, ZN, PB, NI）分别计算。

**数据示例：**



**需要确认的问题：**

1. 为什么要进行减值测试？符合IFRS 孰低计量原则

AI解读：

行业补充：根据IAS 2存货，存货应按成本与可变现净值（NRV）孰低计量。NRV的估计需考虑：

- 完工成本（半成品适用）

- 销售费用

- 市场售价：对于金属，通常取LME Cash \+ 精废价差（Adder）

当Adder无法获取时（本月无该金属入库），采用Scorporo价格作为替代市场价，因其包含了基础金属成本与加工费，更接近实际可回收金额。

减值测试结果：差额部分计入资产减值损失，推送至SAP生成会计凭证。





## 3\.12 Comparable Price（可比价格）

**现有业务逻辑：**

- `Comparable Price = LME Cash + ADDER of Base metal`

- 若 `ADDER = 0`（本月无主成分为该金属的入库），则调整为用月底 Scorporo 价格来评估（紫铜业务中，Ni、Zn 等金属适用）。



**会议备注：**

Scorporo Price：中文含义为标准配方成本价；

Yield ：金属回收率

**待办问题：**

- 升贴水录入规范：需规范价格录入方式；

- Greenlist 手工调整：需确认调整依据，支持备注调整说明；

- Wav 总价差=净重\*adder单价；需调整；

**需要确认的问题：**

1. 为什么要用Scorporo 价格替换？（例如：铜取 `Scorporo_Cu`，锌取 `Scorporo_Zn`）

    市场的价差没有取到情况，采用Scorporo 价差来替代

2. 升贴水明细表：利息计算符号问题，应该是减；运费符号问题，应该是加（需和eric确认）；









