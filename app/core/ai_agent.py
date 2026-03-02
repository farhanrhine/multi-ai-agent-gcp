from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_core.messages import AIMessage, AIMessageChunk, SystemMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from typing import Literal, Generator
import operator
import json

from app.config.settings import settings

# ──────────────────────────────────────────────
# Stream markers (shared with frontend via import)
# ──────────────────────────────────────────────
REASONING_START = "\x00WSEARCH_START\x00"
REASONING_END   = "\x00WSEARCH_END\x00"


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

    model = init_chat_model(llm_id, model_provider="groq", temperature=0.7, max_tokens=4096)

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
    """Stream response token-by-token from the LangGraph agent.

    When web search is used the stream embeds reasoning blocks wrapped in
    REASONING_START / REASONING_END markers so the frontend can display them
    separately without interrupting the main token stream.
    """

    agent = _build_agent(llm_id, allow_search)
    input_data = _build_messages(query, system_prompt)

    # Accumulate tool-call argument chunks so we can read the full query
    pending_tool_calls: dict = {}   # index -> {"name": str, "args": str}
    has_started_reasoning = False

    try:
        for chunk, metadata in agent.stream(input_data, stream_mode="messages"):

            if isinstance(chunk, AIMessageChunk):
                # ── Stream reasoning content if available ──
                reasoning = chunk.additional_kwargs.get("reasoning_content")
                if reasoning:
                    if not has_started_reasoning:
                        yield "<think>\n"
                        has_started_reasoning = True
                    yield reasoning

                # ── Collect streaming tool-call argument chunks ──
                tool_call_chunks = getattr(chunk, "tool_call_chunks", [])
                
                # Close the think tag if we move past reasoning to tool calls or content
                if has_started_reasoning and (tool_call_chunks or chunk.content):
                    yield "\n</think>\n\n"
                    has_started_reasoning = False

                for tc_chunk in tool_call_chunks:
                    idx = tc_chunk.get("index", 0)
                    if idx not in pending_tool_calls:
                        pending_tool_calls[idx] = {"name": "", "args": ""}
                    pending_tool_calls[idx]["name"] += tc_chunk.get("name") or ""
                    pending_tool_calls[idx]["args"] += tc_chunk.get("args") or ""

                # ── Yield normal content tokens ──
                if chunk.content:
                    yield chunk.content

            elif isinstance(chunk, ToolMessage):
                if has_started_reasoning:
                    yield "\n</think>\n\n"
                    has_started_reasoning = False

                # ── Build a reasoning block to send to the frontend ──
                queries_md = ""
                for tc in pending_tool_calls.values():
                    try:
                        args = json.loads(tc["args"])
                        q = args.get("query", "")
                        if q:
                            queries_md += f"**Query:** {q}\n\n"
                    except Exception:
                        pass

                raw_results = chunk.content
                formatted_results = ""
                
                try:
                    # Tavily usually returns a JSON string containing {'results': [...]}
                    if isinstance(raw_results, str):
                        parsed_results = json.loads(raw_results)
                        # Extract the 'results' list from the dict if it's there
                        if isinstance(parsed_results, dict) and "results" in parsed_results:
                            parsed_results = parsed_results["results"]
                    else:
                        parsed_results = raw_results
                        
                    if isinstance(parsed_results, list):
                        for item in parsed_results[:3]:  # Top 3 results
                            url = item.get("url", "#")
                            title = item.get("title", "No Title")
                            snippet = item.get("content", "No content available")
                            # Truncate snippet to keep UI clean
                            snippet = snippet[:150] + "..." if len(snippet) > 150 else snippet
                            formatted_results += f"- **[{title}]({url})**\n  {snippet}\n\n"
                    else:
                        raise ValueError() # Fallback to string processing
                except Exception:
                    # Fallback if it's not the expected list of dicts format
                    raw_str = str(raw_results)
                    # Simple regex-like replacement string cleaning without completely eating the syntax
                    raw_str = raw_str.replace("[{'url': ", "URL: ").replace(", 'title': ", "\nTitle: ").replace(", 'content': ", "\nSummary: ")
                    # Format as markdown quote to look nice
                    formatted_results = "> " + raw_str[:600] + ("…" if len(raw_str) > 600 else "")

                reasoning = (
                    f"### 🔍 Web Search\n\n"
                    f"{queries_md}"
                    f"**Results:**\n"
                    f"{formatted_results}"
                )
                yield REASONING_START + reasoning + REASONING_END

                # Reset for the next potential tool call
                pending_tool_calls = {}

    except Exception as e:
        yield f"\n\nError: {str(e)}"
