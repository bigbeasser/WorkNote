"""
应用配置模块。

集中管理 LLM、Redis 等外部依赖的连接参数。
学习/本地开发时端口与密钥统一使用占位值，生产环境通过环境变量覆盖。
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RedisConfig:
    """Redis 连接配置（Checkpointer 持久化检查点）。"""

    # 占位连接串：本地开发默认不连真实 Redis，USE_REDIS=true 时才会尝试连接
    uri: str = os.getenv("REDIS_URI", "redis://127.0.0.1:6379/0")
    # Redis 需启用 RedisJSON + RediSearch 模块（langgraph-checkpoint-redis 要求）
    enabled: bool = os.getenv("USE_REDIS", "false").lower() == "true"


@dataclass(frozen=True)
class LLMConfig:
    """大模型配置。"""

    # 示例：openai:gpt-4.1-mini / anthropic:claude-3-5-sonnet-latest
    model: str = os.getenv("LLM_MODEL", "openai:gpt-4o-mini")
    # 占位 API Key，实际运行时请设置 OPENAI_API_KEY 等环境变量
    api_key_placeholder: str = "sk-your-api-key-here"


@dataclass(frozen=True)
class AppConfig:
    """应用级配置聚合。"""

    redis: RedisConfig = RedisConfig()
    llm: LLMConfig = LLMConfig()
    # 默认会话线程 ID，同一 thread_id 共享检查点历史（记忆）
    default_thread_id: str = os.getenv("THREAD_ID", "demo-thread-001")
    # 是否在工具执行前打断（interrupt_before），用于人工审批工具调用
    interrupt_before_tools: bool = os.getenv("INTERRUPT_BEFORE_TOOLS", "false").lower() == "true"


# 全局单例，各模块直接 import 使用
settings = AppConfig()
