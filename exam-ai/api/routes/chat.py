from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.schemas import ChatRequest
from agent.assessment_agent import stream_agent

router = APIRouter()


@router.post("/chat", summary="Chat with ExamAI — streams response tokens")
async def chat_endpoint(request: ChatRequest):
    async def token_stream():
        try:
            async for token in stream_agent(query=request.query, context=request.context or ""):
                yield token
        except Exception as exc:
            yield f"\n[Error]: {exc}"

    return StreamingResponse(token_stream(), media_type="text/plain")
