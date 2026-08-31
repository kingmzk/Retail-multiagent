"""Parity tests ensuring LangGraph, LangChain, Google ADK, AutoGen, and Microsoft Agent Framework (MAF) behave consistently."""
import pytest
from app.agents.runtimes.factory import get_agent_runtime


@pytest.mark.parametrize("framework", ["langgraph", "langchain", "adk", "autogen", "maf"])
@pytest.mark.asyncio
async def test_framework_parity_multi_intent(framework):
    """Verifies that all agent runtimes produce accurate, grounded results for the primary scenario."""
    runtime = get_agent_runtime(framework)
    query = "Where is my order #45231? Can I return the shoes if they don't fit?"
    result = await runtime.process_message(query)

    assert "ORDER_STATUS" in result.intents
    assert "RETURN_POLICY" in result.intents
    assert "45231" in result.answer
    assert "SHIPPED" in result.answer.upper() or "shipped" in result.answer.lower()
    assert len(result.sources) > 0


@pytest.mark.parametrize("framework", ["langgraph", "langchain", "adk", "autogen", "maf"])
@pytest.mark.asyncio
async def test_framework_parity_product_info(framework):
    """Verifies product lookup across all frameworks."""
    runtime = get_agent_runtime(framework)
    query = "Tell me about the Running Shoes specifications and price."
    result = await runtime.process_message(query)

    assert "PRODUCT_INFORMATION" in result.intents
    assert "Running Shoes" in result.answer or "120" in result.answer or "SHOE-RN-001" in result.answer
