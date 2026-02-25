from langchain_groq import ChatGroq
from langchain_tavily import TavilySearchResults
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config.settings import settings


# Define Tavily search tool
@tool
def tavily_search(query: str) -> str:
    """Search the web using Tavily for current information."""
    search = TavilySearchResults(max_results=2)
    results = search.invoke({"query": query})
    return str(results)


def get_response_from_ai_agents(llm_id: str, query: list, allow_search: bool, system_prompt: str) -> str:
    """Get response from AI agent using latest LangGraph/LangChain API."""
    
    # Initialize LLM
    llm = ChatGroq(model=llm_id, temperature=0.7)
    
    # Define tools list
    tools = [tavily_search] if allow_search else []
    
    # Create react agent
    agent = create_react_agent(
        model=llm,
        tools=tools
    )
    
    # Build messages
    messages = []
    
    # Add system prompt if provided
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    
    # Add user queries
    if isinstance(query, list):
        for q in query:
            messages.append(HumanMessage(content=q))
    else:
        messages.append(HumanMessage(content=query))
    
    # Invoke agent
    try:
        response = agent.invoke({"messages": messages})
        
        # Extract AI message from response
        messages_list = response.get("messages", [])
        
        # Get the last AI message
        ai_messages = [msg.content for msg in messages_list if isinstance(msg, AIMessage)]
        
        if ai_messages:
            return ai_messages[-1]
        else:
            return "No response generated from the agent."
    
    except Exception as e:
        raise Exception(f"Error invoking agent: {str(e)}")







