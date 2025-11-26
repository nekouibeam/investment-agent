from langgraph.prebuilt import create_react_agent
from ..state import AgentState
from ..tools.finance_tools import get_stock_data
from ..utils import get_llm

def data_analyst_node(state: AgentState):
    """
    Finance Data Analyst that gathers and analyzes market data using a ReAct agent.
    """
    llm = get_llm(temperature=0)
    tools = [get_stock_data]
    
    system_prompt = """You are a Senior Financial Data Analyst at a top-tier investment bank.
    Your goal is to provide a rigorous quantitative analysis of the provided tickers, **specifically addressing the user's question**.
    
    1. Use the `get_stock_data` tool to fetch comprehensive data.
    2. **Context-Aware Analysis**: Look for data points that specifically support or refute the user's hypothesis (e.g., if they ask about "margins", focus on that).
    3. **Valuation Analysis**: Compare P/E, PEG, and EV/EBITDA to historical norms or general market benchmarks. Is the stock cheap or expensive?
    4. **Financial Health**: Analyze margins (Gross/Operating), growth rates (Revenue/Earnings), and balance sheet strength (Cash vs Debt).
    5. **Analyst Consensus**: Summarize the street's view (Target Prices, Recommendations).
    
    Output a structured analysis in **Traditional Chinese (繁體中文)**. Do not just list numbers; interpret them.
    - **Direct Answer to User (針對用戶問題的數據回應)**: What does the data say about their specific concern?
    - **Valuation Verdict (估值判斷)**: Undervalued / Fair / Overvalued (with justification).
    - **Quality Score (品質評分)**: High / Medium / Low (based on margins & ROE).
    - **Growth Outlook (成長展望)**: Strong / Moderate / Weak.
    """
    
    # Create the agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier=system_prompt
    )
    
    tickers = state["tickers"]
    query = state["query"]
    
    # Invoke the agent
    # The agent expects a list of messages. We pass the task as a human message.
    result = agent.invoke({"messages": [("human", f"Analyze the following tickers: {tickers}. \n\nUser's Specific Question: {query}")]})
    
    # The result contains the full state of the agent, including messages.
    # The last message should be the AI's final response.
    last_message = result["messages"][-1]
    
    return {"data_analysis": last_message.content}
