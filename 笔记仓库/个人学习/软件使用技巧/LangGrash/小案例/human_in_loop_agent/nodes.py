"""
图节点（Node）实现。

每个节点函数签名：(state: AgentState) -> dict | Command
返回值是与 AgentState 键对应的增量更新。
"""

from __future__ import annotations

import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

from .config import settings
from .state import AgentState
from .tools import get_all_tools

logger = logging.getLogger(__name__)

# 系统提示：引导模型使用工具，并在获得信息后走人工审核
SYSTEM_PROMPT = """你是一个企业级 LangGraph 学习助手。

能力：
1. 使用 mock_web_search 搜索外部信息
2. 使用 query_knowledge 查询内部知识库
3. 获得关键事实后，使用 human_assistance 工具提交 name/birthday 供人工审核
4. 若只需人工文字答复，可使用 human_assistance_simple

注意：一次最多发起一个工具调用；提交人工审核前请先完成必要的搜索。"""


def create_llm_with_tools():
    """初始化 LLM 并绑定工具 schema。"""
    tools = get_all_tools()
    llm = init_chat_model(settings.llm.model)
    return llm.bind_tools(tools), tools


def chatbot_node(state: AgentState) -> dict:
    """
    核心对话节点：调用 LLM，可能产生普通回复或 tool_calls。

    因工具执行中可能 interrupt，禁用并行工具调用，避免恢复时重复执行。
    参考官方教程 4-human-in-the-loop 中的 assert 说明。
    """
    llm_with_tools, _ = create_llm_with_tools()

    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]

    response = llm_with_tools.invoke(messages)

    if response.tool_calls and len(response.tool_calls) > 1:
        logger.warning("模型返回了多个 tool_calls，仅保留第一个以避免 interrupt 恢复重复")
        response.tool_calls = response.tool_calls[:1]

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }
