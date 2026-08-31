"""Database Seeding Script.

Creates all tables in PostgreSQL and populates realistic retail demo data,
specifically including Order #45231 for the primary multi-intent demonstration.
"""
from datetime import date, datetime, timezone
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import Base, engine, SessionLocal
from app.database.models.customer import Customer
from app.database.models.product import Product
from app.database.models.order import Order
from app.database.models.order_item import OrderItem


def seed_database():
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_order = db.query(Order).filter(Order.order_number == "45231").first()
        if existing_order:
            print("Database already contains demo data (Order #45231 found). Resetting and re-seeding...")
            db.query(OrderItem).delete()
            db.query(Order).delete()
            db.query(Product).delete()
            db.query(Customer).delete()
            db.commit()

        print("Seeding Customers...")
        cust1 = Customer(name="Alex Johnson", email="alex.johnson@example.com", phone="+1-555-0199")
        cust2 = Customer(name="Maria Garcia", email="maria.garcia@example.com", phone="+1-555-0245")
        cust3 = Customer(name="David Smith", email="david.smith@example.com", phone="+1-555-0312")
        db.add_all([cust1, cust2, cust3])
        db.flush()

        print("Seeding Products...")
        prod_shoes = Product(
            sku="SHOE-RN-001",
            name="Running Shoes",
            category="Footwear",
            price=120.00,
            stock_quantity=45,
            description="High-performance lightweight road running shoes with responsive cushioning."
        )
        prod_boots = Product(
            sku="SHOE-HK-002",
            name="Trail Hiking Boots",
            category="Footwear",
            price=160.00,
            stock_quantity=18,
            description="Waterproof full-grain leather hiking boots with Vibram outsole."
        )
        prod_jacket = Product(
            sku="APP-JK-101",
            name="Waterproof Windbreaker Jacket",
            category="Apparel",
            price=89.50,
            stock_quantity=32,
            description="Breathable windproof and water-resistant shell jacket for all-weather training."
        )
        prod_backpack = Product(
            sku="ACC-BP-202",
            name="Commuter Laptop Backpack 25L",
            category="Accessories",
            price=75.00,
            stock_quantity=0,  # Out of stock to test inventory
            description="Durable water-repellent urban daypack with dedicated 16-inch laptop compartment."
        )
        prod_watch = Product(
            sku="ELEC-SW-303",
            name="GPS Fitness Smartwatch",
            category="Electronics",
            price=199.99,
            stock_quantity=12,
            description="Advanced multi-sport GPS smartwatch with wrist-based heart rate and pulse ox."
        )
        db.add_all([prod_shoes, prod_boots, prod_jacket, prod_backpack, prod_watch])
        db.flush()

        print("Seeding Orders...")
        # Mandatory primary demonstration order: #45231
        order_45231 = Order(
            order_number="45231",
            customer_id=cust1.id,
            status="SHIPPED",
            eta=date(2026, 9, 3),
            tracking_number="TRK123456",
            carrier="FedEx Express",
            shipping_address="742 Evergreen Terrace, Springfield, OR 97477",
            created_at=datetime(2026, 8, 28, 14, 30, tzinfo=timezone.utc),
        )
        db.add(order_45231)
        db.flush()

        item_45231 = OrderItem(
            order_id=order_45231.id,
            product_id=prod_shoes.id,
            product_name="Running Shoes",
            quantity=1,
            unit_price=120.00
        )
        db.add(item_45231)

        # Additional Order #98124 (Delivered)
        order_98124 = Order(
            order_number="98124",
            customer_id=cust2.id,
            status="DELIVERED",
            eta=date(2026, 8, 20),
            tracking_number="TRK987654",
            carrier="UPS Ground",
            shipping_address="1200 Sunset Blvd, Los Angeles, CA 90028",
            created_at=datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc),
        )
        db.add(order_98124)
        db.flush()

        item_98124_1 = OrderItem(
            order_id=order_98124.id,
            product_id=prod_jacket.id,
            product_name="Waterproof Windbreaker Jacket",
            quantity=1,
            unit_price=89.50
        )
        item_98124_2 = OrderItem(
            order_id=order_98124.id,
            product_id=prod_backpack.id,
            product_name="Commuter Laptop Backpack 25L",
            quantity=1,
            unit_price=75.00
        )
        db.add_all([item_98124_1, item_98124_2])

        # Additional Order #77310 (Processing)
        order_77310 = Order(
            order_number="77310",
            customer_id=cust3.id,
            status="PROCESSING",
            eta=date(2026, 9, 8),
            tracking_number=None,
            carrier="Standard Carrier",
            shipping_address="456 Elm Street, Chicago, IL 60601",
            created_at=datetime(2026, 8, 30, 9, 15, tzinfo=timezone.utc),
        )
        db.add(order_77310)
        db.flush()

        item_77310 = OrderItem(
            order_id=order_77310.id,
            product_id=prod_watch.id,
            product_name="GPS Fitness Smartwatch",
            quantity=1,
            unit_price=199.99
        )
        db.add(item_77310)

        db.commit()
        print("Database successfully seeded with retail operational data!")
        print(" -> Verified Order #45231: Status=SHIPPED, ETA=2026-09-03, Tracking=TRK123456, Product='Running Shoes'")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
