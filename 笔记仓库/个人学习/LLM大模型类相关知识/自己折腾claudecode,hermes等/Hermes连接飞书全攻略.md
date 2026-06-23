# Hermes 连接飞书全攻略：从扫码入门到生产级自动化，踩坑经验一次讲透

> 打造你的专属 AI 助手，让飞书成为 AI Agent 的交互入口

---

## 开篇：为什么要把 Hermes 接入飞书？

想象一下这个场景：早上到公司，打开飞书，在项目群里 @机器人 发一条「**打包部署一下 UAT 后端**」，5 分钟后收到一张飞书卡片——「✅ UAT 发布完成，打包耗时 3 分钟，部署耗时 2 分钟，点击访问」。整个过程你只发了一条消息，剩下的打包、部署、验证、通知全部由 AI 自动完成。

这不是科幻，这是我日常工作流中每天都在跑的真实场景。

**Hermes** 是 Nous Research 开源的 AI Agent 框架，它像一个"万能插座"，能让 AI 大模型连接各种工具（终端命令、文件读写、网页搜索、API 调用等）。Hermes 通过 **Gateway（网关层）** 统一接入飞书、Telegram、Discord 等消息平台，再由 **Agent Core（核心引擎）** 驱动 LLM 进行推理和工具调度。

本文将从**扫码一键配置**到**生产级自建应用**，结合真实项目踩坑经验，帮你一篇文章搞定 Hermes 连接飞书。

---

## 一、架构概览：一条消息的完整旅程

在动手配置之前，先理解整体架构，这样遇到问题时你才知道该排查哪个环节。

```
用户在飞书群 @机器人
    ↓ ① 发送消息
飞书机器人 Bot
    ↓ ② 事件推送（WebSocket / Webhook）
飞书开放平台
    ↓ ③ 推送至 Gateway
Hermes Gateway（消息路由 & 分发）
    ↓ ④ 分发给飞书适配器
Feishu Adapter（解析消息、去重、批量合并）
    ↓ ⑤ 交给 Agent Core
AI Agent 核心引擎
    ↓ ⑥ 调用 LLM 推理 → ⑦ 按需调用工具 → ⑧ 读写记忆/会话
生成回复
    ↓ ⑨ 经适配器返回（Markdown → 飞书 Post 消息）
Gateway → 飞书 API 发送回复
    ↓ ⑩
用户在飞书看到回复
```

**核心组件速览**：

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **飞书机器人** | 用户在飞书中与之对话的 Bot | 开放平台创建，支持私聊和群聊 @ |
| **Gateway** | 统一网关，连接多种消息平台 | `hermes gateway` 命令管理 |
| **Feishu Adapter** | 飞书消息编解码、去重、批处理 | Gateway 内部组件，自动运行 |
| **Agent Core** | AI 对话循环 + 工具调度 | LLM 配置 + 工具集配置 |
| **Tools 工具集** | 终端命令、文件、搜索、飞书文档等 | 按需启用，建议白名单 |
| **Memory / Sessions** | 跨会话记忆和对话历史 | SQLite 持久化，重启不丢失 |

### 两种连接模式

Hermes 支持两种连接模式，**强烈推荐 WebSocket 模式**：

| 模式 | 原理 | 适用场景 | 依赖 |
|------|------|----------|------|
| **WebSocket** ⭐ | Hermes 主动建立出站 WebSocket 长连接 | 笔记本、工作站、私有服务器（无需公网 URL） | `pip install lark-oapi websockets` |
| **Webhook** | Hermes 启动 HTTP 服务器，飞书回调推送 | 已部署在可访问 HTTP 端点后的场景 | `pip install lark-oapi aiohttp` |

> ⚠️ **重要提醒**：同一时间只能有一个 Hermes 实例使用相同的 App ID。如果启动第二个实例会报错。

---

## 二、快速上手：扫码创建，3 分钟打通

### 方式 A：扫码创建（推荐 ⭐）

Hermes 官方提供了极简的扫码创建流程，一条命令搞定：

```bash
hermes gateway setup
```

选择「飞书 / Lark」，终端会显示一个二维码。用飞书手机端扫码，Hermes 会**自动创建具有正确权限的机器人应用**并保存凭据。无需手动去开放平台操作。

### 方式 B：手动配置

如果扫码不可用，按以下步骤手动完成：

#### 第 1 步：创建飞书应用

1. 打开 [飞书开放平台](https://open.feishu.cn)，用企业账号登录
2. 点击「创建企业自建应用」，填写应用名称
3. 左侧菜单 → **凭证与基础信息**，记录下：
   - **App ID**（格式：`cli_xxxxxx`）
   - **App Secret**（随机字符串）

> ⚠️ **坑 1**：App Secret 只在创建时显示一次，务必立即保存！忘记了只能重置。

#### 第 2 步：配置环境变量

在 `~/.hermes/.env` 中添加：

```bash
FEISHU_APP_ID=cli_xxxxxx
FEISHU_APP_SECRET=your_secret_here
FEISHU_DOMAIN=feishu           # feishu（中国）或 lark（国际版）
FEISHU_CONNECTION_MODE=websocket  # 默认 websocket，无需改动
```

> ⚠️ **坑 2**：`FEISHU_DOMAIN` 是 `feishu` 不是 `feishu.cn`！填错会导致 API 调用失败。

#### 第 3 步：启动 Gateway

```bash
hermes gateway
```

然后在飞书中找到你的机器人，发送「你好」。如果收到回复，基础通道已打通！

---

## 三、权限配置：最容易翻车的地方

很多同学卡在「机器人已读不回」「读不了文档」等问题上，**90% 是权限没配对**。

### 最简权限 JSON（直接复制导入）

在飞书开放平台 → **权限管理** → **批量导入**，粘贴以下 JSON：

```json
{
  "scopes": {
    "tenant": [
      "im:chat:read",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:resource",
      "docx:document",
      "wiki:wiki:readonly",
      "drive:drive",
      "docs:permission",
      "contact:user.base:readonly"
    ]
  }
}
```

覆盖了**消息收发 + 文档读写 + 知识库读取 + 云空间访问**。

### 权限完整对照表

| 功能 | 必需权限 | 说明 |
|------|----------|------|
| 收发私信 | `im:message.p2p_msg:readonly` + `send_as_bot` | 基础聊天 |
| 群聊 @机器人 | `im:message.group_at_msg:readonly` | 群聊中触发 |
| 发送图片/文件 | `im:resource` | 上传下载资源 |
| 读飞书文档 | `docx:document:readonly` | 读取文档内容 |
| 创建/编辑文档 | `docx:document:write_only` | 写入文档 |
| 读知识库 | `wiki:wiki:readonly` | 知识空间访问 |
| 云空间操作 | `drive:drive` | 上传/下载/搜索 |
| 文档权限管理 | `docs:permission.member:create` | 添加协作者 |
| 电子表格 | `sheets:spreadsheet` | 读写表格 |
| 日历/日程 | `calendar:calendar` | 日程管理 |
| 机器人信息 | `application:bot.basic_info:read` | 显示对端机器人名称 |
| 文档评论事件 | `drive.notice.comment_add_v1` | 文档评论智能回复（高级） |

### 权限生效的关键步骤（许多人漏掉）

权限申请通过后，**必须创建版本并发布**才能生效：

1. 开放平台 → 应用详情页 → 顶部「创建版本」
2. 填写版本号（如 `v1.0 - 基础消息和文档权限`）
3. **可用范围**：个人使用就仅选自己（免审批）
4. 提交发布

> ⚠️ **坑 3**：权限申请 ≠ 权限生效。没有发布版本，等于白配。

---

## 四、安全配置：生产环境必做

### 用户白名单

在 `~/.hermes/.env` 中设置允许使用机器人的用户：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

**空白名单意味着任何能访问机器人的用户都可以使用它**。生产环境务必设置。

### 群消息策略

```bash
# open      → 任何群成员均可使用
# allowlist → 仅白名单用户可用（默认）
# disabled  → 完全忽略群消息
FEISHU_GROUP_POLICY=allowlist
```

### Webhook 模式安全（如果使用 Webhook 模式）

```bash
# 加密密钥（签名验证）
FEISHU_ENCRYPT_KEY=your-encrypt-key

# 验证 Token（payload 认证）
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

两者可同时使用，实现纵深防御。

---

## 五、实战案例：从真实项目看一条消息的完整流转

下面以我的 **HME 项目「打包+部署一条龙」** 为例，完整展示一条飞书消息如何驱动整个 CI/CD 流程。这个案例已去敏处理。

### 触发阶段：用户在飞书群 @机器人

```
用户: @AI助手 打包部署 UAT 后端
```

### 阶段一：消息接收与路由

```
飞书客户端
  → 飞书开放平台（Event Subscription）
  → WebSocket 长连接推送到 Hermes Gateway
  → Feishu Adapter 接收事件
    ├── 消息去重（24h TTL，基于 message_id）
    ├── 突发保护（0.6s 内多条消息合并为一批）
    └── 解析消息内容 → "打包部署 UAT 后端"
  → 路由到 Agent Core
```

### 阶段二：Agent 处理流程

Agent 收到消息后，按以下步骤执行：

**① 发送开始通知**（飞书卡片，蓝色）

Agent 调用 `feishu_card.py` 脚本，给群聊发送一张卡片：
> 🚀 开始打包+部署 UAT
> 流水线: hmeback-后端-uat打包
> 分支: hme-uat
> 流程: 打包 → 部署

**② 触发流水线打包**

Agent 调用 terminal 工具执行打包脚本：
```bash
bash run_pipeline.sh <流水线序号> --no-notify
```

`--no-notify` 保证打包脚本本身不重复发通知，由 Agent 统一管理通知节奏。

**③ 轮询打包状态**

Agent 持续检查打包进度，如果失败 → 发送红色失败卡片，流程中止。

**④ 打包完成通知**（蓝色卡片）

> ✅ 打包完成
> 流水线: hmeback-后端-uat打包
> 分支: hme-uat

**⑤ SSH 到服务器执行部署**

Agent 通过 SSH 连接到目标服务器，执行部署脚本，然后轮询 HTTP 端口验证服务启动：

```bash
ssh -i ~/.ssh/id_ed25519 root@<服务器IP> "bash -l /home/deploy.sh"
# 轮询验证
curl -s -o /dev/null -w "%{http_code}" http://<服务器IP>:<端口>/
```

**⑥ 部署完成通知**（绿色卡片，带按钮）

> ✅ UAT 发布完成
> 流水线: hmeback-后端-uat打包
> 分支: hme-uat
> 耗时: 打包 3分 + 部署 2分
> [访问UAT]（可点击按钮直接跳转）

### 阶段三：回复渲染

Agent 的回复经过 Adapter 处理：
- Markdown 自动转为飞书 **Post 消息**（富文本渲染）
- 如果 Post 格式被飞书 API 拒绝 → 自动回退为纯文本（两阶段回退保证消息必达）
- 处理期间，用户消息上显示 "Typing" 表情回应，完成后自动清除

### 通知频率控制

| 阶段 | 是否通知 | 说明 |
|------|----------|------|
| 流程开始 | ✅ 1 条蓝色卡片 | 告知启动 |
| 打包中 | ❌ | 静默执行 |
| 打包完成 | ✅ 1 条蓝色卡片 | 阶段完成 |
| 打包失败 | ✅ 1 条红色卡片 | 流程中止 |
| 部署中 | ❌ | 静默执行 |
| 全部完成 | ✅ 1 条绿色/红色卡片 | 最终结果 |

**整个流程最多 3 条飞书通知**，避免刷屏。

---

## 六、核心功能详解

### 6.1 Home Chat：Cron 任务和系统通知的「消息中心」

在飞书中对机器人发 `/set-home`，将当前聊天设为 Home Chat。所有 Cron 定时任务结果和跨平台通知都会推送到这里。

也可以在 `.env` 中预配置：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

### 6.2 交互式卡片：不只是回复文字

Hermes 支持发送带按钮的交互式卡片。用户点击按钮后，事件回调到 Agent：

```
按钮点击 → /card button {"key": "value", ...}
```

**飞书端必须完成 3 项配置**（缺一不可，否则点击按钮时报 200340 错误）：

| 序号 | 配置项 | 位置 |
|------|--------|------|
| 1 | 订阅 `card.action.trigger` 事件 | 事件订阅 |
| 2 | 开启「交互式卡片」开关 | 应用功能 → 机器人 |
| 3 | 配置卡牌请求 URL | 应用功能 → 机器人 → 消息卡片请求网址（WebSocket 模式自动处理） |

> ⚠️ **坑 4**：卡片能正常发送，但按钮点击报 200340 → 一定是上述 3 项中的某项没配。

### 6.3 命令审批：危险操作二次确认

当 Agent 需要执行危险命令时，会发送一张带有「允许一次 / 本次会话 / 始终允许 / 拒绝」按钮的交互式卡片。用户点击按钮后，审批决定通过卡牌回调传回 Agent。

### 6.4 按群访问控制

可以为不同群聊设置不同策略：

```yaml
# ~/.hermes/config.yaml
platforms:
  feishu:
    extra:
      default_group_policy: "open"
      admins:
        - "ou_admin_open_id"
      group_rules:
        "oc_项目群ID":
          policy: "allowlist"
          allowlist:
            - "ou_dev_lead"
            - "ou_tech_lead"
        "oc_公开群ID":
          policy: "open"
        "oc_只读群ID":
          policy: "disabled"
```

支持的策略：`open`（全员可用）、`allowlist`（白名单）、`blacklist`（黑名单）、`admin_only`（仅管理员）、`disabled`（完全禁用）。

### 6.5 文档评论智能回复

除聊天外，Agent 还可以回复飞书文档中的 @ 提及。当用户在文档中选中文本并 @机器人时：
- Agent 自动读取文档内容和评论线程
- LLM 分析后以线程回复形式发布
- 按文档缓存会话（1 小时有效，最多 50 条消息）

需要额外订阅 `drive.notice.comment_add_v1` 事件，并授予 `docs:doc:readonly` 和 `drive:drive:readonly` 权限。

### 6.6 突发保护与去重

Hermes 内置了消息防抖和去重机制，避免压垮 Agent：

| 机制 | 默认值 | 说明 |
|------|--------|------|
| 去重 TTL | 24 小时 | 基于 message_id，持久化到文件 |
| 文本批处理延迟 | 0.6 秒 | 快速连续消息合并为单事件 |
| 每批最大消息数 | 8 条 | 超过则拆分为多批 |
| 每批最大字符数 | 4000 字符 | 超过则截断 |
| 媒体批处理延迟 | 0.8 秒 | 拖拽多张图片合并为单事件 |

---

## 七、踩坑实录：真实排障经验

### 坑 1：WebSocket 模式依赖缺失

**现象**：启动 Gateway 时报 `lark-oapi not installed` 或 `websockets not installed`

**解决**：
```bash
pip install lark-oapi websockets
```

如果使用 Webhook 模式，还需要：
```bash
pip install aiohttp
```

### 坑 2：机器人不响应群聊 @

**排查清单**（按顺序）：

1. 确认机器人被 @ 提到了（不是 @all）
2. 检查 `FEISHU_GROUP_POLICY` 是否为 `disabled`
3. 如果策略是 `allowlist`，确认发送者在 `FEISHU_ALLOWED_USERS` 中
4. 确认机器人已加入该群聊
5. 确认群聊设置中未禁用机器人

### 坑 3：读不了飞书文档，报 131003

**排查顺序**：
```bash
# 用 feishu-cli 测试权限
feishu-cli doc export <doc_token> --debug

# 错误码含义
# 131003 → 应用权限不足 → 加权限 + 发布版本
# 131001 → 文档不存在或无访问权 → 检查链接和访问权限
# 10019  → 用户自身没有该资源权限 → 先确认自己能打开文档
```

### 坑 4：交互式卡片按钮报 200340

**原因**：飞书端 3 项配置不全（见 6.2 节）

**快速验证**：卡片能发送 ≠ 配置正确。必须到开放平台逐项确认。

### 坑 5：Token 过期导致机器人突然不回复

**现象**：运行一段时间后机器人静默

**原因**：飞书 `tenant_access_token` 有效期 2 小时，Token 刷新失败会导致所有 API 调用失败。

**解决**：
- 确保 Hermes 版本最新（Token 自动刷新是内置逻辑）
- 重启 Gateway 强制重新获取 Token：`hermes gateway restart`
- 设置定时健康检查

### 坑 6：Post 消息显示为纯文本

**这不是 Bug**——这是正常的回退行为。当飞书 API 拒绝 Post payload（如不支持的 Markdown 语法）时，Hermes 自动回退为纯文本发送，保证消息必达。查看日志确认具体原因。

### 坑 7：服务器时区不匹配

**现象**：Cron 任务执行时间不对，日志时间显示混乱

**原因**：服务器 UTC+0，本地 UTC+8，时差 8 小时

**解决**：所有涉及时间的配置统一用 UTC，展示时转换。Cron 表达式确认时区。

### 坑 8：Webhook 模式被限流 429

**现象**：短时间内大量请求返回 HTTP 429

**原因**：Webhook 模式下每（app_id, path, IP）三元组每分钟最多 120 次请求。

**解决**：
- 检查是否有循环调用
- 批量操作增加延迟
- 考虑切换到 WebSocket 模式（无此限制）

---

## 八、常见错误码速查

| 错误码 | 含义 | 快速解决 |
|--------|------|----------|
| `131003` | 应用无权限 | 检查权限配置 + 版本发布 |
| `131001` | 资源不存在 | 检查文档链接/Token |
| `99991663` | 应用不存在 | 检查 App ID 是否正确 |
| `10003` | Token 无效 | App Secret 错误或应用被停用 |
| `10019` | 操作被拒绝 | 用户无该资源操作权限 |
| `10020` | 请求限流 | 降低频率，加延迟重试 |
| `200340` | 卡片按钮无权限 | 飞书端交互式卡片 3 项配置不全 |
| HTTP `401` | Webhook 签名/Token 校验失败 | 检查 `FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` |
| HTTP `429` | Webhook 请求过多 | 每分钟 >120 次，同一 IP |

---

## 九、进阶技巧

### 9.1 通知渠道管理：`hermes send`

无需 Gateway 运行、无需 LLM 调用即可从脚本发送飞书消息：

```bash
# 纯文本
hermes send --to feishu "构建完成"

# 带标题
hermes send --to feishu --subject "[CI]" "构建失败"

# 管道输入
cat /tmp/report.txt | hermes send --to feishu

# 发送图片
hermes send --to feishu "截图如下 MEDIA:/tmp/chart.png"

# 发送到指定群
hermes send --to feishu:oc_<群ID> "通知内容"
```

### 9.2 飞书卡片消息

```bash
python ~/.hermes/scripts/feishu_card.py \
  --title "🤖 任务完成" \
  --content "**任务**: 代码审查\n**状态**: ✅ 通过\n**文件**: 3个" \
  --color green \
  --field "**耗时**: 5分钟" \
  --button "详情|https://example.com"
```

### 9.3 LLM 模型选择建议

| 场景 | 推荐模型 | 理由 |
|------|----------|------|
| 日常对话/问答 | Claude Sonnet | 性价比高，响应快 |
| 代码审查/生成 | Claude Opus | 代码能力最强 |
| 长文档处理 | 支持长上下文的模型 | 200K token 上下文 |
| 轻量通知/脚本 | Claude Haiku | 成本极低，速度极快 |

### 9.4 扩展场景

| 场景 | 流程 |
|------|------|
| **智能运维** | 飞书 @机器人「查一下生产环境状态」→ SSH 执行检查 → 整理报告回复 |
| **自动部署** | 飞书 @机器人「打包部署 UAT」→ 触发流水线 → 部署 → 卡片通知结果 |
| **日志排查** | 飞书 @机器人「UAT 有什么报错」→ SSH 查日志 → 分类分析 → 关联 Git 提交 |
| **文档管理** | 飞书 @机器人「整理本周纪要」→ 搜索聊天 → 提取要点 → 创建飞书文档 |
| **定时巡检** | Cron 每天早上 9 点 → Agent 自动检查服务 → 异常推送到 Home Chat |

---

## 十、经验总结

### ✅ DO：应该做的事

1. **优先用 WebSocket 模式**：无需公网 URL，无需配置 Webhook，开箱即用
2. **设置用户白名单**：`FEISHU_ALLOWED_USERS` 空白等于全员可用，生产必设
3. **凭证用环境变量**：App Secret 写入 `~/.hermes/.env`，绝不硬编码或提交到 Git
4. **通知节奏控制**：整个自动化流程最多 3 条通知（开始、关键节点、结果），避免刷屏
5. **工具白名单**：terminal 工具配置 `allowed_commands`，禁止 `rm -rf` 等危险操作
6. **版本发布是最后一步**：权限申请完必须发布版本，否则不生效

### ❌ DON'T：不要做的事

1. **不要把 App Secret 传到 GitHub**：公开仓库泄露 = 任何人都能以你的应用身份操作
2. **不要同时启动两个实例**：同一 App ID 同时只能有一个 Hermes Gateway 运行
3. **不要跳过交互式卡片 3 项配置**：卡片发送成功 ≠ 配置正确，必须逐项确认
4. **不要在群聊中开放全员使用**：生产环境建议 `allowlist` 模式
5. **不要忽略时区问题**：Cron 和日志时间注意 UTC+0 与 UTC+8 的 8 小时差

---

## 十一、全部环境变量速查

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `FEISHU_APP_ID` | ✅ | — | 飞书 App ID |
| `FEISHU_APP_SECRET` | ✅ | — | 飞书 App Secret |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu`（中国）或 `lark`（国际版） |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket` 或 `webhook` |
| `FEISHU_ALLOWED_USERS` | — | 空 | 用户 open_id 白名单（逗号分隔） |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | `open` / `allowlist` / `disabled` |
| `FEISHU_HOME_CHANNEL` | — | — | Cron/通知输出的聊天 ID |
| `FEISHU_ENCRYPT_KEY` | — | — | Webhook 签名验证密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | — | Webhook payload 验证 Token |
| `FEISHU_ALLOW_BOTS` | — | `none` | 接受其他机器人消息：`none` / `mentions` / `all` |
| `FEISHU_REQUIRE_MENTION` | — | `true` | 群消息是否必须 @ 机器人 |
| `FEISHU_BOT_OPEN_ID` | — | 自动检测 | 机器人 open_id（检测失败时手动设置） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook 服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | Webhook 服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | Webhook 端点路径 |

---

## 写在最后

把 AI Agent 接入飞书，本质上是**把 AI 能力嵌入到日常工作流中**。不是让你学一个新工具，而是让 AI 来到你已经在用的工具里——在聊天中完成部署、排查、巡检、文档管理。

我自己的 HME 项目通过这套方案，把原本需要手动操作的「打开 Jenkins → 选流水线 → 等构建 → SSH 登录 → 执行部署 → 验证 → 群里通知」变成了飞书群里的**一句话搞定**，每天节省大量重复操作时间。

开始动手吧。扫码、配置、发消息——三步就能看到机器人回复你。剩下的进阶功能按需逐步解锁。

---

> **参考资源**
> - Hermes 官方文档：[hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/) · [飞书集成指南](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/messaging/feishu)
> - 飞书开放平台：[open.feishu.cn](https://open.feishu.cn/)
> - 社区经验：[知乎专栏](https://zhuanlan.zhihu.com/p/2025946069759006384) · [CSDN](https://blog.csdn.net/drinkwtr77/article/details/160090694) · [Trilium](https://trilium.atibm.com/share/hermesfeishu)

---

*如果这篇文章对你有帮助，欢迎分享给你的同事和朋友。有配置问题？欢迎在评论区留言交流。*
