"""Runtime Factory for selecting agent orchestrators."""
from typing import Literal, Union
from app.core.config import settings
from app.core.logging import get_logger
from app.agents.runtimes.langgraph.runtime import LangGraphRuntime
from app.agents.runtimes.langchain.runtime import LangChainRuntime
from app.agents.runtimes.adk.runtime import ADKRuntime
from app.agents.runtimes.autogen.runtime import AutoGenRuntime
from app.agents.runtimes.ms_agent_framework.runtime import MicrosoftAgentFrameworkRuntime

logger = get_logger("runtimes.factory")

SupportedRuntime = Union[
    LangGraphRuntime, 
    LangChainRuntime, 
    ADKRuntime, 
    AutoGenRuntime, 
    MicrosoftAgentFrameworkRuntime
]


def get_agent_runtime(framework: str = None) -> SupportedRuntime:
    """Returns the agent runtime corresponding to the configured framework."""
    fw = (framework or settings.AGENT_FRAMEWORK).lower().strip()

    logger.info(f"Instantiating agent runtime for framework: '{fw}'")

    if fw in ["langgraph"]:
        return LangGraphRuntime()
    elif fw in ["langchain"]:
        return LangChainRuntime()
    elif fw in ["adk", "google", "google-adk"]:
        return ADKRuntime()
    elif fw in ["autogen", "autogen-agentchat"]:
        return AutoGenRuntime()
    elif fw in ["ms_agent_framework", "maf", "microsoft", "microsoft-agent-framework", "agent-framework"]:
        return MicrosoftAgentFrameworkRuntime()
    else:
        logger.warning(f"Unknown framework '{fw}', defaulting to LangGraph.")
        return LangGraphRuntime()
