# 浏览器自动化工具选型指南：MCP 对比与 playwright-cli 实战

> **导读**：当 AI Agent 需要「看懂网页、点按钮、填表单」时，浏览器自动化成了刚需。但工具太多——playwright-mcp、browser-use、chrome-mcp、playwright-cli……到底该选哪个？本文综合两篇掘金实战文章，从**工具对比、踩坑经验、使用方法、选型建议**四个维度，帮你一次理清。

---

## 一、先搞清楚：你要解决什么问题？

浏览器自动化工具看似都在「操控浏览器」，但设计目标完全不同。选错工具，轻则 token 烧钱，重则 Windows 环境装不上。

| 场景类型 | 典型需求 | 推荐方向 |
|---------|---------|---------|
| **AI Agent 动态决策** | 让 Claude/GPT 理解页面、自主决定点哪里 | MCP 类（playwright-mcp / browser-use / chrome-mcp） |
| **固定流程脚本化** | 企业内网测试、定时批量操作、零人工干预 | playwright-cli |
| **复用已有 Chrome 登录态** | 不想重复登录、要用现有插件和 Cookie | chrome-mcp 或 playwright-cli `--profile` |
| **跨浏览器兼容性测试** | Chromium / Firefox / WebKit 都要测 | playwright-mcp |

**核心原则**：流程固定 → 别用 AI 逐步决策；需要 AI 理解页面 → 别写死 shell 脚本。

---

## 二、工具全景：6 个名字，3 条路线

### 2.1 MCP 浏览器服务器（给 AI 客户端用）

| 工具 | 维护方 | 底层引擎 | 一句话定位 |
|-----|--------|---------|-----------|
| **playwright-mcp** | 微软 | Playwright | 跨浏览器 MCP，用可访问性树快照，不依赖截图 |
| **browser-use** | 社区 | Playwright + Python | AI Agent 框架，自然语言驱动，每步调用 LLM |
| **chrome-mcp** | lxe | Chrome DevTools Protocol | 直连本地 Chrome，细粒度 CDP 控制 |

### 2.2 脚本化 CLI（给固定流程用）

| 工具 | 维护方 | 一句话定位 |
|-----|--------|-----------|
| **playwright-cli** | 微软 Playwright 团队 | 命令行直接操作浏览器，可输出 `.sh` 脚本，零 token |

### 2.3 踩坑中被淘汰的方案

| 工具 | 主要问题 |
|-----|---------|
| **browser-use**（固定流程场景） | 每步交互都调 LLM，token 消耗大 |
| **Agent Browser / Skyvern** | Windows 兼容性差，依赖、路径问题多 |
| **Playwright MCP 官方版**（脚本场景） | 需起 MCP Server + AI 中间层，不适合定时跑 sh |

---

## 三、三款 MCP 工具深度对比

> 原文：[3款浏览器 MCP 比较](https://juejin.cn/post/7552804183390289966)（作者：火车叼位，2025-09-23）

### 3.1 七个对比维度

1. **控制方式**：Playwright / CDP / 自研自动化
2. **页面感知**：截图 vs 可访问性树 vs DOM
3. **会话状态**：是否复用 profile / Cookie
4. **运行环境**：Node.js / Python / Chrome remote debugging
5. **MCP 工具集**：navigate、click、fill、snapshot 等
6. **安全与隐私**：登录态暴露面、隔离模式
7. **社区成熟度**：Star 数、文档、维护频率

### 3.2 核心对比表

| 维度 | playwright-mcp | browser-use | chrome-mcp |
|-----|----------------|-------------|------------|
| **控制引擎** | Playwright，支持 Chromium/Firefox/WebKit | Python + Playwright | Chrome DevTools Protocol |
| **页面快照** | 可访问性树（结构化，确定性高） | 状态快照 + 可选截图/视觉理解 | CDP 获取 DOM/元素/console |
| **登录态复用** | persistent profile、user-data-dir、扩展连接 | session persistence，视配置而定 | 天然复用本地 Chrome profile |
| **语言栈** | Node.js ≥18 | Python ≥3.11 | Node.js / Bun |
| **MCP 能力** | navigate/click/fill/snapshot/pdf/vision 等 | navigation/click/type/agent 工具集 | 细粒度 CDP 操作 |
| **社区 Star** | ≈ 20k（微软维护） | ≈ 70k（文档丰富） | ≈ 42（小众轻量） |
| **强项** | 跨浏览器、企业级稳定 | 自然语言 Agent、上手快 | 复用已有 Chrome、底层控制 |
| **弱项** | 浏览器 binary 体积大 | 每步 LLM 成本高 | 仅 Chrome、配置门槛高 |

### 3.3 共同点

- 都支持 **MCP 协议**，LLM 客户端可标准化调用
- 都能完成 navigate / click / fill / 获取页面状态
- 都**尽量避免纯视觉截图**作为主定位手段（browser-use 可辅助，但不是核心）
- 都支持某种形式的**状态持久化**
- 都可在**本地环境**运行，用户可控

### 3.4 差异与选型

| 差异项 | playwright-mcp | browser-use | chrome-mcp |
|-------|----------------|-------------|------------|
| 跨浏览器 | ✅ 强 | ⚠️ 偏 Chromium | ❌ 仅 Chrome |
| 结构化 vs 视觉 | 可访问性树为主 | 视觉辅助更灵活 | CDP/DOM 为主 |
| 已有浏览器复用 | profile + extension | 视配置 | ✅ 最方便 |
| 配置成本 | 中等 | 中等 | 较高（remote debug） |
| 适合场景 | 跨浏览器测试、企业 MCP | AI Agent 自然语言任务 | 深度 Chrome 控制、调试 |

**MCP 选型口诀**：

- 跨浏览器测试 → **playwright-mcp**
- 自然语言 Agent、Python 生态 → **browser-use**
- 复用本地 Chrome 登录态/插件 → **chrome-mcp**

---

## 四、实战踩坑：固定流程为什么不该用 MCP？

> 原文：[browser-use / Agent Browser / Playwright MCP 踩坑对比](https://juejin.cn/post/7630657629954228267)（作者：张海潮，2026-04-20）

作者场景：**Windows 企业内网**、流程固定、批量操作 + 自动化测试，不需要 AI 动态决策。

### 坑 1：browser-use —— 每步都在烧 token

流程：截图 → 发给 LLM → 模型返回操作 → 执行 → 再截图……

一个登录流程就消耗大量 token。步骤明确时，让模型「思考」纯属浪费。

### 坑 2：Agent Browser / Skyvern —— Windows 兼容性差

macOS/Linux 尚可，Windows 上依赖不全、路径转义报错、WSL 能跑主机不行。企业环境多数是 Windows，这条路基本堵死。

### 坑 3：Playwright MCP 官方版 —— 不是为脚本化设计

适合「让 Claude 帮你操浏览器」，不适合写固定 sh 脚本、定时跑、零人工干预。需要 MCP Server + AI 中间层，过重。

### 结论：playwright-cli 才是固定流程的最优解

| 对比项 | playwright-cli | browser-use | Playwright MCP | Selenium |
|-------|----------------|-------------|----------------|----------|
| Windows 兼容 | ✅ 好 | ⚠️ 一般 | ✅ 好 | ✅ 好 |
| Token 消耗 | ✅ 零 | ❌ 每步调 LLM | ❌ 需 AI 驱动 | ✅ 零 |
| 登录态复用 | ✅ `--profile` | ⚠️ 需手动处理 | ⚠️ 需手动处理 | ⚠️ 需手动处理 |
| 固定流程 | ✅ 最佳 | ❌ 杀鸡用牛刀 | ❌ 设计目标不同 | ✅ 可以 |
| 上手难度 | ✅ 低（CLI） | ⚠️ 中（Python） | ⚠️ 中（MCP 配置） | ❌ 高 |

---

## 五、playwright-cli 使用方法（固定流程首选）

### 5.1 安装

```bash
npm install -g @playwright/cli@latest
```

### 5.2 核心命令

| 命令 | 作用 |
|-----|------|
| `playwright-cli open` | 打开浏览器（headed/headless） |
| `playwright-cli goto <url>` | 导航到 URL |
| `playwright-cli fill <selector> <value>` | 填写表单 |
| `playwright-cli click <selector>` | 点击元素 |
| `playwright-cli screenshot` | 截图 |
| `playwright-cli snapshot` | 抓取页面快照（含元素结构） |

### 5.3 两个核心设计

#### （1）`--profile`：继承登录态

```bash
playwright-cli open --browser=chrome --profile=./.pw-profile --headed
```

`.pw-profile` 是持久化浏览器配置目录，Cookie、LocalStorage、Session 全部保留。

**好处**：

- 脚本里不用明文写密码
- 不用处理验证码、MFA
- 脚本更短，专注业务流程

> ⚠️ 把 `.pw-profile` 加入 `.gitignore`，不要提交仓库。

#### （2）输出 `.sh` 脚本：零 token 运行

```bash
#!/bin/bash
playwright-cli open --browser=chrome --profile=./.pw-profile --headed
playwright-cli goto https://your-app.com/dashboard
playwright-cli click e38
playwright-cli screenshot --filename=./doc/result.png
```

保存为 `run.sh`，`chmod +x run.sh`，之后 `./run.sh` 无限复用。

**成本控制姿势**：AI 只在「写脚本」时花一次 token，执行阶段零 API 调用。

### 5.4 标准操作流程

**Step 1：首次启动，手动登录**

```bash
playwright-cli open --browser=chrome --profile=./.pw-profile --headed
playwright-cli goto https://your-app.com
# 浏览器窗口打开后，手动登录
playwright-cli snapshot --depth=3
```

**Step 2：用 snapshot 获取元素 ID**

snapshot 输出示例：

```
e20: input[name="username"] - 用户名输入框
e25: input[name="password"] - 密码输入框
e32: button[type="submit"] - 登录按钮
```

`eXX` 就是后续 `click` / `fill` 的 selector。

**Step 3：固化为 sh 脚本**

```bash
#!/bin/bash
playwright-cli open --browser=chrome --profile=./.pw-profile --headed
playwright-cli resize 1920 1080
playwright-cli goto http://your-app.com/dashboard
playwright-cli screenshot --filename=./doc/01-dashboard.png

playwright-cli click e38
playwright-cli screenshot --filename=./doc/02-develop.png

playwright-cli click e39
playwright-cli screenshot --filename=./doc/03-controlled.png

echo "=== 完成 ==="
```

---

## 六、MCP 工具快速上手

### 6.1 playwright-mcp（Cursor / Claude Desktop 常用）

**适用**：在 AI 编程工具里让 Agent 操作浏览器做测试、抓页面信息。

**典型配置思路**（以 Cursor 为例）：

1. 安装 Node.js ≥18
2. 在 MCP 配置中添加 playwright-mcp server
3. Agent 通过 `snapshot` 获取可访问性树，再 `click` / `fill`

**特点**：结构化快照，不依赖视觉模型，跨浏览器。

### 6.2 browser-use

**适用**：Python 生态、自然语言描述任务、需要 Agent 自主探索页面。

**典型用法**：

1. `pip install browser-use`（Python ≥3.11）
2. 配置 LLM API Key
3. 用自然语言描述任务，Agent 逐步决策

**注意**：固定流程场景 token 成本高，不适合批量定时任务。

### 6.3 chrome-mcp

**适用**：必须复用本地 Chrome 已有登录态、插件、DevTools 能力。

**前置条件**：

1. Chrome 以 remote debugging 模式启动
2. 配置 MCP server 连接本地 Chrome 实例

**特点**：延迟低、控制细，但仅 Chrome，配置门槛较高。

---

## 七、一张图看懂怎么选

```
你的需求是什么？
│
├─ 流程固定（测试/批量/定时）
│   └─→ playwright-cli（零 token + --profile）
│
├─ AI 动态理解页面
│   ├─ 跨浏览器 → playwright-mcp
│   ├─ 自然语言 Agent + Python → browser-use
│   └─ 复用本地 Chrome → chrome-mcp
│
└─ Windows 企业内网 + 固定流程
    └─→ 避开 Agent Browser/Skyvern，优先 playwright-cli
```

---

## 八、常见问题

**Q：snapshot 的元素 ID（如 e38）每次会变吗？**

会。编号是动态生成的。建议在脚本里先跑一步 snapshot 确认，或改用稳定的 CSS selector。

**Q：headless 模式可以用吗？**

可以，去掉 `--headed` 即可。CI/CD 环境推荐 headless。

**Q：profile 目录可以多人共享吗？**

不推荐。每人登录态不同，各自维护 `.pw-profile`。

**Q：MCP 和 playwright-cli 能一起用吗？**

可以，但职责不同：MCP 给 AI 交互式操作用；playwright-cli 给固化脚本用。AI 生成 sh 脚本 → playwright-cli 执行，是推荐的人机协作姿势。

**Q：browser-use 完全不能用吗？**

不是。需要 AI **动态决策**、页面结构经常变、探索式任务时，browser-use 很合适。只是不适合「步骤写死的内网批量操作」。

---

## 九、总结

| 工具 | 一句话 | 最佳场景 |
|-----|--------|---------|
| **playwright-cli** | 命令行脚本，零 token | 固定流程自动化 |
| **playwright-mcp** | 微软出品，可访问性树 | 跨浏览器 + AI Agent |
| **browser-use** | Python Agent，自然语言 | 动态探索式任务 |
| **chrome-mcp** | CDP 直连 Chrome | 复用本地浏览器状态 |

**人机协作的正确姿势**：

> AI 负责生成脚本，playwright-cli 负责执行脚本——各司其职，才是正确的成本控制方式。

---

## 参考来源

- [browser-use / Agent Browser / Playwright MCP 踩坑对比——最后我选了 playwright-cli](https://juejin.cn/post/7630657629954228267) — 张海潮
- [3款浏览器 MCP 比较: playwright-mcp browser-use chrome-mcp](https://juejin.cn/post/7552804183390289966) — 火车叼位

---

*本文整理自掘金社区两篇实战文章，仅供技术选型参考。工具版本更新较快，部署前请以各项目官方文档为准。*
