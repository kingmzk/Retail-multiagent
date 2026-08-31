"""Typed Product MCP Client."""
from typing import Dict, Any, Optional
from app.mcp.client.base_client import StatelessHttpMcpClient
from app.core.config import settings
from mcp_servers.product.server import app as product_app


class ProductMcpClient:
    """Client for invoking Product MCP Server tools."""

    def __init__(self, server_url: Optional[str] = None, timeout: Optional[float] = None):
        url = server_url or settings.PRODUCT_MCP_URL
        t = timeout or settings.MCP_REQUEST_TIMEOUT
        self.client = StatelessHttpMcpClient(server_url=url, timeout=t, fallback_app=product_app)

    async def get_product(self, sku_or_id: str) -> Dict[str, Any]:
        """Invokes get_product tool on Product MCP Server."""
        return await self.client.call_tool("get_product", {"sku_or_id": sku_or_id})

    async def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Invokes search_products tool on Product MCP Server."""
        args: Dict[str, Any] = {"limit": limit}
        if query:
            args["query"] = query
        if category:
            args["category"] = category
        return await self.client.call_tool("search_products", args)

    async def check_inventory(self, product_name_or_sku: str) -> Dict[str, Any]:
        """Invokes check_inventory tool on Product MCP Server."""
        return await self.client.call_tool("check_inventory", {"product_name_or_sku": product_name_or_sku})
