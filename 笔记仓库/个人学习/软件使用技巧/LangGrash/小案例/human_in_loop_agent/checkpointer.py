"""
检查点（Checkpointer）工厂。

Checkpointer 负责在每个 super-step 将图状态持久化到 thread，
从而支持：记忆、人工打断恢复、时间旅行调试。

生产推荐 Redis（langgraph-checkpoint-redis）；
本地无 Redis 时自动降级为 MemorySaver（进程内内存，重启丢失）。
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from .config import settings

logger = logging.getLogger(__name__)


def _create_redis_checkpointer() -> BaseCheckpointSaver:
    """
    创建 Redis 检查点保存器。

    首次部署需调用 setup() 初始化 RediSearch 索引。
    参考：https://langchain-ai.github.io/langgraph/how-tos/persistence/
    """
    from langgraph.checkpoint.redis import RedisSaver

    checkpointer = RedisSaver.from_conn_string(settings.redis.uri)
    checkpointer.setup()
    logger.info("已连接 Redis Checkpointer: %s", settings.redis.uri)
    return checkpointer


def create_checkpointer() -> BaseCheckpointSaver:
    """
    根据配置创建检查点保存器。

    USE_REDIS=false（默认）→ MemorySaver，适合本地学习
    USE_REDIS=true        → RedisSaver，适合生产/多实例部署
    """
    if not settings.redis.enabled:
        logger.info("USE_REDIS=false，使用 MemorySaver（内存检查点）")
        return MemorySaver()

    try:
        return _create_redis_checkpointer()
    except Exception as exc:  # noqa: BLE001 — 学习示例中允许宽捕获并降级
        logger.warning("Redis 连接失败，降级为 MemorySaver: %s", exc)
        return MemorySaver()


@contextmanager
def checkpointer_context() -> Generator[BaseCheckpointSaver, None, None]:
    """
    上下文管理器：自动管理 RedisSaver 连接生命周期。

    MemorySaver 无连接开销，直接 yield。
    RedisSaver 使用 from_conn_string 时需配合 with 语句关闭连接。
    """
    if settings.redis.enabled:
        from langgraph.checkpoint.redis import RedisSaver

        with RedisSaver.from_conn_string(settings.redis.uri) as cp:
            cp.setup()
            yield cp
    else:
        yield MemorySaver()
