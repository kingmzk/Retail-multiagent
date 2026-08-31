"""LangChain runtime executor."""
from app.agents.runtimes.langchain.agents import LangChainSupportOrchestrator
from app.agents.schemas import FinalSupportResponse
from app.core.logging import get_logger

logger = get_logger("runtimes.langchain")


class LangChainRuntime:
    """Runtime that executes customer support queries using native LangChain components."""

    def __init__(self):
        self.orchestrator = LangChainSupportOrchestrator()

    async def process_message(self, message: str) -> FinalSupportResponse:
        """Processes a customer message via LangChain."""
        logger.info(
            f"LangChainRuntime processing message: '{message}'",
            extra={"event": "request_received"}
        )
        return await self.orchestrator.execute(message)
