# IC 订单采购端 Credit/Debit Note 生成接口文档

## 1. 接口概述

### 1.1 接口名称

IC 订单采购端 Credit/Debit Note 自动生成接口

### 1.2 接口用途

接收 SAP 推送的销售端 Credit/Debit note JSON 报文，系统自动解析报文数据并生成采购端对应的 Credit/Debit note

### 1.3 接口版本

V1.0

### 1.4 接口协议

HTTPS

请求方法：POST

## 2. 接口地址

**正式环境**：`https://api.xxx.com/api/docking/receiveIcDnDataToCtrm`

**UAT环境**: [http://10.152.160.11:8](http://10.152.160.11:8443/ctrm/api/zlgm/deal/getPhysicalDeals)[0](http://10.152.160.11:8443/ctrm/api/zlgm/deal/getPhysicalDeals)[0](http://10.152.160.11:8443/ctrm/api/zlgm/deal/getPhysicalDeals)[0](http://10.152.160.11:8443/ctrm/api/zlgm/deal/getPhysicalDeals)/api/docking/receiveIcDnDataToCtrm

## 3. 请求参数说明

### 3.1 请求头（Header）

|    参数名     | 必选 |  类型  |      示例值      |           说明           |
| :-----------: | :--: | :----: | :--------------: | :----------------------: |
| Content-Type  |  是  | String | application/json |      请求体数据格式      |
| Authorization |  是  | String | Bearer xxxxxxxx  | 接口访问令牌（按需配置） |

### 3.2 请求体（Body）

采用 JSON 格式，结构如下：

|  层级  |     参数名      | 必选 |     类型      |   示例值   | 长度限制 |                             说明                             |
| :----: | :-------------: | :--: | :-----------: | :--------: | :------: | :----------------------------------------------------------: |
| header |   invoiceDate   |  是  |    String     | 2026-03-12 |    10    |                 发票日期，格式为 YYYY-MM-DD                  |
| header |    postDate     |  是  |    String     | 2026-03-12 |    10    |                 过账日期，格式为 YYYY-MM-DD                  |
| header |   lastPayDate   |  是  |    String     | 2026-03-12 |    10    |               最后付款日期，格式为 YYYY-MM-DD                |
| header |   AccountType   |  是  |    String     |    ICA     |    3     |                     固定值范围：ICA / 空                     |
| header |      item       |  是  | Array[Object] |     -      |    -     |               调账明细列表，至少包含 1 条明细                |
| item[] |  dajustAmount   |  是  |    String     |    100     |    20    | 调整金额，支持小数（如 100.50），正数为 Debit，负数为 Credit（需确认规则） |
| item[] |   sapDnNumber   |  是  |    String     |   500360   |    20    |    SAP 端 Debit/Credit note 编号，唯一标识销售端调账单据     |
| item[] | sapDnLineNumber |  是  |    String     |     10     |    10    |        SAP 端调账单据行项目号，对应单张单据内的明细行        |

### 3.3 请求示例

```json
{
	"PayCDRequest": {
		"invoiceDate": "2026-03-12",
		"postDate": "2026-03-12",
		"lastPayDate": "2026-03-12",
		"AccountType": "ICA",
		"item": [
			{
				"dajustAmount": "100",
				"sapDnNumber": "500360",
				"sapDnLineNumber": "10"
			},
			{
				"dajustAmount": "100",
				"sapDnNumber": "600360",
				"sapDnLineNumber": "20"
			},
			{
				"dajustAmount": "100",
				"sapDnNumber": "700360",
				"sapDnLineNumber": "30"
			}
		]
	}
}
```

## 4. 响应参数说明

### 4.1 响应体（Body）

| 参数名  | 必选 |  类型  |  示例值  |                             说明                             |
| :-----: | :--: | :----: | :------: | :----------------------------------------------------------: |
|  code   |  是  | String |   200    | 响应码：200 - 成功，400 - 参数错误，500 - 系统异常，403 - 权限不足 |
| message |  是  | String | 操作成功 |                 响应描述，失败时返回具体原因                 |

### 4.2 成功响应示例

```json
{
	"code": "1",
	"message": "接收报文成功",
}
```

### 4.3 失败响应示例

```json
{
	"code": "-1",
	"msg": "参数错误：invoiceDate格式不符合要求（需为YYYY-MM-DD）",
	"data": null
}
```

## 5. 接口规则与约束

### 5.1 数据校验规则

1. 日期类参数（invoiceDate/postDate/lastPayDate）必须符合 YYYY-MM-DD 格式，且为有效日期（如 2026-02-30 视为无效）；
2. AccountType 仅支持配置的有效值（当前为 ICA），非有效值直接返回参数错误；
3. dajustAmount 仅允许数字和小数点（最多保留 2 位小数），非数值格式返回参数错误；
4. sapDnNumber + sapDnLineNumber 组合需保证唯一性，避免重复推送导致重复生成采购端单据；
5. item 列表不能为空，且每条 item 的必填参数（dajustAmount/sapDnNumber/sapDnLineNumber）不能为空。