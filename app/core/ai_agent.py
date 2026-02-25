from langchain_groq import ChatGroq
from langchain_tavily import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config.settings import settings

def get_response_from_ai_agents(llm_id, query, allow_search, system_prompt):

    llm = ChatGroq(model=llm_id)

    tools = [TavilySearchResults(max_results=2)] if allow_search else []

    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    # Build message list with system prompt if provided
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    
    # Convert query list to HumanMessage objects
    if isinstance(query, list):
        for q in query:
            messages.append(HumanMessage(content=q))
    else:
        messages.append(HumanMessage(content=query))
    
    state = {"messages": messages}

    response = agent.invoke(state)

    messages_response = response.get("messages", [])

    ai_messages = [message.content for message in messages_response if isinstance(message, AIMessage)]

    return ai_messages[-1] if ai_messages else "No response generated"






