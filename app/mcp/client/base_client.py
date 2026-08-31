"""Base Stateless HTTP JSON-RPC MCP Client with ASGI Fallback."""
import httpx
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger

logger = get_logger("mcp.client")


class MCPClientError(Exception):
    """Exception raised when an MCP tool call fails."""
    def __init__(self, message: str, code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.details = details


class StatelessHttpMcpClient:
    """A robust, stateless HTTP JSON-RPC 2.0 client for MCP servers.

    Supports network HTTP requests with automatic ASGI in-process fallback for unit tests and local dev.
    """

    def __init__(self, server_url: str, timeout: float = 10.0, fallback_app: Optional[Any] = None):
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.fallback_app = fallback_app

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Discovers available tools on the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.server_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                if "error" in data:
                    raise MCPClientError(
                        message=data["error"].get("message", "Unknown RPC error"),
                        code=data["error"].get("code")
                    )
                return data.get("result", {}).get("tools", [])
        except Exception as e:
            if self.fallback_app:
                transport = httpx.ASGITransport(app=self.fallback_app)
                async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                    resp = await client.post("/mcp", json=payload)
                    data = resp.json()
                    return data.get("result", {}).get("tools", [])
            logger.error(f"Failed to connect to MCP server at {self.server_url}: {e}", extra={"event": "error"})
            raise MCPClientError(f"MCP server unavailable at {self.server_url}: {str(e)}")

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calls a tool on the MCP server statelessly over HTTP JSON-RPC."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            },
            "id": 1
        }
        logger.info(
            f"Calling MCP tool: {name}",
            extra={"event": "mcp_request", "extra_data": {"tool": name, "server_url": self.server_url}}
        )

        try:
            # 1. Try real network HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.server_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return self._parse_response(name, data)
        except Exception as net_err:
            # 2. If standalone server process is not running, fallback to in-process ASGI app
            if self.fallback_app:
                logger.info(f"Using ASGI in-process transport for {self.server_url}")
                transport = httpx.ASGITransport(app=self.fallback_app)
                async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                    resp = await client.post("/mcp", json=payload)
                    data = resp.json()
                    return self._parse_response(name, data)

            logger.error(f"MCP HTTP request failed for {name} on {self.server_url}: {net_err}", extra={"event": "error"})
            raise MCPClientError(f"MCP server unavailable at {self.server_url}: {str(net_err)}")

    def _parse_response(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in data:
            err = data["error"]
            logger.error(f"MCP tool error for {name}: {err}", extra={"event": "error"})
            raise MCPClientError(
                message=err.get("message", "Tool execution failed"),
                code=err.get("code")
            )

        result = data.get("result", {})
        structured = result.get("structured")
        if structured is not None:
            logger.info(
                f"MCP tool {name} responded with structured payload",
                extra={"event": "mcp_response", "extra_data": {"success": structured.get("success", False)}}
            )
            return structured

        return result
