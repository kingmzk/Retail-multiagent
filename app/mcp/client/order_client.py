"""Typed Order MCP Client."""
from typing import Dict, Any, Optional
from app.mcp.client.base_client import StatelessHttpMcpClient
from app.core.config import settings
from mcp_servers.order.server import app as order_app


class OrderMcpClient:
    """Client for invoking Order MCP Server tools."""

    def __init__(self, server_url: Optional[str] = None, timeout: Optional[float] = None):
        url = server_url or settings.ORDER_MCP_URL
        t = timeout or settings.MCP_REQUEST_TIMEOUT
        self.client = StatelessHttpMcpClient(server_url=url, timeout=t, fallback_app=order_app)

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Invokes get_order tool on Order MCP Server."""
        return await self.client.call_tool("get_order", {"order_id": order_id})

    async def search_orders(
        self,
        query: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Invokes search_orders tool on Order MCP Server."""
        args: Dict[str, Any] = {"limit": limit}
        if query:
            args["query"] = query
        if status:
            args["status"] = status
        return await self.client.call_tool("search_orders", args)
