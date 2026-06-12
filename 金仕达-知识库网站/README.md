# 金仕达 CTRM 系统知识库

> 大宗商品贸易 ERP 系统知识库 — 基于 MkDocs Material 构建，支持全文搜索、标签分类、自动导航

---

## 快速启动

| 操作 | 方法 |
|------|------|
| **启动** | 双击 `start.vbs`（后台静默运行，无 CMD 窗口） |
| **访问** | 浏览器打开 http://localhost:8899 |
| **关闭** | 双击 `stop.bat` |

> 首次启动需要安装依赖，可双击 `start.bat` 查看安装过程（之后用 `start.vbs` 即可）

---

## 文件结构总览

```
金仕达/
│
├── 🚀 启动 & 配置
│   ├── start.vbs                 # 静默启动脚本（双击使用，无窗口）
│   ├── start.bat                 # 带窗口的启动脚本（调试用，首次安装依赖时可见）
│   ├── stop.bat                  # 关闭服务脚本（双击停止后台进程）
│   ├── mkdocs.yml                # MkDocs 全局配置（主题、插件、Markdown 扩展）
│   └── requirements.txt          # Python 依赖清单
│
├── 📝 知识库源文件 (docs/)
│   ├── .pages                    # 顶级导航排序控制
│   ├── index.md                  # 知识库首页（总导航、快速查找、最近更新）
│   │
│   ├── 公司代码文档/              # 代码调用链分析、类/方法详解
│   │   ├── .pages                # 本目录导航排序（index 在前，其余自动追加）
│   │   ├── index.md              # 模块索引页（按模块分类汇总）
│   │   └── ExecuteHMEFlowTask调用链分析文档.md
│   │
│   ├── 公司需求文档/              # 业务需求、功能规格
│   │   ├── .pages
│   │   └── index.md              # 模块索引页
│   │
│   ├── 问题排查记录/              # 故障排查、根因分析、经验总结
│   │   ├── .pages
│   │   └── index.md              # 模块索引页 + 通用排查步骤
│   │
│   ├── 业务概念/                  # CTRM 业务术语、流程说明
│   │   ├── .pages
│   │   └── index.md              # 术语速查表
│   │
│   └── 模板/                     # 标准文档模板
│       ├── .pages                # 模板排序（固定顺序）
│       ├── index.md              # 模板总览 + 命名规范
│       ├── 需求文档模板.md
│       ├── 代码分析模板.md
│       └── 问题排查模板.md
│
├── 📦 原始资料（未迁入 docs）
│   ├── 公司代码文档/              # 原始代码文档（已复制到 docs/ 中）
│   │   └── ExecuteHMEFlowTask调用链分析文档.md
│   └── 公司需求文档/              # 原始需求资料
│       └── Greenlist相关/
│           └── geenlist price 需求方案.xlsx
│
└── 🌐 构建产物 (site/)            # 自动生成的静态网站（无需手动管理）
```

---

## 各文件详细说明

### 🚀 启动 & 配置

#### `start.vbs` — 主启动入口

- **用途**：日常使用的启动方式，双击即可
- **行为**：在后台静默启动 MkDocs 服务，不弹出 CMD 窗口
- **原理**：通过 VBScript 的 `WScript.Shell.Run` 以隐藏窗口模式运行命令

#### `start.bat` — 调试启动脚本

- **用途**：首次运行或排查问题时使用
- **行为**：
  1. 检查 Python 是否已安装
  2. 检查 `mkdocs-material` 是否已安装，未安装则自动 `pip install`
  3. 在前台启动服务（CMD 窗口可见，关闭窗口即停止服务）

#### `stop.bat` — 关闭服务

- **用途**：停止后台运行的 MkDocs 服务
- **行为**：通过 `wmic` 查找 mkdocs 进程并 `taskkill` 终止

#### `mkdocs.yml` — 全局配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `theme` | Material | Material for MkDocs 主题，支持深色/浅色切换 |
| `language` | zh | 中文界面 |
| `plugins.search` | zh + en | 中英文全文搜索 |
| `plugins.awesome-pages` | 启用 | 自动发现新文档，无需手动维护导航 |
| `markdown_extensions` | 多项 | 代码高亮、表格、任务列表、Admonition 提示框等 |

#### `requirements.txt` — Python 依赖

```
mkdocs-material>=9.5.0            # Material 主题
mkdocs-awesome-pages-plugin>=2.9.0 # 自动导航发现插件
```

---

### 📝 docs/ — 知识库源文件

这是你日常编辑文档的地方。所有 `.md` 文件修改后，MkDocs 会自动重新构建并刷新浏览器。

#### `.pages` 文件 — 导航排序控制

每个目录下的 `.pages` 文件控制该目录在导航栏中的显示方式：

```yaml
title: 代码分析        # 导航栏中显示的名称
nav:
  - index.md           # 概览页固定在第一个
  - ...                # 其余文件自动追加到这里（按文件名排序）
```

**关键规则**：
- `...` 代表"本目录下未被显式列出的所有文件"
- 新文档丢进目录后会自动出现在 `...` 的位置
- 不需要修改 `mkdocs.yml` 或 `.pages` 文件

#### 各模块说明

| 模块 | 目录 | 放什么 | 命名规范 |
|------|------|--------|----------|
| **代码分析** | `公司代码文档/` | 调用链分析、类/方法详解、架构设计 | `类名或功能名分析文档.md` |
| **需求文档** | `公司需求文档/` | 业务需求、功能规格、接口定义 | `REQ-XXX-简短描述.md` |
| **问题排查** | `问题排查记录/` | 故障排查记录、解决方案、经验总结 | `YYYY-MM-DD-问题简述.md` |
| **业务概念** | `业务概念/` | CTRM 术语解释、业务流程说明 | `概念名称.md` |
| **文档模板** | `模板/` | 标准模板，新建文档时复制使用 | — |

#### Front Matter 元数据

每篇文档开头应包含 YAML 元数据（模板中已预设）：

```yaml
---
title: 文档标题
tags: [日结, EOD, Quartz]       # 标签，用于搜索和分类
module: bcadmin-system            # 所属系统模块
date: 2026-06-01                  # 创建日期
type: code-analysis               # 类型：code-analysis | requirement | troubleshooting | concept
related: [EOD日结流程]            # 关联文档
---
```

---

### 📦 原始资料

这些是知识库搭建前已有的文件，保留作为原始备份：

| 路径 | 内容 | 状态 |
|------|------|------|
| `公司代码文档/ExecuteHMEFlowTask调用链分析文档.md` | 日结流程代码分析 | ✅ 已迁入 `docs/公司代码文档/` 并添加元数据 |
| `公司需求文档/Greenlist相关/geenlist price 需求方案.xlsx` | Greenlist 定价需求方案 | ⏳ 待迁入（xlsx 文件建议放入 `docs/公司需求文档/` 并在对应文档中引用） |

---

### 🌐 site/ — 构建产物

`mkdocs build` 或 `mkdocs serve` 时自动生成的静态 HTML 网站。**无需手动管理**，删除后重新构建即可恢复。

---

## 日常使用指南

### 新增一篇文档

1. 从 `docs/模板/` 复制对应模板
2. 粘贴到目标目录，按命名规范重命名
3. 替换模板中的占位符内容
4. 保存 → 浏览器自动刷新，文档自动出现在导航栏

### 搜索文档

- 打开浏览器页面，点击右上角搜索图标（或按 `S` 键）
- 支持中英文关键词，支持模糊匹配

### 与 Obsidian 配合

- 用 Obsidian 打开 `docs/` 文件夹作为 Vault
- Front Matter 中的 `tags` 字段可被 Obsidian 直接识别
- 在 Obsidian 中编辑的 `.md` 文件会触发 MkDocs 热更新

---

## 技术信息

| 项目 | 版本/说明 |
|------|----------|
| Python | 3.13.7 |
| MkDocs | 1.6.1 |
| Material Theme | 9.7.6 |
| awesome-pages | 2.10.1 |
| 服务端口 | 8899 |
| 服务地址 | http://localhost:8899 |

---

## 环境搭建（新机器）

```bash
# 1. 安装 Python 3.8+
# 2. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 启动
# 双击 start.vbs，或命令行执行：
mkdocs serve --dev-addr localhost:8899
```

---

*文档生成日期: 2026-06-02*
