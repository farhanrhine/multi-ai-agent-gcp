from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage

from app.config.settings import settings

def get_response_from_ai_agents(llm_id, query, allow_search, system_prompt):

    llm = ChatGroq(model=llm_id)

    tools = [TavilySearchResults(max_results=2)] if allow_search else []

    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier=system_prompt if system_prompt else None
    )

    # Convert query list to HumanMessage objects
    messages = [HumanMessage(content=q) for q in query] if isinstance(query, list) else [HumanMessage(content=query)]
    state = {"messages": messages}

    response = agent.invoke(state)

    messages = response.get("messages", [])

    ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]

    return ai_messages[-1] if ai_messages else "No response generated"






