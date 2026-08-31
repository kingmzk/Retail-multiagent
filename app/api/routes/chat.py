"""Chat API route for customer inquiries."""
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import ChatRequest, ChatResponse, SourceMetadata
from app.agents.runtimes.factory import get_agent_runtime
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("api.chat")
router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Executes customer support multi-agent workflow for the incoming message."""
    clean_msg = request.message.strip()
    if not clean_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The customer message cannot be empty."
        )

    framework = request.framework or settings.AGENT_FRAMEWORK
    logger.info(
        f"Incoming customer chat request: '{clean_msg}' (Runtime: {framework})",
        extra={"event": "request_received", "extra_data": {"framework": framework}}
    )

    try:
        runtime = get_agent_runtime(framework=framework)
        final_res = await runtime.process_message(clean_msg)

        sources = [
            SourceMetadata(
                document=s.get("document", "policy.md"),
                section=s.get("section")
            )
            for s in final_res.sources
        ]

        return ChatResponse(
            answer=final_res.answer,
            intents=final_res.intents,
            sources=sources,
            escalated_to_human=final_res.escalated_to_human,
            framework=framework
        )

    except Exception as e:
        logger.error(f"Chat processing error: {e}", extra={"event": "error"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="We encountered an unexpected error processing your customer support request. Please try again."
        )
