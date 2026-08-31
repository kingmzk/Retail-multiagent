"""Google ADK runtime executor."""
from app.agents.runtimes.adk.agents import GoogleADKSupportOrchestrator
from app.agents.schemas import FinalSupportResponse
from app.core.logging import get_logger

logger = get_logger("runtimes.adk")


class ADKRuntime:
    """Runtime that executes customer support queries using native Google ADK components."""

    def __init__(self):
        self.orchestrator = GoogleADKSupportOrchestrator()

    async def process_message(self, message: str) -> FinalSupportResponse:
        """Processes a customer message via Google ADK."""
        logger.info(
            f"ADKRuntime processing message: '{message}'",
            extra={"event": "request_received"}
        )
        return await self.orchestrator.execute(message)
