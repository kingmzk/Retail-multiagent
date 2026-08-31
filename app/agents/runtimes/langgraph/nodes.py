"""LangGraph node functions."""
from typing import Dict, Any
from app.agents.runtimes.langgraph.state import CustomerSupportGraphState
from app.agents.domain.router import RouterAgent
from app.agents.domain.order import OrderAgent
from app.agents.domain.product import ProductAgent
from app.agents.domain.policy import PolicyAgent
from app.agents.domain.response import ResponseAgent
from app.agents.schemas import SpecialistResult, IntentType
from app.core.logging import get_logger

logger = get_logger("langgraph.nodes")

router_agent = RouterAgent()
order_agent = OrderAgent()
product_agent = ProductAgent()
policy_agent = PolicyAgent()
response_agent = ResponseAgent()


async def router_node(state: CustomerSupportGraphState) -> Dict[str, Any]:
    """Router node analyzes query and determines intents & entities."""
    query = state["customer_query"]
    decision = await router_agent.route(query)
    return {
        "intents": [i.value for i in decision.intents],
        "entities": decision.entities.model_dump(),
        "specialist_results": []
    }


async def order_agent_node(state: CustomerSupportGraphState) -> Dict[str, Any]:
    """Order specialist node queries Order MCP service."""
    entities = state.get("entities", {})
    order_id = entities.get("order_id")
    query = state.get("customer_query")

    res = await order_agent.execute(order_id=order_id, query=query)
    return {
        "specialist_results": [res.model_dump()]
    }


async def policy_agent_node(state: CustomerSupportGraphState) -> Dict[str, Any]:
    """Policy specialist node queries ChromaDB RAG knowledge base."""
    query = state.get("customer_query")
    entities = state.get("entities", {})
    topic = entities.get("policy_topic") or query

    res = await policy_agent.execute(query=topic)
    return {
        "specialist_results": [res.model_dump()]
    }


async def product_agent_node(state: CustomerSupportGraphState) -> Dict[str, Any]:
    """Product specialist node queries Product MCP service."""
    entities = state.get("entities", {})
    product_name = entities.get("product_name")
    sku = entities.get("sku")
    query = state.get("customer_query")

    res = await product_agent.execute(product_name=product_name, sku=sku, query=query)
    return {
        "specialist_results": [res.model_dump()]
    }


async def escalation_node(state: CustomerSupportGraphState) -> Dict[str, Any]:
    """Escalation node handles customer queries needing human assistance."""
    res = SpecialistResult(
        agent_name="EscalationAgent",
        intent=IntentType.HUMAN_ESCALATION,
        success=True,
        summary="Your request has been escalated to a human support specialist. An agent will contact you shortly during business hours (Mon-Fri 8am-8pm EST)."
    )
    return {
        "specialist_results": [res.model_dump()]
    }


async def response_node(state: CustomerSupportGraphState) -> Dict[str, Any]:
    """Response node fuses specialist outputs into final customer answer."""
    query = state["customer_query"]
    intents = state.get("intents", [])
    raw_results = state.get("specialist_results", [])

    specialist_results = [SpecialistResult(**r) for r in raw_results]
    final_resp = await response_agent.synthesize(
        customer_query=query,
        specialist_results=specialist_results,
        intents=intents
    )

    return {
        "final_response": final_resp.model_dump()
    }
