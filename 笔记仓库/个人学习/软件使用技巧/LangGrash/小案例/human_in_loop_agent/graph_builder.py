"""
StateGraph 构建与编译。

图拓扑（经典 ReAct Agent）：

    START → chatbot → [有 tool_calls?] → tools → chatbot → ...
                              ↓ 否
                             END

编译选项：
- checkpointer：持久化检查点（记忆 + 时间旅行 + interrupt 恢复）
- interrupt_before：在 tools 节点执行前打断，实现「工具调用前人工审批」
"""

from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .config import settings
from .nodes import chatbot_node, create_llm_with_tools
from .state import AgentState


def build_graph(checkpointer: BaseCheckpointSaver):
    """
    构建并编译 LangGraph。

    Args:
        checkpointer: 检查点保存器（MemorySaver 或 RedisSaver）

    Returns:
        编译后的 CompiledStateGraph，可 invoke / stream / get_state
    """
    _, tools = create_llm_with_tools()

    graph_builder = StateGraph(AgentState)

    # 注册节点
    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_node("tools", ToolNode(tools=tools))

    # 边：入口 → chatbot
    graph_builder.add_edge(START, "chatbot")

    # 条件边：chatbot 之后根据是否有 tool_calls 路由
    graph_builder.add_conditional_edges("chatbot", tools_condition)

    # 工具执行完回到 chatbot 继续推理
    graph_builder.add_edge("tools", "chatbot")

    # 编译参数
    compile_kwargs: dict = {"checkpointer": checkpointer}

    # interrupt_before：在 tools 节点执行前暂停（可选的第二种「打断」方式）
    # 启用后需用 Command(resume=...) 或 update_state 继续，适合「审批后再执行工具」
    if settings.interrupt_before_tools:
        compile_kwargs["interrupt_before"] = ["tools"]

    return graph_builder.compile(**compile_kwargs)
