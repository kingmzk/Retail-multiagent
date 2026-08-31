"""Unit tests for individual domain agents."""
import pytest
from app.agents.domain.router import RouterAgent
from app.agents.domain.order import OrderAgent
from app.agents.domain.policy import PolicyAgent
from app.agents.domain.product import ProductAgent
from app.agents.schemas import IntentType


@pytest.mark.asyncio
async def test_router_agent_multi_intent():
    router = RouterAgent()
    query = "Where is my order #45231? Can I return the shoes if they don't fit?"
    decision = await router.route(query)

    assert IntentType.ORDER_STATUS in decision.intents
    assert IntentType.RETURN_POLICY in decision.intents
    assert decision.entities.order_id == "45231"


@pytest.mark.asyncio
async def test_router_agent_single_intent_order():
    router = RouterAgent()
    query = "Track order 45231"
    decision = await router.route(query)
    assert IntentType.ORDER_STATUS in decision.intents


@pytest.mark.asyncio
async def test_policy_agent_execution():
    policy_agent = PolicyAgent()
    res = await policy_agent.execute("Can I return shoes if they don't fit?")
    assert res.success is True
    assert res.intent == IntentType.RETURN_POLICY
    assert len(res.sources) > 0
    assert "30" in res.summary.lower() or "unworn" in res.summary.lower() or "return" in res.summary.lower()
