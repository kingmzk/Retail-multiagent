"""End-to-End tests for Multi-Agent Customer Support Assistant."""
import pytest
from app.agents.runtimes.factory import get_agent_runtime


@pytest.mark.asyncio
async def test_primary_multi_intent_demonstration():
    """Primary demonstration query:

    'Where is my order #45231? Can I return the shoes if they don't fit?'
    """
    runtime = get_agent_runtime("langgraph")
    query = "Where is my order #45231? Can I return the shoes if they don't fit?"
    result = await runtime.process_message(query)

    # 1. Verify detected intents
    assert "ORDER_STATUS" in result.intents
    assert "RETURN_POLICY" in result.intents

    # 2. Verify answer contains order status information
    answer = result.answer
    assert "45231" in answer
    assert "SHIPPED" in answer.upper() or "shipped" in answer.lower()

    # 3. Verify answer contains return policy information
    assert "30" in answer or "return" in answer.lower() or "unworn" in answer.lower()

    # 4. Verify sources metadata returned
    assert len(result.sources) > 0


@pytest.mark.asyncio
async def test_single_intent_order():
    runtime = get_agent_runtime("langgraph")
    query = "What is the status of my order #45231?"
    result = await runtime.process_message(query)

    assert "ORDER_STATUS" in result.intents
    assert "45231" in result.answer
    assert "SHIPPED" in result.answer.upper() or "shipped" in result.answer.lower()


@pytest.mark.asyncio
async def test_single_intent_policy():
    runtime = get_agent_runtime("langgraph")
    query = "Can I return shoes if they don't fit?"
    result = await runtime.process_message(query)

    assert "RETURN_POLICY" in result.intents
    assert len(result.sources) > 0
    assert "return" in result.answer.lower() or "30" in result.answer
