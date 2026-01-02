"""
Black-Box Tests: Decision Table Testing
All Members: Systematic testing of condition combinations

Test File: test_decision_table.py
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from customer_manager import CustomerManager
from order_manager import OrderManager
from payment_delivery_manager import PaymentDeliveryManager
from models import (
    MenuItem, Category, Customer, Order, Cart, Address,
    DeliveryZone, OrderStatus, LoyaltyPoints, DiscountCode, DiscountType
)


class MockStorage:
    def __init__(self):
        self._items = {}
        self._categories = {}
        self._customers = {}
        self._orders = {}
        self._carts = {}
        self._discount_codes = {}
        self._cancellations = {}
    
    def get_menu_item(self, id): return self._items.get(id)
    def save_menu_item(self, item): self._items[item.id] = item
    def get_category(self, id): return self._categories.get(id)
    def save_category(self, cat): self._categories[cat.id] = cat
    def get_customer(self, id): return self._customers.get(id)
    def get_customer_by_email(self, email):
        for c in self._customers.values():
            if c.email.lower() == email.lower(): return c
        return None
    def save_customer(self, c): self._customers[c.id] = c
    def get_customer_order_count(self, id): return len([o for o in self._orders.values() if o.customer_id == id])
    def get_active_orders(self, id): return []
    def get_order(self, id): return self._orders.get(id)
    def save_order(self, o): self._orders[o.id] = o
    def get_cart(self, id): return self._carts.get(id)
    def save_cart(self, c): self._carts[c.id] = c
    def delete_cart(self, id): self._carts.pop(id, None)
    def get_discount_code(self, code): return self._discount_codes.get(code.upper() if code else None)
    def save_discount_code(self, c): self._discount_codes[c.code.upper()] = c
    def has_customer_used_code(self, cid, code): return False
    def reserve_stock(self, id, qty):
        if id in self._items: self._items[id].stock_quantity -= qty
    def release_stock(self, id, qty):
        if id in self._items: self._items[id].stock_quantity += qty
    def log_cancellation(self, oid, cid, reason):
        if cid not in self._cancellations: self._cancellations[cid] = []
        self._cancellations[cid].append({"order_id": oid})
    def get_customer_cancellations(self, cid, days=30): return self._cancellations.get(cid, [])
    def get_recent_reset_requests(self, cid, hours=1): return []
    def invalidate_reset_tokens(self, cid): pass
    def save_reset_token(self, t): pass
    def invalidate_session(self, t): pass
    def block_email(self, e, u): pass
    def schedule_deletion(self, cid, d): pass


class TestDeliveryFeeDecisionTable(unittest.TestCase):
    """
    Decision Table: Delivery Fee Calculation
    
    | Zone | >=30 | Peak | Weather | Result |
    |------|------|------|---------|--------|
    |  1   |  Y   |  -   |   -     | £0     |
    |  1   |  N   |  N   |   N     | £2     |
    |  1   |  N   |  Y   |   N     | £3.50  |
    |  1   |  N   |  N   |   Y     | £3     |
    |  1   |  N   |  Y   |   Y     | £4.50  |
    |  2   |  N   |  N   |   N     | £3.50  |
    |  3   |  N   |  N   |   N     | £5     |
    | Out  |  -   |  -   |   -     | Error  |
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_zone1_free_delivery(self):
        result = self.manager.calculate_delivery_fee("LE1 1AA", 35.00, False, False)
        self.assertEqual(result["fee"], 0)
    
    def test_zone1_base(self):
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, False, False)
        self.assertEqual(result["fee"], 2.00)
    
    def test_zone1_peak(self):
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, True, False)
        self.assertEqual(result["fee"], 3.50)
    
    def test_zone1_weather(self):
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, False, True)
        self.assertEqual(result["fee"], 3.00)
    
    def test_zone1_peak_and_weather(self):
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, True, True)
        self.assertEqual(result["fee"], 4.50)
    
    def test_zone2_base(self):
        result = self.manager.calculate_delivery_fee("LE3 1AA", 20.00, False, False)
        self.assertEqual(result["fee"], 3.50)
    
    def test_zone3_base(self):
        result = self.manager.calculate_delivery_fee("LE7 1AA", 20.00, False, False)
        self.assertEqual(result["fee"], 5.00)
    
    def test_out_of_range(self):
        result = self.manager.calculate_delivery_fee("SW1A 1AA", 20.00, False, False)
        self.assertFalse(result["success"])


class TestDiscountCodeDecisionTable(unittest.TestCase):
    """
    Decision Table: Discount Code Validation
    
    | Exists | Active | Valid Date | Min Met | First Req | Result |
    |--------|--------|------------|---------|-----------|--------|
    |   N    |   -    |     -      |    -    |     -     | Invalid|
    |   Y    |   N    |     -      |    -    |     -     | Inactive|
    |   Y    |   Y    |     N      |    -    |     -     | Expired|
    |   Y    |   Y    |     Y      |    N    |     -     | MinOrd |
    |   Y    |   Y    |     Y      |    Y    |  Y & N    | NotFirst|
    |   Y    |   Y    |     Y      |    Y    |  Y & Y    | Valid  |
    |   Y    |   Y    |     Y      |    Y    |    NA     | Valid  |
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
        
        self.storage.save_discount_code(DiscountCode(
            code="VALID", discount_type=DiscountType.PERCENTAGE, value=10,
            min_order_amount=15.00, is_active=True,
            valid_from=datetime.now() - timedelta(days=1),
            valid_until=datetime.now() + timedelta(days=30)
        ))
        self.storage.save_discount_code(DiscountCode(
            code="INACTIVE", discount_type=DiscountType.PERCENTAGE, value=10,
            is_active=False,
            valid_from=datetime.now() - timedelta(days=1),
            valid_until=datetime.now() + timedelta(days=30)
        ))
        self.storage.save_discount_code(DiscountCode(
            code="EXPIRED", discount_type=DiscountType.PERCENTAGE, value=10,
            is_active=True,
            valid_from=datetime.now() - timedelta(days=60),
            valid_until=datetime.now() - timedelta(days=1)
        ))
        self.storage.save_discount_code(DiscountCode(
            code="FIRSTONLY", discount_type=DiscountType.PERCENTAGE, value=25,
            is_active=True,
            valid_from=datetime.now() - timedelta(days=1),
            valid_until=datetime.now() + timedelta(days=30),
            is_first_order_only=True
        ))
    
    def test_code_not_exists(self):
        result = self.manager.validate_discount_code("NONEXIST", 20.00)
        self.assertFalse(result["valid"])
    
    def test_code_inactive(self):
        result = self.manager.validate_discount_code("INACTIVE", 20.00)
        self.assertFalse(result["valid"])
    
    def test_code_expired(self):
        result = self.manager.validate_discount_code("EXPIRED", 20.00)
        self.assertFalse(result["valid"])
    
    def test_min_order_not_met(self):
        result = self.manager.validate_discount_code("VALID", 10.00)
        self.assertFalse(result["valid"])
    
    def test_first_order_not_first(self):
        result = self.manager.validate_discount_code("FIRSTONLY", 20.00, is_first_order=False)
        self.assertFalse(result["valid"])
    
    def test_first_order_is_first(self):
        result = self.manager.validate_discount_code("FIRSTONLY", 20.00, is_first_order=True)
        self.assertTrue(result["valid"])
    
    def test_all_valid(self):
        result = self.manager.validate_discount_code("VALID", 20.00)
        self.assertTrue(result["valid"])


class TestCancelOrderDecisionTable(unittest.TestCase):
    """
    Decision Table: Order Cancellation
    
    | Exists | Owner | Status    | Result       |
    |--------|-------|-----------|--------------|
    |   N    |   -   |     -     | Not found    |
    |   Y    |   N   |     -     | Unauthorized |
    |   Y    |   Y   | Pending   | 100% refund  |
    |   Y    |   Y   | Confirmed | 100% refund  |
    |   Y    |   Y   | Preparing | 50% refund   |
    |   Y    |   Y   | Ready     | Cannot       |
    |   Y    |   Y   | Delivered | Cannot       |
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = OrderManager(self.storage)
        
        self.storage.save_menu_item(MenuItem(
            id="item1", name="Test", description="Test desc",
            price=20.00, category_id="cat1", is_available=True, stock_quantity=50
        ))
        self.storage.save_customer(Customer(
            id="cust1", email="test@example.com", password_hash="hash",
            first_name="John", last_name="Doe", phone="+447123456789",
            loyalty_points=LoyaltyPoints()
        ))
    
    def _create_order(self, status):
        """Create order directly with given status."""
        from models import PaymentMethod
        order = Order(
            id=f"order_{status.value}",
            order_number=f"ORD-{status.value}",
            customer_id="cust1",
            items=[],
            subtotal=20.00,
            total=24.00,
            tax_amount=4.00,
            delivery_fee=0,
            status=status,
            payment_method=PaymentMethod.CARD
        )
        self.storage.save_order(order)
        return order
    
    def test_order_not_found(self):
        result = self.manager.cancel_order("nonexistent", "cust1", "reason")
        self.assertFalse(result["success"])
    
    def test_not_owner(self):
        order = self._create_order(OrderStatus.PENDING)
        result = self.manager.cancel_order(order.id, "other", "reason")
        self.assertFalse(result["success"])
    
    def test_pending_full_refund(self):
        order = self._create_order(OrderStatus.PENDING)
        result = self.manager.cancel_order(order.id, "cust1", "reason")
        self.assertTrue(result["success"])
        self.assertEqual(result["refund_percentage"], 100)
    
    def test_confirmed_full_refund(self):
        order = self._create_order(OrderStatus.CONFIRMED)
        result = self.manager.cancel_order(order.id, "cust1", "reason")
        self.assertTrue(result["success"])
        self.assertEqual(result["refund_percentage"], 100)
    
    def test_preparing_half_refund(self):
        order = self._create_order(OrderStatus.PREPARING)
        result = self.manager.cancel_order(order.id, "cust1", "reason")
        self.assertTrue(result["success"])
        self.assertEqual(result["refund_percentage"], 50)
    
    def test_ready_cannot_cancel(self):
        order = self._create_order(OrderStatus.READY)
        result = self.manager.cancel_order(order.id, "cust1", "reason")
        self.assertFalse(result["success"])
    
    def test_delivered_cannot_cancel(self):
        order = self._create_order(OrderStatus.DELIVERED)
        result = self.manager.cancel_order(order.id, "cust1", "reason")
        self.assertFalse(result["success"])


class TestLoginDecisionTable(unittest.TestCase):
    """
    Decision Table: Customer Login
    
    | Exists | Active | Locked | Password | Result      |
    |--------|--------|--------|----------|-------------|
    |   N    |   -    |   -    |    -     | Invalid     |
    |   Y    |   N    |   -    |    -     | Deactivated |
    |   Y    |   Y    |   Y    |    -     | Locked      |
    |   Y    |   Y    |   N    |    N     | Invalid     |
    |   Y    |   Y    |   N    |    Y     | Success     |
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
        
        self.manager.register_customer(
            email="active@test.com", password="Test1234!",
            first_name="Active", last_name="User",
            phone="07123456789", terms_accepted=True
        )
        
        self.manager.register_customer(
            email="inactive@test.com", password="Test1234!",
            first_name="Inactive", last_name="User",
            phone="07123456790", terms_accepted=True
        )
        c = self.storage.get_customer_by_email("inactive@test.com")
        c.is_active = False
        self.storage.save_customer(c)
        
        self.manager.register_customer(
            email="locked@test.com", password="Test1234!",
            first_name="Locked", last_name="User",
            phone="07123456791", terms_accepted=True
        )
        c = self.storage.get_customer_by_email("locked@test.com")
        c.locked_until = datetime.now() + timedelta(minutes=30)
        self.storage.save_customer(c)
    
    def test_email_not_exists(self):
        result = self.manager.login("noexist@test.com", "password")
        self.assertFalse(result["success"])
    
    def test_account_inactive(self):
        result = self.manager.login("inactive@test.com", "Test1234!")
        self.assertFalse(result["success"])
    
    def test_account_locked(self):
        result = self.manager.login("locked@test.com", "Test1234!")
        self.assertFalse(result["success"])
    
    def test_wrong_password(self):
        result = self.manager.login("active@test.com", "WrongPass!")
        self.assertFalse(result["success"])
    
    def test_success(self):
        result = self.manager.login("active@test.com", "Test1234!")
        self.assertTrue(result["success"])


if __name__ == '__main__':
    unittest.main()
