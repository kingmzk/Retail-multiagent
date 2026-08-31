"""Product MCP Tools implementation.

Connects to PostgreSQL via ProductRepository and provides tools for product catalog,
specifications, pricing, and inventory availability.
"""
from typing import Dict, Any, Optional
from app.database.session import SessionLocal
from app.database.repositories.product_repo import ProductRepository


def get_product_tool(sku_or_id: str) -> Dict[str, Any]:
    """Retrieves detailed product specifications, category, price, and inventory.

    Args:
        sku_or_id: Product SKU (e.g. 'SHOE-RN-001') or numeric ID.

    Returns:
        Structured product details or error.
    """
    clean_val = str(sku_or_id).strip()
    if not clean_val:
        return {
            "success": False,
            "error": "EMPTY_PRODUCT_IDENTIFIER",
            "message": "Product SKU or ID must be provided."
        }

    db = SessionLocal()
    try:
        repo = ProductRepository(db)
        product = None
        if clean_val.isdigit():
            product = repo.get_by_id(int(clean_val))
        if not product:
            product = repo.get_by_sku(clean_val)
        if not product:
            # Fallback search by exact name
            matches = repo.search_products(query=clean_val, limit=1)
            if matches:
                product = matches[0]

        if not product:
            return {
                "success": False,
                "error": "PRODUCT_NOT_FOUND",
                "message": f"Product '{clean_val}' was not found in the catalog."
            }

        return {
            "success": True,
            "product": repo.product_to_dict(product)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "DATABASE_ERROR",
            "message": f"Failed to retrieve product: {str(e)}"
        }
    finally:
        db.close()


def search_products_tool(
    query: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """Searches the product catalog by keyword or category.

    Args:
        query: Search term for product name or description.
        category: Filter by category (e.g. 'Footwear', 'Apparel', 'Electronics').
        limit: Maximum results (default: 5).

    Returns:
        List of matching products.
    """
    db = SessionLocal()
    try:
        repo = ProductRepository(db)
        products = repo.search_products(query=query, category=category, limit=limit)
        return {
            "success": True,
            "count": len(products),
            "products": [repo.product_to_dict(p) for p in products]
        }
    except Exception as e:
        return {
            "success": False,
            "error": "DATABASE_ERROR",
            "message": f"Failed to search products: {str(e)}"
        }
    finally:
        db.close()


def check_inventory_tool(product_name_or_sku: str) -> Dict[str, Any]:
    """Checks stock availability and inventory levels for a product.

    Args:
        product_name_or_sku: Name or SKU of the product.

    Returns:
        Availability status and quantity.
    """
    clean_val = str(product_name_or_sku).strip()
    if not clean_val:
        return {
            "success": False,
            "error": "EMPTY_IDENTIFIER",
            "message": "Product name or SKU must be provided."
        }

    db = SessionLocal()
    try:
        repo = ProductRepository(db)
        inv = repo.check_inventory(clean_val)
        if not inv:
            return {
                "success": False,
                "error": "PRODUCT_NOT_FOUND",
                "message": f"Cannot check inventory for unknown product '{clean_val}'."
            }
        return {
            "success": True,
            "inventory": inv
        }
    except Exception as e:
        return {
            "success": False,
            "error": "DATABASE_ERROR",
            "message": f"Failed to check inventory: {str(e)}"
        }
    finally:
        db.close()
