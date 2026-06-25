"""
自定义图状态（State）定义。

LangGraph 的核心是「中央状态 + Reducer」：
- 每个节点接收状态快照，返回增量更新
- Annotated 字段上的 reducer 负责合并（如 add_messages 追加消息）
"""

from __future__ import annotations

from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    Agent 图状态。

    除官方教程中的 messages 外，扩展业务字段以演示「自定义状态」：
    - entity_name / entity_birthday：人工审核后的结构化信息
    - review_status：人工审核流转状态
    - step_count：节点执行计数（演示非消息类字段的读写）
    """

    # 对话消息列表；add_messages 作为 reducer 自动追加/按 ID 更新
    messages: Annotated[list, add_messages]

    # --- 自定义业务字段（参考官方教程 5-customize-state）---

    # 实体名称，例如 "LangGraph"
    entity_name: str
    # 实体发布日/生日，例如 "Jan 17, 2024"
    entity_birthday: str
    # 人工审核状态：pending | approved | corrected
    review_status: str
    # 图内步数计数，每次 chatbot 节点 +1
    step_count: int


def initial_state() -> AgentState:
    """返回新会话的默认初始状态。"""
    return {
        "messages": [],
        "entity_name": "",
        "entity_birthday": "",
        "review_status": "pending",
        "step_count": 0,
    }
