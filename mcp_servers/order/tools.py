"""Order MCP Tools implementation.

Connects to PostgreSQL via OrderRepository and provides tools for order discovery and status.
"""
from typing import Dict, Any, Optional
from app.database.session import SessionLocal
from app.database.repositories.order_repo import OrderRepository


def get_order_tool(order_id: str) -> Dict[str, Any]:
    """Retrieves operational order status, ETA, tracking number, and line items.

    Args:
        order_id: The order identifier (e.g., '45231' or '#45231').

    Returns:
        Structured order information or error.
    """
    clean_id = str(order_id).strip().lstrip("#")
    if not clean_id:
        return {
            "success": False,
            "error": "EMPTY_ORDER_ID",
            "message": "Order ID must be provided."
        }

    db = SessionLocal()
    try:
        repo = OrderRepository(db)
        order = repo.get_by_order_number(clean_id)
        if not order:
            return {
                "success": False,
                "error": "ORDER_NOT_FOUND",
                "message": f"Order #{clean_id} was not found in the retail system."
            }

        order_data = repo.order_to_dict(order)
        return {
            "success": True,
            "order": order_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": "DATABASE_ERROR",
            "message": f"Failed to retrieve order: {str(e)}"
        }
    finally:
        db.close()


def search_orders_tool(
    query: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Searches for orders matching query keywords, tracking numbers, or statuses.

    Args:
        query: Keyword or tracking number to search.
        status: Filter by order status (e.g. 'SHIPPED', 'DELIVERED').
        limit: Maximum number of orders to return.

    Returns:
        List of matching orders.
    """
    db = SessionLocal()
    try:
        repo = OrderRepository(db)
        orders = repo.search_orders(query=query, status=status, limit=limit)
        return {
            "success": True,
            "count": len(orders),
            "orders": [repo.order_to_dict(o) for o in orders]
        }
    except Exception as e:
        return {
            "success": False,
            "error": "DATABASE_ERROR",
            "message": f"Failed to search orders: {str(e)}"
        }
    finally:
        db.close()
