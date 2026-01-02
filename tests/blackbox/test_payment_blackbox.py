"""
Black-Box Tests: Equivalence Partitioning & Boundary Value Analysis
Member D: Payment, Delivery & Reports (US-D1 to US-D9)

Test File: memberD_test_blackbox.py
"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from payment_delivery_manager import PaymentDeliveryManager
from models import (
    DeliveryZone, CardType, DiscountCode, DiscountType, Order, OrderStatus,
    MenuItem, Category, CartItem, SalesReport, PaymentMethod
)


class MockStorage:
    """Mock storage for payment/delivery testing."""
    
    def __init__(self):
        self._orders = {}
        self._items = {}
        self._customers = {}
        self._categories = {}
        self._discount_codes = {}
        self._refunds = {}
    
    def get_order(self, order_id):
        return self._orders.get(order_id)
    
    def save_order(self, order):
        self._orders[order.id] = order
    
    def get_orders_in_range(self, start_date, end_date):
        return [o for o in self._orders.values() 
                if start_date <= o.created_at.date() <= end_date]
    
    def get_menu_item(self, item_id):
        return self._items.get(item_id)
    
    def save_menu_item(self, item):
        self._items[item.id] = item
    
    def get_category(self, category_id):
        return self._categories.get(category_id)
    
    def save_category(self, category):
        self._categories[category.id] = category
    
    def get_customer(self, customer_id):
        return self._customers.get(customer_id)
    
    def save_customer(self, customer):
        self._customers[customer.id] = customer
    
    def get_discount_code(self, code):
        return self._discount_codes.get(code.upper() if code else None)
    
    def save_discount_code(self, code):
        self._discount_codes[code.code.upper()] = code
    
    def has_customer_used_code(self, customer_id, code):
        return False
    
    def save_refund(self, refund):
        if refund.order_id not in self._refunds:
            self._refunds[refund.order_id] = []
        self._refunds[refund.order_id].append(refund)
    
    def get_order_refunds(self, order_id):
        return self._refunds.get(order_id, [])
    
    def create_notification(self, customer_id, message):
        pass


class TestDeliveryFeeEquivalence(unittest.TestCase):
    """US-D1: Calculate Delivery Fee - Equivalence Partitioning"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_zone_1_delivery_fee(self):
        """EP: Zone 1 postcode (LE1) - £2.00"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, False)
        self.assertTrue(result["success"])
        self.assertEqual(result["fee"], 2.00)
    
    def test_zone_2_delivery_fee(self):
        """EP: Zone 2 postcode (LE3) - £3.50"""
        result = self.manager.calculate_delivery_fee("LE3 1AA", 20.00, False)
        self.assertTrue(result["success"])
        self.assertEqual(result["fee"], 3.50)
    
    def test_zone_3_delivery_fee(self):
        """EP: Zone 3 postcode (LE7) - £5.00"""
        result = self.manager.calculate_delivery_fee("LE7 1AA", 20.00, False)
        self.assertTrue(result["success"])
        self.assertEqual(result["fee"], 5.00)
    
    def test_out_of_range_postcode(self):
        """EP: Out of range postcode"""
        result = self.manager.calculate_delivery_fee("SW1A 1AA", 20.00)
        self.assertFalse(result["success"])
    
    def test_free_delivery_at_threshold(self):
        """EP: Order exactly £30 - free delivery"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 30.00, False)
        self.assertTrue(result["success"])
        self.assertEqual(result["fee"], 0)
    
    def test_peak_time_surcharge(self):
        """EP: Peak time adds £1.50"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, True)
        self.assertTrue(result["success"])
        self.assertEqual(result["fee"], 3.50)
    
    def test_bad_weather_surcharge(self):
        """EP: Bad weather adds £1.00"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 20.00, False, True)
        self.assertTrue(result["success"])
        self.assertEqual(result["fee"], 3.00)


class TestDeliveryFeeBoundary(unittest.TestCase):
    """US-D1: Calculate Delivery Fee - Boundary Values"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_threshold_29_99(self):
        """BVA: £29.99 - just below free delivery"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 29.99, False)
        self.assertEqual(result["fee"], 2.00)
    
    def test_threshold_30_00(self):
        """BVA: £30.00 - exactly at free delivery"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 30.00, False)
        self.assertEqual(result["fee"], 0)
    
    def test_threshold_30_01(self):
        """BVA: £30.01 - just above free delivery"""
        result = self.manager.calculate_delivery_fee("LE1 1AA", 30.01, False)
        self.assertEqual(result["fee"], 0)


class TestDiscountCodeEquivalence(unittest.TestCase):
    """US-D2: Apply Discount Codes - Equivalence Partitioning"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
        
        self.storage.save_discount_code(DiscountCode(
            code="SAVE10", discount_type=DiscountType.PERCENTAGE, value=10,
            min_order_amount=15.00, is_active=True,
            valid_from=datetime.now() - timedelta(days=1),
            valid_until=datetime.now() + timedelta(days=30)
        ))
        
        self.storage.save_discount_code(DiscountCode(
            code="EXPIRED", discount_type=DiscountType.PERCENTAGE, value=20,
            is_active=True,
            valid_from=datetime.now() - timedelta(days=60),
            valid_until=datetime.now() - timedelta(days=1)
        ))
        
        self.storage.save_discount_code(DiscountCode(
            code="FIRSTORDER", discount_type=DiscountType.PERCENTAGE, value=25,
            is_active=True,
            valid_from=datetime.now() - timedelta(days=1),
            valid_until=datetime.now() + timedelta(days=30),
            is_first_order_only=True
        ))
    
    def test_valid_percentage_code(self):
        """EP: Valid percentage discount code"""
        result = self.manager.validate_discount_code("SAVE10", 20.00)
        self.assertTrue(result["valid"])
        self.assertEqual(result["discount"], 2.00)
    
    def test_invalid_code(self):
        """EP: Non-existent code"""
        result = self.manager.validate_discount_code("INVALID123", 20.00)
        self.assertFalse(result["valid"])
    
    def test_expired_code(self):
        """EP: Expired code"""
        result = self.manager.validate_discount_code("EXPIRED", 20.00)
        self.assertFalse(result["valid"])
    
    def test_min_order_not_met(self):
        """EP: Minimum order amount not met"""
        result = self.manager.validate_discount_code("SAVE10", 10.00)
        self.assertFalse(result["valid"])
    
    def test_first_order_code_valid(self):
        """EP: First order code with first order"""
        result = self.manager.validate_discount_code("FIRSTORDER", 20.00, is_first_order=True)
        self.assertTrue(result["valid"])
    
    def test_first_order_code_invalid(self):
        """EP: First order code with non-first order"""
        result = self.manager.validate_discount_code("FIRSTORDER", 20.00, is_first_order=False)
        self.assertFalse(result["valid"])


class TestPaymentValidationEquivalence(unittest.TestCase):
    """US-D3: Payment Validation - Equivalence Partitioning"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_valid_visa_card(self):
        """EP: Valid Visa card"""
        result = self.manager.validate_payment(
            "4111111111111111", 12, datetime.now().year + 2, "123", "John Doe", 50.00
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["card_type"], "visa")
    
    def test_valid_mastercard(self):
        """EP: Valid Mastercard"""
        result = self.manager.validate_payment(
            "5500000000000004", 12, datetime.now().year + 2, "123", "John Doe", 50.00
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["card_type"], "mastercard")
    
    def test_valid_amex(self):
        """EP: Valid American Express"""
        result = self.manager.validate_payment(
            "340000000000009", 12, datetime.now().year + 2, "1234", "John Doe", 50.00
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["card_type"], "amex")
    
    def test_invalid_luhn_number(self):
        """EP: Card number fails Luhn check"""
        result = self.manager.validate_payment(
            "4111111111111112", 12, datetime.now().year + 2, "123", "John Doe", 50.00
        )
        self.assertFalse(result["valid"])
    
    def test_expired_card(self):
        """EP: Expired card"""
        result = self.manager.validate_payment(
            "4111111111111111", 1, datetime.now().year - 1, "123", "John Doe", 50.00
        )
        self.assertFalse(result["valid"])
    
    def test_invalid_cvv_length(self):
        """EP: Invalid CVV length"""
        result = self.manager.validate_payment(
            "4111111111111111", 12, datetime.now().year + 2, "12", "John Doe", 50.00
        )
        self.assertFalse(result["valid"])
    
    def test_zero_amount(self):
        """EP: Zero payment amount"""
        result = self.manager.validate_payment(
            "4111111111111111", 12, datetime.now().year + 2, "123", "John Doe", 0
        )
        self.assertFalse(result["valid"])


class TestTipCalculation(unittest.TestCase):
    """US-D6: Tip Calculation"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_tip_10_percent(self):
        """EP: 10% tip"""
        result = self.manager.calculate_tip(50.00, percentage=10)
        self.assertTrue(result["success"])
        self.assertEqual(result["tip"], 5.00)
    
    def test_tip_15_percent(self):
        """EP: 15% tip"""
        result = self.manager.calculate_tip(50.00, percentage=15)
        self.assertTrue(result["success"])
        self.assertEqual(result["tip"], 7.50)
    
    def test_tip_20_percent(self):
        """EP: 20% tip"""
        result = self.manager.calculate_tip(50.00, percentage=20)
        self.assertTrue(result["success"])
        self.assertEqual(result["tip"], 10.00)
    
    def test_custom_tip_valid(self):
        """EP: Valid custom tip"""
        result = self.manager.calculate_tip(50.00, custom_amount=8.00)
        self.assertTrue(result["success"])
        self.assertEqual(result["tip"], 8.00)
    
    def test_custom_tip_too_small(self):
        """EP: Custom tip below minimum"""
        result = self.manager.calculate_tip(50.00, custom_amount=0.25)
        self.assertFalse(result["success"])
    
    def test_tip_over_100_percent(self):
        """EP: Tip > 100%"""
        result = self.manager.calculate_tip(50.00, percentage=150)
        self.assertFalse(result["success"])


class TestDeliveryTimeEstimation(unittest.TestCase):
    """US-D5: Delivery Time Estimation"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_small_order_zone_1(self):
        """EP: Small order, Zone 1"""
        result = self.manager.estimate_delivery_time(2, DeliveryZone.ZONE_1, 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["breakdown"]["prep"], 15)
        self.assertEqual(result["breakdown"]["travel"], 10)
    
    def test_medium_order_zone_2(self):
        """EP: Medium order, Zone 2"""
        result = self.manager.estimate_delivery_time(5, DeliveryZone.ZONE_2, 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["breakdown"]["prep"], 25)
        self.assertEqual(result["breakdown"]["travel"], 20)
    
    def test_large_order_zone_3(self):
        """EP: Large order, Zone 3"""
        result = self.manager.estimate_delivery_time(8, DeliveryZone.ZONE_3, 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["breakdown"]["prep"], 35)
        self.assertEqual(result["breakdown"]["travel"], 30)
    
    def test_with_queue(self):
        """EP: Order with queue"""
        result = self.manager.estimate_delivery_time(2, DeliveryZone.ZONE_1, 3)
        self.assertTrue(result["success"])
        self.assertEqual(result["breakdown"]["queue"], 15)


class TestSalesReport(unittest.TestCase):
    """US-D7: Sales Report Generation"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
        
        for i in range(5):
            order = Order(
                id=f"order{i}", order_number=f"ORD-{i}", customer_id="cust1",
                items=[], subtotal=25.00 + (i * 5), total=30.00 + (i * 5),
                tax_amount=5.00, delivery_fee=2.00, tip_amount=3.00,
                status=OrderStatus.DELIVERED, payment_method=PaymentMethod.CARD
            )
            order.created_at = datetime.now() - timedelta(days=i)
            self.storage.save_order(order)
    
    def test_report_valid_date_range(self):
        """EP: Valid date range with orders"""
        result = self.manager.generate_sales_report(
            date.today() - timedelta(days=7), date.today()
        )
        self.assertTrue(result["success"])
        self.assertGreater(result["report"].total_orders, 0)
    
    def test_report_invalid_date_range(self):
        """EP: Invalid date range"""
        result = self.manager.generate_sales_report(
            date.today(), date.today() - timedelta(days=7)
        )
        self.assertFalse(result["success"])


class TestRevenueDashboard(unittest.TestCase):
    """US-D9: Revenue Analytics Dashboard"""
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = PaymentDeliveryManager(self.storage)
    
    def test_daily_dashboard(self):
        """EP: Daily dashboard"""
        result = self.manager.get_revenue_dashboard(period="daily")
        self.assertTrue(result["success"])
        self.assertEqual(result["dashboard"]["period"], "daily")
    
    def test_weekly_dashboard(self):
        """EP: Weekly dashboard"""
        result = self.manager.get_revenue_dashboard(period="weekly")
        self.assertTrue(result["success"])
        self.assertEqual(result["dashboard"]["period"], "weekly")
    
    def test_monthly_dashboard(self):
        """EP: Monthly dashboard"""
        result = self.manager.get_revenue_dashboard(period="monthly")
        self.assertTrue(result["success"])
        self.assertEqual(result["dashboard"]["period"], "monthly")
    
    def test_invalid_period(self):
        """EP: Invalid period"""
        result = self.manager.get_revenue_dashboard(period="yearly")
        self.assertFalse(result["success"])


if __name__ == '__main__':
    unittest.main()
