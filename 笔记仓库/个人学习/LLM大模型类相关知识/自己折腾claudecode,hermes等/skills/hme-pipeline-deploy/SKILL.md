---
name: hme-pipeline-deploy
description: Trigger and monitor Huawei Cloud CodeArts CI/CD pipelines for the HME project. Use this skill when the user wants to build, package, deploy, or trigger any pipeline (backend/frontend, UAT/DEV/prod), check pipeline status, or automate the build process. This skill uses the hcloud CLI tool (KooCLI) to trigger pipelines and poll their status, with different polling intervals for backend (1 min) vs frontend (5 min) builds.
---

# HME Pipeline Deploy

Trigger and monitor Huawei Cloud CodeArts pipelines for the HME (欧洲大宗商品交易与风险管理系统) project.

## ⚠️ 核心原则：一次执行，全自动

**所有操作通过一个 shell 脚本完成，Claude 只需执行一次 Bash 命令。** 脚本内部自动处理触发、轮询、飞书通知，不需要额外的权限确认。

脚本位置：`~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh`

## 使用方式

### 触发并等待（默认）
```bash
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh <序号>
```

### 仅触发，不等待
```bash
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh <序号> --no-wait
```

### 不发飞书通知
```bash
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh <序号> --no-notify
```

### 列出所有流水线
```bash
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh --list
```

## 流水线序号表

| 序号 | 名称 | 分支 | 类型 | 轮询间隔 |
|------|------|------|------|----------|
| 1 | hmeback-后端-uat打包 | hme-uat | Backend | 1 min |
| 2 | 后端-退货uat打包 | hme-uat-return | Backend | 1 min |
| 3 | hmefront-前端-uat打包 | uat | Frontend | 5 min |
| 4 | 前端-退货-uat打包 | uat-return | Frontend | 5 min |
| 5 | hmeback-后端prod打包 ⚠️ | hme-prod-release | Backend | 1 min |
| 6 | hmefront-前端-prod打包 ⚠️ | hme-prod-release | Frontend | 5 min |
| 7 | hmeback-后端-DEV打包 | dev | Backend | 1 min |
| 8 | hmefront-前端-DEV打包 | dev | Frontend | 5 min |
| 9 | hmeback-后端-DEV-退货 | dev-return | Backend | 1 min |
| 10 | hmefront-前端-DEV-退货 | dev-return | Frontend | 5 min |
| 11 | hmeback (旧版) | dev | Backend | 1 min |

## 识别用户意图

当用户请求构建时，根据关键词匹配流水线序号：

**按环境+类型：**
- "uat后端" / "uat backend" → 序号 1
- "uat前端" / "uat frontend" → 序号 3
- "dev后端" / "dev backend" → 序号 7
- "dev前端" / "dev frontend" → 序号 8
- "prod" / "生产" → 序号 5 或 6（确认哪个）

**按关键词：**
- "退货" / "return" → 退货变体（序号 2, 4, 9, 10）
- "后端" / "backend" / "back" → hmeback 流水线
- "前端" / "frontend" / "front" → hmefront 流水线

如果无法确定，问用户确认。

## 执行流程

1. **识别**流水线序号
2. **执行一条命令**（脚本自动完成触发+轮询+飞书通知）：
   ```bash
   bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh <序号>
   ```
3. **报告结果**给用户

**生产环境流水线（序号 5、6）必须先确认再执行。**

## 脚本内置功能

- ✅ AK/SK 认证（hcloud CLI，无需登录）
- ✅ 自动轮询（后端 60s / 前端 300s）
- ✅ 最大轮询 60 次（防无限循环）
- ✅ 飞书通知（触发时 + 完成时，共 2 条）
- ✅ 状态卡片（蓝色触发 / 绿色成功 / 红色失败 / 橙色取消/超时）
- ✅ `--no-wait` 仅触发不等待
- ✅ `--no-notify` 不发飞书通知

## 重要：只执行一次命令

**Claude 必须只执行一次 `bash run_pipeline.sh` 命令**，不要分步执行 hcloud 命令。脚本内部自动处理触发、轮询、通知全流程。

错误做法（会发多条消息）：
```bash
# ❌ 不要这样做
hcloud CodeArtsPipeline RunPipeline ...  # 第1次调用
hcloud CodeArtsPipeline ShowPipelineRunDetail ...  # 第2次调用
hermes send ...  # 第3次调用
```

正确做法（只发 1 条消息）：
```bash
# ✅ 一次执行，全自动
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh 1
```

## 示例

**用户**: "触发uat后端打包"

**Claude 执行**:
```bash
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh 1
```

**用户**: "打包dev前端，不用等"

**Claude 执行**:
```bash
bash ~/.claude/skills/hme-pipeline-deploy/scripts/run_pipeline.sh 8 --no-wait
```

## 注意事项

- 脚本使用 `hcloud` CLI（已配置 AK/SK，region: cn-east-3）
- 后端流水线通常 5-10 分钟完成
- 前端流水线通常 10-20 分钟完成
- 最大轮询 60 次，超时后停止等待并发飞书通知
- 飞书通知通过 `hermes send` 发送，无需额外配置
