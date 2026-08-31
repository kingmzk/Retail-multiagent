"""Unit tests for Database Models and Repositories."""
import pytest
from app.database.session import SessionLocal
from app.database.repositories.order_repo import OrderRepository
from app.database.repositories.product_repo import ProductRepository


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_order_retrieval_success(db_session):
    repo = OrderRepository(db_session)
    order = repo.get_by_order_number("45231")
    assert order is not None
    assert order.order_number == "45231"
    assert order.status == "SHIPPED"
    assert order.tracking_number == "TRK123456"
    assert len(order.items) >= 1
    assert any(item.product_name == "Running Shoes" for item in order.items)


def test_order_retrieval_with_hash(db_session):
    repo = OrderRepository(db_session)
    order = repo.get_by_order_number("#45231")
    assert order is not None
    assert order.order_number == "45231"


def test_order_retrieval_not_found(db_session):
    repo = OrderRepository(db_session)
    order = repo.get_by_order_number("999999")
    assert order is None


def test_product_retrieval_by_sku(db_session):
    repo = ProductRepository(db_session)
    product = repo.get_by_sku("SHOE-RN-001")
    assert product is not None
    assert product.name == "Running Shoes"
    assert product.price == 120.00
    assert product.stock_quantity > 0


def test_product_search_by_name(db_session):
    repo = ProductRepository(db_session)
    products = repo.search_products(query="shoes")
    assert len(products) >= 1
    assert any("Running Shoes" in p.name for p in products)


def test_check_inventory(db_session):
    repo = ProductRepository(db_session)
    # In stock item
    inv_in = repo.check_inventory("SHOE-RN-001")
    assert inv_in is not None
    assert inv_in["in_stock"] is True

    # Out of stock item
    inv_out = repo.check_inventory("Commuter Laptop Backpack 25L")
    assert inv_out is not None
    assert inv_out["in_stock"] is False
    assert inv_out["stock_quantity"] == 0

    # Non-existent item
    inv_none = repo.check_inventory("NonExistentItem12345")
    assert inv_none is None
