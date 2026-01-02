"""
White-Box Tests: Concolic Testing (Research Component)
All Members: Systematic path exploration using concrete + symbolic execution

Test File: test_whitebox_concolic.py

CONCOLIC TESTING METHODOLOGY:
============================
Concolic testing combines CONCrete and symbOLIC execution:
1. Start with concrete input
2. Collect path constraints during execution
3. Negate constraints to explore alternative paths
4. Generate new concrete inputs to cover new paths

This file demonstrates concolic testing for key functions with
high cyclomatic complexity (>=10 branches).
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
    DiscountCode, DiscountType, PaymentMethod, SpecialOffer, OfferType
)


class MockStorage:
    """Mock storage for concolic testing."""
    
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
        return []
    
    def get_order(self, order_id):
        return self._orders.get(order_id)
    
    def save_order(self, order):
        self._orders[order.id] = order
    
    def get_orders_in_range(self, start_date, end_date):
        return [o for o in self._orders.values() 
                if start_date <= o.created_at.date() <= end_date]
    
    def get_cart(self, cart_id):
        return self._carts.get(cart_id)
    
    def save_cart(self, cart):
        self._carts[cart.id] = cart
    
    def delete_cart(self, cart_id):
        if cart_id in self._carts:
            del self._carts[cart_id]
    
    def get_discount_code(self, code):
        return self._discount_codes.get(code.upper() if code else None)
    
    def save_discount_code(self, code):
        self._discount_codes[code.code.upper()] = code
    
    def has_customer_used_code(self, customer_id, code):
        return False
    
    def reserve_stock(self, item_id, quantity):
        item = self._items.get(item_id)
        if item:
            item.stock_quantity -= quantity
    
    def release_stock(self, item_id, quantity):
        item = self._items.get(item_id)
        if item:
            item.stock_quantity += quantity
    
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


class TestAddMenuItemConcolic(unittest.TestCase):
    """
    CONCOLIC TESTING: add_menu_item (US-A1)
    
    Function under test has 12+ decision points.
    
    CONSTRAINT COLLECTION:
    ======================
    Initial concrete input: name="Test", desc="Description", price=10.0, cat="cat1"
    
    Execution path with this input collects constraints:
    C1: name != None                    (TRUE)
    C2: len(name) >= 2                  (TRUE) 
    C3: len(name) <= 50                 (TRUE)
    C4: valid_chars(name)               (TRUE)
    C5: desc != None                    (TRUE)
    C6: len(desc) >= 10                 (TRUE)
    C7: len(desc) <= 500                (TRUE)
    C8: price >= 0.50                   (TRUE)
    C9: price <= 500                    (TRUE)
    C10: category_exists(cat)           (TRUE)
    C11: prep_time >= 5                 (TRUE)
    C12: prep_time <= 120               (TRUE)
    C13: name_unique(name, cat)         (TRUE)
    
    PATH EXPLORATION:
    =================
    To explore all paths, we negate each constraint systematically:
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        self.storage.save_category(Category(id="cat1", name="Mains"))
    
    # ITERATION 1: Concrete input - all constraints TRUE
    def test_concolic_iteration1_all_valid(self):
        """
        Iteration 1: Initial concrete execution
        All constraints satisfied → SUCCESS path
        
        Constraints: C1 ∧ C2 ∧ C3 ∧ C4 ∧ C5 ∧ C6 ∧ C7 ∧ C8 ∧ C9 ∧ C10 ∧ C11 ∧ C12 ∧ C13
        """
        result = self.manager.add_menu_item(
            name="Valid Item",          # Satisfies C1, C2, C3, C4
            description="This is a valid description",  # Satisfies C5, C6, C7
            price=15.00,                # Satisfies C8, C9
            category_id="cat1",         # Satisfies C10
            preparation_time=30         # Satisfies C11, C12
        )
        self.assertTrue(result["success"])
    
    # ITERATION 2: Negate C1 (name != None)
    def test_concolic_iteration2_negate_c1(self):
        """
        Iteration 2: Negate C1 (name is None)
        Constraint: ¬C1 → name == None
        
        Expected: Fail on name validation
        """
        result = self.manager.add_menu_item(
            name=None,
            description="Valid description text",
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 3: Negate C2 (len(name) >= 2)
    def test_concolic_iteration3_negate_c2(self):
        """
        Iteration 3: Negate C2 (name too short)
        Constraint: C1 ∧ ¬C2 → len(name) < 2
        Concrete: name = "A" (len=1)
        """
        result = self.manager.add_menu_item(
            name="A",
            description="Valid description text",
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 4: Negate C3 (len(name) <= 50)
    def test_concolic_iteration4_negate_c3(self):
        """
        Iteration 4: Negate C3 (name too long)
        Constraint: C1 ∧ C2 ∧ ¬C3 → len(name) > 50
        Concrete: name = "A" * 51
        """
        result = self.manager.add_menu_item(
            name="A" * 51,
            description="Valid description text",
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 5: Negate C4 (valid_chars)
    def test_concolic_iteration5_negate_c4(self):
        """
        Iteration 5: Negate C4 (invalid characters in name)
        Constraint: C1 ∧ C2 ∧ C3 ∧ ¬C4
        Concrete: name = "Test@#$"
        """
        result = self.manager.add_menu_item(
            name="Test@#$",
            description="Valid description text",
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 6: Negate C6 (len(desc) >= 10)
    def test_concolic_iteration6_negate_c6(self):
        """
        Iteration 6: Negate C6 (description too short)
        Constraint: C1-C5 ∧ ¬C6 → len(desc) < 10
        Concrete: description = "Short"
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="Short",
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 7: Negate C7 (len(desc) <= 500)
    def test_concolic_iteration7_negate_c7(self):
        """
        Iteration 7: Negate C7 (description too long)
        Constraint: C1-C6 ∧ ¬C7 → len(desc) > 500
        Concrete: description = "A" * 501
        """
        result = self.manager.add_menu_item(
            name="Valid Item Two",
            description="A" * 501,
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 8: Negate C8 (price >= 0.50)
    def test_concolic_iteration8_negate_c8(self):
        """
        Iteration 8: Negate C8 (price too low)
        Constraint: C1-C7 ∧ ¬C8 → price < 0.50
        Concrete: price = 0.25
        """
        result = self.manager.add_menu_item(
            name="Valid Item Three",
            description="Valid description text",
            price=0.25,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 9: Negate C9 (price <= 500)
    def test_concolic_iteration9_negate_c9(self):
        """
        Iteration 9: Negate C9 (price too high)
        Constraint: C1-C8 ∧ ¬C9 → price > 500
        Concrete: price = 501.00
        """
        result = self.manager.add_menu_item(
            name="Valid Item Four",
            description="Valid description text",
            price=501.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 10: Negate C10 (category_exists)
    def test_concolic_iteration10_negate_c10(self):
        """
        Iteration 10: Negate C10 (category doesn't exist)
        Constraint: C1-C9 ∧ ¬C10 → ¬exists(category)
        Concrete: category_id = "nonexistent"
        """
        result = self.manager.add_menu_item(
            name="Valid Item Five",
            description="Valid description text",
            price=15.00,
            category_id="nonexistent"
        )
        self.assertFalse(result["success"])
    
    # ITERATION 11: Negate C11 (prep_time >= 5)
    def test_concolic_iteration11_negate_c11(self):
        """
        Iteration 11: Negate C11 (prep time too low)
        Constraint: C1-C10 ∧ ¬C11 → prep_time < 5
        Concrete: preparation_time = 4
        """
        result = self.manager.add_menu_item(
            name="Valid Item Six",
            description="Valid description text",
            price=15.00,
            category_id="cat1",
            preparation_time=4
        )
        self.assertFalse(result["success"])
    
    # ITERATION 12: Negate C12 (prep_time <= 120)
    def test_concolic_iteration12_negate_c12(self):
        """
        Iteration 12: Negate C12 (prep time too high)
        Constraint: C1-C11 ∧ ¬C12 → prep_time > 120
        Concrete: preparation_time = 121
        """
        result = self.manager.add_menu_item(
            name="Valid Item Seven",
            description="Valid description text",
            price=15.00,
            category_id="cat1",
            preparation_time=121
        )
        self.assertFalse(result["success"])
    
    # ITERATION 13: Negate C13 (name_unique)
    def test_concolic_iteration13_negate_c13(self):
        """
        Iteration 13: Negate C13 (duplicate name)
        Constraint: C1-C12 ∧ ¬C13 → ¬unique(name)
        Requires: existing item with same name
        """
        # First create an item
        self.manager.add_menu_item(
            name="Duplicate Name",
            description="First item description",
            price=10.00,
            category_id="cat1"
        )
        
        # Try to create with same name
        result = self.manager.add_menu_item(
            name="Duplicate Name",
            description="Second item description",
            price=15.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])


class TestValidatePaymentConcolic(unittest.TestCase):
    """
    CONCOLIC TESTING: validate_payment (US-D3)
    
    This function has multiple decision points for card validation.
    
    CONSTRAINT COLLECTION:
    ======================
    C1: luhn_valid(card_number)
    C2: card_type != UNKNOWN
    C3: len(card_number) in valid_lengths
    C4: expiry_year >= current_year
    C5: expiry_month valid (1-12)
    C6: !(expiry_year == current_year && expiry_month < current_month)
    C7: expiry_year <= current_year + 10
    C8: cvv_length_valid
    C9: card_holder not empty
    C10: amount > 0
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
        self.current_year = datetime.now().year
    
    # All constraints TRUE
    def test_concolic_all_valid(self):
        """All constraints satisfied - valid payment"""
        result = self.manager.validate_payment(
            "4111111111111111",  # Valid Visa (Luhn passes)
            12,
            self.current_year + 2,
            "123",
            "John Doe",
            50.00
        )
        self.assertTrue(result["valid"])
    
    # Negate C1 (Luhn invalid)
    def test_concolic_negate_c1_luhn(self):
        """¬C1: Luhn check fails"""
        result = self.manager.validate_payment(
            "4111111111111112",  # Invalid (Luhn fails)
            12,
            self.current_year + 2,
            "123",
            "John Doe",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C2 (unknown card type)
    def test_concolic_negate_c2_unknown_type(self):
        """¬C2: Unknown card type"""
        result = self.manager.validate_payment(
            "9999999999999999",  # Unknown prefix
            12,
            self.current_year + 2,
            "123",
            "John Doe",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C4 (expired year)
    def test_concolic_negate_c4_expired_year(self):
        """¬C4: Expiry year in past"""
        result = self.manager.validate_payment(
            "4111111111111111",
            12,
            self.current_year - 1,
            "123",
            "John Doe",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C5 (invalid month)
    def test_concolic_negate_c5_invalid_month(self):
        """¬C5: Invalid expiry month (13)"""
        result = self.manager.validate_payment(
            "4111111111111111",
            13,
            self.current_year + 2,
            "123",
            "John Doe",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C7 (expiry too far)
    def test_concolic_negate_c7_expiry_too_far(self):
        """¬C7: Expiry > 10 years in future"""
        result = self.manager.validate_payment(
            "4111111111111111",
            12,
            self.current_year + 11,
            "123",
            "John Doe",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C8 (CVV length invalid)
    def test_concolic_negate_c8_cvv_short(self):
        """¬C8: CVV too short"""
        result = self.manager.validate_payment(
            "4111111111111111",
            12,
            self.current_year + 2,
            "12",  # Too short
            "John Doe",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C9 (cardholder empty)
    def test_concolic_negate_c9_no_cardholder(self):
        """¬C9: Empty card holder"""
        result = self.manager.validate_payment(
            "4111111111111111",
            12,
            self.current_year + 2,
            "123",
            "",
            50.00
        )
        self.assertFalse(result["valid"])
    
    # Negate C10 (amount zero/negative)
    def test_concolic_negate_c10_zero_amount(self):
        """¬C10: Zero amount"""
        result = self.manager.validate_payment(
            "4111111111111111",
            12,
            self.current_year + 2,
            "123",
            "John Doe",
            0
        )
        self.assertFalse(result["valid"])


class TestRedeemPointsConcolic(unittest.TestCase):
    """
    CONCOLIC TESTING: redeem_points (US-B5)
    
    CONSTRAINTS:
    C1: customer exists
    C2: points >= MIN_POINTS_TO_REDEEM (500)
    C3: customer.loyalty_points.total_points >= points
    C4: discount <= order_total * 0.5 (50% max)
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
        
        # Create customer with 1000 points
        self.manager.register_customer(
            email="test@example.com", password="Test1234!",
            first_name="John", last_name="Doe",
            phone="07123456789", terms_accepted=True
        )
        customer = self.storage.get_customer_by_email("test@example.com")
        customer.loyalty_points.total_points = 1000
        self.storage.save_customer(customer)
        self.customer_id = customer.id
    
    def test_concolic_all_valid(self):
        """All constraints satisfied"""
        result = self.manager.redeem_points(
            self.customer_id, 
            points=500, 
            order_total=50.00
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["discount"], 5.00)
    
    def test_concolic_negate_c1_no_customer(self):
        """¬C1: Customer doesn't exist"""
        result = self.manager.redeem_points(
            "nonexistent", 
            points=500, 
            order_total=50.00
        )
        self.assertFalse(result["success"])
    
    def test_concolic_negate_c2_below_minimum(self):
        """¬C2: Points below minimum (500)"""
        result = self.manager.redeem_points(
            self.customer_id, 
            points=499, 
            order_total=50.00
        )
        self.assertFalse(result["success"])
    
    def test_concolic_negate_c3_insufficient_points(self):
        """¬C3: Insufficient points balance"""
        result = self.manager.redeem_points(
            self.customer_id, 
            points=2000,  # More than available 1000
            order_total=50.00
        )
        self.assertFalse(result["success"])
    
    def test_concolic_c4_max_50_percent(self):
        """C4: Discount capped at 50% of order"""
        # Try to redeem 1000 points (£10) on £15 order
        # Max should be £7.50 (50%)
        result = self.manager.redeem_points(
            self.customer_id, 
            points=1000, 
            order_total=15.00
        )
        self.assertTrue(result["success"])
        self.assertLessEqual(result["discount"], 7.50)


if __name__ == '__main__':
    unittest.main()
