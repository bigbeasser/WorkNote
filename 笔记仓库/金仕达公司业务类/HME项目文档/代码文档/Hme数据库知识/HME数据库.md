# HME数据库

## HME一些专有名词和方法

> [!tip] 寻找金属价的方法
> 先找到商品，再找最上层的父商品：
> 1. 例如 6004136 商品，它的父商品 → C33 → C34
> 2. 去合约文本里按照名字 C34 去搜索出合约文本
> 3. 取每日市场行情，根据合约文本和时间找对应金属价   



# 数据库表名和关系

> [!info] 脚本地址
> - **新增量脚本地址**：`\\10.253.47.221\部门文件\产业金融产品部\CTRM产品组\海亮\hme\v8-20240604`
> - **前端开发**：v8 wb 文件地址同上
> - **后端开发**：全量更新的配置表有，不需要增量脚本

### 配置表清单

| 分类 | 表名 | 说明 |
| :---: | :--- | :--- |
| **字典** | `admindb.sys_dict` | 字典主表 |
| | `admindb.sys_dict_detail` | 字典明细 |
| **动态表单** | `systemdb.web_forms` | 表单 |
| | `systemdb.web_from_panels` | 表单面板 |
| | `systemdb.web_from_attributes` | 表单属性 |
| **出入库配置** | `systemdb.document_actions` | 单据动作 |
| | `systemdb.document_action_items` | 单据动作明细 |
| **计价公式** | `systemdb.pricing_formulas` | 计价公式 |
| | `systemdb.event_type` | 事件类型 |
| | `systemdb.pricing_range_rules` | 区间规则 |
| **国际化** | `systemdb.lang_resources` | 多语言资源 |
| **透视表** | `systemdb.pivotgrid` | 透视表 |
| | `systemdb.pivotgrid_field` | 透视表字段 |
| | `systemdb.pivotgrid_sql` | 透视表SQL |
| **导入模板** | `systemdb.template_config` | 模板配置 |
| | `systemdb.template_config_row` | 模板行 |
| | `systemdb.template_config_column` | 模板列 |

### 期货表

| 表名 | 说明 |
| :--- | :--- |
| `futures_record` | 成交流水 |
| `forward_curve` | 合约文本 |
| `forward_contract` | 合约管理 |
| `publication` | 作价市场 |
| `forward_price` | 每日市场行情 |

## 合约之间的关系

成交流水   futures\_record

合约文本   forward\_curve

合约管理   forward\_contract

作价市场    publication

每日市场行情  forward\_price

合约文本 对应多个 合约管理   使用商品最顶端的父商品id \+ 业务机构id在publication对应的作价市场id = 订单唯一的合约文本

每日市场行情 对应一个合约管理 对应一个合约文本  对应一个作价市场

交割日的日期 在合约管理里面是一一对应的,一个合约管理只有一个交割日,开始交易日和最后交易日是一段时间

\(也就是一个合约文本通过交割日,在一年里拆分成多个合约管理 ,在每日市场行情里分别负责每天的价格体现\)



## 业务部门，业务机构，业务板块, 交易对家（客户公司）

> [!note] 组织维度表对照
> | 维度 | 字段名 | 表名 |
> | :---: | :--- | :--- |
> | 业务机构 | `legal_entity_id` | `admindb.sys_company` |
> | 业务部门 | `portfolio_id` | `admindb.sys_department` |
> | 业务板块 | `business_segment_id` | `admindb.sys_business_segment` |
> | 交易对家 | `counterparty_id` | `admindb.counterparty` |
> | 制单人 | `created_by` | `wolf.wb_user` (通过 USER_NAME 关联) |

```Plain Text
legal_entity_id              bigint           null comment '业务机构',
portfolio_id                 bigint           null comment '业务部门',
business_segment_id          bigint           null comment '业务板块',
counterparty_id              bigint           null comment '交易对家',
```



```Plain Text
LEFT JOIN admindb.sys_company com ON main.legal_entity_id = com.`ID`

LEFT JOIN admindb.sys_department dept ON c.portfolio_id = dept.ID

LEFT JOIN admindb.sys_business_segment sbe ON p.business_segment_id = sbe.id



LEFT JOIN admindb.sys_company sc ON ds.legal_entity_id = sc.ID
LEFT JOIN admindb.sys_department sd ON ds.portfolio_id = sd.ID
LEFT JOIN admindb.sys_personnel sp ON sp.id = ds.trader_id
LEFT JOIN admindb.sys_business_segment sbe ON sbe.id = 
                ds.business_segment_id
 lEFT JOIN admindb.counterparty c1 ON ds.counterparty_id = c1.id
```



## 关于Document表

- offset\_flag   是否冲销

### 入库登记的单据筛选

```Plain Text
select * FROM documents doc
WHERE doc.inactive_flag = 0
  AND doc.document_number LIKE CONCAT('%', 'PR20230830_00010', '%')
  AND ((doc.action_id = 42 AND (doc.bill_flag = false or doc.bill_flag is null)) 
        or doc.action_id = 56)
```

### 出库登记的单据筛选

```Plain Text
select * FROM documents doc
WHERE doc.inactive_flag = 0
 WHERE doc.inactive_flag = 0
  AND doc.action_id = 41



出入库登记一起查询的
AND (((ds.action_id = 42 AND (ds.bill_flag = false or ds.bill_flag is null)) or ds.action_id = 56)  
or ds.action_id = 41)
```



### 查询合同下出入库登记的数量 并且是减去冲销的

```Plain Text
select sum(case when doc.offset_flag = 'N' then doci.quantity END) -  sum(case when doc.offset_flag = 'Y' then doci.quantity END)
from documents doc
         left join document_items doci on doc.id = doci.document_id
where doc.inactive_flag = false
  and doci.inactive_flag = false
  and doc.action_id in (41, 42)
  and doci.rd_flag = 'D'
  and DATE_FORMAT(doc.title_transfer_date, '%Y-%m-%d') >= DATE_FORMAT('2023-10-01', '%Y-%m-%d')
  and DATE_FORMAT(doc.title_transfer_date, '%Y-%m-%d') <= DATE_FORMAT('2023-10-18', '%Y-%m-%d')
  and doc.physical_deal_id = 3836308553072640
```



## Document\_items表

- offset\_quantity

- rd\_flag  收发方向    W       D   

```Plain Text

// 出入库冲销，（除拣配之外）
D("D",2),
// 拣配
W("W", 3)
```

### 出库通知和拣配明细的对应关系

**而且在出库通知单据上是一条出库通知对应一条减配明细  ，对应关系 而且拣配明细行上的link\_document\_id对应的是出库通知明细单据的id  **



### 关于拣配明细对应的物资明细

拣配明细的source\_document\_item\_id

## rdd物资明细表 receipt\_delivery\_details

> [!note] 物资明细字段解释
> | 字段 | 说明 |
> | :--- | :--- |
> | `header_number` | 单据主表上的单据号（documents 上的 document_number） |
> | `action_id` | 单据主表的类型（出入库登记、出入库通知、出入库计划） |
> | `header_type` | 合同表的类型（PO/SO/LP/LA/LR） |
> | `link_id` | 两条 document 主表 id，一条合同主表 physical_deals 的 id |
> | `contract_number` | 合同主表的合同号 |
> | `receipt_delivery_status` | 库存量消耗=2，合同量消耗=1 |
> | `receipt_deliver_type_id` | 收发货类型：1收货，2发货 |
> | `storage_statistics_type` | 仓库统计类型（1=总量库存，2或空=批次） |
> | `warehouse_type_id` | 库存类型：1现货，2仓单 |



## physical\_deals和physical\_deal\_line

合同表和现金流的关系

```Plain Text
cashflow_model_header_values cmhv
LEFT JOIN cashflow_model_values ON cmhv.cashflow_model_header_value_id =
cashflow_model_values.cashflow_model_header_vaule_id
LEFT JOIN storage_facility ON storage_facility.id = cmhv.storage_id
LEFT JOIN product ON product.id = cmhv.product_id
left join physical_deals dl ON cmhv.physical_deal_id = dl.id
LEFT JOIN physical_deal_line phl ON cmhv.physical_deal_id = phl.physical_deal_id
AND cmhv.line_number = phl.line_number
```

### 判断周期合同和月度计划的查询标志

```Plain Text
月度执行计划
  AND p.contract_type <> 'WarehouseReceipt'
  AND p.long_term_contract_number IS NOT NULL
  AND p.contract_type in ('LongTerm', 'ShortTerm')
  
  

  周期合同
  AND p.contract_type <> 'WarehouseReceipt'
  AND p.contract_type in ('LongTerm', 'ShortTerm')
  AND p.long_term_contract_number IS NULL
```

### 执行月都计划查询的时候需要再自关联上physical\_deal

```Plain Text
FROM physical_deals p
LEFT JOIN physical_deal_line pl ON p.id = pl.physical_deal_id 
  AND pl.inative_flag = 0
LEFT JOIN physical_deals cycle_pd ON cycle_pd.id = p.long_term_contract_number
```



## 关于人员查询的表（创建人，业务员，部门，业务机构）分布表

```Plain Text
LEFT JOIN admindb.sys_company com ON p.legal_entity_id = com.`ID`
         LEFT JOIN admindb.sys_department dept ON p.portfolio_id = dept.`ID`
         LEFT JOIN admindb.counterparty cp ON p.counterparty_id = cp.id
         LEFT JOIN admindb.sys_personnel sp ON sp.id = p.trader_id
         LEFT JOIN wolf.wb_user cb ON cb.USER_NAME = p.created_by
         LEFT JOIN wolf.wb_user ub ON ub.USER_NAME = p.updated_by
```



## 结算单据settlement

### 结算单据有中间表 settlement\_cash\_flow

1. cashflow\_model\_value\_id   

2. settlement\_id

3. physical\_deal\_id



### 通过结算单找出入库登记的单据如下

```Plain Text
FROM cashflow_model_header_values cmhv
             LEFT JOIN cashflow_model_values ON cmhv.cashflow_model_header_value_id =
              cashflow_model_values.cashflow_model_header_vaule_id
             LEFT JOIN receipt_delivery_details ON cmhv.receipt_delivery_id = receipt_delivery_details.receipt_delivery_id
             LEFT JOIN document_items doci ON doci.id = receipt_delivery_details.header_id
             LEFT JOIN documents ds ON ds.id = doci.document_id
             left join settlement_cash_flow scf
                       on scf.cashflow_model_value_id = cashflow_model_values.cashflow_model_value_id
             left join settlement on settlement.id = scf.settlement_id
    where   scf.inactive_flag = 0
            and ds.inactive_flag = 0
```



## 现金流模型表的查询

**cashflow\_model\_values**是子表   **cashflow\_model\_header\_values**是主表

```Plain Text
FROM cashflow_model_header_values
    LEFT JOIN cashflow_model_values ON cashflow_model_values.cashflow_model_header_vaule_id =
    cashflow_model_header_values.cashflow_model_header_value_id
    LEFT JOIN receipt_delivery_details ON cashflow_model_header_values.receipt_delivery_id =
    receipt_delivery_details.receipt_delivery_id
    LEFT JOIN document_items ON document_items.id = receipt_delivery_details.header_id
    LEFT JOIN document_properties dp ON dp.document_item_id = document_items.id
    AND dp.property_id = 1
    LEFT JOIN product_properties_value ppv ON dp.property_value_id = ppv.id
    LEFT JOIN document_properties dp2 ON dp2.document_item_id = document_items.id
    AND dp2.property_id = 3
    LEFT JOIN product_properties_value ppv2 ON dp2.property_value_id = ppv2.id
    LEFT JOIN product ON product.id = document_items.product_id
    LEFT JOIN settlement_cash_flow s ON s.cashflow_model_value_id = cashflow_model_values.cashflow_model_value_id
    AND s.inactive_flag = 0
    left join settlement on s.settlement_id = settlement.id
    left join invoice_documents on invoice_documents.cashflow_model_value_id =
    cashflow_model_values.cashflow_model_value_id and invoice_documents.inactive_flag = 0
```

**注意：现金流模型是针对于合同的维度**



### cashflow\_model\_header\_values字段

- physical\_deal\_id

- detail\_number 

- receipt\_delivery\_id

- header\_id

- contract\_number

### cashflow\_model\_values字段

> [!note] 关键字段
> | 字段 | 说明 |
> | :--- | :--- |
> | `settlement_net_price` | **总价字段** |
> | `settlement_price` | **单价字段** |
>
> **注意**：统计合同的**总金额**需要把 `settlement_net_price` 字段进行 `SUM()` 求和



## 收付款登记receipt和收付款认领receipt\_claim

receipt是主表对应多个receipt\_claim\.receipt\_id  

## 关于商品和规格，品牌的关联关系

```Plain Text
FROM  document_properties dp
LEFT JOIN systemdb.product_properties pp ON dp.property_id = pp.id
LEFT JOIN systemdb.product_properties_value ppv ON dp.property_value_id = ppv.id
WHERE dp.inactive_flag = 0
and dp.document_item_id IN
```

## 经常关联的表

```Plain Text
FROM
cashflow_model_header_values cmhv
LEFT JOIN cashflow_model_values ON cmhv.cashflow_model_header_value_id =
cashflow_model_values.cashflow_model_header_vaule_id
LEFT JOIN storage_facility ON storage_facility.id = cmhv.storage_id
LEFT JOIN product ON product.id = cmhv.product_id
left join physical_deals dl ON cmhv.physical_deal_id = dl.id
LEFT JOIN physical_deal_line phl ON cmhv.physical_deal_id = phl.physical_deal_id
AND cmhv.line_number = phl.line_number
LEFT JOIN tax_code_rate on tax_code_rate.tax_code_id = phl.tax_code_id
LEFT JOIN receipt_delivery_details ON cmhv.receipt_delivery_id = receipt_delivery_details.receipt_delivery_id
LEFT JOIN document_items doci ON doci.id = receipt_delivery_details.header_id
LEFT JOIN documents ds ON ds.id = doci.document_id
LEFT JOIN document_properties dp ON dp.document_item_id = doci.id
AND dp.property_id = 1
LEFT JOIN product_properties_value ppv ON dp.property_value_id = ppv.id
LEFT JOIN document_properties dp2 ON dp2.document_item_id = doci.id
AND dp2.property_id = 3
LEFT JOIN product_properties_value ppv2 ON dp2.property_value_id = ppv2.id
LEFT JOIN unit ON cashflow_model_values.settlement_net_unit_id = unit.id
left join invoice_documents on invoice_documents.cashflow_model_value_id =
cashflow_model_values.cashflow_model_value_id and invoice_documents.inactive_flag = 0
```



业务部门表  admindb\.sys\_department   \-\- portfolio\_Id \-\- portfolioId

业务机构表 admindb\.sys\_company  \-\- legal\_entity\_id    \-\- legalEntityId

# 单据流转之终极sql

```Plain Text
SELECT *
FROM (
         SELECT d.action_id,
                d.document_number,
                d.id                                                                 warehouse_in_register_doc_id,
                di.id                                                                warehouse_in_register_doc_item_id,
                rdd.receipt_delivery_id                                              rdd_Id,
                !(ABS(IFNULL(di.quantity, 0) - IFNULL(freeze.quantity, 0) - IFNULL(realOut.quantity, 0) -
                      IFNULL(mortgage.quantity, 0) - IFNULL(rdd.quantity, 0)) < 0.1) result,
                ABS(IFNULL(di.quantity, 0) - IFNULL(freeze.quantity, 0) - IFNULL(realOut.quantity, 0) -
                    IFNULL(mortgage.quantity, 0) - IFNULL(rdd.quantity, 0))          result_quantity,  -- 单据量减去物资量
                (IFNULL(di.quantity, 0) - IFNULL(freeze.quantity, 0) - IFNULL(realOut.quantity, 0) -
                 IFNULL(mortgage.quantity, 0))                                       balance_quantity, -- 单据表的最后剩余量
                IFNULL(rdd.quantity, 0)                                              rdd_quantity,     -- 物资明细表的最后剩余量
                IFNULL(di.quantity, 0)                                               inNotice_quantity,
                IFNULL(freeze.quantity, 0)                                           freeze_quantity,
                IFNULL(realOut.quantity, 0)                                          out_quantity,
                IFNULL(mortgage.quantity, 0)                                         mortgage_quantity,
                IFNULL(rdd.block_number, 0)                                          rdd_block_number,
                IFNULL(di.block_number, 0)                                           doc_block_number,
                IFNULL(freeze.block_number, 0)                                       freeze_block_number,
                IFNULL(realOut.block_number, 0)                                      out_block_number,
                IFNULL(mortgage.block_number, 0)                                     mortgage_block_number
         FROM document_items di
                  LEFT JOIN documents d on di.document_id = d.id
                  LEFT JOIN receipt_delivery_details rdd on rdd.header_id = di.id
             -- 从39出库计划、40出库通知、50移库出库、54预拣配计算出出库冻结量 -->
                  LEFT JOIN (
             SELECT di.original_document_id,
                    SUM(
                            IF(
                                    doc.action_id = 50,
                                    IF(
                                        -- 移库出库初始状态为3，已提交为2，冻结数量计算已提交的移库出库单据明细数量 -->
                                            doc.status = 2,
                                            di.quantity - IFNULL(di.offset_quantity, 0) -
                                            IFNULL(str.matched_quantity, 0),
                                            0
                                        ),
                                    GREATEST(di.quantity - IFNULL(di.offset_quantity, 0) - IFNULL(di1.quantity, 0), 0)
                                )
                        ) AS quantity,
                    SUM(
                            IF(
                                    doc.action_id = 50,
                                    IF(
                                            doc.status = 2,
                                            di.block_number,
                                            0
                                        ),
                                    GREATEST(di.block_number - IFNULL(di1.block_number, 0), 0)
                                )
                        ) AS block_number
             FROM documents doc
                      LEFT JOIN document_items di
                                ON doc.id = di.document_id AND (doc.action_id IN (50, 54) or di.rd_flag = 'W')
                      LEFT JOIN (
                 SELECT source_document_item_id,
                        SUM(matched_quantity) AS matched_quantity
                 FROM stock_transfer_rela
                 GROUP BY source_document_item_id
             ) str ON di.id = str.source_document_item_id
                      LEFT JOIN (
                 SELECT source_document_item_id,
                        SUM(quantity - IFNULL(offset_quantity, 0)) AS quantity,
                        SUM(block_number)                          AS block_number

                 FROM document_items di
                 WHERE di.inactive_flag = 0
                 GROUP BY source_document_item_id
             ) di1 ON di.id = di1.source_document_item_id
             WHERE doc.inactive_flag = 0
               AND di.inactive_flag = 0
               AND (doc.offset_flag IS NULL OR doc.offset_flag = 'N')
               AND doc.action_id IN (39, 40, 50, 54)
             GROUP BY di.original_document_id
         ) freeze on di.id = freeze.original_document_id
             -- 从41出库登记、50移库出库、55库存调差计算出实际出库量 -->
                  LEFT JOIN (
             SELECT di.original_document_id,
                    SUM(
                            CASE
                                WHEN doc.action_id = 50
                                    THEN str.matched_quantity
                                ELSE di.quantity - IFNULL(di.offset_quantity, 0)
                                END
                        ) AS quantity,
                    SUM(
                            CASE
                                WHEN doc.action_id = 50
                                    THEN 0
                                ELSE di.block_number
                                END
                        ) AS block_number
             FROM documents doc
                      LEFT JOIN document_items di
                                ON doc.id = di.document_id AND (doc.action_id IN (50, 55) or di.rd_flag = 'W')
                      LEFT JOIN (
                 SELECT source_document_item_id,
                        SUM(matched_quantity) AS matched_quantity
                 FROM stock_transfer_rela
                 GROUP BY source_document_item_id
             ) str ON di.id = str.source_document_item_id
             WHERE doc.inactive_flag = 0
               AND di.inactive_flag = 0
               AND (doc.offset_flag IS NULL OR doc.offset_flag = 'N')
               AND doc.action_id IN (41, 50, 55)
               AND (doc.status = 2 OR doc.action_id != 55)
             GROUP BY di.original_document_id
         ) realOut on di.id = realOut.original_document_id
                  LEFT JOIN (
             SELECT *
             FROM (
                      SELECT y.quantity                                                                              quantity,
                             y.block_number,
                             y.source_document_item_id,
                             y.item_status,
                             y.created_time,
                             ROW_NUMBER()
                                     over ( PARTITION BY y.source_document_item_id ORDER BY y.CREATED_TIME desc ) AS rn
                      FROM document_items y
                               LEFT JOIN documents z on z.id = y.document_id
                      WHERE y.inactive_flag = 0
                        AND y.item_status in (9, 10)
                  ) t
             WHERE t.rn = 1
         ) mortgage on di.id = mortgage.source_document_item_id
             -- 从42入库登记、41出库登记、50移库出库、计算出实际件数块数 -->
                  LEFT JOIN (
             select di.original_document_id,
                    SUM(IF(d.action_id IN (41, 50) AND d.offset_flag != 'Y' AND di.offset_quantity IS NULL,
                           -di.block_number, di.block_number))   AS block_number,
                    SUM(IF(d.action_id IN (41, 50) AND d.offset_flag != 'Y' AND di.offset_quantity IS NULL,
                           -di.pieces_number, di.pieces_number)) AS pieces_number
             from documents d
                      LEFT JOIN document_items di ON di.document_id = d.id
             WHERE d.inactive_flag = 0
               AND di.inactive_flag = 0
               AND (d.offset_flag IS NULL OR d.offset_flag = 'N')
               AND d.action_id in (41, 42, 50)
             GROUP BY di.original_document_id
         ) AS blockPieces on di.id = blockPieces.original_document_id
         WHERE 1 = 1
           AND di.inactive_flag = 0
           AND d.inactive_flag = 0
           AND rdd.inactive_flag = 0
           AND d.action_id in (13, 42, 51)
           AND d.bill_flag = 0
           AND rdd.match_number is null
           -- AND d.document_number =
           -- AND di.id =
         order by d.action_id,
                  d.document_number
     ) t
WHERE 1 = 1
  -- balance_quantity: 可以设置小于0 来做筛选  result: 1 单据和物资不一致  0 一致
  AND (t.balance_quantity < 0 or t.result = 1)
```



# 数据权限问题表的追踪

> [!info] 权限相关表（wolf库）
> | 表名 | 说明 |
> | :--- | :--- |
> | `ks_role` | 角色表 |
> | `ks_function` | 功能表（通过 role_id 查找 qtip） |
> | `ks_role_function` | 角色功能关联表 |
> | `ks_menu` | 菜单表 |
> | `ks_user_role` | 用户角色关联表（通过 user_id 找 role_id） |
> | `wb_user` | 用户表（通过角色找到 user_id） |

> [!note] 权限校验原理
> 程序里的自定义注解 `@PreAuthorize("@el.check('document:info')")` 的实现逻辑：
> 1. 通过用户名找到用户 ID
> 2. 查到所有的 qtip
> 3. 检查 qtip 里面是否含有 `document:info` 这个关键词











## 查询数据库表状态

> [!tip] 常用查询命令
> 
> **查进程**
> ```sql
> SHOW PROCESSLIST;
> -- kill thread_id
> ```
> 
> **查事务**
> ```sql
> SELECT * FROM information_schema.INNODB_TRX;
> ```
> 
> **查看正在锁的事务**
> ```sql
> SELECT * FROM performance_schema.data_locks;
> ```
> 
> **查看等待锁的事务**
> ```sql
> SELECT * FROM performance_schema.data_lock_waits;
> ```
> 
> **查看表使用状态**
> ```sql
> SHOW OPEN TABLES WHERE In_use > 0;
> ```
> - `In_use`：表示该表当前有 N 个线程正在使用它
> - `Last_access`：自上次访问以来的时间（秒），0 表示即时访问



