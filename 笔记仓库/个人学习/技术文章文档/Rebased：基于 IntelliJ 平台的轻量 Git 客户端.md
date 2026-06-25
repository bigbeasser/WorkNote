---
tags:
  - git
  - rebased
  - IntelliJ
  - 开发工具
  - 开源
created: 2026-06-24
category: 技术文章/开发工具
aliases:
  - Rebased Git Client
  - DetachHead rebased
source: https://github.com/DetachHead/rebased
---

# Rebased：基于 IntelliJ 平台的轻量 Git 客户端

> **一句话总结**：Rebased 是社区对 JetBrains 独立 Git 客户端的「复活版」——在 IntelliJ IDEA Community 的 Git 能力之上，剥离 IDE 臃肿插件，并针对「只搞 Git、不污染仓库」的场景做了专属优化。

> **项目地址**：[https://github.com/DetachHead/rebased](https://github.com/DetachHead/rebased)

---

## 一、Rebased 是什么？

Rebased 是一款**基于 IntelliJ 平台的开源 Git 客户端**。

它的本质可以理解为：

> **JetBrains IDE − 绝大多数 bundled 插件 + Git 集成保留 + 若干 Git 场景专属 UI 调整**

换句话说，你不是在用又一个「小型 Git GUI」，而是在用 **IntelliJ 社区版里那套经过大量工程验证的 Git 引擎**，只是外壳被刻意瘦身，专注做版本控制这一件事。

### 项目背景

| 维度 | 说明 |
|------|------|
| 作者 | [DetachHead](https://github.com/DetachHead) |
| 代码基座 | Fork 自 [JetBrains/intellij-community](https://github.com/jetbrains/intellij-community) |
| 前身参考 | [obiscr/intellij-community](https://github.com/obiscr/intellij-community)（早期独立 Git 客户端尝试） |
| 灵感来源 | JetBrains 曾短暂推出过独立 Git Client，但很快下线；社区诉求持续近十年 |
| 社区热度 | GitHub **~4.4k Stars**，**176 Forks**（截至 2026-06） |
| 最新版本 | **v1.1.4**（2026-06-22） |
| 许可证 | Apache 2.0（继承自 IntelliJ Community） |

Rebased 是对 JetBrains [短命的官方 Git Client](https://youtrack.jetbrains.com/issue/IJPL-72504/Make-git-client-a-standalone-app) 的开源复刻与延续。README 指出，相关 YouTrack 议题长期是 JetBrains 平台上**投票数最高的开放需求之一**——说明「只要 Git、不要整套 IDE」并非小众诉求，而是被官方长期忽视的真实痛点。

---

## 二、它解决哪些痛点？

### 2.1 核心痛点：「我只要 Git，为什么要装整个 IDE？」

日常 Git 操作——看 log、rebase、cherry-pick、解决冲突、interactive rebase——JetBrains 的 Git 集成公认是**第一梯队**。但完整 IntelliJ IDEA / WebStorm / PyCharm 意味着：

- 启动慢、内存占用高
- 大量与 Git 无关的语言插件、框架支持、索引分析
- 对「偶尔打开仓库看一眼历史」的场景严重 overkill

**Rebased 的定位**：保留 JetBrains Git 集成的全部能力，去掉 IDE 的「开发环境」包袱，做一个**专职 Git 工作台**。

### 2.2 官方迟迟不做的独立 Git Client

社区在 YouTrack 上呼吁 JetBrains 推出独立 Git 应用已接近十年，议题 [IJPL-72504](https://youtrack.jetbrains.com/issue/IJPL-72504/Make-git-client-a-standalone-app) 长期高票置顶。官方曾短暂试水后又撤回，Rebased 由社区接手这一空缺。

| 对比项 | 完整 JetBrains IDE | Rebased |
|--------|-------------------|---------|
| Git 能力 | 完整 | 完整（同源） |
| 语言/框架插件 | 大量 bundled | 移除，仅保留 Git 相关 |
| 启动与资源 | 重 | 相对轻量 |
| 定位 | 编码 IDE | Git 专用客户端 |

### 2.3 打开任意仓库时 `.idea` 目录污染

这是 Rebased **最具差异化**的痛点修复之一。

JetBrains IDE 默认会在项目根目录生成 `.idea/` 配置。与 `.vscode/` 不同，`.idea/` 里大量文件含**本机绝对路径**，通常**不适合提交到 Git**，但很多仓库的 `.gitignore` 并未排除它。

当你用 IDE 的 Git 功能去浏览一个「非 JetBrains 项目」的仓库时，常见后果是：

- 工作区出现未跟踪的 `.idea/` 文件
- 容易误提交，或每次打开都看到脏工作区
- 团队混用 VS Code / Vim / 其他 IDE 时尤其尴尬

**Rebased 的解法**：可在设置中关闭「在项目根目录存储项目设置」，改为将各项目配置集中存放到 IDE 全局配置目录下的统一 `.idea` 中——**打开别人的仓库，不再污染对方项目树**。

路径：`Settings > Appearance and Behavior > System Settings` → 取消勾选 **Store project settings in the project root directory**

### 2.4 Git Log 布局不符合「Git 优先」工作流

在标准 JetBrains IDE 中，Git Log 默认挤在底部 Tool Window，编辑区留给代码。对 Git GUI 用户而言，**分支图 / 提交历史才是主角**。

Rebased 默认将 **Git Log 放在主编辑器区域**，以图形化历史为中心；若你习惯 IDE 布局，也可在 `Settings > Version Control > Log` 中关闭 **Show the log in the editor window**，恢复底部面板模式。

### 2.5 轻量浏览代码时，语法高亮被付费插件「锁死」

IntelliJ Community 通过 TextMate Bundles 插件支持多种语言的语法高亮。但部分语言（如 Vue）的完整支持被放在付费 IDE / 插件里。

Rebased 的目标之一是：**不想为「看一眼 diff」安装臃肿语言插件**。因此额外内置了 Community 版没有的 TextMate bundle（目前已包含 **Vue**），后续可通过 Issue / PR 扩展更多语言。

---

## 三、功能一览

### 3.1 继承自 IntelliJ IDEA Community 的 Git 能力

Rebased 并非重新发明 Git GUI，而是直接继承 IntelliJ Community 的 Git 模块，包括但不限于：

- 可视化分支图与 Log 浏览
- Commit / Amend / Revert
- Merge、Rebase、Cherry-pick
- Interactive Rebase
- 三路合并与冲突解决 UI
- Blame、Compare with Branch、Show History
- Git hooks、子模块、LFS 等生态能力（随上游同步）

对于已经熟悉 IntelliJ Git 快捷键和操作习惯的用户，**零学习成本迁移**。

### 3.2 Rebased 独占特性

| 特性 | 说明 |
|------|------|
| **可定制 Git Log 位置** | 默认主编辑区展示；可切回 IDE 式底部 Tool Window |
| **禁用项目根 `.idea` 目录** | 配置集中存储，避免污染非 JetBrains 仓库 |
| **额外 TextMate Bundles** | 目前内置 Vue 高亮，无需安装完整 Vue 插件 |

---

## 四、安装方式

### Linux

从 [GitHub Releases](https://github.com/DetachHead/rebased/releases) 下载 **AppImage**。

推荐配合 [AppManager](https://github.com/kem-a/AppManager) 或 [Gear Lever](https://github.com/mijorus/gearlever) 安装到应用菜单并启用自动更新。

### Windows

**方式一**：Releases 页下载 `.exe` 安装包。

**方式二**：winget 一键安装：

```powershell
winget install detachhead.rebased --source winget
```

### macOS

**推荐**：Homebrew

```bash
brew install detachhead/tap/rebased
```

**手动安装**：下载 `.dmg` 后拖入 Applications。若提示「应用已损坏」，是因为未使用 Apple Developer 证书签名，执行：

```bash
xattr -rd com.apple.quarantine /Applications/Rebased.app
```

---

## 五、适用场景与选型建议

### 5.1 适合用 Rebased 的情况

- 你**认可 JetBrains Git 交互**，但不想为 Git 操作单独开完整 IDE
- 经常浏览、review **非 JetBrains 生态**的仓库，且不想产生 `.idea` 脏文件
- 需要 Interactive Rebase、图形化分支管理等「高级 Git GUI」能力
- 希望在 Windows / macOS / Linux 上使用**同一套** Git 客户端体验

### 5.2 可能不适合的情况

- 你需要在该工具内**深度编码**（重构、调试、测试运行）→ 请用对应语言 IDE
- 你偏好极简原生 Git GUI（如 GitKraken、Fork、命令行）且不接受 JetBrains 交互范式
- 机器内存极低（官方建议构建源码至少 8GB RAM；日常使用也需 JVM 开销）

### 5.3 与常见 Git 客户端对比（简表）

| 工具 | 底层引擎 | 优势 | 劣势 |
|------|---------|------|------|
| **Rebased** | IntelliJ Git 模块 | JetBrains 级 Git 操作、可禁 `.idea`、跨平台 | JVM 应用，体积与内存高于原生 GUI |
| **IntelliJ IDEA** | 同源 | 编码 + Git 一体 | 过重，污染 `.idea` |
| **GitKraken / Fork** | 自研 / libgit2 | 原生体验、启动快 | 交互模型与 JetBrains 不同 |
| **VS Code + Git Graph** | 内置 Git | 轻量、与 VS Code 一体 | 高级 Git 操作弱于 JetBrains |
| **命令行 git + tig/lazygit** | git CLI | 极轻、可脚本化 | 学习曲线、图形化弱 |

---

## 六、技术架构（简要）

```
JetBrains intellij-community (上游)
        │
        ├── 移除绝大多数 bundled 语言/框架插件
        ├── 保留 Git / VCS / 基础 Editor / TextMate 等核心模块
        └── Rebased 专属补丁
                ├── Git Log 默认布局调整
                ├── .idea 存储策略选项
                └── 额外 TextMate Bundles (Vue)
```

- **发布策略**：`master` 分支定期合并上游；正式 Release 从独立的 **release branch** 构建，与 IntelliJ Community 版本线对齐。
- **构建系统**：随上游迁移至 **Bazel**（仍在过渡中）；从源码构建需 IntelliJ IDEA 2023.2+、JBR 25（无 JCEF）、Bazel 插件。
- **技术栈**：Java ~50%、Kotlin ~37%、Python ~9% 等（与 intellij-community 一致）。

---

## 七、个人使用建议

若你已经在日常开发中使用 JetBrains 系 IDE，Rebased 最适合作为**「第二窗口」**：

1. **主 IDE** 负责写代码、跑测试、调试。
2. **Rebased** 负责跨仓库 log 浏览、复杂 rebase、冲突处理、历史考古。
3. 打开他人仓库前，先开启「禁用项目根 `.idea`」——保持工作区干净。

Windows 用户可通过 `winget install detachhead.rebased` 快速试用，迁移成本几乎为零。

---

## 八、参考链接

| 资源 | 链接 |
|------|------|
| GitHub 仓库 | [DetachHead/rebased](https://github.com/DetachHead/rebased) |
| Releases 下载 | [GitHub Releases](https://github.com/DetachHead/rebased/releases) |
| JetBrains 独立 Git Client 议题 | [IJPL-72504](https://youtrack.jetbrains.com/issue/IJPL-72504/Make-git-client-a-standalone-app) |
| 上游代码库 | [JetBrains/intellij-community](https://github.com/jetbrains/intellij-community) |
| 早期尝试 | [obiscr/intellij-community](https://github.com/obiscr/intellij-community) |

---

## 附录：关键设置速查

| 需求 | 设置路径 |
|------|---------|
| Git Log 改回底部面板 | Settings → Version Control → Log → 取消「Show the log in the editor window」 |
| 禁止在项目根生成 `.idea` | Settings → Appearance and Behavior → System Settings → 取消「Store project settings in the project root directory」 |
