from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from ..utils import get_llm

def risk_manager_node(state: AgentState):
    """
    Risk Manager that assesses risks based on data and news analysis.
    """
    llm = get_llm(temperature=0)
    
    system_prompt = """You are a Chief Risk Officer at a major investment fund.
    Your job is to play "Devil's Advocate" and identify the downside risks that others might miss, **specifically regarding the user's question**.
    
    Input:
    - User Query: The specific question or hypothesis the user has.
    - Data Analysis (Valuation, Financials)
    - News Analysis (Catalysts, Sentiment)
    
    Output in **Traditional Chinese (繁體中文)**:
    1. **Stress Test User's Hypothesis (壓力測試用戶假設)**: If the user is asking "Is X a bottleneck?", explore "What if X is NOT a bottleneck?" or "What if X gets worse?".
    2. **Bear Case Scenario (看空情境)**: Describe a specific scenario where the stock could drop 20%+.
    3. **Risk Categorization (風險分類)**: Macro, Sector, Company.
    4. **Risk Score (風險評分)**: Assign a score (1-10) with justification.
    
    Be conservative. If the stock is "priced for perfection," highlight that as a major risk.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """User Query:
{user_query}

Data Analysis:
{data_analysis}

News Analysis:
{news_analysis}

Please provide your risk assessment.""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "user_query": state.get("query", "No specific query provided."),
        "data_analysis": state.get("data_analysis", "No data analysis provided."),
        "news_analysis": state.get("news_analysis", "No news analysis provided.")
    })
    
    return {"risk_assessment": response.content}
