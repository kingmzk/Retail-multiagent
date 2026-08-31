"""Product Specialist Agent Domain Logic.

Communicates exclusively through Product MCP Client to fetch product details and inventory.
"""
from typing import Optional, Dict, Any
from app.agents.schemas import SpecialistResult, IntentType
from app.mcp.client.product_client import ProductMcpClient
from app.core.logging import get_logger

logger = get_logger("agents.product")


class ProductAgent:
    """Specialist agent for handling product and inventory inquiries via MCP."""

    def __init__(self, mcp_client: Optional[ProductMcpClient] = None):
        self.mcp_client = mcp_client or ProductMcpClient()

    async def execute(
        self,
        product_name: Optional[str] = None,
        sku: Optional[str] = None,
        query: Optional[str] = None
    ) -> SpecialistResult:
        """Executes product lookup or inventory check using Product MCP Server."""
        logger.info(
            f"ProductAgent started for product: {product_name or sku or query}",
            extra={"event": "agent_started", "agent": "ProductAgent"}
        )

        identifier = sku or product_name or query
        if not identifier:
            return SpecialistResult(
                agent_name="ProductAgent",
                intent=IntentType.PRODUCT_INFORMATION,
                success=False,
                summary="Please specify a product name or SKU to look up specifications or inventory."
            )

        try:
            # Check inventory and product details
            prod_res = await self.mcp_client.get_product(identifier)
            if prod_res.get("success"):
                p = prod_res.get("product", {})
                stock_status = f"In Stock ({p.get('stock_quantity')} available)" if p.get("in_stock") else "Currently Out of Stock"
                summary = (
                    f"Product: {p.get('name')} (SKU: {p.get('sku')}). "
                    f"Category: {p.get('category')}. "
                    f"Price: ${p.get('price'):.2f}. "
                    f"Availability: {stock_status}. "
                    f"Description: {p.get('description')}."
                )
                return SpecialistResult(
                    agent_name="ProductAgent",
                    intent=IntentType.PRODUCT_INFORMATION,
                    success=True,
                    summary=summary,
                    raw_data=p
                )

            # Fallback to search
            search_res = await self.mcp_client.search_products(query=identifier)
            if search_res.get("success") and search_res.get("products"):
                products = search_res.get("products", [])
                summary = f"Found {len(products)} matching product(s): " + ", ".join(
                    [f"{p['name']} (${p['price']:.2f})" for p in products]
                )
                return SpecialistResult(
                    agent_name="ProductAgent",
                    intent=IntentType.PRODUCT_INFORMATION,
                    success=True,
                    summary=summary,
                    raw_data={"products": products}
                )

            return SpecialistResult(
                agent_name="ProductAgent",
                intent=IntentType.PRODUCT_INFORMATION,
                success=False,
                summary=f"No products found matching '{identifier}'."
            )

        except Exception as e:
            logger.error(f"ProductAgent MCP execution error: {e}", extra={"event": "error"})
            return SpecialistResult(
                agent_name="ProductAgent",
                intent=IntentType.PRODUCT_INFORMATION,
                success=False,
                summary=f"Product catalog service temporarily unavailable: {str(e)}"
            )
