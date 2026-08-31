"""Stateless HTTP JSON-RPC Product MCP Server.

Provides tools for the Product Agent via standard JSON-RPC 2.0 over HTTP.
Default port: 8102
"""
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
from mcp_servers.product.tools import get_product_tool, search_products_tool, check_inventory_tool

app = FastAPI(
    title="Product MCP Microservice",
    description="Stateless HTTP MCP Server providing product specifications, catalog search, and inventory checks.",
    version="1.0.0"
)


PRODUCT_TOOL_SCHEMAS = [
    {
        "name": "get_product",
        "description": "Get detailed product specifications, category, price, and description by SKU or product ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku_or_id": {
                    "type": "string",
                    "description": "Product SKU (e.g. 'SHOE-RN-001') or numeric ID."
                }
            },
            "required": ["sku_or_id"]
        }
    },
    {
        "name": "search_products",
        "description": "Search the product catalog by keyword or category.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword to search in product name or description."
                },
                "category": {
                    "type": "string",
                    "description": "Category filter (e.g. 'Footwear', 'Apparel', 'Accessories', 'Electronics')."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)."
                }
            }
        }
    },
    {
        "name": "check_inventory",
        "description": "Check if a product is in stock and get current available quantity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_name_or_sku": {
                    "type": "string",
                    "description": "Product name (e.g. 'Running Shoes') or SKU."
                }
            },
            "required": ["product_name_or_sku"]
        }
    }
]


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = 1


@app.get("/health")
def health():
    return {"status": "ok", "service": "product-mcp-server", "port": 8102}


@app.post("/mcp")
@app.post("/mcp/rpc")
async def handle_mcp_rpc(request: JsonRpcRequest):
    """Stateless JSON-RPC 2.0 handler for Product MCP tool discovery and execution."""
    method = request.method
    params = request.params or {}
    req_id = request.id

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": PRODUCT_TOOL_SCHEMAS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_product":
            sku_or_id = arguments.get("sku_or_id", "")
            output = get_product_tool(sku_or_id)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(output)
                        }
                    ],
                    "structured": output,
                    "isError": not output.get("success", False)
                }
            }

        elif tool_name == "search_products":
            query = arguments.get("query")
            category = arguments.get("category")
            limit = arguments.get("limit", 5)
            output = search_products_tool(query=query, category=category, limit=limit)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(output)
                        }
                    ],
                    "structured": output,
                    "isError": not output.get("success", False)
                }
            }

        elif tool_name == "check_inventory":
            product_name_or_sku = arguments.get("product_name_or_sku", "")
            output = check_inventory_tool(product_name_or_sku)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(output)
                        }
                    ],
                    "structured": output,
                    "isError": not output.get("success", False)
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8102)
