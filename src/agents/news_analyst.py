from langchain.agents import create_agent
from ..state import AgentState
from ..tools.search_tools import search_news
from ..utils import get_llm

def news_analyst_node(state: AgentState):
    """
    Finance News Analyst that searches for and summarizes news using a ReAct agent.
    """
    llm = get_llm(temperature=0)
    tools = [search_news]
    
    system_prompt = """You are a Senior News Analyst at a top-tier investment bank.
    Your goal is to synthesize market news into actionable insights, **specifically addressing the user's question**.
    
    1. Use the `search_news` tool to find the latest news.
    2. **Context-Aware Search**: Look for news that specifically discusses the user's concern (e.g., "bottlenecks", "competitor moves").
    3. **Debate Analysis**: What are the Bulls saying? What are the Bears saying? (Specifically regarding the user's topic).
    4. **Catalyst Identification**: Identify specific events that could move the stock price.
    5. **Sentiment Analysis**: Assess the market sentiment.
    
    Output a structured analysis in **Traditional Chinese (繁體中文)**:
    - **Market Debate (市場辯論)**: Summarize the Bull vs Bear arguments on the user's specific question.
    - **Key Catalysts (關鍵催化劑)**: List of upcoming or recent major events.
    - **Sentiment Score (情緒評分)**: Average score (1-10) with reasoning.
    - **Headline Summary (頭條摘要)**: Concise bullet points with sources.
    """
    
    # Create the agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    
    tickers = state["tickers"]
    query = state["query"]
    
    # Invoke the agent
    result = agent.invoke({"messages": [("human", f"Find and analyze news for the following tickers: {tickers}. \n\nUser's Specific Question: {query}")]})
    
    # The result contains the full state of the agent, including messages.
    last_message = result["messages"][-1]
    
    return {"news_analysis": last_message.content}
