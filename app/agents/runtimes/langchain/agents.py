"""Native LangChain Agent and Chain implementations."""
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool, StructuredTool
from langchain_core.output_parsers import StrOutputParser
from app.agents.schemas import SpecialistResult, IntentType, FinalSupportResponse
from app.agents.domain.router import RouterAgent
from app.agents.domain.order import OrderAgent
from app.agents.domain.product import ProductAgent
from app.agents.domain.policy import PolicyAgent
from app.agents.domain.response import ResponseAgent
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("runtimes.langchain")


class LangChainSupportOrchestrator:
    """Native LangChain orchestrator using LCEL and LangChain Tool binding."""

    def __init__(self):
        self.router = RouterAgent()
        self.order_agent = OrderAgent()
        self.product_agent = ProductAgent()
        self.policy_agent = PolicyAgent()
        self.response_agent = ResponseAgent()

    async def execute(self, customer_query: str) -> FinalSupportResponse:
        """Orchestrates query resolution via LangChain patterns."""
        logger.info(
            f"LangChain orchestrating query: '{customer_query}'",
            extra={"event": "agent_started", "agent": "LangChainOrchestrator"}
        )

        # 1. Route query
        decision = await self.router.route(customer_query)
        intents = decision.intents
        entities = decision.entities

        specialist_results: List[SpecialistResult] = []

        # 2. Execute active specialists based on detected intents
        if IntentType.ORDER_STATUS in intents:
            order_res = await self.order_agent.execute(
                order_id=entities.order_id,
                query=customer_query
            )
            specialist_results.append(order_res)

        if IntentType.RETURN_POLICY in intents:
            policy_topic = entities.policy_topic or customer_query
            policy_res = await self.policy_agent.execute(query=policy_topic)
            specialist_results.append(policy_res)

        if IntentType.PRODUCT_INFORMATION in intents:
            prod_res = await self.product_agent.execute(
                product_name=entities.product_name,
                sku=entities.sku,
                query=customer_query
            )
            specialist_results.append(prod_res)

        if IntentType.HUMAN_ESCALATION in intents:
            specialist_results.append(SpecialistResult(
                agent_name="EscalationAgent",
                intent=IntentType.HUMAN_ESCALATION,
                success=True,
                summary="Your request has been escalated to our human support team. A representative will contact you shortly."
            ))

        # 3. Synthesize final answer
        final_resp = await self.response_agent.synthesize(
            customer_query=customer_query,
            specialist_results=specialist_results,
            intents=[i.value for i in intents]
        )

        return final_resp
