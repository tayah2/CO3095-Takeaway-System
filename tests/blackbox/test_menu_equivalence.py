"""
Black-Box Tests: Equivalence Partitioning
Member A: Menu Management

Test File: studentid_test_blackbox_equivalence.py
Replace 'studentid' with your actual student ID.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from menu_manager import MenuManager
from models import MenuItem, Category, DietaryTag


class MockStorage:
    """Mock storage for testing."""
    
    def __init__(self):
        self._items = {}
        self._categories = {}
        self._offers = {}
        self._change_logs = {}
    
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
    
    def get_special_offer(self, offer_id):
        return self._offers.get(offer_id)
    
    def save_special_offer(self, offer):
        self._offers[offer.id] = offer
    
    def log_item_changes(self, item_id, changes):
        self._change_logs[item_id] = changes
    
    def log_stock_adjustment(self, item_id, change, reason):
        pass
    
    def get_customer_offer_usage(self, customer_id, offer_id):
        return 0


class TestAddMenuItemEquivalence(unittest.TestCase):
    """
    US-A1: Add Menu Item with Validation
    
    Equivalence Partitioning:
    - Name: Valid (2-50 chars), Too Short (<2), Too Long (>50), Invalid chars
    - Price: Valid (0.50-500), Too Low (<0.50), Too High (>500), Invalid format
    - Description: Valid (10-500), Too Short (<10), Too Long (>500)
    - Category: Valid (exists), Invalid (doesn't exist)
    - Preparation Time: Valid (5-120), Too Low (<5), Too High (>120)
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        
        # Create a valid category for testing
        self.valid_category = Category(id="cat1", name="Mains")
        self.storage.save_category(self.valid_category)
    
    # ===== NAME VALIDATION EQUIVALENCE CLASSES =====
    
    def test_add_item_valid_name_minimum(self):
        """Valid partition: Name at minimum length (2 chars)."""
        result = self.manager.add_menu_item(
            name="AB",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["item"])
        self.assertEqual(result["item"].name, "AB")
    
    def test_add_item_valid_name_maximum(self):
        """Valid partition: Name at maximum length (50 chars)."""
        name = "A" * 50
        result = self.manager.add_menu_item(
            name=name,
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
        self.assertEqual(len(result["item"].name), 50)
    
    def test_add_item_invalid_name_too_short(self):
        """Invalid partition: Name too short (<2 chars)."""
        result = self.manager.add_menu_item(
            name="A",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("2 characters", result["error"])
    
    def test_add_item_invalid_name_too_long(self):
        """Invalid partition: Name too long (>50 chars)."""
        name = "A" * 51
        result = self.manager.add_menu_item(
            name=name,
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("50 characters", result["error"])
    
    def test_add_item_invalid_name_empty(self):
        """Invalid partition: Empty name."""
        result = self.manager.add_menu_item(
            name="",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_add_item_invalid_name_special_chars(self):
        """Invalid partition: Name with invalid special characters."""
        result = self.manager.add_menu_item(
            name="Item@#$%",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("invalid characters", result["error"])
    
    # ===== PRICE VALIDATION EQUIVALENCE CLASSES =====
    
    def test_add_item_valid_price_minimum(self):
        """Valid partition: Price at minimum (£0.50)."""
        result = self.manager.add_menu_item(
            name="Budget Item",
            description="A valid description for this item",
            price=0.50,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["item"].price, 0.50)
    
    def test_add_item_valid_price_maximum(self):
        """Valid partition: Price at maximum (£500)."""
        result = self.manager.add_menu_item(
            name="Premium Item",
            description="A valid description for this item",
            price=500.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["item"].price, 500.00)
    
    def test_add_item_invalid_price_too_low(self):
        """Invalid partition: Price too low (<£0.50)."""
        result = self.manager.add_menu_item(
            name="Cheap Item",
            description="A valid description for this item",
            price=0.49,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("0.50", result["error"])
    
    def test_add_item_invalid_price_too_high(self):
        """Invalid partition: Price too high (>£500)."""
        result = self.manager.add_menu_item(
            name="Expensive Item",
            description="A valid description for this item",
            price=500.01,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("500", result["error"])
    
    def test_add_item_invalid_price_negative(self):
        """Invalid partition: Negative price."""
        result = self.manager.add_menu_item(
            name="Negative Item",
            description="A valid description for this item",
            price=-5.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ===== DESCRIPTION VALIDATION EQUIVALENCE CLASSES =====
    
    def test_add_item_valid_description_minimum(self):
        """Valid partition: Description at minimum (10 chars)."""
        result = self.manager.add_menu_item(
            name="Test Item",
            description="A" * 10,
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_add_item_invalid_description_too_short(self):
        """Invalid partition: Description too short (<10 chars)."""
        result = self.manager.add_menu_item(
            name="Test Item",
            description="Short",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("10 characters", result["error"])
    
    def test_add_item_invalid_description_too_long(self):
        """Invalid partition: Description too long (>500 chars)."""
        result = self.manager.add_menu_item(
            name="Test Item",
            description="A" * 501,
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
        self.assertIn("500 characters", result["error"])
    
    # ===== CATEGORY VALIDATION EQUIVALENCE CLASSES =====
    
    def test_add_item_valid_category(self):
        """Valid partition: Category exists."""
        result = self.manager.add_menu_item(
            name="Valid Category Item",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_add_item_invalid_category_not_exists(self):
        """Invalid partition: Category doesn't exist."""
        result = self.manager.add_menu_item(
            name="No Category Item",
            description="A valid description for this item",
            price=10.00,
            category_id="nonexistent"
        )
        self.assertFalse(result["success"])
        self.assertIn("Category", result["error"])
    
    # ===== PREPARATION TIME EQUIVALENCE CLASSES =====
    
    def test_add_item_valid_prep_time_minimum(self):
        """Valid partition: Prep time at minimum (5 mins)."""
        result = self.manager.add_menu_item(
            name="Quick Item",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1",
            preparation_time=5
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["item"].preparation_time, 5)
    
    def test_add_item_valid_prep_time_maximum(self):
        """Valid partition: Prep time at maximum (120 mins)."""
        result = self.manager.add_menu_item(
            name="Slow Item",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1",
            preparation_time=120
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["item"].preparation_time, 120)
    
    def test_add_item_invalid_prep_time_too_low(self):
        """Invalid partition: Prep time too low (<5 mins)."""
        result = self.manager.add_menu_item(
            name="Too Quick Item",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1",
            preparation_time=4
        )
        self.assertFalse(result["success"])
        self.assertIn("5", result["error"])
    
    def test_add_item_invalid_prep_time_too_high(self):
        """Invalid partition: Prep time too high (>120 mins)."""
        result = self.manager.add_menu_item(
            name="Too Slow Item",
            description="A valid description for this item",
            price=10.00,
            category_id="cat1",
            preparation_time=121
        )
        self.assertFalse(result["success"])
        self.assertIn("120", result["error"])


class TestSearchItemsEquivalence(unittest.TestCase):
    """
    US-A4: Search Menu Items
    
    Equivalence Partitioning:
    - Query: Valid match, Partial match, No match, Empty
    - Price range: Valid range, Invalid range
    - Dietary tags: Single tag, Multiple tags, Invalid tag
    """
    
    def setUp(self):
        """Set up test fixtures with sample items."""
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        
        # Create category
        cat = Category(id="cat1", name="Mains")
        self.storage.save_category(cat)
        
        # Create sample items
        items = [
            MenuItem(id="1", name="Chicken Curry", description="Spicy chicken dish",
                    price=12.00, category_id="cat1", dietary_tags=[],
                    stock_quantity=10, is_available=True),
            MenuItem(id="2", name="Vegetable Curry", description="Mild veg dish",
                    price=10.00, category_id="cat1", 
                    dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN],
                    stock_quantity=10, is_available=True),
            MenuItem(id="3", name="Pad Thai", description="Thai noodles",
                    price=11.00, category_id="cat1",
                    dietary_tags=[DietaryTag.GLUTEN_FREE],
                    stock_quantity=10, is_available=True),
        ]
        for item in items:
            self.storage.save_menu_item(item)
    
    def test_search_exact_match(self):
        """Valid partition: Exact name match."""
        result = self.manager.search_items(query="Chicken Curry")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0].name, "Chicken Curry")
    
    def test_search_partial_match(self):
        """Valid partition: Partial name match."""
        result = self.manager.search_items(query="Curry")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 2)
    
    def test_search_case_insensitive(self):
        """Valid partition: Case insensitive search."""
        result = self.manager.search_items(query="chicken")
        self.assertTrue(result["success"])
        self.assertGreaterEqual(len(result["items"]), 1)
    
    def test_search_no_match(self):
        """Valid partition: No matches found."""
        result = self.manager.search_items(query="Pizza")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 0)
    
    def test_search_valid_price_range(self):
        """Valid partition: Price range filter."""
        result = self.manager.search_items(min_price=10.00, max_price=11.00)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 2)
    
    def test_search_dietary_single_tag(self):
        """Valid partition: Single dietary tag filter."""
        result = self.manager.search_items(
            dietary_tags=[DietaryTag.VEGETARIAN]
        )
        self.assertTrue(result["success"])
        self.assertGreaterEqual(len(result["items"]), 1)
    
    def test_search_dietary_multiple_tags(self):
        """Valid partition: Multiple dietary tags (AND)."""
        result = self.manager.search_items(
            dietary_tags=[DietaryTag.VEGETARIAN, DietaryTag.VEGAN],
            combine_filters="AND"
        )
        self.assertTrue(result["success"])


class TestCategoryEquivalence(unittest.TestCase):
    """
    US-A2: Categorize Menu Items
    
    Equivalence Partitioning:
    - Name: Valid, Too short, Too long
    - Parent: Valid parent, Invalid parent, Exceeds depth
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
    
    def test_create_category_valid(self):
        """Valid partition: Valid category creation."""
        result = self.manager.create_category(
            name="Appetizers",
            description="Starter dishes"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["category"].name, "Appetizers")
    
    def test_create_category_valid_with_parent(self):
        """Valid partition: Valid subcategory."""
        # Create parent
        parent = self.manager.create_category(name="Mains")
        self.assertTrue(parent["success"])
        
        # Create child
        result = self.manager.create_category(
            name="Curries",
            parent_id=parent["category"].id
        )
        self.assertTrue(result["success"])
    
    def test_create_category_invalid_name_short(self):
        """Invalid partition: Name too short."""
        result = self.manager.create_category(name="A")
        self.assertFalse(result["success"])
    
    def test_create_category_invalid_parent_not_exists(self):
        """Invalid partition: Parent doesn't exist."""
        result = self.manager.create_category(
            name="Orphan",
            parent_id="nonexistent"
        )
        self.assertFalse(result["success"])
    
    def test_create_category_duplicate_name_same_level(self):
        """Invalid partition: Duplicate name at same level."""
        self.manager.create_category(name="Mains")
        result = self.manager.create_category(name="Mains")
        self.assertFalse(result["success"])
        self.assertIn("exists", result["error"])


if __name__ == '__main__':
    unittest.main()
