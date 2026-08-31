from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from app.database.models.order import Order
from app.database.models.order_item import OrderItem


class OrderRepository:
    """Data access layer for Orders and Order Items."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """Retrieves an order by its order number along with order items and customer."""
        cleaned_number = str(order_number).strip().lstrip("#")
        return (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.customer))
            .filter(Order.order_number == cleaned_number)
            .first()
        )

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Retrieves an order by primary key ID."""
        return (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.customer))
            .filter(Order.id == order_id)
            .first()
        )

    def search_orders(
        self,
        query: Optional[str] = None,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Order]:
        """Searches orders by number, status, or customer."""
        q = self.db.query(Order).options(joinedload(Order.items), joinedload(Order.customer))
        if customer_id:
            q = q.filter(Order.customer_id == customer_id)
        if status:
            q = q.filter(Order.status.ilike(f"%{status}%"))
        if query:
            clean_query = query.strip().lstrip("#")
            q = q.filter(
                (Order.order_number.ilike(f"%{clean_query}%")) |
                (Order.tracking_number.ilike(f"%{clean_query}%"))
            )
        return q.order_by(Order.created_at.desc()).limit(limit).all()

    def order_to_dict(self, order: Order) -> Dict[str, Any]:
        """Converts an Order model to a clean dictionary response."""
        return {
            "order_id": order.order_number,
            "status": order.status,
            "eta": order.eta.isoformat() if order.eta else None,
            "tracking_number": order.tracking_number,
            "carrier": order.carrier,
            "customer_name": order.customer.name if order.customer else None,
            "customer_email": order.customer.email if order.customer else None,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price)
                }
                for item in order.items
            ]
        }
