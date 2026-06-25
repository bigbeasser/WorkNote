# LangGraph 人机协作 Agent 小案例

> 参考官方教程：[添加人工在环](https://langgraph.com.cn/tutorials/get-started/4-human-in-the-loop/) · [自定义状态](https://langgraph.com.cn/tutorials/get-started/5-customize-state/) · [时间旅行](https://langgraph.com.cn/tutorials/get-started/6-time-travel/)

## 能力清单

| 能力 | 实现位置 | 说明 |
| --- | --- | --- |
| 工具调用 | `tools.py` | mock 搜索 + 知识库查询 |
| 人工干预 | `tools.human_assistance` | `interrupt()` 暂停，人工审核结构化字段 |
| 打断恢复 | `demo.py` | `Command(resume=...)` 恢复执行 |
| 自定义状态 | `state.py` | `entity_name` / `review_status` 等 |
| 记忆 | `checkpointer.py` | `thread_id` + Checkpointer 多轮持久化 |
| Redis 持久化 | `checkpointer.py` | `USE_REDIS=true` 切换 RedisSaver |
| 时间旅行 | `demo.py` | `get_state_history` + checkpoint 重放 |
| 手动改状态 | `demo.py` | `graph.update_state()` |

## 目录结构

```
human_in_loop_agent/
├── config.py          # 环境配置（端口/密钥占位）
├── state.py           # 自定义 AgentState
├── tools.py           # 工具 + interrupt 人工协助
├── nodes.py           # chatbot 节点
├── checkpointer.py    # Memory / Redis 检查点工厂
├── graph_builder.py   # StateGraph 构图
└── demo.py            # 五场景串联演示
```

## 快速开始

```bash
cd 小案例
pip install -r requirements.txt

# 配置 LLM（示例 OpenAI）
set OPENAI_API_KEY=sk-your-key
set LLM_MODEL=openai:gpt-4o-mini

# 运行演示
python -m human_in_loop_agent.demo
```

## Redis 配置（可选）

```bash
# 需 Redis 8+ 或安装 RedisJSON + RediSearch 模块
set USE_REDIS=true
set REDIS_URI=redis://127.0.0.1:6379/0
python -m human_in_loop_agent.demo
```

未启用 Redis 时自动使用 `MemorySaver`（进程内内存，适合本地学习）。

## 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `OPENAI_API_KEY` | — | OpenAI API 密钥 |
| `LLM_MODEL` | `openai:gpt-4o-mini` | `init_chat_model` 模型名 |
| `USE_REDIS` | `false` | 是否使用 Redis Checkpointer |
| `REDIS_URI` | `redis://127.0.0.1:6379/0` | Redis 连接串（占位） |
| `THREAD_ID` | `demo-thread-001` | 会话线程 ID |
| `INTERRUPT_BEFORE_TOOLS` | `false` | 工具执行前打断审批 |

## 图拓扑

```
START → chatbot → (有 tool_calls?) → tools → chatbot → END
```

## 关联笔记

[[../📋 LangGraph索引]]
