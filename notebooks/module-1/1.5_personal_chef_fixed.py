import uuid
from dotenv import load_dotenv
from typing import Dict, Any
from tavily import TavilyClient
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver 

load_dotenv()

tavily_client = TavilyClient()

@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information"""
    return tavily_client.search(query)

system_prompt = """
You are a personal chef. The user will give you a list of ingredients they have left over in their house.
Using the web search tool, search the web for recipes that can be made with the ingredients they have.
Return recipe suggestions and eventually the recipe instructions to the user, if requested.
"""

# 1. Initialize a checkpointer to save thread state
# (Use PostgresSaver instead of MemorySaver for true production)
#memory = MemorySaver() #persistence is automatically handled with LangGraph API platform

# 2. Pass the checkpointer to the agent
agent = create_agent(
    model="claude-haiku-4-5-20251001",
    # model="gpt-4o-mini", 
    tools=[web_search], 
    system_prompt=system_prompt,
    checkpointer=memory
)

# 3. Dynamic Thread ID Management Example
if __name__ == "__main__":
    # Generate a unique thread ID for a new user/session
    user_session_id = str(uuid.uuid4())
    
    # Configure the invocation with the dynamic thread ID
    config = {
        "configurable": {
            "thread_id": user_session_id
        }
    }
    
    user_input = {"messages": [("user", "I have some leftover chicken and rice.")]}
    
    # Invoke the agent, passing the config so it remembers THIS specific thread
    response = agent.invoke(user_input, config=config)
    
    print(f"Session ID: {user_session_id}")
    print(response["messages"][-1].content)