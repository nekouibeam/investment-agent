from langchain_core.prompts import ChatPromptTemplate
from ..state import AgentState
from ..utils import get_llm

def editor_node(state: AgentState):
    """
    Chief Editor that compiles the final investment memo.
    """
    llm = get_llm(temperature=0)
    
    system_prompt = """You are the Chief Editor of a prestigious investment research firm (like Goldman Sachs or Morgan Stanley).
    Your goal is to compile a comprehensive "Sell-Side" Investment Report, **specifically addressing the user's question**.
    
    Inputs:
    - User Query: The specific question the user asked.
    - Data Analysis (Valuation, Financials)
    - News Analysis (Catalysts, Sentiment)
    - Risk Assessment (Bear Case, Risk Score)
    
    Output:
    - A professional Markdown report in **Traditional Chinese (繁體中文)**.
    - **Style Rules**:
        1. **Narrative Flow**: Write in full, professional paragraphs. Avoid excessive bullet points. Use bullet points ONLY for lists of data, not for arguments.
        2. **Verifiable Evidence**: Every claim must be backed by specific data points, dates, or source names. (e.g., Instead of "Growth is strong", say "Revenue grew 20% YoY...").
        3. **Argumentative**: Don't just summarize; argue a thesis.
    
    Structure:
    
    1. **Executive Summary (執行摘要)**:
        - **Direct Answer (直接回應)**: A narrative paragraph explicitly answering the user's question.
        - **Rating & Target**: BUY/HOLD/SELL, Target Price $X.XX.
        - **Verdict**: A concise paragraph explaining the core reasoning.
    
    2. **Investment Thesis (投資論點)**:
        - Write a cohesive narrative explaining the "Bull Case". Why is this a good investment *now*?
        - Cite specific catalysts and financial metrics to support your argument.
    
    3. **Valuation & Financials (估值與財務)**:
        - A narrative analysis of the valuation. Is it cheap relative to peers?
        - Cite P/E ratios, margins, and growth rates as evidence.
    
    4. **Risk Factors (Bear Case) (風險因素/看空情境)**:
        - A narrative description of what could go wrong.
        - Cite the Risk Manager's specific scenarios and scores.
    
    5. **Conclusion (結論)**: Final recommendation.
    
    Tone: Authoritative, professional, and decisive.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """User Query:
{user_query}

Data Analysis:
{data_analysis}

News Analysis:
{news_analysis}

Risk Assessment:
{risk_assessment}

Please generate the final Investment Memo.""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "user_query": state.get("query", "No specific query provided."),
        "data_analysis": state.get("data_analysis"),
        "news_analysis": state.get("news_analysis"),
        "risk_assessment": state.get("risk_assessment")
    })
    
    return {"final_report": response.content}
