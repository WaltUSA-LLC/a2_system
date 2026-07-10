from fastapi import APIRouter, HTTPException, Query
from app.agent.agent import agent

router = APIRouter()


@router.get("/chat")
async def chat(msg: str = Query(..., min_length=1)):
    try:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": msg}]}
        )
        return {"feedback": result["messages"][-1].content}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to get feedback from the agent.",
        ) from exc
