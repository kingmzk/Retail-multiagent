"""Health check route."""
import httpx
from fastapi import APIRouter
from sqlalchemy import text
from app.api.schemas import HealthResponse
from app.core.config import settings
from app.database.session import SessionLocal
from app.rag.ingestion import get_chroma_client

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Returns overall health of the application and connected microservices."""
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"unhealthy ({str(e)})"

    chroma_status = "connected"
    try:
        client = get_chroma_client()
        client.heartbeat()
    except Exception as e:
        chroma_status = f"unhealthy ({str(e)})"

    # Check MCP microservices
    mcp_statuses = {}
    for name, url in [("order_mcp", settings.ORDER_MCP_URL), ("product_mcp", settings.PRODUCT_MCP_URL)]:
        try:
            base_url = url.replace("/mcp", "")
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{base_url}/health")
                mcp_statuses[name] = "healthy" if res.status_code == 200 else f"status {res.status_code}"
        except Exception:
            mcp_statuses[name] = "offline"

    overall = "healthy" if db_status == "connected" and chroma_status == "connected" else "degraded"

    return HealthResponse(
        status=overall,
        app_name=settings.APP_NAME,
        framework=settings.AGENT_FRAMEWORK,
        database=db_status,
        chromadb=chroma_status,
        mcp_servers=mcp_statuses
    )
