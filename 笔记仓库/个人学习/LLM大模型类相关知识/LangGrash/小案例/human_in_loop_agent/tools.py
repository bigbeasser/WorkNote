"""
Agent 工具定义。

包含：
1. mock_web_search  — 模拟外部搜索（避免依赖 Tavily API Key）
2. human_assistance — 人工在环工具，内部调用 interrupt() 暂停图执行
3. query_knowledge  — 模拟查询内部知识库
"""

from __future__ import annotations

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt

# 模拟知识库：生产环境可替换为 Redis / 向量库检索
_MOCK_KB: dict[str, str] = {
    "langgraph": "LangGraph 是 LangChain 生态的图结构 Agent 编排框架，支持循环、持久化与人机协作。",
    "checkpoint": "Checkpoint 在每个 super-step 保存状态快照，是记忆与时间旅行的基础。",
    "interrupt": "interrupt() 在节点/工具内调用可暂停执行，通过 Command(resume=...) 恢复。",
}

# 模拟搜索结果：避免真实调用 Tavily，结构对齐官方教程
_MOCK_SEARCH_RESULTS: dict[str, list[dict[str, str]]] = {
    "langgraph release date": [
        {
            "url": "https://blog.langchain.com/langgraph/",
            "content": "LangGraph was announced in early 2024. Stable release followed in 2024.",
        },
        {
            "url": "https://langgraph.com.cn/",
            "content": "LangGraph 中文文档：支持 StateGraph、Checkpointer、interrupt 人机协作。",
        },
    ],
    "default": [
        {
            "url": "https://example.com/placeholder",
            "content": "这是占位搜索结果，请配置真实搜索 API 后替换。",
        },
    ],
}


@tool
def mock_web_search(query: str) -> str:
    """
    模拟网络搜索工具。

    生产环境可替换为 langchain_tavily.TavilySearch 或自建检索服务。
    """
    key = query.lower().strip()
    for pattern, results in _MOCK_SEARCH_RESULTS.items():
        if pattern in key or key in pattern:
            return str(results)
    return str(_MOCK_SEARCH_RESULTS["default"])


@tool
def query_knowledge(topic: str) -> str:
    """查询内部知识库（模拟 Redis/向量库中的静态知识）。"""
    return _MOCK_KB.get(topic.lower().strip(), f"知识库中暂无「{topic}」相关条目。")


@tool
def human_assistance(
    name: str,
    birthday: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    请求人工协助并审核结构化信息。

    参考官方教程：
    https://langgraph.com.cn/tutorials/get-started/4-human-in-the-loop/
    https://langgraph.com.cn/tutorials/get-started/5-customize-state/

    流程：
    1. interrupt() 暂停图执行，将待审核数据暴露给外部 UI/运维
    2. 人工通过 Command(resume={...}) 回复
    3. 工具内用 Command(update=...) 写回自定义状态字段
    """
    # interrupt 类似 Python input()，但状态已由 Checkpointer 持久化，可随时恢复
    human_response = interrupt(
        {
            "question": "请确认以下信息是否正确？",
            "name": name,
            "birthday": birthday,
            "hint": "回复 correct=y 表示确认；否则提供修正后的 name/birthday",
        }
    )

    # 人工确认「正确」
    if str(human_response.get("correct", "")).lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        review_status = "approved"
        response_text = "人工已确认信息正确。"
    else:
        # 人工提供了修正值
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        review_status = "corrected"
        response_text = f"人工已修正: {human_response}"

    # 通过 Command 同时更新自定义状态 + 返回 ToolMessage
    return Command(
        update={
            "entity_name": verified_name,
            "entity_birthday": verified_birthday,
            "review_status": review_status,
            "messages": [
                ToolMessage(content=response_text, tool_call_id=tool_call_id),
            ],
        }
    )


@tool
def human_assistance_simple(query: str) -> str:
    """
    简化版人工协助（仅返回文本，不更新自定义状态）。

    对应官方教程第 4 节最基础的 interrupt 用法。
    """
    human_response = interrupt({"query": query})
    return human_response.get("data", str(human_response))


def get_all_tools() -> list:
    """返回注册到图中的全部工具。"""
    return [mock_web_search, query_knowledge, human_assistance, human_assistance_simple]
