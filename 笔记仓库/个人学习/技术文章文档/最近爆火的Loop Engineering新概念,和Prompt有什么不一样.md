# 我读完 Loop Engineering 三篇文章后的一些小感悟
文章顺列表:
> - [Loop Engineering 概念解析、思考与实践](https://mp.weixin.qq.com/s/ael7aIEoomk4AU84E-mpGg)
> - [Loop Engineering 实践指南：在 Code Buddy 中构建自主循环系统](https://mp.weixin.qq.com/s/YqIyL7uW4EV2r5HLDW7wcA)
> - [Prompt 被淘汰了？深度拆解 Loop Engineering，炒作还是趋势？](https://mp.weixin.qq.com/s/daezGa5JxGcl-FokX_-zvg)

---

## 一、读后感：三篇文章，三次认知刷新

上周五晚上，我在飞书知识库里连续刷到了三篇 Loop Engineering 的文章。顺序恰好是从浅到深——第一遍读完觉得自己懂了，第二遍读完发现自己根本没懂，第三遍读完才意识到，这东西跟我想的完全不一样。

### 第一篇文章：《Prompt 被淘汰了？深度拆解 Loop Engineering》

这篇像是一个全景地图。Addy Osmani 的定义很简洁——「Loop Engineering 就是用你设计的系统来替代你自己去 prompt agent」。

但真正让我停下来的是文章里这句话：

> **Boris Cherny（Anthropic Claude Code 负责人）："我不再手动提示 Claude 了。我有 loop 在跑，它们负责提示 Claude、决定下一步做什么。我的工作是写 loop。"**

一个做 Claude Code 的人说自己不再手写 prompt 了——这句话的分量，比任何趋势分析都重。

文章拆解的五大模块 + Memory，我看第一遍的时候觉得：这不就是定时任务 + Git Worktree + 文档 + MCP + 子进程 + 状态文件吗？每个词我都认识，拼在一起怎么就变成「新范式」了？

**这个疑问，我后来在实操里才真正解开。**

### 第二篇文章：《Loop Engineering 概念解析、思考与实践》

这篇补上了理论层面的关键区分——**Agent Loop ≠ Loop Engineering**。

Agent Loop 是底层执行机制：模型输出 Function Call → 执行 → 结果回传 → 再输出，这是 ReAct 模式的内置循环。Loop Engineering 是架在它上面的一层：**面向需求验收的外部闭环**。

类比很到位：ReAct 是工人砌墙，Loop Engineering 是项目经理编排工程。

另一个让我印象深刻的点是 **HITL（Human-in-the-Loop）压缩**。传统模式是「人在循环」——你给 Agent 任务 → 它出结果 → 你检查 → 发现问题 → 手动告诉它改。Loop Engineering 是把「人催 AI」这个环节从循环里拿掉，让模型自己闭环跑。人只在最后验收。

但文章也坦诚地说了：**Loop 不是银弹**。需求模糊时不适用，而且 Loop 对需求描述的要求比手动 Prompt 更高——开头没写清楚，会烧大量 token 但结果差。

### 第三篇文章：《Loop Engineering 实践指南：在 Code Buddy 中构建自主循环系统》

这篇是真正让我手痒的。它直接给了可操作的命令：

```bash
/goal all tests in test/auth pass and the lint step is clean
/goal all tests pass or stop after 20 turns
/loop 3m 检查一下流水线是否跑完
```

还有一个关键细节：`/goal` 的判断者**不是写代码的那个模型**，而是独立的小模型评估器。它返回三态结果：
- `ok: true` → 条件满足，完成
- `ok: false` → 继续下一轮
- `ok: false, impossible: true` → 目标不可达，立即停止

**让「判断是否完成」和「执行任务」用不同的模型——这个设计太妙了。** 它解决的正是我们最熟悉的问题：自己做的东西自己查，永远有盲区。

---

**三篇文章读完，我的结论是：必须自己动手试一下。不亲眼看一次它自己跑起来，所有的理解都停留在纸面上。**

---

## 二、实操：从 0 到 1 搭一个自动循环系统

### 选什么实验？

我决定不做一个纯 demo。选了一个**真实但可控**的任务：

> 每天自动检查项目代码仓库中是否存在不符合规范的导入语句（比如应该用 `@/` 别名但用了相对路径 `../../`），发现问题就自动修复并提交 PR。

这个任务的特点是：
- **需求明确**：检查规则可以写死在 Skill 里
- **验证可量化**：lint 脚本 exit code 就是客观标准
- **有真实价值**：我们团队确实有这个规范，但经常被忽略
- **风险可控**：只改 import 路径，不会破坏逻辑

### Step 1：写一个 Skill 固化规范

按照文章里的建议，不能每次都让 AI 重新「猜」我们的规范。先把规范写成 `SKILL.md`：

```markdown
# Import 规范检查与修复

## 项目约定
1. 所有内部模块导入必须使用 `@/` 别名，禁止使用相对路径（`../../`）
2. 第三方包导入使用包名
3. 导入顺序：第三方包 → 内部模块 → 相对路径（类型定义）

## 检查方法
运行 `pnpm lint:imports` 获取违规列表，exit code 0 表示全部合规

## 修复原则
- 只修改 import 语句，不修改任何业务逻辑
- 不确定路径映射时，在注释中标注 TODO
- 每次修复后重新运行检查验证

## 常见路径映射
- `../../components/` → `@/components/`
- `../../utils/` → `@/utils/`
- `../../hooks/` → `@/hooks/`
- `../../../shared/` → `@/shared/`
```

写这个 Skill 的时候，我想起文章里说的：**「一个简洁、无聊的描述，比一个聪明但模糊的描述更好用」**。所以我刻意把所有路径映射写得机械、明确，不留想象空间。

### Step 2：手动测试——让 AI 先在单次对话里修一个文件

在正式搭 Loop 之前，先手动跑一遍，确认 Skill 能被正确理解：

```
@Claude 使用 import-fix skill，检查 src/pages/login/index.tsx 的导入语句是否符合规范，不符合就修复
```

AI 读取了 SKILL.md，运行了 `pnpm lint:imports`，找到了 3 处违规，全部修复正确。

**手动验证通过，现在可以交给 Loop 了。**

### Step 3：搭第一个 Loop——定时巡检

用 `/loop` 命令设置一个每 2 小时检查一次的监控：

```bash
/loop 2h 使用 import-fix skill，检查整个 src/ 目录的 import 规范，如果发现违规就修复，修复结果写入 /tmp/import-fix-report.md
```

第一次手动触发：

```
[Loop 第1轮] 10:00 AM
  → 运行 lint:imports
  → 发现 12 处违规，分布在 8 个文件
  → 逐个文件修复
  → 重新检查：0 处违规 ✓
  → 写入报告：/tmp/import-fix-report.md
```

**第一个惊喜**：它确实是「修完再重新检查」的，不是一个一次性操作。文章里说的「自验证闭环」，在这里第一次亲眼看到。

但问题也来了——**它一次性改了 8 个文件**，我不敢直接合并。这个 Loop 的质量没问题，但我作为人的审查带宽跟不上了。

**这就是文章里说的 Orchestration Tax。** Worktree 消除了文件冲突，但你一天能认真 review 多少份产出，才是真正的上限。

### Step 4：加入 Sub-agent 审查——执行者和检查者分离

按文章的建议，不能让写代码的模型自己检查自己。我搭了一个两阶段的团队模式：

```
主 Agent（执行者）          →  修复 import
Sub Agent（审查者，不同模型） →  检查修复是否正确
                                - 是否误改了非 import 语句？
                                - 路径映射是否正确？
                                - 是否遗漏了违规项？
```

改成了工作流脚本：

```bash
# 第一遍：执行修复
/goad fix-eslint-errors

# 第二遍：独立审查（用更强的模型）
@Claude[Opus] 审查刚才的所有修改：
1. 是否只修改了 import 语句？有没有误改业务逻辑？
2. import 路径映射是否正确？用 @/ 别名是否正确对应了目录结构？
3. 修复后是否所有文件都能通过编译检查？
如果有任何问题，列出具体文件和行号。
```

**第二个惊喜出现了**：审查 Agent 真的发现了问题——有一处 import，执行 Agent 把它从 `../../utils/format` 改成了 `@/utils/format`，但实际上这个文件的正确路径应该是 `@/shared/utils/format`。因为项目里存在两个 `utils` 目录，Skill 里的映射规则不够精细。

**这就是「让两种不同模型对抗验证」的价值**——如果让同一个模型自己检查，它大概率会「觉得自己的映射没问题」。独立的审查者用更高的推理力度重新审视，才抓住了这个我大概率也会漏掉的错误。

### Step 5：改成 `/goal`——从定时触发到条件驱动

定时触发的问题在于：即使没有发现问题，Loop 也会跑。改成条件驱动的 `/goal`：

```bash
/goal pnpm lint:imports 返回 exit code 0，然后确认所有修改都已通过 review 并提交为 PR
or stop after 10 turns
```

这个命令的意思是：
- 持续运行，直到 import 检查完全通过
- 每轮修复后自动重新检查
- 最多跑 10 轮（兜底上限，防止 token 失控）
- 最终提交为 PR

跑的结果：

```
[Turn 1] lint → 12 errors → 修复 8 个 → lint → 4 errors
[Turn 2] lint → 4 errors → 修复 3 个 → lint → 1 error
[Turn 3] lint → 1 error → 修复 1 个（路径映射需要调整）
           → 审查 Agent 介入 → 确认修复正确
[Turn 4] lint → 0 errors ✓
           → 独立评估器判断 ok: true
           → 自动提交 PR
```

**第三个惊喜（或者说惊吓）**：我在晚上 11 点搭完这个，然后就去睡了。第二天早上醒来，发现这个 Loop 在凌晨 3 点自己触发了一轮（因为有人合了一个 PR，引入了新的违规 import），它在 3 轮内修完，提了一个新 PR，等我早上 review。

**这就是文章中说的「Loop 在无人值守的情况下工作」——我第一次体验到了。**

---

## 三、实操中踩到的坑

### 坑 1：Skill 的路径映射不够细

我的 SKILL.md 写了 4 条映射规则，但项目里实际有 10+ 种路径模式。Skill 不完整导致 Agent 在模糊情况下做出了错误映射。**解决方案**：不是让 AI 更聪明，而是让 Skill 更详细——我把所有路径映射补全，从 4 条扩展到 12 条。

**教训**：Loop 的质量上限 = Skill 的质量上限。Loop 不会「灵机一动」做对你没写清楚的事。

### 坑 2：第一次跑的时候忘了设兜底上限

我第一个 `/goal` 没写 `or stop after N turns`。结果有一次路径映射全错，它修了 → lint 不过 → 再修 → 还不过，循环了 7 轮才被我手动打断。**Token 消耗是正常情况的 3 倍。**

从那以后，所有 `/goal` 必带 `or stop after N turns`。

### 坑 3：审查 Agent 太强了，反而成了瓶颈

我用 Opus 做审查，发现它审得非常细，但一轮审查要 3-5 分钟。后来换成 Sonnet 做初审（过滤出可疑修改），只有 Sonnet 标记为「存疑」的才交给 Opus 做深度审查。**不是所有环节都需要最强模型，分级审查既保证质量又控制成本。**

### 坑 4：State File 只记了「做了什么」，没记「为什么」

文章强调 State File 要记录「为什么选 A 不选 B」，我一开始只记了执行结果（「12 处违规 → 12 处修复 ✓」）。后来有一次复杂映射失败，我回看 State File 发现根本不知道上次的决策逻辑是什么，没法排查。

**改成记录**：「第 3 处违规 `../../shared/utils/format` → 映射为 `@/shared/utils/format`，备选为 `@/utils/format`，选择依据：检查目录结构确认文件在 shared/utils 下」。

---

## 四、感言：Loop Engineering 真正教会我的五件事

### 1. 「设计 Loop」和「手动 Prompt」是两种完全不同的思维模式

手动 Prompt 时，你的注意力在「这一轮怎么做」。设计 Loop 时，你的注意力在「整个流程怎么收束」——终态怎么定义、验证怎么自动化、异常怎么处理、多久算超时。

这俩不是一个等级的脑力消耗。**Loop 更难，但杠杆更高。**

### 2. 验证逻辑比执行逻辑更重要

搭 Loop 的过程中，我花了 30% 的时间写执行逻辑（修复 import），花了 70% 的时间写验证逻辑（怎么确认修对了）。

一个跑偏的 Loop 比没有 Loop 更危险——它会自信地犯错，而且是在你不在场的时候。

### 3. 理解债是真实存在的

Loop 跑了一周后，我发现有好几个文件的修改历史里全是 AI 的提交记录。我读了其中两个，发现我完全不知道某段代码为什么要那样写——尽管它确实通过了所有检查。

**文章里说的「最舒服的姿势，很可能是最危险的」就是这个意思。** 从此我给自己定了规矩：AI 提的 PR，我至少读一遍核心逻辑，不只是看「测试全过」。

### 4. 状态外置是让 Loop 能「跨天工作」的隐形骨架

同一个 Loop 跑了 3 天，每次都能从上次停下的地方继续。这不是因为 AI 记性好——恰恰相反，每次新回合它都从头开始，但它读到 State File 里上一轮的结果后，能立刻接上。

**模型会忘，但磁盘不会。** 这个简单的道理，实操过一次才会刻进骨髓。

### 5. Loop 不是取代你，是放大你

一周后，我回头看那些被 Loop 自动修复的 import 问题——那些琐碎的、频繁的、但每次都要人工盯的事情，现在被自动化了。我节省下来的时间，用在了更有价值的系统设计和 Code Review 上。

但前提是：**我知道它做了什么、怎么做的、边界在哪里。** 如果我只是「按下启动键的人」，这种自动化最终会反噬。

---

## 写在最后

如果你也在读 Loop Engineering 的文章，我的建议是：**挑一个真实的、小范围的、有明确验收标准的任务，搭一个 Loop，让它跑 24 小时。** 

纸面上的理解和亲眼看到它半夜自己运行一轮、早上给你提了一个 PR 的体验，是完全不同的。

Loop Engineering 不是要淘汰 Prompt，而是把你的位置从「循环里的操作工」挪到了「循环之上的设计师」。挪对位置，它是放大器；挪错了，它是盲区加速器。

**Build the loop. Stay the engineer. 这句话，我一周前读的时候以为懂了。现在我确认我懂了。**

---

> **参考阅读**
> - [Loop Engineering 概念解析、思考与实践](https://mp.weixin.qq.com/s/ael7aIEoomk4AU84E-mpGg)
> - [Loop Engineering 实践指南：在 Code Buddy 中构建自主循环系统](https://mp.weixin.qq.com/s/YqIyL7uW4EV2r5HLDW7wcA)
> - [Prompt 被淘汰了？深度拆解 Loop Engineering，炒作还是趋势？](https://mp.weixin.qq.com/s/daezGa5JxGcl-FokX_-zvg)

---

*这篇文章是我的真实实验记录。如果你也在尝试 Loop Engineering，欢迎在评论区分享你的经验——踩过的坑、惊艳的时刻、或者对「认知投降」的担忧，都想听。*
