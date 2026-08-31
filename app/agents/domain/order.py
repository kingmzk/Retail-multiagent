"""Order Specialist Agent Domain Logic.

Communicates exclusively through Order MCP Client to fetch order statuses and tracking details.
"""
from typing import Optional, Dict, Any
from app.agents.schemas import SpecialistResult, IntentType
from app.mcp.client.order_client import OrderMcpClient
from app.core.logging import get_logger

logger = get_logger("agents.order")


class OrderAgent:
    """Specialist agent for handling order operational queries via MCP."""

    def __init__(self, mcp_client: Optional[OrderMcpClient] = None):
        self.mcp_client = mcp_client or OrderMcpClient()

    async def execute(self, order_id: Optional[str] = None, query: Optional[str] = None) -> SpecialistResult:
        """Executes order discovery or status retrieval using Order MCP Server."""
        logger.info(
            f"OrderAgent started for order_id: {order_id}",
            extra={"event": "agent_started", "agent": "OrderAgent"}
        )

        clean_id = str(order_id).strip().lstrip("#") if order_id else None

        # If order_id was provided or extracted
        if clean_id:
            try:
                response = await self.mcp_client.get_order(clean_id)
                if response.get("success"):
                    order = response.get("order", {})
                    items_str = ", ".join([f"{item['quantity']}x {item['product_name']}" for item in order.get("items", [])])
                    summary = (
                        f"Order #{order.get('order_id')} is currently {order.get('status')}. "
                        f"Expected arrival date (ETA): {order.get('eta')}. "
                        f"Carrier tracking number: {order.get('tracking_number') or 'Not yet assigned'} "
                        f"via {order.get('carrier', 'Standard Carrier')}. "
                        f"Items in order: {items_str}."
                    )
                    return SpecialistResult(
                        agent_name="OrderAgent",
                        intent=IntentType.ORDER_STATUS,
                        success=True,
                        summary=summary,
                        raw_data=order
                    )
                else:
                    err_msg = response.get("message", f"Order #{clean_id} could not be found.")
                    return SpecialistResult(
                        agent_name="OrderAgent",
                        intent=IntentType.ORDER_STATUS,
                        success=False,
                        summary=err_msg,
                        raw_data=response
                    )
            except Exception as e:
                logger.error(f"OrderAgent MCP execution failed: {e}", extra={"event": "error"})
                return SpecialistResult(
                    agent_name="OrderAgent",
                    intent=IntentType.ORDER_STATUS,
                    success=False,
                    summary=f"Unable to retrieve order details due to an internal service error: {str(e)}"
                )

        # Fallback to search if no specific ID
        if query:
            try:
                search_res = await self.mcp_client.search_orders(query=query)
                if search_res.get("success") and search_res.get("orders"):
                    orders = search_res.get("orders", [])
                    summary = f"Found {len(orders)} matching order(s): " + ", ".join([f"#{o['order_id']} ({o['status']})" for o in orders])
                    return SpecialistResult(
                        agent_name="OrderAgent",
                        intent=IntentType.ORDER_STATUS,
                        success=True,
                        summary=summary,
                        raw_data={"orders": orders}
                    )
            except Exception as e:
                logger.error(f"OrderAgent search failed: {e}", extra={"event": "error"})

        return SpecialistResult(
            agent_name="OrderAgent",
            intent=IntentType.ORDER_STATUS,
            success=False,
            summary="Please provide a valid order number (e.g., #45231) so I can locate your order details."
        )
