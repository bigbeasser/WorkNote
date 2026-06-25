"""
完整功能演示入口。

演示场景（对应官方教程 4/5/6 节）：
  1. 记忆       — 同一 thread_id 多轮对话，状态由 Checkpointer 持久化
  2. 工具调用   — mock_web_search / query_knowledge
  3. 人工打断   — human_assistance 内 interrupt() 暂停，Command(resume=) 恢复
  4. 自定义状态 — entity_name / entity_birthday / review_status
  5. 手动改状态 — graph.update_state() 在中断时也可覆盖字段
  6. 时间旅行   — get_state_history() 回溯检查点，从指定 checkpoint 重放

用法：
  cd 小案例
  pip install -r requirements.txt
  set OPENAI_API_KEY=sk-xxx
  python -m human_in_loop_agent.demo

  # 使用 Redis 持久化（需本地 Redis + RedisJSON + RediSearch）
  set USE_REDIS=true
  set REDIS_URI=redis://127.0.0.1:6379/0
  python -m human_in_loop_agent.demo
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from .checkpointer import checkpointer_context
from .config import settings
from .graph_builder import build_graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _thread_config(thread_id: str | None = None) -> dict[str, Any]:
    """构造 LangGraph 运行配置；thread_id 决定检查点所属会话线程。"""
    return {"configurable": {"thread_id": thread_id or settings.default_thread_id}}


def _print_last_message(event: dict) -> None:
    """流式输出时打印最新一条消息。"""
    if "messages" in event and event["messages"]:
        event["messages"][-1].pretty_print()


def _print_custom_state(graph, config: dict) -> None:
    """打印自定义状态字段。"""
    snapshot = graph.get_state(config)
    fields = ("entity_name", "entity_birthday", "review_status", "step_count")
    data = {k: snapshot.values.get(k) for k in fields}
    print(f"\n📦 自定义状态: {data}\n")


def demo_memory_and_tools(graph, config: dict) -> None:
    """
    场景 1：记忆 + 工具调用。

    第一次调用触发搜索；同一 thread 内再次调用可读取历史（需 LLM 理解上下文）。
    """
    print("\n" + "=" * 60)
    print("【场景 1】记忆 + 工具调用")
    print("=" * 60)

    user_input = (
        "请帮我查一下 LangGraph 的发布相关信息，"
        "查到后使用 human_assistance 工具，name 填 LangGraph，"
        "birthday 填你搜索到的日期，提交人工审核。"
    )

    print(f"\n👤 用户: {user_input}\n")

    for event in graph.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config,
        stream_mode="values",
    ):
        _print_last_message(event)

    snapshot = graph.get_state(config)
    print(f"\n⏸️  图暂停位置 next={snapshot.next}")
    if snapshot.next:
        print("   → 已触发 interrupt，等待人工 resume")


def demo_human_interrupt_resume(graph, config: dict) -> None:
    """
    场景 2：人工打断与恢复。

    interrupt() 暂停后，用 Command(resume=...) 注入人工输入继续执行。
    """
    print("\n" + "=" * 60)
    print("【场景 2】人工打断 → Command(resume) 恢复")
    print("=" * 60)

    snapshot = graph.get_state(config)
    if not snapshot.next:
        print("当前无中断，跳过 resume 演示")
        return

    # 模拟人工审核：修正 birthday（官方教程中为 Jan 17, 2024）
    human_command = Command(
        resume={
            "name": "LangGraph",
            "birthday": "Jan 17, 2024",
            # 不设 correct=y，走「修正」分支
        }
    )

    print("\n🧑‍💼 人工修正: name=LangGraph, birthday=Jan 17, 2024\n")

    for event in graph.stream(human_command, config, stream_mode="values"):
        _print_last_message(event)

    _print_custom_state(graph, config)


def demo_manual_update_state(graph, config: dict) -> None:
    """
    场景 3：手动覆盖状态（官方教程 5-customize-state 第 5 节）。

    在任意时刻（含中断时）可用 update_state 直接改写字段。
    """
    print("\n" + "=" * 60)
    print("【场景 3】graph.update_state() 手动改状态")
    print("=" * 60)

    new_config = graph.update_state(
        config,
        {"entity_name": "LangGraph (library)"},
    )
    print(f"update_state 返回新 config: {new_config['configurable']}")

    snapshot = graph.get_state(config)
    print(
        f"覆盖后 entity_name={snapshot.values.get('entity_name')}, "
        f"birthday={snapshot.values.get('entity_birthday')}"
    )


def demo_time_travel(graph, config: dict) -> None:
    """
    场景 4：时间旅行（官方教程 6-time-travel）。

    - get_state_history：列出 thread 内所有检查点（新→旧）
    - 选定历史 checkpoint，stream(None, checkpoint_config) 从该点重放
    """
    print("\n" + "=" * 60)
    print("【场景 4】时间旅行 — get_state_history + 检查点重放")
    print("=" * 60)

    history = list(graph.get_state_history(config))
    if not history:
        print("无历史检查点（请先完成场景 1/2）")
        return

    print(f"\n共 {len(history)} 个检查点（新 → 旧）：\n")
    for i, state in enumerate(history):
        msg_count = len(state.values.get("messages", []))
        print(
            f"  [{i}] messages={msg_count}, next={state.next}, "
            f"checkpoint_id={state.config['configurable'].get('checkpoint_id', 'N/A')[:8]}..."
        )

    # 选取一个中间检查点重放（示例：消息数在 2~6 之间的某个点）
    to_replay = None
    for state in history:
        msg_count = len(state.values.get("messages", []))
        if 2 <= msg_count <= 8 and state.next:
            to_replay = state
            break

    if to_replay is None:
        print("\n未找到合适的重放检查点")
        return

    print(f"\n🔙 从检查点重放: messages={len(to_replay.values['messages'])}, next={to_replay.next}")
    print("   （传入 input=None，从该 checkpoint 继续执行后续节点）\n")

    for event in graph.stream(None, to_replay.config, stream_mode="values"):
        _print_last_message(event)


def demo_second_turn_memory(graph, config: dict) -> None:
    """
    场景 5：同 thread 第二轮对话，验证记忆是否生效。
    """
    print("\n" + "=" * 60)
    print("【场景 5】同 thread 第二轮 — 验证记忆")
    print("=" * 60)

    follow_up = "我们刚才确认的实体名称和发布日分别是什么？请根据已保存的状态回答。"
    print(f"\n👤 用户: {follow_up}\n")

    for event in graph.stream(
        {"messages": [HumanMessage(content=follow_up)]},
        config,
        stream_mode="values",
    ):
        _print_last_message(event)

    _print_custom_state(graph, config)


def run_demo() -> None:
    """串联运行全部演示场景。"""
    print("LangGraph Human-in-the-Loop Agent 演示")
    print(f"  LLM_MODEL      = {settings.llm.model}")
    print(f"  USE_REDIS      = {settings.redis.enabled}")
    print(f"  REDIS_URI      = {settings.redis.uri}")
    print(f"  THREAD_ID      = {settings.default_thread_id}")
    print(f"  INTERRUPT_BEFORE_TOOLS = {settings.interrupt_before_tools}")

    config = _thread_config()

    with checkpointer_context() as checkpointer:
        graph = build_graph(checkpointer)

        try:
            demo_memory_and_tools(graph, config)
            demo_human_interrupt_resume(graph, config)
            demo_manual_update_state(graph, config)
            demo_time_travel(graph, config)
            demo_second_turn_memory(graph, config)
        except Exception as exc:
            logger.error("演示执行失败: %s", exc)
            logger.info(
                "请确认已设置 OPENAI_API_KEY（或对应模型的 API Key），"
                "且已安装 requirements.txt 中的依赖。"
            )
            raise

    print("\n✅ 全部演示场景执行完毕。")


if __name__ == "__main__":
    run_demo()
