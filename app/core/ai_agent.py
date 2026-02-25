from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_core.messages import AIMessage, AIMessageChunk, SystemMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from typing import Literal, Generator
import operator

from app.config.settings import settings


# ──────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────

@tool
def tavily_search(query: str) -> str:
    """Search the web using Tavily for current, real-time information.

    Args:
        query: The search query to look up on the web.
    """
    search = TavilySearch(max_results=2)
    results = search.invoke({"query": query})
    return str(results)


# ──────────────────────────────────────────────
# State
# ──────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    system_prompt: str


# ──────────────────────────────────────────────
# Build the LangGraph agent (shared by both modes)
# ──────────────────────────────────────────────

def _build_agent(llm_id: str, allow_search: bool):
    """Build and compile the LangGraph StateGraph agent."""

    model = init_chat_model(llm_id, model_provider="groq", temperature=0.7)

    tools = [tavily_search] if allow_search else []
    tools_by_name = {t.name: t for t in tools}

    model_with_tools = model.bind_tools(tools) if tools else model

    # ── Node: LLM call ──
    def llm_node(state: AgentState):
        """LLM decides whether to call a tool or respond directly."""
        prompt = state.get("system_prompt", "You are a helpful assistant.")
        msgs = [SystemMessage(content=prompt)] + state["messages"]
        response = model_with_tools.invoke(msgs)
        return {"messages": [response]}

    # ── Node: Tool execution ──
    def tool_node(state: AgentState):
        """Execute tool calls from the LLM response."""
        results = []
        last_message = state["messages"][-1]
        for tool_call in last_message.tool_calls:
            tool_fn = tools_by_name[tool_call["name"]]
            result = tool_fn.invoke(tool_call["args"])
            results.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )
        return {"messages": results}

    # ── Conditional edge ──
    def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
        """Route to tool_node if LLM made tool calls, otherwise end."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tool_node"
        return END

    # ── Build graph ──
    graph = StateGraph(AgentState)
    graph.add_node("llm_node", llm_node)
    graph.add_node("tool_node", tool_node)
    graph.add_edge(START, "llm_node")
    graph.add_conditional_edges("llm_node", should_continue, ["tool_node", END])
    graph.add_edge("tool_node", "llm_node")

    return graph.compile()


def _build_messages(query, system_prompt: str) -> dict:
    """Build the input dict for the agent."""
    messages = []
    if isinstance(query, list):
        for q in query:
            messages.append(HumanMessage(content=q))
    else:
        messages.append(HumanMessage(content=query))

    return {
        "messages": messages,
        "system_prompt": system_prompt if system_prompt else "You are a helpful assistant."
    }


# ──────────────────────────────────────────────
# Standard invoke (full response)
# ──────────────────────────────────────────────

def get_response_from_ai_agents(llm_id: str, query: list, allow_search: bool, system_prompt: str) -> str:
    """Get full response from the LangGraph agent."""

    agent = _build_agent(llm_id, allow_search)
    input_data = _build_messages(query, system_prompt)

    try:
        response = agent.invoke(input_data)
        messages_list = response.get("messages", [])
        ai_messages = [msg.content for msg in messages_list if isinstance(msg, AIMessage)]
        return ai_messages[-1] if ai_messages else "No response generated."

    except Exception as e:
        raise Exception(f"Error invoking agent: {str(e)}")


# ──────────────────────────────────────────────
# Streaming (token-by-token)
# ──────────────────────────────────────────────

def stream_response_from_ai_agents(llm_id: str, query: list, allow_search: bool, system_prompt: str) -> Generator[str, None, None]:
    """Stream response token-by-token from the LangGraph agent."""

    agent = _build_agent(llm_id, allow_search)
    input_data = _build_messages(query, system_prompt)

    try:
        for chunk, metadata in agent.stream(input_data, stream_mode="messages"):
            # Only yield content from AI message chunks (not tool calls)
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield chunk.content

    except Exception as e:
        yield f"\n\nError: {str(e)}"
