from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models.product import Product


class ProductRepository:
    """Data access layer for Products and Inventory."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Retrieves a product by SKU."""
        return self.db.query(Product).filter(Product.sku.ilike(sku.strip())).first()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Retrieves a product by primary key ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Product]:
        """Searches products by keyword in name, description, or category."""
        q = self.db.query(Product)
        if category:
            q = q.filter(Product.category.ilike(f"%{category.strip()}%"))
        if query:
            clean_q = query.strip()
            q = q.filter(
                (Product.name.ilike(f"%{clean_q}%")) |
                (Product.description.ilike(f"%{clean_q}%")) |
                (Product.sku.ilike(f"%{clean_q}%")) |
                (Product.category.ilike(f"%{clean_q}%"))
            )
        return q.order_by(Product.name.asc()).limit(limit).all()

    def check_inventory(self, sku_or_name: str) -> Optional[Dict[str, Any]]:
        """Checks inventory availability for a product by SKU or name."""
        clean = sku_or_name.strip()
        product = (
            self.db.query(Product)
            .filter((Product.sku.ilike(clean)) | (Product.name.ilike(f"%{clean}%")))
            .first()
        )
        if not product:
            return None
        return {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "stock_quantity": product.stock_quantity,
            "in_stock": product.stock_quantity > 0,
            "price": float(product.price)
        }

    def product_to_dict(self, product: Product) -> Dict[str, Any]:
        """Converts a Product model to a clean dictionary response."""
        return {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "in_stock": product.stock_quantity > 0,
            "description": product.description
        }
