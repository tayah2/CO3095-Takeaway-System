"""
Black-Box Tests: Equivalence Partitioning & Boundary Value Analysis
Member B: Customer Management (US-B1 to US-B9)

Test File: memberB_test_blackbox.py
"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from customer_manager import CustomerManager
from models import Customer, Address, LoyaltyPoints, DeliveryZone


class MockStorage:
    """Mock storage for customer testing."""
    
    def __init__(self):
        self._customers = {}
        self._orders = {}
        self._reset_tokens = {}
        self._blocked_emails = {}
        self._menu_items = {}
        self._deletions = {}
    
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
    
    def get_menu_item(self, item_id):
        return self._menu_items.get(item_id)
    
    def block_email(self, email, until):
        self._blocked_emails[email.lower()] = until
    
    def unblock_email(self, email):
        if email.lower() in self._blocked_emails:
            del self._blocked_emails[email.lower()]
    
    def anonymize_customer_orders(self, customer_id):
        pass
    
    def schedule_deletion(self, customer_id, delete_at):
        self._deletions[customer_id] = delete_at
    
    def get_scheduled_deletion(self, customer_id):
        if customer_id in self._deletions:
            return {"delete_at": self._deletions[customer_id]}
        return None
    
    def cancel_deletion(self, customer_id):
        if customer_id in self._deletions:
            del self._deletions[customer_id]


class TestCustomerRegistrationEquivalence(unittest.TestCase):
    """
    US-B1: Customer Registration with Validation
    
    Equivalence Partitions:
    - Email: Valid format, Invalid format, Disposable domain, Already registered
    - Password: Valid (all requirements), Missing uppercase, Missing lowercase,
                Missing number, Missing special char, Too short
    - Phone: Valid UK mobile, Valid UK landline, Invalid format
    - Name: Valid (2-50 chars), Too short, Too long
    - Age: 16+, Under 16
    - Terms: Accepted, Not accepted
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
    
    # ===== EMAIL EQUIVALENCE CLASSES =====
    
    def test_email_valid_format(self):
        """EP: Valid email format"""
        result = self.manager.register_customer(
            email="test@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertTrue(result["success"])
    
    def test_email_invalid_format_no_at(self):
        """EP: Invalid email - missing @"""
        result = self.manager.register_customer(
            email="testexample.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("email", result["error"].lower())
    
    def test_email_invalid_format_no_domain(self):
        """EP: Invalid email - missing domain"""
        result = self.manager.register_customer(
            email="test@",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
    
    def test_email_disposable_domain(self):
        """EP: Disposable email domain"""
        result = self.manager.register_customer(
            email="test@tempmail.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("disposable", result["error"].lower())
    
    def test_email_already_registered(self):
        """EP: Email already registered"""
        # First registration
        self.manager.register_customer(
            email="existing@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        
        # Second registration with same email
        result = self.manager.register_customer(
            email="existing@example.com",
            password="Test1234!",
            first_name="Jane",
            last_name="Smith",
            phone="07987654321",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("already registered", result["error"].lower())
    
    # ===== PASSWORD EQUIVALENCE CLASSES =====
    
    def test_password_valid_all_requirements(self):
        """EP: Password meets all requirements"""
        result = self.manager.register_customer(
            email="valid.pwd@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertTrue(result["success"])
    
    def test_password_missing_uppercase(self):
        """EP: Password missing uppercase"""
        result = self.manager.register_customer(
            email="test2@example.com",
            password="test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("uppercase", result["error"].lower())
    
    def test_password_missing_lowercase(self):
        """EP: Password missing lowercase"""
        result = self.manager.register_customer(
            email="test3@example.com",
            password="TEST1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("lowercase", result["error"].lower())
    
    def test_password_missing_number(self):
        """EP: Password missing number"""
        result = self.manager.register_customer(
            email="test4@example.com",
            password="TestTest!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("number", result["error"].lower())
    
    def test_password_missing_special_char(self):
        """EP: Password missing special character"""
        result = self.manager.register_customer(
            email="test5@example.com",
            password="Test12345",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("special", result["error"].lower())
    
    def test_password_too_short(self):
        """EP: Password too short (< 8 chars)"""
        result = self.manager.register_customer(
            email="test6@example.com",
            password="Te1!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("8", result["error"])
    
    # ===== PHONE EQUIVALENCE CLASSES =====
    
    def test_phone_valid_uk_mobile(self):
        """EP: Valid UK mobile number"""
        result = self.manager.register_customer(
            email="mobile@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertTrue(result["success"])
    
    def test_phone_valid_with_country_code(self):
        """EP: Valid UK mobile with +44"""
        result = self.manager.register_customer(
            email="mobile2@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="+447123456789",
            terms_accepted=True
        )
        self.assertTrue(result["success"])
    
    def test_phone_invalid_format(self):
        """EP: Invalid phone format"""
        result = self.manager.register_customer(
            email="invalid.phone@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="12345",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("phone", result["error"].lower())
    
    # ===== NAME EQUIVALENCE CLASSES =====
    
    def test_name_valid(self):
        """EP: Valid name (2-50 chars)"""
        result = self.manager.register_customer(
            email="name.test@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertTrue(result["success"])
    
    def test_first_name_too_short(self):
        """EP: First name too short (< 2 chars)"""
        result = self.manager.register_customer(
            email="short.name@example.com",
            password="Test1234!",
            first_name="J",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("first name", result["error"].lower())
    
    def test_last_name_too_short(self):
        """EP: Last name too short (< 2 chars)"""
        result = self.manager.register_customer(
            email="short.last@example.com",
            password="Test1234!",
            first_name="John",
            last_name="D",
            phone="07123456789",
            terms_accepted=True
        )
        self.assertFalse(result["success"])
        self.assertIn("last name", result["error"].lower())
    
    # ===== TERMS EQUIVALENCE CLASSES =====
    
    def test_terms_not_accepted(self):
        """EP: Terms not accepted"""
        result = self.manager.register_customer(
            email="no.terms@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=False
        )
        self.assertFalse(result["success"])
        self.assertIn("terms", result["error"].lower())


class TestCustomerLoginEquivalence(unittest.TestCase):
    """
    US-B2: Customer Login with Security
    
    Equivalence Partitions:
    - Credentials: Valid, Invalid email, Invalid password
    - Account status: Active, Deactivated, Locked
    - Failed attempts: 0-4 (allowed), 5+ (locked)
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
        
        # Create a test customer
        self.manager.register_customer(
            email="login.test@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
    
    def test_login_valid_credentials(self):
        """EP: Valid credentials"""
        result = self.manager.login("login.test@example.com", "Test1234!")
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["customer"])
    
    def test_login_invalid_email(self):
        """EP: Non-existent email"""
        result = self.manager.login("nonexistent@example.com", "Test1234!")
        self.assertFalse(result["success"])
        self.assertIn("invalid", result["error"].lower())
    
    def test_login_invalid_password(self):
        """EP: Wrong password"""
        result = self.manager.login("login.test@example.com", "WrongPass!")
        self.assertFalse(result["success"])
        self.assertIn("invalid", result["error"].lower())
    
    def test_login_account_locked_after_five_attempts(self):
        """EP: Account locked after 5 failed attempts"""
        # Make 5 failed attempts
        for i in range(5):
            self.manager.login("login.test@example.com", "WrongPass!")
        
        # 6th attempt should show locked
        result = self.manager.login("login.test@example.com", "Test1234!")
        self.assertFalse(result["success"])
        self.assertIn("locked", result["error"].lower())
    
    def test_login_deactivated_account(self):
        """EP: Deactivated account"""
        customer = self.storage.get_customer_by_email("login.test@example.com")
        customer.is_active = False
        self.storage.save_customer(customer)
        
        result = self.manager.login("login.test@example.com", "Test1234!")
        self.assertFalse(result["success"])
        self.assertIn("deactivated", result["error"].lower())


class TestDeliveryAddressBoundary(unittest.TestCase):
    """
    US-B3: Manage Delivery Addresses
    
    Boundary Values:
    - Number of addresses: 0, 1, 4, 5, 6 (max 5)
    - Address line 1 length: 4, 5, 100, 101
    - Postcode: Valid UK formats, Invalid formats
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
        
        # Create a test customer
        result = self.manager.register_customer(
            email="address.test@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.customer_id = result["customer"].id
    
    def test_add_first_address(self):
        """BVA: Add first address (0 -> 1)"""
        result = self.manager.add_address(
            self.customer_id,
            line1="123 Test Street",
            line2="",
            city="Leicester",
            postcode="LE1 1AA"
        )
        self.assertTrue(result["success"])
        self.assertTrue(result["address"].is_default)  # First address should be default
    
    def test_add_fifth_address(self):
        """BVA: Add fifth address (at max)"""
        # Add 4 addresses first
        for i in range(4):
            self.manager.add_address(
                self.customer_id,
                line1=f"{i+1} Test Street",
                line2="",
                city="Leicester",
                postcode=f"LE{i+1} 1AA"
            )
        
        # Add 5th address
        result = self.manager.add_address(
            self.customer_id,
            line1="5 Final Street",
            line2="",
            city="Leicester",
            postcode="LE5 1AA"
        )
        self.assertTrue(result["success"])
    
    def test_add_sixth_address_fails(self):
        """BVA: Adding 6th address should fail (exceeds max 5)"""
        # Add 5 addresses first
        for i in range(5):
            self.manager.add_address(
                self.customer_id,
                line1=f"{i+1} Test Street",
                line2="",
                city="Leicester",
                postcode=f"LE{i+1} 1AA"
            )
        
        # Try to add 6th
        result = self.manager.add_address(
            self.customer_id,
            line1="6 Too Many Street",
            line2="",
            city="Leicester",
            postcode="LE1 2BB"
        )
        self.assertFalse(result["success"])
        self.assertIn("5", result["error"])
    
    def test_address_line1_at_minimum(self):
        """BVA: Address line 1 = 5 chars (minimum)"""
        result = self.manager.add_address(
            self.customer_id,
            line1="12345",
            line2="",
            city="Leicester",
            postcode="LE1 1AA"
        )
        self.assertTrue(result["success"])
    
    def test_address_line1_below_minimum(self):
        """BVA: Address line 1 = 4 chars (below minimum)"""
        result = self.manager.add_address(
            self.customer_id,
            line1="1234",
            line2="",
            city="Leicester",
            postcode="LE1 1AA"
        )
        self.assertFalse(result["success"])
    
    def test_postcode_valid_format(self):
        """BVA: Valid UK postcode format"""
        result = self.manager.add_address(
            self.customer_id,
            line1="123 Test Street",
            line2="",
            city="Leicester",
            postcode="LE1 1AA"
        )
        self.assertTrue(result["success"])
    
    def test_postcode_invalid_format(self):
        """BVA: Invalid postcode format"""
        result = self.manager.add_address(
            self.customer_id,
            line1="123 Test Street",
            line2="",
            city="Leicester",
            postcode="INVALID"
        )
        self.assertFalse(result["success"])
        self.assertIn("postcode", result["error"].lower())
    
    def test_postcode_outside_delivery_area(self):
        """BVA: Postcode outside delivery zone"""
        result = self.manager.add_address(
            self.customer_id,
            line1="123 Test Street",
            line2="",
            city="London",
            postcode="SW1A 1AA"
        )
        self.assertFalse(result["success"])
        self.assertIn("delivery", result["error"].lower())


class TestLoyaltyPointsBoundary(unittest.TestCase):
    """
    US-B5: Customer Loyalty Points
    
    Boundary Values:
    - Earn: 0, 1, 100+ points
    - Redeem: 499, 500, 501 (min 500 to redeem)
    - Max redemption: 49%, 50%, 51% of order
    - Points balance: 0, positive, after redemption
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
        
        # Create customer with some points
        result = self.manager.register_customer(
            email="points.test@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.customer_id = result["customer"].id
        
        # Add initial points
        customer = self.storage.get_customer(self.customer_id)
        customer.loyalty_points.total_points = 1000
        self.storage.save_customer(customer)
    
    def test_earn_points_for_order(self):
        """BVA: Earn points (1 point per £1 + 100 first order bonus)"""
        result = self.manager.earn_points(
            self.customer_id,
            order_amount=25.50,
            order_id="order1"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["points_earned"], 125)  # 25 (floor) + 100 (first order bonus)
    
    def test_redeem_below_minimum(self):
        """BVA: Redeem 499 points (below min 500)"""
        result = self.manager.redeem_points(
            self.customer_id,
            points=499,
            order_total=50.00
        )
        self.assertFalse(result["success"])
        self.assertIn("500", result["error"])
    
    def test_redeem_at_minimum(self):
        """BVA: Redeem 500 points (at minimum)"""
        result = self.manager.redeem_points(
            self.customer_id,
            points=500,
            order_total=50.00
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["discount"], 5.00)  # 500 points = £5
    
    def test_redeem_above_minimum(self):
        """BVA: Redeem 501 points (above minimum)"""
        result = self.manager.redeem_points(
            self.customer_id,
            points=501,
            order_total=50.00
        )
        self.assertTrue(result["success"])
    
    def test_redeem_max_fifty_percent(self):
        """BVA: Cannot redeem more than 50% of order"""
        # Order total £20, max discount £10 = 1000 points
        result = self.manager.redeem_points(
            self.customer_id,
            points=1000,  # Would be £10 discount
            order_total=20.00  # 50% max = £10
        )
        self.assertTrue(result["success"])
        self.assertLessEqual(result["discount"], 10.00)
    
    def test_redeem_insufficient_points(self):
        """BVA: Insufficient points balance"""
        result = self.manager.redeem_points(
            self.customer_id,
            points=5000,  # More than available 1000
            order_total=100.00
        )
        self.assertFalse(result["success"])
        self.assertIn("insufficient", result["error"].lower())


class TestAccountDeletionEquivalence(unittest.TestCase):
    """
    US-B9: Customer Account Deletion
    
    Equivalence Partitions:
    - Password: Correct, Incorrect
    - Active orders: None, Has active orders
    - Points balance: Zero, Has points
    - Grace period: Within, Expired
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = CustomerManager(self.storage)
        
        result = self.manager.register_customer(
            email="delete.test@example.com",
            password="Test1234!",
            first_name="John",
            last_name="Doe",
            phone="07123456789",
            terms_accepted=True
        )
        self.customer_id = result["customer"].id
    
    def test_delete_with_correct_password(self):
        """EP: Delete account with correct password"""
        result = self.manager.delete_account(
            self.customer_id,
            password="Test1234!",
            reason="Testing deletion"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["grace_period_days"], 30)
    
    def test_delete_with_incorrect_password(self):
        """EP: Delete account with wrong password"""
        result = self.manager.delete_account(
            self.customer_id,
            password="WrongPassword!",
            reason="Testing deletion"
        )
        self.assertFalse(result["success"])
        self.assertIn("password", result["error"].lower())


if __name__ == '__main__':
    unittest.main()
