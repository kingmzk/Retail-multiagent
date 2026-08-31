"""Microsoft AutoGen runtime executor."""
from app.agents.runtimes.autogen.agents import MicrosoftAutoGenSupportOrchestrator
from app.agents.schemas import FinalSupportResponse
from app.core.logging import get_logger

logger = get_logger("runtimes.autogen")


class AutoGenRuntime:
    """Runtime that executes customer support queries using native Microsoft AutoGen agent components."""

    def __init__(self):
        self.orchestrator = MicrosoftAutoGenSupportOrchestrator()

    async def process_message(self, message: str) -> FinalSupportResponse:
        """Processes a customer message via Microsoft AutoGen."""
        logger.info(
            f"AutoGenRuntime processing message: '{message}'",
            extra={"event": "request_received"}
        )
        return await self.orchestrator.execute(message)
