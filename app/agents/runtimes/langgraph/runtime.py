"""LangGraph runtime executor."""
from typing import Dict, Any
from app.agents.runtimes.langgraph.workflow import build_customer_support_graph
from app.agents.schemas import FinalSupportResponse
from app.core.logging import get_logger

logger = get_logger("runtimes.langgraph")


class LangGraphRuntime:
    """Runtime that executes queries via LangGraph compiled StateGraph."""

    def __init__(self):
        self.app = build_customer_support_graph()

    async def process_message(self, message: str) -> FinalSupportResponse:
        """Processes a customer message using LangGraph StateGraph workflow."""
        logger.info(
            f"LangGraphRuntime processing message: '{message}'",
            extra={"event": "request_received"}
        )

        initial_state = {
            "customer_query": message,
            "intents": [],
            "entities": {},
            "specialist_results": [],
            "final_response": {}
        }

        result = await self.app.ainvoke(initial_state)
        final_dict = result.get("final_response", {})

        return FinalSupportResponse(
            answer=final_dict.get("answer", "I processed your request."),
            intents=final_dict.get("intents", []),
            sources=final_dict.get("sources", []),
            escalated_to_human=final_dict.get("escalated_to_human", False)
        )
