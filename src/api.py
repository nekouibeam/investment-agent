from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.graph import create_graph

load_dotenv()

app = FastAPI(title="Investment Agent API")

class ResearchRequest(BaseModel):
    query: str

@app.post("/research")
async def research(request: ResearchRequest):
    try:
        graph = create_graph()
        # Initialize state with just the query, other fields will be populated by agents
        initial_state = {
            "query": request.query,
            "tickers": [],
            "data_analysis": None,
            "news_analysis": None,
            "risk_assessment": None,
            "final_report": None
        }
        result = graph.invoke(initial_state)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
