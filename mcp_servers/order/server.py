"""Stateless HTTP JSON-RPC Order MCP Server.

Provides tools for the Order Agent via standard JSON-RPC 2.0 over HTTP.
Default port: 8101
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from mcp_servers.order.tools import get_order_tool, search_orders_tool

app = FastAPI(
    title="Order MCP Microservice",
    description="Stateless HTTP MCP Server providing order status, tracking, and details.",
    version="1.0.0"
)


ORDER_TOOL_SCHEMAS = [
    {
        "name": "get_order",
        "description": "Get detailed operational information for a specific order including status, ETA, tracking number, and line items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The unique order number (e.g. '45231' or '#45231')."
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "search_orders",
        "description": "Search for orders by tracking number, customer ID, or status keyword.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term, order number, or tracking number."
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (e.g. 'SHIPPED', 'DELIVERED', 'PROCESSING')."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)."
                }
            }
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
    return {"status": "ok", "service": "order-mcp-server", "port": 8101}


@app.post("/mcp")
@app.post("/mcp/rpc")
async def handle_mcp_rpc(request: JsonRpcRequest):
    """Stateless JSON-RPC 2.0 handler for MCP tool discovery and execution."""
    method = request.method
    params = request.params or {}
    req_id = request.id

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": ORDER_TOOL_SCHEMAS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_order":
            order_id = arguments.get("order_id", "")
            output = get_order_tool(order_id)
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

        elif tool_name == "search_orders":
            query = arguments.get("query")
            status = arguments.get("status")
            limit = arguments.get("limit", 5)
            output = search_orders_tool(query=query, status=status, limit=limit)
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
    uvicorn.run(app, host="0.0.0.0", port=8101)
