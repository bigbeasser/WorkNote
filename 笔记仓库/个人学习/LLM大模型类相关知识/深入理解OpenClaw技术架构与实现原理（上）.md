# 深入理解OpenClaw技术架构与实现原理（上）

## 一、背景

OpenClaw已成为当下最热门且实用的个人AI助手。本文旨在系统性剖析其技术架构与实现细节。OpenClaw在个人助手方向上的卓越表现，不仅得益于其灵活先进的智能体架构，还在于其围绕个人助手的完整工具与生态实现。最令人惊讶的是，这些能力几乎全部通过**AI-Coding**实现，彻底改变了软件开发范式。其清晰简洁的架构设计与表达，比传统人类编程系统具有更高的标准，堪称开启新软件构建范式的开山之作。

由于涉及技术点众多，建议读者按以下模块选择性阅读：

1. 统一控制平面Gateway网关
2. Agentic Loop/Pi Loop
3. 定时任务系统
4. 工具系统
5. Channels
6. 上下文管理
7. SubAgent子智能体
8. SandBox沙箱系统
9. 记忆管理
10. Skills模块
11. Session管理
12. 自进化机制
13. 工作区与Agent路由
14. Nodes
15. 安全策略
16. 配置管理

本文（上篇）将详解前7个模块。

## 二、OpenClaw总体架构

OpenClaw的架构设计以**本地优先(Local-First)多端联动**为核心，旨在构建一个高度灵活且可扩展的个人AI助手系统。其架构可概括为一个以**Gateway(网关)**为核心控制平面的分布式系统。

### 技术架构全景

- **执行大脑**: Pi Agent与技能系统
- **输入触角**: 多渠道通信(Channels)
- **执行终端**: 节点与自动化工具(Nodes & Tools)
- **安全与部署层 (Security & Deployment Layer)** 安全沙箱 (Sandboxing): 非主会话（如群组）运行在Docker沙箱中，限制bash等敏感工具访问。 远程访问: 集成Tailscale Funnel，可安全暴露网关仪表盘，无需公网IP。

### 核心组件详述

#### 1. 核心控制平面: Gateway(网关)

Gateway是OpenClaw的心脏，充当系统的单一控制平面。

- **功能职责**: 负责管理会话(Sessions)、状态感知(Presence)、配置、定时任务(Cron)、网络钩子(Webhooks)、控制界面(Control UI)和Canvas宿主。
- **通信协议**: 基于WebSocket(WS)构建，为所有客户端、工具和事件提供统一的连接通道。
- **运行环境**: 推荐在Node ≥ 22环境下运行，通常作为守护进程（Daemon）常驻后台。

#### 2. 智能体运行时: Pi Agent

Pi Agent是处理逻辑和生成回复的核心引擎。

- **RPC模型**: 以RPC(远程过程调用)模式运行，支持工具流(Tool Streaming)和块流(Block Streaming)，确保高效与实时响应。
- **多智能体路由**: 能够将来自不同频道、账户或同伴的输入路由到相互隔离的智能体（拥有独立的Workspace和会话）。
- **会话模型**: 提供`main`模式用于用户直接对话，并支持群组隔离、激活模式切换和队列管理。

#### 3. 连接生态: Channels(频道)

OpenClaw的一大特色是其极强的连接性，将AI能力注入用户已有的社交生态。

- **多频道集成**: 原生支持WhatsApp、Telegram、Slack、Discord、Google Chat、Signal、iMessage、Microsoft Teams、Matrix、Zalo等多种通讯平台。
- **路由规则**: 具备复杂的群组路由逻辑，包括提及门控（Mention gating）、回复标签处理及针对不同频道的自动消息分块。

#### 4. 设备节点与伴侣应用: Nodes & Apps

通过将不同设备定义为“节点”，实现跨设备的硬件控制。

- **跨平台支持**: 包括macOS菜单栏应用、iOS节点和Android节点。
- **硬件能力调用**: 通过`node.invoke`协议，智能体可远程调用各节点上的硬件功能，如摄像头拍照/录码、屏幕录制、地理位置获取以及macOS特有的系统命令执行（`system.run`）。
- **Voice Wake & Talk Mode**: 利用ElevenLabs等技术，在macOS/iOS/Android上提供始终在线的语音唤醒和连续对话能力。

#### 5. 工具与自动化：Tools & Skills

架构中集成了丰富的生产力工具。

- **浏览器控制**: 内置托管的Chrome/Chromium实例，支持快照、动作执行和文件上传。
- **Live Canvas**: 基于A2UI构建的实时交互画布，允许智能体驱动视觉化的工作空间。
- **技能平台 (ClawHub)**: 提供技能注册表，支持捆绑技能、托管技能和工作区技能的自动搜索与安装。

#### 6. 安全与沙箱机制 (Security & Sandboxing)

- **DM配对策略**: 默认情况下，未知发送者必须通过配对码验证，bot才会处理其消息，防止不受信任的输入。
- **Docker沙箱**: 支持将**非主会话**（如群组或外部频道）放入独立的Docker容器中运行，限制其对主机的访问权限，并对敏感工具（如浏览器、系统命令）进行黑白名单管理。

#### 7. 部署与远程访问

- **本地/远程灵活部署**: Gateway可运行在本地或小型Linux实例上。
- **内网穿透**: 集成Tailscale Serve/Funnel或SSH隧道，使用户能够安全地从远程访问Gateway面板和WebSocket服务。

## 三、各系统模块详解

### 3.1 统一控制平面Gateway网关

#### 3.1.1 核心定位

Gateway是OpenClaw的统一控制平面，是一个WebSocket服务器，负责：

1. **消息路由** - 所有频道（Telegram、Discord、Slack等）的消息路由
2. **会话管理** - Agent会话的生命周期管理
3. **工具调用** - Agent工具的执行协调
4. **节点通信** - iOS/Android等移动节点的通信桥接
5. **HTTP API** - 提供OpenAI兼容的REST API

#### 3.1.2 架构模型

```xml-dtd
┌─────────────────────────────────────────────────────┐
│                 Gateway 进程                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │WebSocket │  │ HTTP API │  │ Control  │          │
│  │  Server  │  │ (OpenAI) │  │   UI     │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │             │             │                 │
│       └─────────────┴─────────────┘                 │
│                     │                               │
│              ┌──────┴──────┐                        │
│              │  RPC Router │                        │
│              └──────┬──────┘                        │
│       ┌─────────────┼─────────────┐                 │
│  ┌────┴────┐  ┌─────┴─────┐  ┌────┴────┐          │
│  │Channels │  │  Agents   │  │  Nodes  │          │
│  │(消息路由)│  │ (会话管理) │  │(设备节点)│          │
│  └─────────┘  └───────────┘  └─────────┘          │
└─────────────────────────────────────────────────────┘
```

#### 3.1.3 关键特性

| 特性       | 说明                                                         |
| ---------- | ------------------------------------------------------------ |
| 单端口复用 | WebSocket RPC + HTTP API + Control UI 共用一个端口（默认 18789） |
| 协议版本化 | 客户端声明`minProtocol`/`maxProtocol`，服务端拒绝不匹配的连接 |
| 角色分离   | `operator`（控制面）和`node`（能力节点）两种角色             |
| 作用域控制 | 细粒度的scopes控制（`operator.read`、`operator.write`、`operator.admin`等） |
| 设备认证   | 支持设备身份验证和配对机制                                   |
| 热重载     | 支持`hot`/`restart`/`hybrid`三种配置重载模式                 |

#### 3.1.4 协议机制

- **连接握手流程**：

```xml-dtd
Gateway                       Client
│                             │
│◄──── connect.challenge ──────│  (可选：带 nonce 的挑战)
│                             │
│─────── connect (req) ───────►│  携带 auth + role + scopes
│                             │
│◄────── hello-ok (res) ───────│  返回 policy + 设备令牌
│                             │
│◄─────── events ──────────────│  持续推送状态变更
```

- **帧类型**： **Request**: `{type:"req", id, method, params}` **Response**: `{type:"res", id, ok, payload\|error}` **Event**: `{type:"event", event, payload, seq?, stateVersion?}`

#### 3.1.5 认证模式

| 模式          | 使用场景                       |
| ------------- | ------------------------------ |
| token         | 共享令牌认证（默认）           |
| password      | 共享密码认证                   |
| trusted-proxy | 反向代理认证（如 Pomerium）    |
| device-token  | 设备身份认证（配对后自动获取） |

- **安全强制**： 非环回地址绑定**必须**启用认证 明文`ws://`禁止连接非本机地址（CWE-319）

#### 3.1.6 绑定模式

| 模式     | 地址         | 用途             |
| -------- | ------------ | ---------------- |
| loopback | 127.0.0.1    | 默认，仅本机访问 |
| lan      | 0.0.0.0      | 局域网访问       |
| tailnet  | Tailscale IP | Tailscale 网络   |
| auto     | 自动选择     | 根据环境自动判断 |
| custom   | 自定义地址   | 特定绑定需求     |

#### 3.1.7 服务生命周期

- **macOS (launchd)**：

```xml-dtd
openclaw gateway install   # 安装 LaunchAgent
openclaw gateway start     # 启动服务
openclaw gateway stop      # 停止服务
openclaw gateway restart   # 重启服务
```

- **Linux (systemd)**：

```
openclaw gateway install
systemctl --user enable --now openclaw-gateway.service
```

#### 3.1.8 配置热重载

| 模式    | 行为                             |
| ------- | -------------------------------- |
| off     | 不重载                           |
| hot     | 仅应用安全热更新                 |
| restart | 需要重启时自动重启               |
| hybrid  | 安全时热更新，必要时重启（默认） |

#### 3.1.9 关键配置项

```xml-dtd
{
  "gateway": {
    "port": 18789,
    "bind": "loopback",
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "your-token"
    },
    "tls": {
      "enabled": true,
      "certPath": "/path/to/cert.pem",
      "keyPath": "/path/to/key.pem"
    },
    "reload": {
      "mode": "hybrid",
      "debounceMs": 300
    }
  }
}
```

#### 3.1.10 常用命令

```xml-dtd
# 启动网关
openclaw gateway --port 18789
# 查看状态
openclaw gateway status
openclaw gateway status --deep  # 深度检查
# 健康检查
openclaw gateway health
openclaw channels status --probe
# 发现局域网网关
openclaw gateway discover
# 查看日志
openclaw logs --follow
```

#### 3.1.11 核心源码位置

| 模块        | 路径                          |
| ----------- | ----------------------------- |
| CLI 入口    | `src/cli/gateway-cli/`        |
| 客户端      | `src/gateway/client.ts`       |
| 协议定义    | `src/gateway/protocol/`       |
| 服务端 HTTP | `src/gateway/server-http.ts`  |
| 配置类型    | `src/config/types.gateway.ts` |

### 3.2 Agentic Loop / Pi Loop

这是构成整个系统执行的大脑思考核心，系统中所有的运行逻辑都由这个**事件驱动**的推理循环架构来控制。

#### 3.2.1 核心推理循环

- **主循环架构** (`runEmbeddedPiAgent`in run.ts:192)

```xml-dtd
runEmbeddedPiAgent()
└── while (true) {  // 行538 - 主重试循环
    ├── 检查重试次数限制 (MAX_RUN_LOOP_ITERATIONS)
    ├── 调用 runEmbeddedAttempt()  // 单次推理尝试
    ├── 处理 context overflow → 自动压缩
    ├── 处理 auth failure → profile轮换
    ├── 处理 timeout → 重试或报错
    └── 成功则返回 payloads
}
```

- **单次推理尝试** (`runEmbeddedAttempt`in run/attempt.ts:306)

```xml-dtd
runEmbeddedAttempt()
├── 1. 准备阶段
│   ├── 创建 workspace 和 session
│   ├── 解析 tools (createOpenClawCodingTools)
│   ├── 构建 system prompt
│   └── 创建 session manager
├── 2. 会话初始化
│   ├── createAgentSession()  // 行688
│   ├── 设置 streamFn (LLM调用函数)
│   └── 安装事件订阅器 subscribeEmbeddedPiSession()  // 行921
├── 3. 执行推理
│   ├── await activeSession.prompt(effectivePrompt)  // 行1180-1182
│   │   └── 调用 LLM API (streamSimple / streamFn)
│   │       └── 事件流处理:
│   ├── message_start / message_update / message_end → handleMessageStart/Update/End
│   ├── tool_execution_start / update / end → handleToolExecutionStart/Update/End
│   └── agent_start / agent_end             → handleAgentStart/End
└── 4. 返回结果
    ├── assistantTexts(生成的文本)
    ├── toolMetas(工具调用元数据)
    └── usage(token使用统计)
```

- **工具调用循环** 工具调用由底层SDK (`@mariozechner/pi-coding-agent`) 的`createAgentSession`自动管理。当模型返回`tool_use`时：

```xml-dtd
LLM Response (tool_use)
└── SDK 自动执行:
    ├── handleToolExecutionStart()  // 记录工具开始
    │   └── emitAgentEvent({stream:"tool", data:{phase:"start", name, toolCallId, args}})
    ├── 执行工具函数
    ├── handleToolExecutionUpdate()  // 流式更新
    │   └── emitAgentEvent({stream:"tool", data:{phase:"update", ...}})
    └── handleToolExecutionEnd()  // 工具完成
        ├── emitAgentEvent({stream:"tool", data:{phase:"result", ...}})
        ├── 调用 after_tool_call hook
        └── SDK 自动将 tool_result 添加到消息历史
            └── 继续调用 LLM (下一轮推理)
```

- **消息处理流程** (`subscribeEmbeddedPiSession`in pi-embedded-subscribe.ts:34) 事件分发 (`createEmbeddedPiSessionEventHandler`):

```xml-dtd
├── message_start    → handleMessageStart()
│   └── 重置状态，准备新消息
├── message_update   → handleMessageUpdate()
│   ├── 处理 text_delta
│   ├── 处理 thinking 块
│   └── 调用 onPartialReply / onBlockReply
├── message_end      → handleMessageEnd()
│   ├── 提取最终文本
│   ├── 处理 reasoning
│   └── 推送最终回复
├── tool_execution_* → handleToolExecution*()
│   └── 跟踪工具状态，发送工具事件
└── agent_start/end  → handleAgentStart/End()
    └── 生命周期事件广播
```

#### 3.2.2 关键调用链

```xml-dtd
用户消息
↓
runAgentTurnWithFallback() (agent-runner-execution.ts:72)
↓
runEmbeddedPiAgent() (pi-embedded-runner/run.ts:192)
↓ [while循环 - 重试]
runEmbeddedAttempt() (pi-embedded-runner/run/attempt.ts:306)
↓
createAgentSession() + activeSession.prompt()
↓ [LLM调用 + 工具循环]
subscribeEmbeddedPiSession() → 事件处理器
↓
onPartialReply / onBlockReply / onToolResult
↓
回复消息发送
```

#### 3.2.3 LLM调用函数

- 默认: `streamSimple`(来自`@mariozechner/pi-ai`)
- Ollama: `createOllamaStreamFn()`
- 可通过`applyExtraParamsToAgent()`包装添加额外参数

### 3.3 定时任务系统

定时任务是OpenClaw重要的基础设施，用于满足长任务在后台单次或周期性运行的诉求，通过与Heartbeat交互增强系统的拟人化体验。

#### 3.3.1 核心架构

```xml-dtd
┌─────────────────────────────────────────────────────────────────────┐
│                     CronService                                     │
│  (src/cron/service.ts)                                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐       │
│  │   Timer       │  │    Store     │  │   State            │       │
│  │  (timer.ts)   │  │  (store.ts)  │  │  (state.ts)        │       │
│  └───────┬───────┘  └──────┬───────┘  └────────────────────┘       │
│          │                 │                                        │
│          ▼                 ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │               Jobs Collection(jobs.json)                │       │
│  └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 调度类型

```
type CronSchedule =
  | { kind: "at"; at: string }                // 一次性任务，指定时间
  | { kind: "every"; everyMs: number; anchorMs?: number }  // 周期性任务
  | { kind: "cron"; expr: string; tz?: string; staggerMs?: number }  // Cron表达式
```

#### 3.3.3 定时器机制

核心实现在`src/cron/service/timer.ts`:

```typescript
const MAX_TIMER_DELAY_MS = 60_000;    // 最大延迟60秒
const MIN_REFIRE_GAP_MS = 2_000;      // 最小重触发间隔2秒

// 定时器armed函数
export function armTimer(state: CronServiceState){
  const nextAt = nextWakeAtMs(state);   // 计算下次唤醒时间
  const delay = Math.max(nextAt - now, 0);
  const clampedDelay = Math.min(delay, MAX_TIMER_DELAY_MS);
  state.timer = setTimeout(() => {
    void onTimer(state).catch(...);
  }, clampedDelay);
}
```

**关键特性**：

- 定时器最大延迟60秒，防止时钟漂移
- 支持并发运行控制 (`maxConcurrentRuns`)
- 错误指数退避 (30s → 1min → 5min → 15min → 60min)
- 自动清理卡住的任务 (2小时超时)

#### 3.3.4 任务持久化机制

- **存储位置**： 默认路径: `~/.openclaw/cron/jobs.json` 可通过配置`cron.store`自定义
- **存储格式**：

```ts
type CronStoreFile = { version: 1; jobs: CronJob[]; };
type CronJob = {
  id: string;
  name: string;
  enabled: boolean;
  schedule: CronSchedule;
  sessionTarget: "main" | "isolated";
  payload: CronPayload;
  state: CronJobState;  // 运行时状态
  // ...
};
```

- **持久化流程**： 原子写入（临时文件 + rename） 自动备份 支持热重载（文件修改时间检测）
- **运行日志**： 路径: `~/.openclaw/cron/runs/<jobId>.jsonl` 自动裁剪（默认2MB，保留2000行）

#### 3.3.5 任务恢复机制

启动恢复流程 (`src/cron/service/ops.ts`):

```ts
export async function start(state: CronServiceState){
  // 1. 加载存储
  await ensureLoaded(state, { skipRecompute: true });
  // 2. 清理卡住的任务
  for (const job of jobs) {
    if (job.state.runningAtMs) {
      job.state.runningAtMs = undefined;  // 清除过期标记
    }
  }
  // 3. 运行错过的任务
  await runMissedJobs(state);
  // 4. 重新计算下次运行时间
  recomputeNextRuns(state);
  // 5. 启动定时器
  armTimer(state);
}
```

#### 3.3.6 任务执行类型

两种执行模式：

1. **Main Session** (`sessionTarget: "main"`) 注入系统事件到主会话 payload必须为`{ kind: "systemEvent", text: string }`
2. **Isolated Agent** (`sessionTarget: "isolated"`) 独立agent会话执行 payload必须为`{ kind: "agentTurn", message: string, ... }` 支持模型覆盖、thinking模式、超时设置

**超时控制**：

```java
export async function executeJobCoreWithTimeout(state, job){
  const jobTimeoutMs = resolveCronJobTimeoutMs(job);
  return await Promise.race([
    executeJobCore(state, job, abortSignal),
    new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        abortController.abort();
        reject(new Error("cron: job execution timed out"));
      }, jobTimeoutMs);
    }),
  ]);
}
```

#### 3.3.7 与Heartbeat的集成

定时任务通过Heartbeat机制唤醒agent：

```javascript
// src/gateway/server-cron.ts
const cron = new CronService({
  enqueueSystemEvent: (text, opts) => {
    enqueueSystemEvent(text, { sessionKey, contextKey });
  },
  requestHeartbeatNow: (opts) => {
    requestHeartbeatNow({ reason, agentId, sessionKey });
  },
  runHeartbeatOnce: async (opts) => {
    return await runHeartbeatOnce({ cfg, reason, agentId, sessionKey });
  },
  // ...
});
```

**Wake模式**：

- `next-heartbeat`- 等待下次心跳执行
- `now`- 立即触发心跳

#### 3.3.8 Webhook通知

支持任务完成后的Webhook回调：

```javascript
if (webhookTarget && evt.summary) {
  await fetch(webhookTarget.url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${webhookToken}`,
    },
    body: JSON.stringify(evt),
  });
}
```

#### 3.3.9 CLI命令

```xml-dtd
openclaw cron status      # 查看调度器状态
openclaw cron list        # 列出任务
openclaw cron add         # 添加任务
openclaw cron edit        # 编辑任务
openclaw cron remove <id> # 删除任务
openclaw cron run <id>    # 手动触发任务
```

#### 3.3.10 关键设计特点

1. **单一定时器设计** - 只维护一个定时器，基于最近任务的nextRunAtMs
2. **文件持久化** - JSON存储，支持跨进程共享
3. **错误隔离** - 单个任务失败不影响其他任务
4. **自动恢复** - 启动时检测并运行错过的任务
5. **并发控制** - 可配置最大并发任务数
6. **进度追踪** - 完整的运行日志和状态跟踪
7. **Agent集成** - 可通过cron工具在agent中管理任务

### 3.4 工具系统

#### 3.4.1 总体架构

工具系统采用分层架构：

1. **工具创建层**: `createOpenClawCodingTools()`（主入口）和`createOpenClawTools`
2. **工具定义层**: 核心类型`AnyAgentTool`和内置工具实现（浏览器、记忆、消息、执行等）
3. **Schema规范化层**: `normalizeToolParameters()`，针对不同AI提供商（Anthropic、OpenAI、Google/Gemini）处理Schema差异
4. **策略管道层**: `applyToolPolicyPipeline()`，应用7步策略过滤
5. **执行层**: AI模型交互、Hook系统（`before_tool_call`/`after_tool_call`）
6. **插件系统**: `resolvePluginTools()`，支持插件工具扩展
7. **HTTP调用API**: `POST /tools/invoke`，允许外部系统直接调用工具

#### 3.4.2 核心组件详解

- **工具创建层入口**: `createOpenClawCodingTools()`(`pi-tools.ts:182`)
- **核心类型**: `AnyAgentTool`(`tools/common.ts:8`)
- **策略管道步骤**（优先级从低到高）： `Profile Policy → Provider Profile → Global Policy → Agent Policy → Group Policy → Sandbox Policy → Subagent Policy`
- **策略配置结构**: `type ToolPolicyConfig = {  allow?: string[];  // 白名单  alsoAllow?: string[];  // 追加白名单  deny?: string[];  // 黑名单  profile?: "minimal" | "coding" | "messaging" | "full"; };`

#### 3.4.3 工具调用完整流程

```xml-dtd
用户消息
│
▼
┌─────────────────┐
│ Gateway 接收    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 构建工具列表    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 应用策略过滤    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 规范化 Schema   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 发送给 AI 模型  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AI 生成 tool_use│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 工具执行前检查  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ tool.execute()  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 工具执行后处理  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 返回 tool_result│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AI 继续推理     │
└─────────────────┘
```

#### 3.4.4 关键设计特点

1. **分层架构**: 创建 → 定义 → 规范化 → 策略 → 执行，职责清晰
2. **策略管道**: 多级策略叠加，支持精细控制
3. **Provider适配**: 自动处理不同AI提供商的Schema差异
4. **插件扩展**: 插件工具与核心工具统一管理
5. **Hook机制**: 支持工具调用前后拦截处理
6. **沙箱支持**: 隔离环境下的工具执行

### 3.5 Channels

Channels是OpenClaw进行社交生态连接最重要的设计，它将AI能力真正注入到了用户的社交与工作动线中。

#### 3.5.1 核心架构

- **Channel抽象设计**: 基于`ChannelPlugin`接口，包含12个独立适配器，职责分离清晰。
- **12个核心适配器**: `config`: 账户配置管理 `setup`: 账户设置流程 `outbound`: 消息发送 `status`: 状态探测 `gateway`: Gateway生命周期 `security`: 安全策略 `pairing`: 配对管理 `groups`: 群组管理 `threading`: 线程处理 `mentions`: 提及解析 `directory`: 目录查询 `resolver`: 路由解析 `actions`: 消息动作 `messaging`: 消息扩展

#### 3.5.2 消息流转完整架构

**INBOUND（入站）流程**:

```xml-dtd
外部平台 (Telegram, Discord等)
│
▼
Channel Monitor (接收层)
│
▼
Allowlist 验证 (基于优先级匹配)
│
▼
resolveAgent Route (路由解析)
│
▼
Session 管理
│
▼
Agent AI Engine 处理消息
```

**OUTBOUND（出站）流程**:

```xml-dtd
Agent 生成回复
│
▼
Outbound Deliver
│
▼
加载 OutboundAdapter
│
▼
消息分块 (chunker)
│
▼
Channel Outbound Adapter
│
▼
具体实现 (Telegram: bot.ts, Discord: send.ts等)
```

**路由优先级**（从高到低）：

1. `binding.peer`(精确用户/群组)
2. `binding.peer.parent`(线程继承)
3. `binding.guild + roles`
4. `binding.guild`
5. `binding.team`
6. `binding.account`
7. `binding.channel`
8. `default agent`

**Session Key格式**:

```xml-dtd
{agentId}:{mainKey}:{channel}:{accountId}:{peerKind}:{peerId}
```

#### 3.5.3 插件生命周期

1. **注册阶段**: 插件通过`registerChannel()`注册到PluginRegistry
2. **初始化阶段**: 轻量加载: `getChannelDock()`→ 仅元数据 完整加载: `getChannelPlugin()`→ 完整插件
3. **配置阶段**: SetupAdapter: `resolveAccountId()`, `applyAccountConfig()` ConfigAdapter: `listAccountIds()`, `resolveAccount()`
4. **运行阶段**: Gateway启动: `startAccount()`[可选] 消息接收: inbound handlers 路由解析: `resolveAgentRoute()` 消息发送: `OutboundAdapter.sendText()`/`sendMedia()`
5. **监控阶段**: StatusAdapter: `probeAccount()`, `auditAccount()` HeartbeatAdapter: `checkReady()`

#### 3.5.4 目录结构映射

```xml-dtd
src/
├── channels/          # Channel核心抽象
│   ├── plugins/      # 插件系统
│   ├── dock.ts       # 轻量级Dock
│   ├── registry.ts   # Channel ID规范化
│   ├── allow-from.ts # Allowlist匹配
│   ├── channel-config.ts # 配置匹配
│   └── session.ts    # 会话状态管理
├── routing/          # 路由系统
├── telegram/         # Telegram实现
├── discord/          # Discord实现
├── slack/            # Slack实现
├── signal/           # Signal实现
├── imessage/         # iMessage实现
├── web/              # WhatsApp Web实现
├── infra/outbound/   # 出站消息基础设施
└── plugins/          # 插件注册系统
extensions/           # 扩展插件
├── msteams/          # Microsoft Teams
├── matrix/           # Matrix协议
├── zalo/             # Zalo
└── voice-call/       # 语音通话
```

#### 3.5.5 关键设计要点

1. **分层抽象**: Application → Channel Abstraction → Implementation → Plugin Registry
2. **适配器模式**: 12个独立适配器，职责清晰分离
3. **性能优化**: Dock轻量加载、延迟加载、路由缓存、Update去重
4. **扩展性**: 新增Channel只需实现`ChannelPlugin`接口并注册
5. **安全隔离**: 每个channel独立的security、pairing、allowlist逻辑

### 3.6 上下文管理

#### 3.6.1 核心概念

- **Context（上下文）**: OpenClaw在一次运行中发送给模型的**所有内容**，受模型的上下文窗口（token限制）约束。
- **注意**: Context ≠ Memory。记忆可持久化到磁盘，Context是模型当前窗口内的内容。

#### 3.6.2 上下文窗口管理

**上下文解析优先级**：

1. 显式覆盖 `contextTokensOverride`→ 直接使用
2. 配置参数 `context1m: true`(Anthropic 1M模型) → 1,048,576 tokens
3. 模型注册表 → 从`models.json`或`provider catalog`发现
4. 配置文件覆盖 → `models.providers.*.models[].contextWindow`
5. Fallback → 使用传入的默认值

**上下文窗口守卫** (`src/agents/context-window-guard.ts`):

- `CONTEXT_WINDOW_HARD_MIN_TOKENS = 16_000`// 低于此值阻断运行
- `CONTEXT_WINDOW_WARN_BELOW_TOKENS = 32_000`// 低于此值警告
- 三种检查结果: `shouldWarn`(窗口 < 32K tokens), `shouldBlock`(窗口 < 16K tokens)

#### 3.6.3 上下文压缩

压缩机制 (`src/agents/compaction.ts`): 当会话接近或超过上下文窗口时自动触发。

```xml-dtd
旧消息 ──→ LLM 总结 ──→ 紧凑摘要条目 ──→ 持久化到 JSONL
```

**核心流程**：

1. **Token估算** (`estimateMessagesTokens`) - 计算当前消息总token
2. **分块** (`chunkMessagesByMaxTokens`) - 按token限制分块
3. **摘要生成** (`summarizeWithFallback`) - 带重试的摘要生成
4. **历史裁剪** (`pruneHistoryForContextShare`) - 裁剪旧消息保持预算

**自适应分块**:

- `BASE_CHUNK_RATIO = 0.4`// 基础分块比例
- `MIN_CHUNK_RATIO = 0.15`// 最小分块比例
- `SAFETY_MARGIN = 1.2`// 20%缓冲补偿估算误差
- 当消息平均大小 > 上下文10%时，自动减小分块比例。

#### 3.6.4 上下文剪枝

与压缩的区别:

| 特性     | Compaction   | Pruning                |
| -------- | ------------ | ---------------------- |
| 作用范围 | 整个历史     | 仅toolResult消息       |
| 持久化   | ✓ 写入JSONL  | ✗ 仅内存               |
| 触发时机 | 接近窗口上限 | 每次请求前 (TTL过期时) |
| 内容变更 | 生成摘要     | 软修剪/硬清除          |

**剪枝配置** (`src/agents/pi-extensions/context-pruning/settings.ts`):

```xml-dtd
DEFAULT_CONTEXT_PRUNING_SETTINGS = {
  mode: "cache-ttl",
  ttlMs: 5 * 60 * 1000,  // 5分钟TTL
  keepLastAssistants: 3,  // 保护最后3条助手消息
  softTrimRatio: 0.3,     // 上下文占用 > 30%触发软修剪
  hardClearRatio: 0.5,    // 上下文占用 > 50%触发硬清除
  minPrunableToolChars: 50_000,
  softTrim: {
    maxChars: 4_000,      // > 4K字符触发软修剪
    headChars: 1_500,     // 保留头部1500字符
    tailChars: 1_500,     // 保留尾部1500字符
  },
  hardClear: {
    enabled: true,
    placeholder: "[Old tool result content cleared]",
  },
}
```

**剪枝执行流程** (`src/agents/pi-extensions/context-pruning/pruner.ts`):

```xml-dtd
1. 检查TTL是否过期
   ↓ 过期
2. 计算上下文占用比例
   ↓ 超过softTrimRatio
3. 软修剪：对可修剪工具结果截取head + tail
   ↓ 仍超过hardClearRatio
4. 硬清除：替换为占位符
```

**保护机制**：

- 不修改用户/助手消息
- 跳过包含图片的toolResult
- 保护bootstrap阶段消息（第一条用户消息之前）
- 保护最后N条助手消息之后的工具结果

#### 3.6.5 工具结果上下文守卫

(`src/agents/pi-embedded-runner/tool-result-context-guard.ts`)

- **单条工具结果限制**: `SINGLE_TOOL_RESULT_CONTEXT_SHARE = 0.5`// 单条最多占上下文50%
- **估算系数**: `TOOL_RESULT_CHARS_PER_TOKEN_ESTIMATE = 2`// 更保守的估算
- **执行逻辑**: 每条工具结果限制: `maxSingleToolResultChars = contextWindowTokens * 2 * 0.5` 总上下文预算 (75% headroom): `contextBudgetChars = contextWindowTokens * 4 * 0.75` 超预算时压缩最旧的工具结果，替换为`"[compacted: tool output removed to free context]"`

#### 3.6.6 运行时上下文注入

- **默认注入文件**（如果存在）: `AGENTS.md`- 项目规则 `SOUL.md`- 角色定义 `TOOLS.md`- 工具指南 `IDENTITY.md`- 身份信息 `USER.md`- 用户偏好 `HEARTBEAT.md`- 心跳状态 `BOOTSTRAP.md`- 首次运行引导
- **截断配置**: `{  "agents": {    "defaults": {      "bootstrapMaxChars": 20000,     // 单文件上限      "bootstrapTotalMaxChars": 150000 // 总上限    }  } }`
- **压缩后上下文刷新**: 压缩完成后，重新注入`AGENTS.md`中的关键章节（## Session Startup, ## Red Lines），确保模型在压缩后仍遵循关键规则。

#### 3.6.7 检查与调试命令

```shell
/status           # 快速查看窗口占用率 + 会话设置
/context list     # 查看注入文件大小、工具schema大小
/context detail   # 详细分解各组件大小
/usage tokens     # 每次回复显示token使用量
/compact          # 手动触发压缩
```

#### 3.6.8 关键配置汇总

```json
{
  "agents": {
    "defaults": {
      // 上下文窗口
      "contextTokens": 200000,
      // Bootstrap注入
      "bootstrapMaxChars": 20000,
      "bootstrapTotalMaxChars": 150000,
      // 压缩配置
      "compaction": {
        "mode": "auto",
        "targetTokens": 0.7  // 目标占用率
      },
      // 剪枝配置
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "5m",
        "keepLastAssistants": 3,
        "softTrimRatio": 0.3,
        "hardClearRatio": 0.5
      }
    }
  },
  // 模型上下文窗口覆盖
  "models": {
    "providers": {
      "anthropic": {
        "models": [
          {
            "id": "claude-sonnet-4",
            "contextWindow": 200000
          }
        ]
      }
    }
  }
}
```

### 3.7 SubAgent架构详解

#### 3.7.1 核心概念

**SubAgent（子智能体）**是从现有Agent运行中生成的**后台独立运行实例**。它们在独立的会话中执行任务，完成后将结果自动**通告**回请求者的聊天渠道。

**关键特征**:

- **会话隔离**: 每个SubAgent拥有独立的会话键`agent:<agentId>:subagent:<uuid>`
- **后台执行**: 非阻塞式运行，支持并行处理
- **结果通告**: 完成时自动向父会话推送结果摘要
- **嵌套支持**: 支持多层嵌套（最大5层深度，推荐2层）

#### 3.7.2 架构组件

**会话键系统**:

| 深度 | 会话键格式                                   | 角色                     | 能否派生子智能体         |
| ---- | -------------------------------------------- | ------------------------ | ------------------------ |
| 0    | `agent:<id>:main`                            | 主智能体                 | 总是可以                 |
| 1    | `agent:<id>:subagent:<uuid>`                 | 子智能体（编排者）       | 仅当`maxSpawnDepth >= 2` |
| 2    | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | 子子智能体（叶子工作者） | 永远不能                 |

**注册表核心数据结构** (`subagent-registry.types.ts:6-35`):

```java
type SubagentRunRecord = {
  runId: string;                // 运行标识符
  childSessionKey: string;      // 子会话键
  requesterSessionKey: string;  // 请求者会话键
  requesterOrigin?: DeliveryContext; // 请求者来源（渠道、账号等）
  task: string;                 // 任务描述
  cleanup: "delete" | "keep";   // 清理策略
  label?: string;               // 显示标签
  model?: string;               // 使用的模型
  runTimeoutSeconds?: number;   // 运行超时
  spawnMode?: SpawnSubagentMode; // 运行模式
  createdAt: number;            // 创建时间
  startedAt?: number;           // 开始时间
  endedAt?: number;             // 结束时间
  outcome?: SubagentRunOutcome; // 运行结果
  suppressAnnounceReason?: "steer-restart" | "killed"; // 抑制通告原因
  endedReason?: SubagentLifecycleEndedReason; // 结束原因
};
```

**核心职责**:

1. **运行跟踪**: 维护所有活跃和历史SubAgent运行记录
2. **生命周期监听**: 通过`onAgentEvent`监听`lifecycle`事件（start/error/end）
3. **持久化**: 运行记录持久化到磁盘，支持网关重启后恢复
4. **级联停止**: 停止父运行时自动停止所有子运行
5. **孤儿检测**: 恢复时检测并清理孤儿运行（缺失会话条目）

**派生逻辑核心流程** (`subagent-spawn.ts:166-550`):

```xml-dtd
1. 权限与深度检查
   - 检查调用者深度 < maxSpawnDepth
   - 检查活跃子运行数 < maxChildrenPerAgent
   - 检查agentId允许列表
   ↓
2. 创建子会话
   - 生成子会话键: agent:<id>:subagent:<uuid>
   - 通过sessions.patch设置spawnDepth
   - 设置模型和思考级别
   ↓
3. 线程绑定（可选）
   - 调用subagent_spawning钩子准备线程绑定
   - 失败时回滚删除会话
   ↓
4. 启动子运行
   - 构建子智能体系统提示
   - 调用gateway.agent()启动运行
   - 使用专属lane: AGENT_LANE_SUBAGENT
   ↓
5. 注册运行记录
   - 调用registerSubagentRun()注册到registry
   - 开始等待完成
   - 触发subagent_spawned钩子
```

**通告机制核心流程** (`subagent-announce.ts:1053-1382`):

```xml-dtd
1. 等待运行结束
   - 等待嵌入式运行完成（如果是嵌入式）
   - 调用agent.wait等待运行完成
   - 读取最新助手回复或工具结果
   ↓
2. 构建通告消息
   - 提取运行结果文本
   - 计算运行统计（运行时间、token使用量、成本）
   - 生成状态标签（成功/超时/失败）
   ↓
3. 确定投递目标
   - 检查线程绑定路由（bound模式）
   - 调用subagent_delivery_target钩子（hook模式）
   - 回退到请求者来源（fallback模式）
   ↓
4. 投递通告
   - 直接投递：调用gateway.agent()或gateway.send()
   - 队列投递：当请求者忙时入队等待
   - 嵌套处理：如果请求者是子智能体，向上冒泡
   ↓
5. 清理
   - 更新会话标签（如果有）
   - 删除子会话（如果cleanup: "delete"）
   - 触发subagent_ended钩子
```

**嵌套通告冒泡**: 如果请求者子智能体已结束，通告会向上冒泡到其父会话。

#### 3.7.3 配置与限制

**核心配置项**:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,           // 最大派生深度（1-5，默认1）
        "maxChildrenPerAgent": 5,     // 每个会话最大活跃子运行数（1-20）
        "maxConcurrent": 8,           // 全局并发上限（默认8）
        "runTimeoutSeconds": 900,     // 默认超时（0=无超时）
        "archiveAfterMinutes": 60,    // 自动归档时间（默认60分钟）
        "model": "claude-3-haiku",    // 子智能体默认模型
        "thinking": "medium",         // 默认思考级别
      }
    },
    "list": [{
      "agentId": "orchestrator",
      "subagents": {
        "allowAgents": ["*"],         // 允许派生任意agentId
      }
    }]
  },
  "tools": {
    "subagents": {
      "tools": {
        "deny": ["gateway", "cron"],  // 工具黑名单
        "allow": ["read", "exec"],    // 工具白名单
      }
    }
  }
}
```

**工具策略**:

- **叶子子智能体**: 无会话工具（`sessions_*`）
- **编排者子智能体**（深度1，当maxSpawnDepth >= 2）: 获得`sessions_spawn`、`subagents`、`sessions_list`、`sessions_history` 仍被拒绝: `sessions_send`、`sessions_delete`等系统工具

#### 3.7.4 插件钩子系统

| 钩子名称                   | 触发时机     | 用途                   |
| -------------------------- | ------------ | ---------------------- |
| `subagent_spawning`        | 派生前       | 准备线程绑定，验证权限 |
| `subagent_spawned`         | 派生成功后   | 记录日志，更新UI状态   |
| `subagent_delivery_target` | 确定投递目标 | 自定义通告路由         |
| `subagent_ended`           | 运行结束     | 清理资源，发送告别消息 |

#### 3.7.5 并发与队列

- **Lane系统**: 子智能体使用专属`Subagent`lane
- **并发控制**: 全局并发上限由`maxConcurrent`控制（默认8） 每个会话的子运行数由`maxChildrenPerAgent`控制（默认5）
- **队列集成**: 当请求者会话忙时，通告会被入队等待

#### 3.7.6 典型场景

1. **并行研究**: `用户: "研究这三个主题并生成报告" 主智能体:  - sessions_spawn(task: "研究主题A", label: "research-a")  - sessions_spawn(task: "研究主题B", label: "research-b")  - sessions_spawn(task: "研究主题C", label: "research-c") [等待通告...] research-a: ✅ 完成 - [结果摘要] research-b: ✅ 完成 - [结果摘要] research-c: ✅ 完成 - [结果摘要] 主智能体: 综合结果生成最终报告`
2. **编排者模式** (maxSpawnDepth=2): `用户: "重构这个大型项目" 主智能体:  - sessions_spawn(task: "协调重构工作", agentId: "orchestrator", label: "refactor-coordinator") refactor-coordinator（深度1编排者）:  - sessions_spawn(task: "重构模块A", label: "worker-a")  - sessions_spawn(task: "重构模块B", label: "worker-b")  - sessions_spawn(task: "重构模块C", label: "worker-c") [等待子运行通告...] worker-a: ✅ 完成 worker-b: ✅ 完成 worker-c: ✅ 完成 refactor-coordinator: 综合结果，通知主智能体 主智能体: 向用户报告完成`
3. **线程绑定会话**: `用户（在Discord线程中）: "监控这个服务的性能" 主智能体:  - sessions_spawn(task: "启动性能监控", thread: true, mode: "session") [Discord扩展创建专用线程] [子智能体在专用线程中运行] 用户（在同一Discord线程）: "当前状态如何？" [消息路由到绑定的子智能体会话] 子智能体: "当前CPU 45%, 内存 2.1GB..." 用户: "/unfocus" [解除线程绑定，后续消息路由回主智能体]`

#### 3.7.7 总结

**SubAgent架构的设计哲学**:

1. **隔离与独立**: 每个子智能体在独立会话中运行，拥有独立的上下文、token配额和工具集
2. **推式通知**: 结果自动通告，避免轮询开销和复杂性
3. **嵌套编排**: 支持多层嵌套，实现复杂的编排模式
4. **资源可控**: 通过深度限制、并发上限和工具策略控制资源消耗
5. **可扩展性**: 通过插件钩子系统支持自定义行为（线程绑定、路由策略等）

**关键设计决策**:

- 使用会话键深度而非独立字段跟踪嵌套层级
- 通告机制而非返回值，支持异步和非阻塞语义
- 工具策略按深度区分，编排者获得管理工具而工作者专注任务
- 持久化注册表确保网关重启后不丢失运行状态

------

**篇幅原因更多精彩内容在《深入理解OpenClaw技术架构与实现原理（下）》，请持续关注～**