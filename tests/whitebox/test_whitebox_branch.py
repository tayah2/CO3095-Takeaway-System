"""
White-Box Tests: Branch Coverage
All Members: Menu, Customer, Order, Payment Management

Test File: test_whitebox_branch.py

Branch Coverage ensures every decision point (if/else, loops, switch)
has both TRUE and FALSE outcomes tested.
"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from menu_manager import MenuManager
from customer_manager import CustomerManager
from order_manager import OrderManager
from payment_delivery_manager import PaymentDeliveryManager
from models import (
    MenuItem, Category, Customer, Order, Cart, CartItem,
    Address, DietaryTag, DeliveryZone, OrderStatus, LoyaltyPoints,
    DiscountCode, DiscountType, PaymentMethod
)


class MockStorage:
    """Comprehensive mock storage for testing."""
    
    def __init__(self):
        self._items = {}
        self._categories = {}
        self._customers = {}
        self._orders = {}
        self._carts = {}
        self._discount_codes = {}
        self._offers = {}
        self._refunds = {}
        self._reset_tokens = {}
        self._cancellations = {}
    
    # Menu methods
    def get_menu_item(self, item_id):
        return self._items.get(item_id)
    
    def get_all_menu_items(self):
        return list(self._items.values())
    
    def get_items_by_category(self, category_id):
        return [i for i in self._items.values() if i.category_id == category_id]
    
    def save_menu_item(self, item):
        self._items[item.id] = item
    
    def get_category(self, category_id):
        return self._categories.get(category_id)
    
    def get_all_categories(self):
        return list(self._categories.values())
    
    def get_categories_by_parent(self, parent_id):
        return [c for c in self._categories.values() if c.parent_id == parent_id]
    
    def get_subcategories(self, parent_id):
        return self.get_categories_by_parent(parent_id)
    
    def save_category(self, category):
        self._categories[category.id] = category
    
    def delete_category(self, category_id):
        if category_id in self._categories:
            del self._categories[category_id]
    
    def clear_all_items(self):
        self._items = {}
    
    def clear_all_categories(self):
        self._categories = {}
    
    # Customer methods
    def get_customer(self, customer_id):
        return self._customers.get(customer_id)
    
    def get_customer_by_email(self, email):
        for c in self._customers.values():
            if c.email.lower() == email.lower():
                return c
        return None
    
    def save_customer(self, customer):
        self._customers[customer.id] = customer
    
    def get_customer_orders(self, customer_id):
        return [o for o in self._orders.values() if o.customer_id == customer_id]
    
    def get_customer_order_count(self, customer_id):
        return len(self.get_customer_orders(customer_id))
    
    def get_active_orders(self, customer_id):
        active = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING]
        return [o for o in self._orders.values() 
                if o.customer_id == customer_id and o.status in active]
    
    # Order methods
    def get_order(self, order_id):
        return self._orders.get(order_id)
    
    def save_order(self, order):
        self._orders[order.id] = order
    
    def get_orders_in_range(self, start_date, end_date):
        return [o for o in self._orders.values() 
                if start_date <= o.created_at.date() <= end_date]
    
    # Cart methods
    def get_cart(self, cart_id):
        return self._carts.get(cart_id)
    
    def save_cart(self, cart):
        self._carts[cart.id] = cart
    
    def delete_cart(self, cart_id):
        if cart_id in self._carts:
            del self._carts[cart_id]
    
    # Discount methods
    def get_discount_code(self, code):
        return self._discount_codes.get(code.upper() if code else None)
    
    def save_discount_code(self, code):
        self._discount_codes[code.code.upper()] = code
    
    def has_customer_used_code(self, customer_id, code):
        return False
    
    # Stock methods
    def reserve_stock(self, item_id, quantity):
        item = self._items.get(item_id)
        if item:
            item.stock_quantity -= quantity
    
    def release_stock(self, item_id, quantity):
        item = self._items.get(item_id)
        if item:
            item.stock_quantity += quantity
    
    # Other methods
    def get_special_offer(self, offer_id):
        return self._offers.get(offer_id)
    
    def save_special_offer(self, offer):
        self._offers[offer.id] = offer
    
    def log_item_changes(self, item_id, changes):
        pass
    
    def log_stock_adjustment(self, item_id, change, reason):
        pass
    
    def get_customer_offer_usage(self, customer_id, offer_id):
        return 0
    
    def get_recent_reset_requests(self, customer_id, hours=1):
        return []
    
    def invalidate_reset_tokens(self, customer_id):
        pass
    
    def save_reset_token(self, token):
        self._reset_tokens[token.token] = token
    
    def get_reset_token(self, token):
        return self._reset_tokens.get(token)
    
    def invalidate_session(self, token):
        pass
    
    def block_email(self, email, until):
        pass
    
    def unblock_email(self, email):
        pass
    
    def anonymize_customer_orders(self, customer_id):
        pass
    
    def schedule_deletion(self, customer_id, delete_at):
        pass
    
    def get_scheduled_deletion(self, customer_id):
        return None
    
    def cancel_deletion(self, customer_id):
        pass
    
    def log_cancellation(self, order_id, customer_id, reason):
        if customer_id not in self._cancellations:
            self._cancellations[customer_id] = []
        self._cancellations[customer_id].append({"order_id": order_id})
    
    def get_customer_cancellations(self, customer_id, days=30):
        return self._cancellations.get(customer_id, [])
    
    def save_refund(self, refund):
        if refund.order_id not in self._refunds:
            self._refunds[refund.order_id] = []
        self._refunds[refund.order_id].append(refund)
    
    def get_order_refunds(self, order_id):
        return self._refunds.get(order_id, [])
    
    def create_notification(self, customer_id, message):
        pass


# ============== MEMBER A: MENU MANAGEMENT BRANCH COVERAGE ==============

class TestMenuManagerBranchCoverage(unittest.TestCase):
    """Branch coverage tests for MenuManager."""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        self.storage.save_category(Category(id="cat1", name="Mains"))
    
    # add_menu_item branches
    def test_add_item_name_none_branch(self):
        """Branch: name is None"""
        result = self.manager.add_menu_item(
            name=None, description="Valid desc text", price=10.00, category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_add_item_name_valid_branch(self):
        """Branch: name is valid"""
        result = self.manager.add_menu_item(
            name="Valid Name", description="Valid desc text", price=10.00, category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_add_item_price_too_low_branch(self):
        """Branch: price < 0.50"""
        result = self.manager.add_menu_item(
            name="Item", description="Valid desc text", price=0.25, category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_add_item_price_too_high_branch(self):
        """Branch: price > 500"""
        result = self.manager.add_menu_item(
            name="Expensive", description="Valid desc text", price=501.00, category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_add_item_category_not_found_branch(self):
        """Branch: category doesn't exist"""
        result = self.manager.add_menu_item(
            name="No Cat", description="Valid desc text", price=10.00, category_id="nonexistent"
        )
        self.assertFalse(result["success"])
    
    def test_add_item_duplicate_name_branch(self):
        """Branch: duplicate name in category"""
        self.manager.add_menu_item(
            name="Duplicate", description="First item desc", price=10.00, category_id="cat1"
        )
        result = self.manager.add_menu_item(
            name="Duplicate", description="Second item desc", price=15.00, category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # search_items branches
    def test_search_with_query_branch(self):
        """Branch: query is provided"""
        self.storage.save_menu_item(MenuItem(
            id="1", name="Chicken Curry", description="Spicy",
            price=12.00, category_id="cat1", is_available=True, stock_quantity=10
        ))
        result = self.manager.search_items(query="Chicken")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 1)
    
    def test_search_without_query_branch(self):
        """Branch: query is empty/None"""
        self.storage.save_menu_item(MenuItem(
            id="1", name="Chicken Curry", description="Spicy",
            price=12.00, category_id="cat1", is_available=True, stock_quantity=10
        ))
        result = self.manager.search_items(query="")
        self.assertTrue(result["success"])
    
    def test_search_with_price_range_branch(self):
        """Branch: price range provided"""
        self.storage.save_menu_item(MenuItem(
            id="1", name="Cheap", description="Budget item",
            price=5.00, category_id="cat1", is_available=True, stock_quantity=10
        ))
        self.storage.save_menu_item(MenuItem(
            id="2", name="Expensive", description="Premium",
            price=50.00, category_id="cat1", is_available=True, stock_quantity=10
        ))
        result = self.manager.search_items(min_price=10.00, max_price=40.00)
        self.assertTrue(result["success"])
    
    def test_search_available_only_true_branch(self):
        """Branch: available_only = True"""
        self.storage.save_menu_item(MenuItem(
            id="1", name="Available", description="In stock",
            price=10.00, category_id="cat1", is_available=True, stock_quantity=10
        ))
        self.storage.save_menu_item(MenuItem(
            id="2", name="Unavailable", description="Out of stock",
            price=10.00, category_id="cat1", is_available=False, stock_quantity=0
        ))
        result = self.manager.search_items(available_only=True)
        self.assertTrue(result["success"])


# ============== MEMBER B: CUSTOMER MANAGEMENT BRANCH COVERAGE ==============

class TestCustomerManagerBranchCoverage(unittest.TestCase):
    """Branch coverage tests for CustomerManager."""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
    
    # register_customer branches
    def test_register_email_invalid_branch(self):
        """Branch: invalid email format"""
        result = self.manager.register_customer(
            email="invalid", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        self.assertFalse(result["success"])
    
    def test_register_email_valid_branch(self):
        """Branch: valid email format"""
        result = self.manager.register_customer(
            email="valid@example.com", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        self.assertTrue(result["success"])
    
    def test_register_password_no_uppercase_branch(self):
        """Branch: password missing uppercase"""
        result = self.manager.register_customer(
            email="test@example.com", password="test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        self.assertFalse(result["success"])
    
    def test_register_password_no_lowercase_branch(self):
        """Branch: password missing lowercase"""
        result = self.manager.register_customer(
            email="test2@example.com", password="TEST1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        self.assertFalse(result["success"])
    
    def test_register_terms_not_accepted_branch(self):
        """Branch: terms not accepted"""
        result = self.manager.register_customer(
            email="test3@example.com", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=False
        )
        self.assertFalse(result["success"])
    
    # login branches
    def test_login_customer_not_found_branch(self):
        """Branch: customer not found"""
        result = self.manager.login("nonexistent@example.com", "password")
        self.assertFalse(result["success"])
    
    def test_login_customer_inactive_branch(self):
        """Branch: customer is inactive"""
        self.manager.register_customer(
            email="inactive@example.com", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        customer = self.storage.get_customer_by_email("inactive@example.com")
        customer.is_active = False
        self.storage.save_customer(customer)
        
        result = self.manager.login("inactive@example.com", "Test1234!")
        self.assertFalse(result["success"])
    
    def test_login_customer_locked_branch(self):
        """Branch: customer is locked"""
        self.manager.register_customer(
            email="locked@example.com", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        customer = self.storage.get_customer_by_email("locked@example.com")
        customer.locked_until = datetime.now() + timedelta(minutes=30)
        self.storage.save_customer(customer)
        
        result = self.manager.login("locked@example.com", "Test1234!")
        self.assertFalse(result["success"])
    
    def test_login_password_correct_branch(self):
        """Branch: password is correct"""
        self.manager.register_customer(
            email="correct@example.com", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        result = self.manager.login("correct@example.com", "Test1234!")
        self.assertTrue(result["success"])
    
    def test_login_password_incorrect_branch(self):
        """Branch: password is incorrect"""
        self.manager.register_customer(
            email="wrong@example.com", password="Test1234!", first_name="John",
            last_name="Doe", phone="07123456789", terms_accepted=True
        )
        result = self.manager.login("wrong@example.com", "WrongPassword!")
        self.assertFalse(result["success"])


# ============== MEMBER C: ORDER MANAGEMENT BRANCH COVERAGE ==============

class TestOrderManagerBranchCoverage(unittest.TestCase):
    """Branch coverage tests for OrderManager."""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = OrderManager(self.storage)
        
        self.storage.save_menu_item(MenuItem(
            id="item1", name="Test Item", description="Test",
            price=15.00, category_id="cat1", is_available=True, stock_quantity=50
        ))
        
        self.storage.save_customer(Customer(
            id="cust1", email="test@example.com", password_hash="hash",
            first_name="John", last_name="Doe", phone="+447123456789",
            loyalty_points=LoyaltyPoints()
        ))
    
    # add_to_cart branches
    def test_add_to_cart_new_cart_branch(self):
        """Branch: cart doesn't exist (create new)"""
        result = self.manager.add_to_cart("new_cart", "item1", 1)
        self.assertTrue(result["success"])
    
    def test_add_to_cart_existing_cart_branch(self):
        """Branch: cart exists"""
        self.manager.add_to_cart("existing", "item1", 1)
        result = self.manager.add_to_cart("existing", "item1", 1)
        self.assertTrue(result["success"])
    
    def test_add_to_cart_item_unavailable_branch(self):
        """Branch: item is unavailable"""
        self.storage.save_menu_item(MenuItem(
            id="unavail", name="Unavailable", description="Out",
            price=10.00, category_id="cat1", is_available=False, stock_quantity=0
        ))
        result = self.manager.add_to_cart("cart", "unavail", 1)
        self.assertFalse(result["success"])
    
    def test_add_to_cart_item_not_found_branch(self):
        """Branch: item doesn't exist"""
        result = self.manager.add_to_cart("cart", "nonexistent", 1)
        self.assertFalse(result["success"])
    
    def test_add_to_cart_insufficient_stock_branch(self):
        """Branch: insufficient stock"""
        self.storage.save_menu_item(MenuItem(
            id="lowstock", name="Low Stock", description="Few left",
            price=10.00, category_id="cat1", is_available=True, stock_quantity=2
        ))
        result = self.manager.add_to_cart("cart", "lowstock", 10)
        self.assertFalse(result["success"])
    
    # place_order branches
    def test_place_order_cart_empty_branch(self):
        """Branch: cart is empty"""
        cart = Cart(id="empty")
        self.storage.save_cart(cart)
        
        address = Address(line1="123 St", city="Leicester", postcode="LE1 1AA",
                         delivery_zone=DeliveryZone.ZONE_1)
        result = self.manager.place_order("empty", "cust1", address, "card")
        self.assertFalse(result["success"])
    
    def test_place_order_below_minimum_branch(self):
        """Branch: order below minimum amount"""
        self.storage.save_menu_item(MenuItem(
            id="cheap", name="Cheap", description="Budget",
            price=5.00, category_id="cat1", is_available=True, stock_quantity=10
        ))
        self.manager.add_to_cart("cart", "cheap", 1)
        
        address = Address(line1="123 St", city="Leicester", postcode="LE1 1AA",
                         delivery_zone=DeliveryZone.ZONE_1)
        result = self.manager.place_order("cart", "cust1", address, "card")
        self.assertFalse(result["success"])
    
    def test_place_order_out_of_zone_branch(self):
        """Branch: address out of delivery zone"""
        self.manager.add_to_cart("cart", "item1", 1)
        
        address = Address(line1="123 St", city="London", postcode="SW1A 1AA",
                         delivery_zone=DeliveryZone.OUT_OF_RANGE)
        result = self.manager.place_order("cart", "cust1", address, "card")
        self.assertFalse(result["success"])


# ============== MEMBER D: PAYMENT MANAGEMENT BRANCH COVERAGE ==============

class TestPaymentManagerBranchCoverage(unittest.TestCase):
    """Branch coverage tests for PaymentDeliveryManager."""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    # calculate_delivery_fee branches
    def test_delivery_zone_1_branch(self):
        """Branch: Zone 1 postcode"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, False)
        self.assertEqual(result["fee"], 2.00)
    
    def test_delivery_zone_2_branch(self):
        """Branch: Zone 2 postcode"""
        result = self.manager.calculate_delivery_fee("LE3 1AA", 20.00, False)
        self.assertEqual(result["fee"], 3.50)
    
    def test_delivery_zone_3_branch(self):
        """Branch: Zone 3 postcode"""
        result = self.manager.calculate_delivery_fee("LE7 1AA", 20.00, False)
        self.assertEqual(result["fee"], 5.00)
    
    def test_delivery_out_of_range_branch(self):
        """Branch: Out of range"""
        result = self.manager.calculate_delivery_fee("SW1A 1AA", 20.00)
        self.assertFalse(result["success"])
    
    def test_delivery_free_threshold_met_branch(self):
        """Branch: free delivery threshold met"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 30.00, False)
        self.assertEqual(result["fee"], 0)
    
    def test_delivery_free_threshold_not_met_branch(self):
        """Branch: free delivery threshold not met"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 25.00, False)
        self.assertGreater(result["fee"], 0)
    
    def test_delivery_peak_time_true_branch(self):
        """Branch: peak time = True"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, True)
        self.assertIn("peak_surcharge", result["breakdown"])
    
    def test_delivery_peak_time_false_branch(self):
        """Branch: peak time = False"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, False)
        self.assertNotIn("peak_surcharge", result["breakdown"])
    
    # validate_payment branches
    def test_payment_valid_visa_branch(self):
        """Branch: valid Visa card"""
        result = self.manager.validate_payment(
            "4111111111111111", 12, datetime.now().year + 2, "123", "John", 50.00
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["card_type"], "visa")
    
    def test_payment_valid_mastercard_branch(self):
        """Branch: valid Mastercard"""
        result = self.manager.validate_payment(
            "5500000000000004", 12, datetime.now().year + 2, "123", "John", 50.00
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["card_type"], "mastercard")
    
    def test_payment_valid_amex_branch(self):
        """Branch: valid Amex"""
        result = self.manager.validate_payment(
            "340000000000009", 12, datetime.now().year + 2, "1234", "John", 50.00
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["card_type"], "amex")
    
    def test_payment_luhn_invalid_branch(self):
        """Branch: Luhn check fails"""
        result = self.manager.validate_payment(
            "4111111111111112", 12, datetime.now().year + 2, "123", "John", 50.00
        )
        self.assertFalse(result["valid"])
    
    def test_payment_expired_branch(self):
        """Branch: card expired"""
        result = self.manager.validate_payment(
            "4111111111111111", 1, datetime.now().year - 1, "123", "John", 50.00
        )
        self.assertFalse(result["valid"])


if __name__ == '__main__':
    unittest.main()
