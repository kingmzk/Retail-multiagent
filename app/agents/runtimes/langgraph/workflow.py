"""LangGraph Workflow Graph Definition."""
from typing import List
from langgraph.graph import StateGraph, START, END
from app.agents.runtimes.langgraph.state import CustomerSupportGraphState
from app.agents.runtimes.langgraph.nodes import (
    router_node,
    order_agent_node,
    policy_agent_node,
    product_agent_node,
    escalation_node,
    response_node
)


def route_to_specialists(state: CustomerSupportGraphState) -> List[str]:
    """Conditional routing function determining which specialist nodes to execute."""
    intents = state.get("intents", [])
    targets = []

    if "ORDER_STATUS" in intents:
        targets.append("order_agent")
    if "RETURN_POLICY" in intents:
        targets.append("policy_agent")
    if "PRODUCT_INFORMATION" in intents:
        targets.append("product_agent")
    if "HUMAN_ESCALATION" in intents:
        targets.append("escalation_agent")

    # If no specific specialist needed, route directly to response synthesizer
    if not targets:
        targets.append("response_agent")

    return targets


def build_customer_support_graph() -> StateGraph:
    """Builds and compiles the multi-agent StateGraph."""
    workflow = StateGraph(CustomerSupportGraphState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("order_agent", order_agent_node)
    workflow.add_node("policy_agent", policy_agent_node)
    workflow.add_node("product_agent", product_agent_node)
    workflow.add_node("escalation_agent", escalation_node)
    workflow.add_node("response_agent", response_node)

    # Edge from START to router
    workflow.add_edge(START, "router")

    # Conditional branching from router to specialists
    workflow.add_conditional_edges(
        "router",
        route_to_specialists,
        {
            "order_agent": "order_agent",
            "policy_agent": "policy_agent",
            "product_agent": "product_agent",
            "escalation_agent": "escalation_agent",
            "response_agent": "response_agent"
        }
    )

    # Fan-in edges from specialists to response agent
    workflow.add_edge("order_agent", "response_agent")
    workflow.add_edge("policy_agent", "response_agent")
    workflow.add_edge("product_agent", "response_agent")
    workflow.add_edge("escalation_agent", "response_agent")

    # Edge from response agent to END
    workflow.add_edge("response_agent", END)

    return workflow.compile()
