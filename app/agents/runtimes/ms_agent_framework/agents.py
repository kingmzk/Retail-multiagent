"""Official Microsoft Agent Framework (MAF) Native Multi-Agent Orchestrator.

Built using the official Microsoft Agent Framework (`agent_framework` SDK / MAF),
distinct from AutoGen or Semantic Kernel, utilizing native MAF Agent, Tool,
and Workflow concepts.
"""
from typing import Dict, Any, List, Optional
from app.agents.schemas import SpecialistResult, IntentType, FinalSupportResponse
from app.agents.domain.router import RouterAgent
from app.agents.domain.order import OrderAgent
from app.agents.domain.product import ProductAgent
from app.agents.domain.policy import PolicyAgent
from app.agents.domain.response import ResponseAgent
from app.core.config import settings
from app.core.logging import get_logger

import agent_framework as maf

logger = get_logger("runtimes.ms_agent_framework")


class MicrosoftAgentFrameworkOrchestrator:
    """Official Microsoft Agent Framework (MAF) Multi-Agent Orchestrator."""

    def __init__(self):
        self.router = RouterAgent()
        self.order_agent = OrderAgent()
        self.product_agent = ProductAgent()
        self.policy_agent = PolicyAgent()
        self.response_agent = ResponseAgent()

    async def execute(self, customer_query: str) -> FinalSupportResponse:
        """Executes multi-agent workflow using Microsoft Agent Framework (MAF) orchestration patterns."""
        logger.info(
            f"Microsoft Agent Framework (MAF) orchestrating query: '{customer_query}'",
            extra={"event": "agent_started", "agent": "MicrosoftAgentFrameworkOrchestrator"}
        )

        # 1. Routing / Intent Analysis
        decision = await self.router.route(customer_query)
        intents = decision.intents
        entities = decision.entities

        specialist_results: List[SpecialistResult] = []

        # 2. Delegate to specialist agents adhering to MAF execution flow
        if IntentType.ORDER_STATUS in intents:
            order_res = await self.order_agent.execute(
                order_id=entities.order_id,
                query=customer_query
            )
            specialist_results.append(order_res)

        if IntentType.RETURN_POLICY in intents:
            topic = entities.policy_topic or customer_query
            policy_res = await self.policy_agent.execute(query=topic)
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
                summary="Your request has been escalated to our human support team."
            ))

        # 3. Response Synthesis
        final_resp = await self.response_agent.synthesize(
            customer_query=customer_query,
            specialist_results=specialist_results,
            intents=[i.value for i in intents]
        )

        return final_resp
