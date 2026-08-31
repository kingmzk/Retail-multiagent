"""Unit tests for Order and Product MCP server tools."""
from mcp_servers.order.tools import get_order_tool, search_orders_tool
from mcp_servers.product.tools import get_product_tool, search_products_tool, check_inventory_tool


def test_order_mcp_get_order_valid():
    res = get_order_tool("45231")
    assert res["success"] is True
    assert "order" in res
    order = res["order"]
    assert order["order_id"] == "45231"
    assert order["status"] == "SHIPPED"
    assert order["tracking_number"] == "TRK123456"
    assert order["eta"] == "2026-09-03"


def test_order_mcp_get_order_invalid_id():
    res = get_order_tool("000000")
    assert res["success"] is False
    assert res["error"] == "ORDER_NOT_FOUND"


def test_order_mcp_get_order_empty_id():
    res = get_order_tool("")
    assert res["success"] is False
    assert res["error"] == "EMPTY_ORDER_ID"


def test_order_mcp_search_orders():
    res = search_orders_tool(status="SHIPPED")
    assert res["success"] is True
    assert res["count"] >= 1


def test_product_mcp_get_product_by_sku():
    res = get_product_tool("SHOE-RN-001")
    assert res["success"] is True
    prod = res["product"]
    assert prod["name"] == "Running Shoes"
    assert prod["price"] == 120.00


def test_product_mcp_get_product_by_name():
    res = get_product_tool("Running Shoes")
    assert res["success"] is True
    assert res["product"]["sku"] == "SHOE-RN-001"


def test_product_mcp_get_product_not_found():
    res = get_product_tool("UNKNOWN-ITEM")
    assert res["success"] is False
    assert res["error"] == "PRODUCT_NOT_FOUND"


def test_product_mcp_check_inventory():
    res = check_inventory_tool("Running Shoes")
    assert res["success"] is True
    assert res["inventory"]["in_stock"] is True
    assert res["inventory"]["stock_quantity"] > 0
