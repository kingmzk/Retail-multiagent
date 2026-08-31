"""Integration tests for MCP Server and Client."""
import pytest
from httpx import AsyncClient, ASGITransport
from mcp_servers.order.server import app as order_app
from mcp_servers.product.server import app as product_app
from app.mcp.client.base_client import StatelessHttpMcpClient


@pytest.mark.asyncio
async def test_order_mcp_server_tools_list():
    transport = ASGITransport(app=order_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        tools = [t["name"] for t in data["result"]["tools"]]
        assert "get_order" in tools
        assert "search_orders" in tools


@pytest.mark.asyncio
async def test_order_mcp_server_tools_call():
    transport = ASGITransport(app=order_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "get_order", "arguments": {"order_id": "45231"}},
            "id": 1
        }
        resp = await client.post("/mcp", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert data["result"]["structured"]["success"] is True
        assert data["result"]["structured"]["order"]["order_id"] == "45231"


@pytest.mark.asyncio
async def test_product_mcp_server_tools_call():
    transport = ASGITransport(app=product_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "check_inventory", "arguments": {"product_name_or_sku": "Running Shoes"}},
            "id": 1
        }
        resp = await client.post("/mcp", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["structured"]["success"] is True
        assert data["result"]["structured"]["inventory"]["in_stock"] is True
