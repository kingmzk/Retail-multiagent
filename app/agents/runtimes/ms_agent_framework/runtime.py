"""Official Microsoft Agent Framework (MAF) Runtime Executor."""
from app.agents.runtimes.ms_agent_framework.agents import MicrosoftAgentFrameworkOrchestrator
from app.agents.schemas import FinalSupportResponse
from app.core.logging import get_logger

logger = get_logger("runtimes.ms_agent_framework")


class MicrosoftAgentFrameworkRuntime:
    """Runtime that executes customer support queries using the official Microsoft Agent Framework (MAF)."""

    def __init__(self):
        self.orchestrator = MicrosoftAgentFrameworkOrchestrator()

    async def process_message(self, message: str) -> FinalSupportResponse:
        """Processes a customer message via Microsoft Agent Framework."""
        logger.info(
            f"MicrosoftAgentFrameworkRuntime processing message: '{message}'",
            extra={"event": "request_received"}
        )
        return await self.orchestrator.execute(message)
