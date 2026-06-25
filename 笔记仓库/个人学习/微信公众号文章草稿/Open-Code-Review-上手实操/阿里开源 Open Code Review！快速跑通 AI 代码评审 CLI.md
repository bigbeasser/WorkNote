# 阿里开源 Open Code Review！快速跑通 AI 代码评审 CLI

> 参考来源：[大厂技术文章-DailyTech/阿里重磅开源！Open Code Review：一周 5k star，为你的代码保驾护航](../../大厂技术文章-DailyTech/阿里重磅开源！Open Code Review：一周 5k star，为你的代码保驾护航.md)  
> 开源地址：https://github.com/alibaba/open-code-review

---

很多小伙伴用 Claude Code 写代码越写越快，**评审却跟不上**——改动几百行，人工 CR 看不过来；让通用 Agent 审，又容易漏文件、评论位置还对不准。

今天快速带你跑通阿里开源的 Open Code Review（简称 OCR）**，一款专注「AI 审代码」的 CLI 工具。看完你能独立完成：**安装 → 配模型 → 审 diff → 扫全库**。

![封面](<file-20260624112659777 1.png>)

---

## 它是什么？一句话讲清

**Open Code Review = 给 Git 变更做 AI 代码评审的命令行工具。**

- 前身是阿里内部官方 CR 助手，**2 万月活、370 万次任务**验证过
- 开源一周 **5k Star**，命令叫 `ocr`
- 和「让 Claude 随便看看代码」不同：OCR 用**工程逻辑管住流程**（筛文件、打包、定位），Agent 只负责该推理的部分——**噪声更少，评论位置准确率 97%+**

可以把它想成：**AI 写代码是「厨师炒菜」，OCR 是「专职品控」**——专业的事交给专业的工具。

---

## 第一步：安装

前提：本机已装 **Node.js 18+**。

```bash
npm install -g @alibaba-group/open-code-review
ocr version
```

看到版本号就 OK，`ocr` 命令全局可用。

---

## 第二步：配置 LLM（必做）

审代码前要告诉 OCR 用哪家模型。交互式配置，跟着提示选就行：

```bash
ocr config provider    # 选内置供应商，或添加自定义 API
ocr config model       # 为当前供应商选模型
```

![配置模型](<file-20260624112659776.jpg>)

**小白提示**：provider 就是「模型从哪来」——OpenAI、Anthropic、通义等；配一次，后面反复用。

---

## 第三步：审代码变更（最常用）

进入任意 **Git 仓库**，根据场景选命令：

### 场景 A：审当前工作区改动（日常开发）

```bash
ocr review
```

会评审所有**暂存 + 未暂存 + 未追踪**的变更。改完代码、提交前跑一遍，很顺手。

### 场景 B：审分支对比（提 PR 前）

```bash
ocr review --from main --to feature-login
```

对比两个分支之间的 diff，适合合并前做最后一道检查。

### 场景 C：审某次提交

```bash
ocr review --commit abc123
```

### 场景 D：带上需求背景（减少误报）

```bash
ocr review --background "实现用户登录的手机号验证逻辑"
```

**为什么要加 background？** 就像跟同事说「这段代码是故意这么写的」——OCR 能区分 **by design** 和 **真 bug**，误报会少很多。

---

## 常用参数速查

| 参数 | 默认值 | 干什么 |
|------|--------|--------|
| `--repo` | 当前目录 | 指定 Git 仓库根目录 |
| `--format` | text | 输出 `text` 或 `json`（CI 用 json） |
| `--concurrency` | 8 | 同时审几个文件 |
| `--audience` | human | `human` 看进度；`agent` 只要结果 |
| `--background` | — | 需求背景，降误报 |
| `--preview` / `-p` | — | 只预览会审哪些文件，不耗 Token |

**记两个就够**：日常 `--background` 降误报；CI 里 `--format json --audience agent`。

---

## 第四步：全库扫描（可选）

`ocr review` 审 **diff（变更）**；`ocr scan` 审 **整份源码**——接手老项目、重构前体检时用。

```bash
# 扫整个仓库
ocr scan

# 先预览要扫哪些文件（不调用 LLM，不花钱）
ocr scan --preview

# 限制 Token 上限，防止大仓库失控
ocr scan --max-tokens-budget 500000
```

![成本预估](<file-20260624112659777.png>)

扫之前会打印 **Token 成本预估**，心里有个数再开跑。

---

## 第五步：团队规则（进阶）

想统一团队规范？在项目根建 `.opencodereview/rule.json`：

```json
{
  "rules": [
    {
      "path": "**/*.java",
      "rule": "金额计算必须使用 BigDecimal，禁止 double"
    }
  ]
}
```

**规则优先级**（从高到低）：命令行 `--rule` > 项目配置 > 用户全局 `~/.opencodereview/rule.json` > 系统默认（13 套语言规则开箱即用）。

调试某文件命中哪条规则：

```bash
ocr rules check src/main/Foo.java
```

---

## 一个真实开发场景

你刚用 Cursor 改完登录模块，准备 push：

```bash
git add .
ocr review --background "新增手机号+验证码登录"
# 看输出，修完 OCR 指出的问题
git commit -m "feat: 手机号登录"
```

**流程**：装 → 配模型 → 审 → 改 → 提交。不用等同事有空 CR。

---

## 和 Claude Code /review 怎么选？

| | Open Code Review | Claude Code /review |
|--|------------------|---------------------|
| 定位 | 专用 CR CLI | 通用 Agent 能力之一 |
| 准确率 | 更高，评论更准 | 召回更高，覆盖更全 |
| Token | 352K–743K，更省 | 2M+，更贵 |
| 适合 | 日常 CR、降噪 | 安全审计、宁可多查 |

**日常开发优先 OCR**；安全审计可以 OCR + CC 双跑。

---

## 小结

① **安装**：`npm i -g @alibaba-group/open-code-review`  
② **配模型**：`ocr config provider` + `ocr config model`  
③ **审变更**：`ocr review`（工作区）或 `--from/--to`（分支）  
④ **降误报**：加 `--background` 说明需求背景  
⑤ **全库扫**：`ocr scan --preview` 先看范围再扫  

---

以上就是 Open Code Review 上手全流程，**照着敲就能跑**。

GitHub：[https://github.com/alibaba/open-code-review  ]()
有问题欢迎评论交流，后续继续更新 AI 开发实用技巧！

