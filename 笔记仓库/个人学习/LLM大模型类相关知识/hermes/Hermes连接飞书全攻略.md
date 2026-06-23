# Hermes 连接飞书全攻略：从入门到自动化，踩坑经验一次讲透

> 打造你的专属 AI 助手，让飞书成为 AI Agent 的交互入口

---

## 开篇：为什么要把 Hermes 接入飞书？

想象一下这个场景：早上到公司，打开飞书，给机器人发一条消息——「帮我检查一下生产环境状态」，30 秒后收到一份完整的服务器健康报告。再发一条——「把昨天客户会议的要点整理成文档」，一分钟后一个格式精美的飞书文档链接就发过来了。

这不是科幻，而是 **Hermes + 飞书** 能做到的事。

**Hermes** 是 Nous Research 开源的 AI Agent 框架，它像一个"万能插座"，能让 AI 大模型连接各种工具（终端命令、文件读写、网页搜索、API 调用等）。而飞书作为国内最主流的办公协作平台，把它作为 Agent 的交互入口，意味着你可以在日常聊天中完成大量工作，无需切换工具。

本文将从**新手快速上手**到**自建应用深度配置**，结合真实踩坑经验，帮你一篇文章搞定 Hermes 连接飞书。

---

## 一、架构概览：一条消息的完整旅程

在动手配置之前，先理解整体架构，这样遇到问题时你才知道该排查哪个环节。

一条消息从你发出到 Agent 回复，要经过 **11 个步骤**：

```
用户在飞书发消息
    ↓ ①
飞书机器人 Bot App
    ↓ ② 事件推送
飞书开放平台（Event Subscription）
    ↓ ③ Webhook
Hermes Gateway（消息路由 & 分发）
    ↓ ④ 分发给飞书适配器
Feishu Adapter（解析消息格式）
    ↓ ⑤ 交给 Agent Core
AI Agent 核心引擎（run_conversation）
    ↓ ⑥ 调用 LLM 推理 → ⑦ 按需调用工具 → ⑧ 读写记忆
生成回复
    ↓ ⑨ 经适配器返回
Gateway → 飞书 API 发送回复
    ↓ ⑩
用户在飞书看到回复
```

**核心组件说明**：

| 组件 | 作用 | 关键配置 |
|------|------|----------|
| **飞书机器人** | 用户在飞书中与之对话的 Bot | 飞书开放平台创建 |
| **开放平台事件订阅** | 将飞书消息事件推送到你的服务器 | Request URL + 事件权限 |
| **Hermes Gateway** | 统一网关，连接多种消息平台 | `hermes gateway setup` |
| **Feishu Adapter** | 处理飞书消息的编解码 | Gateway 内自动管理 |
| **Agent Core** | AI 对话循环 + 工具调度 | LLM 配置 + 工具配置 |
| **Tools 工具集** | terminal、文件、搜索、飞书文档等 | 按需启用 |
| **Memory / Sessions** | 跨会话记忆和对话历史 | SQLite 持久化 |

---

## 二、快速上手：3 步让 AI 在飞书回复你

### 第 1 步：在飞书开放平台创建应用

1. 打开 [飞书开放平台](https://open.feishu.cn)，用企业账号登录
2. 点击「创建企业自建应用」，填写应用名称（如「我的 AI 助手」）
3. 创建完成后，左侧菜单进入「**凭证与基础信息**」，记录下：
   - **App ID**（格式：`cli_xxxxxx`）
   - **App Secret**（随机字符串，妥善保管）

> ⚠️ **第一个坑**：App Secret 只在创建时显示一次，务必立即保存！如果忘记了只能重置。

### 第 2 步：配置事件订阅

在飞书开放平台的应用配置中：

1. 左侧菜单 → **事件订阅** → 开启
2. **请求地址**（Request URL）：填写你的 Hermes Gateway 公网地址
   - 本地测试可以用 ngrok 等内网穿透工具
   - 生产环境建议用 Nginx 反向代理 + HTTPS
3. **添加事件**：搜索并添加 `im.message.receive_v1`（接收消息事件）
4. 保存配置

> ⚠️ **第二个坑**：Request URL 必须能通过飞书的 **Challenge 验证**。飞书在保存时会发一个 POST 请求到你的 URL，要求你在 1 秒内返回相同的 challenge 值。Hermes Gateway 会自动处理这个验证，但你**必须确保 Gateway 先启动、URL 可访问**，再保存飞书配置。

### 第 3 步：配置 Hermes Gateway

在安装了 Hermes 的环境中执行：

```bash
# 配置飞书通道
hermes gateway setup

# 按提示填写：
# - App ID
# - App Secret
# - 其他选项默认即可

# 安装为后台服务
hermes gateway install

# 启动 Gateway
hermes gateway start
```

配置完成后，在飞书中找到你的机器人，发送「你好」测试一下。如果收到回复，恭喜，基础通道已打通！

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

以上覆盖了**消息收发 + 文档读写 + 知识库读取 + 云空间访问**，满足 99% 的日常场景。

### 权限完整对照表

| 功能 | 必需权限 | 说明 |
|------|----------|------|
| 收发私信 | `im:message.p2p_msg:readonly` + `im:message:send_as_bot` | 基础聊天 |
| 群聊 @机器人 | `im:message.group_at_msg:readonly` | 群聊中触发 |
| 发送图片/文件 | `im:resource` | 上传下载资源 |
| 读飞书文档 | `docx:document:readonly` | 读取文档内容 |
| 创建/编辑文档 | `docx:document:write_only` | 写入文档 |
| 读知识库 | `wiki:wiki:readonly` | 知识空间访问 |
| 云文件操作 | `drive:drive` | 上传/下载/搜索 |
| 管理文档权限 | `docs:permission.member:create` | 添加协作者 |
| 操作电子表格 | `sheets:spreadsheet` | Excel 类操作 |
| 日历/日程 | `calendar:calendar` | 日程管理 |

### 权限生效的关键步骤（很多人漏掉这步）

权限申请通过后，**必须创建版本并发布**才能生效：

1. 飞书开放平台 → 应用详情页 → 顶部「创建版本」
2. 填写版本号和说明（如 `v1.0 - 基础消息和文档权限`）
3. **可用范围**：个人使用就仅选自己（免审批）
4. 提交发布

> ⚠️ **第三个坑**：只在权限管理页面申请了权限但**没发布版本**，权限实际不生效！这是新手最容易犯的错误。

---

## 四、踩坑实录：那些让我抓狂的瞬间

### 坑 1：事件订阅 URL 验证失败

**现象**：保存事件订阅配置时报错「请求地址验证失败」

**原因**：
- Gateway 没启动或 URL 不可达
- 防火墙/安全组拦截了飞书的回调请求
- 使用了自签名 HTTPS 证书

**解决**：
```bash
# 先启动 Gateway
hermes gateway start

# 检查端口是否监听
netstat -tlnp | grep <gateway_port>

# 用 curl 模拟飞书的 Challenge 请求验证
curl -X POST https://your-domain.com/feishu/callback \
  -H "Content-Type: application/json" \
  -d '{"challenge":"test123","token":"xxx","type":"url_verification"}'
# 应该返回: {"challenge":"test123"}
```

### 坑 2：机器人不回复群聊消息

**现象**：私聊正常，群聊 @机器人 没反应

**原因**：
- 没有添加 `im:message.group_at_msg:readonly` 权限
- 机器人不在该群聊中
- 群聊设置中禁用了机器人

**解决**：
1. 确认权限中包含 `im:message.group_at_msg:readonly`
2. 在群聊设置 → 群机器人 → 添加你的机器人
3. 确保 @的是完整的机器人名称

### 坑 3：读不了飞书文档，报 131003 错误

**现象**：让机器人读文档，返回 `no permission (131003)`

**原因链**：
1. 应用没申请 `docx:document` 权限
2. 或申请了但没发布版本
3. 或文档设置了访问限制（仅特定人可读）

**排查顺序**：
```bash
# 1. 先用 feishu-cli 测试权限
feishu-cli doc export <doc_token> --debug

# 2. 查看具体错误码
# 131003 → 应用权限不足 → 去开放平台加权限
# 131001 → 文档不存在或无访问权 → 检查文档链接和你的访问权限
# 10019  → 用户本身没有该资源权限 → 先用自己账号确认能打开文档
```

### 坑 4：Gateway 时区/时间不同步

**现象**：消息延迟、事件推送偶尔失效

**原因**：飞书 API 对请求时间戳有校验，服务器时间偏差过大会导致签名验证失败

**解决**：
```bash
# 同步系统时间
sudo ntpdate -u ntp.aliyun.com

# 或者配置定时同步
sudo systemctl enable chronyd
```

### 坑 5：Token 过期不刷新

**现象**：运行一段时间后机器人突然不回复了

**原因**：飞书的 `tenant_access_token` 有效期 2 小时，如果 Hermes 的 Token 刷新逻辑有问题，过期后请求全部失败

**解决**：
- 确保 Hermes 版本是最新的（Token 自动刷新是内置逻辑）
- 重启 Gateway 可以强制重新获取 Token：
  ```bash
  hermes gateway restart
  ```
- 设置定时健康检查，发现异常自动重启

---

## 五、自建应用进阶：从能用到好用

基础配置完成后，下面这些进阶操作让你的机器人真正发挥价值。

### 5.1 工具集配置：给 Agent 装上手脚

在 Hermes 配置中启用更多工具能力：

```yaml
# ~/.hermes/config.yaml
tools:
  terminal:
    enabled: true          # 执行终端命令
    allowed_commands:      # 白名单模式，安全第一
      - "cat"
      - "ls"
      - "grep"
      - "df"
      - "top -n 1"
  file:
    enabled: true          # 文件读写
    workspace: "/data/hermes-workspace"
  feishu_doc:
    enabled: true          # 飞书文档操作
  web_search:
    enabled: true          # 网页搜索
```

### 5.2 定时任务：自动巡检 + 推送

```yaml
# ~/.hermes/cron.yaml
tasks:
  - name: "morning-health-check"
    schedule: "0 9 * * 1-5"          # 工作日早上 9 点
    prompt: "检查生产环境状态（CPU、内存、磁盘），排查异常日志，整理成简报发送到飞书群"
    
  - name: "daily-report"
    schedule: "0 18 * * 1-5"         # 工作日晚上 6 点
    prompt: "汇总今天处理的关键事项和待跟进问题，生成日报"
```

### 5.3 多身份配置

如果你有多个飞书企业需要用同一个 Hermes 实例：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "accounts": {
        "company_a": {
          "appId": "cli_xxxxx",
          "appSecret": "xxxxx",
          "botName": "A公司助手"
        },
        "company_b": {
          "appId": "cli_yyyyy",
          "appSecret": "yyyyy",
          "botName": "B公司助手"
        }
      }
    }
  }
}
```

### 5.4 LLM 模型选择建议

| 场景 | 推荐模型 | 理由 |
|------|----------|------|
| 日常对话/问答 | Claude Sonnet 4.6 | 性价比高，响应快 |
| 代码审查/生成 | Claude Opus 4.8 | 代码能力最强 |
| 长文档处理 | 模型 + 长上下文 | 200K token 上下文 |
| 轻量任务 | Claude Haiku | 成本极低，速度极快 |

通过 OpenRouter 可以统一接入多个模型，在 `config.yaml` 中配置 API Key 即可：

```yaml
llm:
  provider: "openrouter"
  model: "anthropic/claude-sonnet-4-20250514"
  api_key: "${OPENROUTER_API_KEY}"
```

---

## 六、经验总结：做对这几件事

### ✅ DO：应该做的事

1. **最小权限原则**：飞书应用只申请实际需要的权限，每多一个权限就多一分安全风险
2. **凭证用环境变量**：App Secret 绝不写进代码或配置文件，用 `export FEISHU_APP_SECRET=xxx` 注入
3. **给 Agent 设定系统提示词**：在 Hermes 中配置 System Prompt，明确告诉 AI 它的身份、能力边界和行为规范
4. **开启审计日志**：飞书开放平台会记录所有 API 操作，定期检查确保没有异常调用
5. **工具白名单**：terminal 工具一定要配置 `allowed_commands`，防止 Agent 执行危险命令
6. **先测试后上线**：在测试群充分验证各种场景后再推广给团队使用

### ❌ DON'T：不要做的事

1. **不要把 App Secret 传到 GitHub**：公开仓库中一旦泄露，任何人都能以你的应用身份操作
2. **不要给 Agent 开放所有终端命令**：`rm -rf`、`DROP TABLE` 这类破坏性命令必须限制
3. **不要跳过版本发布**：权限申请 ≠ 权限生效，少了「创建版本发布」这一步等于白配
4. **不要在生产环境直连 LLM**：敏感文档内容需要脱敏处理后再发送给外部模型
5. **不要忽略限流**：飞书 API 默认 100 次/分钟，批量操作需要加延迟或排队

---

## 七、常见错误码速查

| 错误码 | 含义 | 快速解决 |
|--------|------|----------|
| `131003` | 应用无权限 | 检查开放平台权限配置 + 版本发布 |
| `131001` | 资源不存在 | 检查文档链接/Token 是否有效 |
| `99991663` | 应用不存在 | 检查 App ID 是否正确 |
| `10003` | Token 无效 | App Secret 错误或应用被停用 |
| `10019` | 操作被拒绝 | 用户本身没有该资源权限 |
| `10020` | 请求限流 | 降低频率，加延迟重试 |

调试技巧：在命令后加 `--debug` 查看详细请求响应信息。

---

## 八、拓展：能玩出的花活

当你把基础配置搞定后，下面是几个有趣的方向：

### 场景 1：智能运维助手
> 飞书发「查一下生产环境 CPU 使用率」→ Agent SSH 到服务器执行 `top` → 结果整理成易读格式回复

### 场景 2：自动化文档管理
> 飞书发「把本周会议纪要按照模板整理成文档」→ Agent 搜索聊天记录 → 提取关键信息 → 创建飞书文档 → 自动添加参与者为协作者 → 返回文档链接

### 场景 3：代码审查机器人
> 飞书发「review 一下 main 分支最新 PR」→ Agent 执行 `git diff` + `gh pr view` → LLM 审查代码质量 → 输出审查意见 + 是否可合并建议

### 场景 4：数据看板自动生成
> 飞书发「分析上月销售数据，画趋势图」→ Agent 读取 CSV/数据库 → Python 数据分析 → 生成图 → 图表 + 分析文字一起发回

### 场景 5：跨平台消息桥接
> Hermes Gateway 同时接入飞书、Slack、Telegram → 一条消息同步推送到所有平台 → 统一消息管理中心

---

## 九、推荐学习路径

1. **第一步**：按照本文「快速上手」部分，15 分钟内完成基础配置，确保飞书能收到机器人回复
2. **第二步**：阅读 [Hermes 官方文档 - 飞书集成](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/messaging/feishu)，了解全部配置项
3. **第三步**：为 Agent 添加 2-3 个实用工具（terminal、飞书文档、网页搜索），让它在真实场景中跑起来
4. **第四步**：配置定时任务，让 Agent 自动执行周期性工作
5. **第五步**：根据团队反馈持续优化 System Prompt 和工具配置

---

## 写在最后

把 AI Agent 接入飞书，本质上是**把 AI 能力嵌入到日常工作流中**。不是让你去学一个新工具，而是让 AI 来到你已经在用的工具里。

配置过程中你大概率会遇到各种报错，但别慌——90% 的问题都在本文的「踩坑实录」和「错误码速查」中能找到答案。剩下的 10%，`--debug` 参数和飞书开放平台的日志会告诉你。

开始动手吧，期待你的第一个 AI 机器人成功上线！

---

> **参考资源**
> - Hermes 官方文档：[hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/)
> - 飞书开放平台：[open.feishu.cn](https://open.feishu.cn/)
> - 本文参考的社区经验：[知乎专栏](https://zhuanlan.zhihu.com/p/2025946069759006384) · [CSDN 博客](https://blog.csdn.net/drinkwtr77/article/details/160090694) · [Trilium 笔记](https://trilium.atibm.com/share/hermesfeishu)

---

*如果这篇文章对你有帮助，欢迎分享给你的同事和朋友，让更多人把 AI 用起来。*

*有配置问题？欢迎在评论区留言交流。*
