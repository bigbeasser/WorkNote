---
name: hme-uat-deploy
description: "Use when deploying, restarting, or checking the UAT environment. Triggers: UAT+部署/发布/重启/更新/上线/发版, deploy/restart+uat, or status/version queries about UAT."
---

# UAT 环境一键部署

通过 SSH 连接 UAT 服务器（10.152.128.12），执行部署流程：预检 → 部署 → 启动检测。

## 触发规则

**模式 A（完整部署）**：包含 "uat" + 部署/发布/重启/更新/上线/发版/deploy/restart/release → 执行 Phase 1→2→3

**模式 B（状态检查）**：包含 "uat" + 检查/查看/状态/版本/是否正常，不含部署关键词 → 仅执行 Phase 1 + Phase 3

## 输出规则

- 全流程只输出每个阶段的最终结果，不输出中间过程
- 纯文本输出，禁止使用 Markdown 格式符号（**、##、` 等），用缩进和符号（● ✓ ✗）体现层次

## 服务器信息

| 项目 | 值 |
|------|-----|
| IP | 10.152.128.12 |
| 端口 | 22 |
| 用户 | root |
| 密钥 | C:\Users\ADMIN\.ssh\id_ed25519 |
| 部署脚本 | /home/obs_deploy_uat.sh |
| Tomcat 目录 | /home/ctrm/linux_v8.7.0.3_2/apache-tomcat-9.0.87-linux |
| Web 端口 | 8443（HTTP，非 SSL） |
| UAT 地址 | http://10.152.128.12:8443/ks/#/dashboard |

> 8443 是纯 HTTP 端口，所有验证必须用 http://，禁止用 https://

## SSH 命令模板

```bash
ssh -i "/c/Users/ADMIN/.ssh/id_ed25519" -p 22 -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 root@10.152.128.12 "bash -l -c '你的命令'"
```

## 时区转换

服务器 UTC+0，用户 UTC+8。所有服务器时间展示时加 8 小时。

## 危险命令防护

### 绝对禁止

`rm -rf /`、`rm -rf /*`、`rm -rf ~`、`rm -rf /home|/etc|/usr|/var`、`mkfs`、`dd if=`、fork bomb、`chmod -R 777 /`

### 需二次确认

任何 `rm`（脚本内安全操作除外）、`drop`/`truncate`、`format`/`fdisk`/`mkfs`、修改 `/etc/` 配置、`kill -9`（部署脚本内 Tomcat 管理除外）

### 安全原则

1. 只执行部署脚本 `/home/obs_deploy_uat.sh`，不自行编写破坏性命令
2. 不修改部署脚本本身（除非用户要求）
3. 不操作非部署相关目录
4. 部署前确认 war/zip 包已存在于 `/home/obs/uat/`

## 部署流程

### Phase 1: 预检

检查 SSH 连通性、部署包（/home/obs/uat/ctrm.war 和 ctrm.zip）、部署脚本是否存在。任一失败则中止。

预检通过后直接继续，不询问确认。部署包时间从 UTC 转为北京时间显示。

### Phase 2: 执行部署

```bash
ssh -i "/c/Users/ADMIN/.ssh/id_ed25519" -p 22 -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 root@10.152.128.12 "bash -l /home/obs_deploy_uat.sh"
```

timeout 设置 180 秒。

### Phase 3: 等待启动

轮询检测 http://10.152.128.12:8443/ks/ 是否返回 200。最长 5 分钟，每 10 秒检查一次。

成功输出：
```
  UAT Deploy — 等待启动
  ─────────────────
  ● 启动完成       ✓  耗时 50s
  ● UAT 地址       http://10.152.128.12:8443/ks/#/dashboard
  ─────────────────
```

超时则输出诊断信息（进程状态、端口监听、最后 30 行日志）。

## 异常处理

| 场景 | 处理 |
|------|------|
| SSH 连接失败 | 提示检查网络、密钥、服务器是否在线 |
| 部署包不存在 | 提示先上传 war/zip 到 /home/obs/uat/ |
| 端口未监听 | 等 30 秒重试，仍失败输出 catalina.out 最后 200 行 |
| 部署脚本失败 | 输出错误信息，建议检查日志 |

## 注意事项

1. 必须用 `bash -l` 加载环境变量，否则 JAVA_HOME 缺失导致 Tomcat 启动失败
2. timeout 至少 180 秒
3. Tomcat 启动需 30-120 秒，轮询自动等待
4. 部署包时间 UTC+0 → 北京时间 UTC+8
