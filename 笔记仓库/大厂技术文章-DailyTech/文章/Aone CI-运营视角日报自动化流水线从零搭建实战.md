---
tags:
  - tech-article
  - AI
  - CI-CD
  - Aone
  - Qwen
  - 运营自动化
  - 钉钉
created: 2026-06-29
category: 技术文章/AI
aliases:
  - Aone CI日报自动化
  - 火种起源 CI实战
  - 运营CI流水线
---

# Aone CI：运营视角日报自动化流水线从零搭建实战

> **原文链接**: [https://mp.weixin.qq.com/s/GNEshVzcCV5HvGJXSQ4W6w](https://mp.weixin.qq.com/s/GNEshVzcCV5HvGJXSQ4W6w)

> **原标题**: 火种&起源：一个运营从0到1搭建CI自动化流水线的实战记录

> **一句话总结**: 高德运营同学用 Aone CI 从零搭建「ODPS 取数 → Qwen 生成解读 → 钉钉推送 → Pages 部署」日报流水线，两条流水线分离、多分支 public 合并部署，附 10 条真实踩坑表。

> **前置知识检查**:
> - [ ] 了解 Git 分支与 Merge Request 基本概念
> - [ ] 了解 CI/CD 流水线（触发 → 步骤 → 产出）基本模型
> - [ ] 了解 Webhook 或钉钉机器人推送（可选）

## 原文

![图1](<assets/Aone CI-运营视角日报自动化流水线从零搭建实战/img_01.jpg>)

阿里妹导读

文章内容基于作者个人技术实践与独立思考，旨在分享经验，仅代表个人观点。

摘要

作为一名高德打车的区域运营同学，和常规运营同学一样，日常工作中需要大量时间和精力在盯数据、写日报、做分析上。半年前，我对"CI/CD"这个词一无所知，甚至不理解代码库、git存在的意义——认为那些都是开发同学才需要懂的东西。

但现在，我独立搭建了一套完整的日报自动化流水线：每天定时从ODPS取数、用Qwen大模型生成日报解读、自动推送钉钉群、自动部署到在线站点。整个流程无需人工干预，从数据到阅读只需要10分钟。

这篇文章不是技术科普，而是一个运营视角的真实实战记录——我是怎么从零开始，一步步踩坑、一步步用AI解决技术问题，最终把整套系统跑起来的。

一、背景：为什么运营要搞CI

**1.1 日报的痛点**

运营团队应该都需要有这样一份日报，要覆盖前一天的目标达成、大盘数据、商户异动、城市峰值、分时应答情况等诸多模块。以前这份日报的制作流程是这样的：

- 打开ODPS进行SQL取数
- 把数据复制到Excel里整理
- 手动写分析解读
- 排版成文档，发到钉钉群
- 如果要留档，还得手动上传到某个地方

每天至少花1小时，而且依赖人工读数和业务经验，分析质量高度依赖处理人的经验和细心程度。

**1.2 团队AI化的契机**

2026年初，我们团队开始全面推进AI工具落地。Qwen Code、提示词工程、自动化流程……大家都在探索怎么用AI把重复性工作自动化。

我的leader提出了一个想法：日报能不能自动化？ 每天的数据结构是固定的，分析框架是固定的，唯一变化的是数字本身——这不就是最适合自动化的场景吗？

**1.3 为什么选Aone CI**

说实话，一开始我根本不知道用什么工具。我尝试过几个方案：

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| 本地Python脚本 | 简单直接 | 每天要手动跑，电脑关了就无法运行 |
| 定时任务（crontab） | 能定时 | 依赖某台机器，不透明 |
| Aone CI流水线 | 云端运行、有日志、能定时触发 | YAML语法，零基础有学习成本 |

最终选Aone CI的原因很简单：我们的代码仓库就在Aone上，CI是现成的能力，不用额外搭环境。 而且团队里已经有同学在用CI做静态站点托管，有现成的经验可以参考。

二、第一次接触CI：从静态站点开始

**2.1 第一个任务：让HTML能被在线访问**

我的CI之旅不是从日报开始的，而是从一个更简单的需求开始——把HTML文件放到在线站点上。

在Aone代码库里有一个静态站点（Aone Pages），可以把HTML文件托管成在线页面。团队里其他同学已经搭好了这个站点，我需要做的是：把我生成的HTML文件推送到仓库的`public/`目录下，它就能自动部署到在线地址。

听起来很简单对吧？但实际操作起来，坑一个接一个。

**2.2 第一个坑：实战中理解代码库的分支隔离**

我在master分支的`public/`文件夹里放了一个HTML文件，然后发现——我自己的分支能看到这个文件夹，但其他同学的分支看不到。

我当时很困惑：明明在master里建了文件夹，为什么别人的分支没有？

后来问了AI才知道，这是Git分支隔离的正常现象。每个分支是独立的，`public/`文件夹只存在于创建或合并了它的那些分支上。要让别人的分支也有，需要每个人自己执行一次`git pull origin master`。

**2.3 第二个坑：master是保护分支**

更头疼的问题来了。我们仓库的master分支是受保护分支，不能直接push。每次往`public/`目录合入新的HTML文件，都需要提MR（Merge Request）审核。

这意味着：

- 每次上传HTML → 提MR → 等审核 → 合入master → 手动更新README（生成新的访问链接）
- 流程繁琐，效率很低

**2.4 用CI解决：自动更新README**

如果能配置一条流水线，在每次push HTML文件后自动生成README索引并推送回去，不就不用手动更新了吗？

这是我第一次真正动手配置CI流水线。 整个过程是在AI的辅助下一步步完成的，大致分为以下几步：

#### 第一步：申请PAT（个人访问令牌）

CI容器里要往仓库push代码，需要一个"通行证"——PAT（Personal Access Token）。CI自带的Token是只读的，不能push。

操作路径：打开 code.alibaba-inc.com → 右上角头像 → 设置 → Private Token → 重置并复制。

#### 第二步：配置Secrets

PAT不能明文写在YAML里（会泄露到日志中），需要通过仓库的变量管理配置为 Secrets 类型。

| 类型 | 引用语法 | 适用场景 |
| --- | --- | --- |
| Secrets | ${{ secrets.X }} | 敏感信息（Token、密码、API Key） |
| Variables | ${{vars.X}} | 非敏感配置（项目名、端点地址） |

千万别混用——用secrets语法引用Variables类型的变量，值会是空字符串。

#### 第三步：写YAML流水线

这是我写的第一条YAML流水线（`.aoneci/update-readme.yaml`），核心逻辑是：

- 检测本次push是否涉及`public/*.html`文件变更
- 如果有，执行scripts/update-readme.sh脚本重新生成README
- 用PAT把更新后的README推回当前分支

写YAML的过程充满了挫折感——语法错误不会报错，只是流水线不触发。比如`trigger`要写成`triggers`（复数），`run: |`要写成数组格式，`checkout`要写成`- uses: checkout`而不是`- checkout`。这些调试过程全部依赖AI读取运行日志，一步一步和AI共创问题的解决方案。在这个过程中，我深刻体会到网上那个梗——"我和AI对话的时候，就像绝望的李鸿章，不管他端上来什么，只能无能地点【接受并运行】"......

由此我总结出一个经验：不要从零写YAML，先复制仓库里已经跑通的流水线，再改。

**2.5 跑通的那一刻**

当我第一次看到流水线执行成功、README被自动推回分支的时候，那种成就感是真实的。

```
[INFO] 当前分支: qioyue_370902
[INFO] Token 长度: 20
[INFO] 检测到 HTML 变更: public/test_ci.html
[INFO] 推送到 origin/qioyue_370902（用户: judy.qy）
[OK] README 已自动推回 qioyue_370902
```

虽然只是一个简单的README自动更新，但它让我理解了CI的基本工作原理：触发条件 → 执行步骤 → 产出结果。这为后面搭建日报流水线打下了基础。

三、搭建日报自动化流水线

**3.1 整体架构设计**

有了CI的基础认知后，我开始设计日报自动化流水线。整体思路是：

```
定时触发 → 取数 → 生成日报 → 转HTML → 推钉钉 → 推仓库 → 自动部署
```

具体来说，分为7个步骤：

| 步骤 | 动作 | 工具/技术 |
| --- | --- | --- |
| 1 | FBI数据抓取 | DataClaw API |
| 2 | ODPS SQL执行 | MaxCompute（5个模块各配专属SQL） |
| 3 | AI生成日报 | Qwen大模型（自然语言总结） |
| 4 | Markdown转HTML | Python脚本 |
| 5 | 推送钉钉 | Webhook + 加签 |
| 6 | HTML留档 | git push到个人分支的public/目录 |
| 7 | 自动部署 | 触发deploy-pages流水线 |

**3.2 变量配置：一次配好，全仓库共享**

日报流水线需要很多配置：ODPS的AccessKey、Qwen的API Key、钉钉Webhook地址等等。

好消息是：代码库的变量配置是仓库级别共享的。只要在Aone CI的变量管理中配置一次，同仓库的所有YAML流水线都可以通过相同语法调用。

我配置的变量包括：

| 变量名 | 类型 | 用途 |
| --- | --- | --- |
| ODPS_ACCESS_ID | Secret | MaxCompute AccessKey ID |
| ODPS_ACCESS_KEY | Secret | MaxCompute AccessKey Secret |
| DASHSCOPE_API_KEY | Secret | Qwen大模型API Key |
| DINGTALK_WEBHOOK | Secret | 钉钉机器人Webhook URL |
| GIT_PUSH_TOKEN | Secret | PAT（用于HTML推送回仓库） |
| ODPS_PROJECT | Variable | ODPS项目名 |

这里有一个值得分享的经验：ODPS权限建议用团队公共账号。申请一个公共AccessKey，授权所需的数据表，然后统一配置到仓库Secrets中。这样：

- 避免个人AK泄露风险
- 人员变动无需更换凭证
- 新人上手零配置

**3.3 两条流水线的分离设计**

最终我搭建了两条独立的流水线：

流水线一：daily-report-auto（日报生成）

- 镜像：`python:3.11`
- 触发：工作日10:30定时 + 个人分支push
- 职责：取数 → 生成日报 → 推钉钉 → 推HTML到public/

流水线二：deploy-pages（站点部署）

- 镜像：`alios-8u`（自带jq + git）
- 触发：push到public/时实时触发 + 每天17:00定时兜底
- 职责：合并所有分支的public/内容 → 部署到生产站点

为什么要拆成两条？因为Aone CI的`uses:`组件运行在隔离容器中，python:3.11镜像缺少deploy-pages需要的jq工具，而且无法在流水线中补装。所以把"生成"和"发布"拆开，各用各的镜像，互不干扰。

四、并发问题：多人协作的终极挑战

日报流水线跑通后，我以为大功告成了。但很快遇到了一个更棘手的问题——多人协作时HTML互相覆盖。

**4.1 问题是怎么发生的**

我们团队只有一个Aone Pages静态站点，`deploy-pages`每次部署是全量替换（不是增量追加）。

场景还原：

- 我在个人分支生成了日报HTML → 推到`public/daily-report/` → 触发部署 → 站点上有了日报 ✅
- 其他同学往master分支合入了一个活动页面 → 触发master的deploy-pages → 用master的public/全量替换站点
- 我的日报消失了 ❌（因为master的public/里没有我的daily-report/）

核心矛盾：所有人都在各自分支生成HTML，但站点只有一份，每次部署都是全量替换。

**4.2 解决方案：每次部署前合并所有分支**

思路很明确：每次部署前，先把所有远程分支的 `public/` 内容合并到一起，再部署完整集合。

具体实现是在`deploy-pages.yaml`的部署步骤前加一个"合并"环节：

```
# 动态发现所有远程分支
git fetch origin --depth=1
ALL_BRANCHES=$(git branch -r | grep -v 'HEAD' | sed 's|origin/||' | tr -d ' ')
# 逐一拉取每个分支的public/内容
for branch in $ALL_BRANCHES; do
  git fetch origin $branch --depth=1 2>/dev/null || true
  git checkout origin/$branch -- public/ 2>/dev/null || true
done
# 当前触发分支的内容最后覆盖（保证最新变更优先）
git checkout HEAD -- public/ 2>/dev/null || true
```

这样无论谁触发部署，所有人的HTML都会先合并进来，再一起部署。

**4.3 为什么每个分支都要有deploy-pages.yaml**

Aone CI读取的是被推送分支上的YAML。如果你的分支上没有`deploy-pages.yaml`，你推`public/`时不会触发任何部署。

好消息是：所有分支的YAML内容完全一样，不用各自定制。 如果你是从master新建的分支，这个文件已经自动继承了。

**4.4 防护机制**

我设计了几层防护，确保系统健壮：

| 异常场景 | 防护措施 |
| --- | --- |
| 新分支没放yaml | 不会触发部署，不会覆盖别人（无害） |
| 新分支放了正确yaml | 自动合并所有分支内容后部署（安全） |
| 新分支放了错误yaml | 下次正确分支部署时自动恢复 |
| 站点被意外覆盖 | 每天17:00定时部署自动恢复完整内容 |

17:00的定时任务是一个兜底机制，应对极端情况。正常情况下，每次push触发的实时部署就已经包含了所有分支的内容。

**4.5 为什么不用[skip ci]防循环**

最初我想用`[skip ci]`标记来防止部署流水线重复触发，但后来发现`[skip ci]`会杀死所有流水线（包括日报生成流水线）。

更好的方案是用`paths`过滤：只在`public/**`有变更时才触发deploy-pages。这样不该跑的流水线不会被误杀。

五、经验总结与可复用模板

**5.1 新人接入最容易踩的坑（实战总结）**

以下是搭建CI流水线过程中真实踩过的坑，涵盖语法陷阱、环境隔离和平台机制差异，按配置流程顺序排列：

| # | 坑点 | 现象 | 根因 | 正确做法 |
| --- | --- | --- | --- | --- |
| 1 | YAML触发器关键字写错 | push后流水线列表无新任务 | 必须写 triggers:（复数），写成 trigger: 不报错但不生效 | triggers: 固定复数，下面嵌套 push: / schedule: |
| 2 | Secrets/Variables语法混用 | 环境变量为空，脚本报"key not found" | 两种类型引用语法不同，混用取空 | Secrets用 ${{ secrets.X }}，Variables用 ${{ vars.X }}；Variables需在YAML中显式export |
| 3 | git push报403 | fatal: The requested URL returned error: 403 | 阿里内网不支持 oauth2:TOKEN 格式 | 必须用 https://用户名:PAT@code.alibaba-inc.com/repo.git 格式 |
| 4 | uses:组件看不到前面装的工具 | apt install jq 成功但 uses: deploy-pages 报 "jq: command not found" | uses: 运行在完全隔离的容器，不继承run步骤的环境 | 拆成两条流水线，各用各的镜像 |
| 5 | $CI_COMMIT_BRANCH不存在 | fatal: invalid refspec 'HEAD:' | Aone CI没有此内置变量（不是GitLab CI） | 用 git rev-parse --abbrev-ref HEAD 动态获取分支名 |
| 6 | 定时任务写在个人分支不触发 | cron配了但到点无反应 | schedule调度器只从master分支读取配置 | YAML必须push到master；job内 git fetch + checkout 切个人分支执行 |
| 7 | cron时间差8小时 | 想10:30触发，凌晨2:30跑了 | Aone CI cron按北京时间CST解释，不是UTC | 直接写北京时间，如 "30 10 * * 1-5" |
| 8 | [skip ci]杀全局 | 循环解决了但日报流水线也不跑了 | [skip ci] 全局生效，所有流水线都不触发 | 用 paths 过滤精确控制触发范围，如 daily-report/** / public/** |
| 9 | 手动重跑用旧配置 | 改了YAML但重跑还是旧逻辑 | 重跑加载的是所选commit对应的YAML | 改完YAML先push新commit（不含[skip ci]），再触发新commit |
| 10 | run:多行语法报错 | YAML解析通过但执行报语法错误 | Aone CI的 run: 要求数组格式 | 写成 run: 下接 - \| 数组元素，不能用 run: \| |

**总结心法：** 遇到CI问题别自己死磕。把完整的报错日志复制给AI，让它帮你分析定位。配置CI的效率不取决于你记住了多少语法，而是你能不能快速定位问题。

**5.2 调试CI的正确姿势**

善用调试三板斧：查官方手册 → 对比已跑通的YAML → 加诊断输出。

遇到报错不要慌，把完整的日志信息复制给AI，让它帮你分析。 这是我整个CI搭建过程中最高效的调试方式。

**5.3 关键设计决策回顾**

| 决策 | 为什么这么做 |
| --- | --- |
| 全部部署在个人分支 | master有保护，无法直接push；个人分支无限制，PAT即可跑全流程 |
| 用独立流水线做部署 | 日报流水线的环境缺少发布所需的工具且无法补装，拆开后互不干扰 |
| 用paths而不是[skip ci]防循环 | [skip ci]会杀死所有流水线；paths只拦不该跑的 |
| 用团队公共ODPS账号 | 避免个人AK泄露风险，人员变动无需换凭证，新人零配置 |
| SQL取数+AI总结 | 数据准确性由SQL保证（0幻觉），AI只负责自然语言解读 |

**5.4 关键代码文件清单**

如果你也想搭建类似的日报自动化流水线，以下是你需要关注的文件：

| 文件 | 职责 |
| --- | --- |
| .aoneci/daily-report-auto.yaml | 主流水线：触发器 + 环境变量注入 + 日报生成全流程 |
| .aoneci/deploy-pages.yaml | 部署流水线：push public/实时触发 + 定时兜底 |
| daily-report/config.py | 统一配置：路径、URL、开关、仓库信息 |
| daily-report/generator.py | ODPS SQL执行 + Qwen prompt组装 + Markdown生成 |
| daily-report/md_to_html.py | Markdown → 自包含HTML转换 |
| daily-report/notifier.py | 钉钉Webhook推送（加签 + 精简格式） |
| daily-report/publish_html.py | HTML推送到public/ + 触发Pages部署 |
| daily-report/sql/ | 各模块专属SQL文件 |
| daily-report/prompts/ | 各模块Qwen prompt模板 |

写在最后

回头看这半年的经历，从一个连YAML是什么都不知道的运营，到能独立搭建和维护CI自动化流水线，最大的感触是：

AI不会替代运营，但会用AI的运营会替代不会用的。

搭建CI的过程中，我遇到的每一个技术问题——YAML语法、Git认证、ODPS权限、多分支并发——都是在AI的辅助下解决的。我不需要记住每一个技术细节，我只需要知道我要实现什么效果，然后把报错信息告诉AI，让它帮我找到解决方案。

当然，有些东西是需要自己理解的：

- 业务逻辑：哪些数据重要、怎么分析、怎么呈现——这是运营的核心能力
- 系统设计：为什么要拆两条流水线、为什么要合并分支——这些决策需要理解业务场景
- 质量把控：AI生成的内容需要人工校验，数据准确性需要机制保障

技术工具在变，但运营的核心价值没变：用数据驱动决策，用效率创造价值。 CI只是帮我把重复性工作自动化了，让我有更多时间去做真正需要人判断的事情。

如果你也是一个想用技术提效的运营同学，我的建议是：不要怕，从最简单的开始，一步步来，遇到问题就问AI，与AI协同找到解决方案。 你会发现，那些看起来很"技术"的东西，其实并没有那么难。

本文是「火种&起源」系列的一部分，记录一线运营同学在AI工具实践中的真实故事。

![图2](<assets/Aone CI-运营视角日报自动化流水线从零搭建实战/img_02.png>)

> **图片说明**: 配图位于 assets/Aone CI-运营视角日报自动化流水线从零搭建实战/，CDN 可能过期

---

## 核心概念脑图

```mermaid
mindmap
  root((Aone CI 日报自动化))
    触发与取数
      工作日10:30 cron
      ODPS五模块SQL
      DataClaw API
    AI生成
      Qwen自然语言解读
      SQL保证零幻觉
      Markdown转HTML
    分发留档
      钉钉Webhook加签
      git push public/
    部署架构
      daily-report-auto
      deploy-pages分离
      多分支public合并
    踩坑清单
      triggers复数
      secrets vs vars
      paths防循环
```

## 与你已有知识的关联

**《[[大厂技术文章-DailyTech/文章/千问云-Agent-first模型服务Skill与CLI化|千问云 Agent-first]]》**：本文用 Qwen 大模型做日报解读，与千问云 Agent-first 产品化方向一致，可对照 API/CLI 接入方式。

**《[[大厂技术文章-DailyTech/文章/LLM Wiki-直播数据知识底座编译实践|LLM Wiki 数据底座]]》**：同为「SQL 取数 + LLM 解读」模式，Wiki 侧强调知识编译，本文侧重运营日报 CI 编排。

**《[[大厂技术文章-DailyTech/文章/verify-data一个端到端的数据验数Agent Skill|verify-data 验数 Skill]]》**：SQL 保证数据准确、AI 只做解读的分工，与验数 Agent「数据层确定性 + LLM 辅助」同源。

**《[[大厂技术文章-DailyTech/文章/AI时代程序员技能转型-转转前端周刊199期|AI 时代技能转型]]》**：运营用 AI+CI 提效，印证非开发岗同样需 Loop/自动化思维。

**《[[大厂技术文章-DailyTech/文章/Loop Engineering-6个Hook玩法入门|Loop Hook 入门]]》**：CI 定时触发 + 失败回灌日志，与 Hook 驱动的事件循环在架构上可类比。

## 重难点理解

- **重点1**: 两条流水线分离 — python:3.11 生成 vs alios-8u 部署 — 误区：在一条流水线里 uses 继承 run 环境
- **重点2**: 多分支 public 全量替换 — 部署前 fetch 所有分支合并 — 误区：以为 push 个人分支即永久上线
- **重点3**: SQL 取数 + AI 总结 — 数字由 SQL 保证、AI 只写解读 — 误区：让 LLM 直接算指标产生幻觉
- **重点4**: schedule 只读 master YAML — 个人分支 cron 不触发 — 误区：把定时配置只放在 feature 分支
- **难点5**: paths 替代 [skip ci] — 精确过滤 public/** 避免误杀日报流水线 — 误区：用全局 skip ci 防循环

## 原文内容流程图

```mermaid
flowchart TD
  A[静态站点 README 自动更新] --> B[理解 CI: 触发→步骤→产出]
  B --> C[daily-report-auto: ODPS→Qwen→钉钉→push public]
  C --> D[deploy-pages: 合并全部分支 public]
  D --> E[Aone Pages 全量部署]
  C --> F{多人协作?}
  F -->|是| G[fetch 各分支 public 再部署]
  F -->|否| E
  G --> H[17:00 定时兜底恢复]
```

## 经验

1. **复制已跑通 YAML**: 不要从零写 triggers/run — **应用场景**: Aone CI 首次配置
2. **团队公共 ODPS AK**: Secrets 统一、人员零配置 — **应用场景**: 多人共用数据流水线
3. **报错日志喂 AI**: 效率取决于定位速度而非背语法 — **应用场景**: CI 调试三板斧
4. **paths 精确触发**: 替代 [skip ci] 防误杀 — **应用场景**: push 回仓库防循环
5. **个人分支 + PAT**: 绕过 master 保护跑全流程 — **应用场景**: 内网保护分支仓库

## 知识

| 知识点 | 定义 | 关键要素 | 关联概念 |
|-------|------|---------|---------|
| Aone CI | 阿里内网 CI 平台 | triggers 复数、CST cron | GitLab CI 差异 |
| PAT | 个人访问令牌 | CI push 需写权限 Token | Secrets 管理 |
| deploy-pages | 静态站点部署流水线 | jq 镜像、全量替换 | Aone Pages |
| public 合并 | 多分支资源聚合 | fetch all branches | 并发覆盖问题 |
| SQL+LLM 分工 | 确定性数据 + 自然语言 | 5 模块 SQL + prompts | 零幻觉 |

## 可复用建议

1. **先 README 再日报**: 最小 CI 练手再扩展七步 — **适用场景**: 零基础运营 — **预期效果**: 降低 YAML 学习曲线
2. **生成/发布拆流水线**: 各选合适镜像 — **适用场景**: uses 与 run 工具链冲突 — **预期效果**: 避免 jq 等依赖问题
3. **部署前合并 public/**: for 循环 checkout 各分支 — **适用场景**: 单站点多人 HTML — **预期效果**: 防止他人部署覆盖日报
4. **10 条踩坑表 onboarding**: 新人对照 secrets/cron/paths — **适用场景**: 团队复用模板 — **预期效果**: 减少重复踩坑
5. **17:00 定时兜底**: 极端覆盖后自动恢复 — **适用场景**: 生产 Pages — **预期效果**: 提升站点可用性

## 实施办法

1. **第1步**: 申请 PAT，在仓库 Secrets 配置 ODPS/Qwen/钉钉/GIT_PUSH_TOKEN
2. **第2步**: 复制已有 `.aoneci/*.yaml`，改 triggers（push + schedule 北京时间）
3. **第3步**: 实现 `daily-report-auto`：generator → md_to_html → notifier → publish_html
4. **第4步**: 独立 `deploy-pages`：合并全分支 public → 部署，paths 仅 `public/**`
5. **第5步**: master 合入 YAML（schedule 生效），个人分支 push 验证端到端
6. **第6步**: 人工抽检 AI 解读质量，SQL 模块迭代 prompts/
