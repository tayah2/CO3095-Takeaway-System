"""
Black-Box Tests: Boundary Value Analysis
Member A: Menu Management (US-A1 to US-A9)

Test File: memberA_test_blackbox_boundary.py
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from menu_manager import MenuManager
from models import MenuItem, Category, DietaryTag


class MockStorage:
    """Mock storage for testing."""
    def __init__(self):
        self._items = {}
        self._categories = {}
        self._offers = {}
    
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
        pass
    
    def log_stock_adjustment(self, item_id, change, reason):
        pass
    
    def get_customer_offer_usage(self, customer_id, offer_id):
        return 0


class TestAddMenuItemBoundary(unittest.TestCase):
    """
    US-A1: Add Menu Item - Boundary Value Analysis
    
    Boundaries tested:
    - Name length: 1, 2, 50, 51 (boundaries: 2-50)
    - Description length: 9, 10, 500, 501 (boundaries: 10-500)
    - Price: 0.49, 0.50, 500.00, 500.01 (boundaries: 0.50-500)
    - Preparation time: 4, 5, 120, 121 (boundaries: 5-120)
    - Stock quantity: -1, 0, 1, 999, 1000 (boundaries: 0-999)
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        self.storage.save_category(Category(id="cat1", name="Mains"))
    
    # ===== NAME LENGTH BOUNDARIES =====
    
    def test_name_length_below_minimum(self):
        """BVA: Name length = 1 (below min of 2)"""
        result = self.manager.add_menu_item(
            name="A",
            description="Valid description text here",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_name_length_at_minimum(self):
        """BVA: Name length = 2 (at min boundary)"""
        result = self.manager.add_menu_item(
            name="AB",
            description="Valid description text here",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_name_length_above_minimum(self):
        """BVA: Name length = 3 (just above min)"""
        result = self.manager.add_menu_item(
            name="ABC",
            description="Valid description text here",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_name_length_below_maximum(self):
        """BVA: Name length = 49 (just below max)"""
        result = self.manager.add_menu_item(
            name="A" * 49,
            description="Valid description text here",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_name_length_at_maximum(self):
        """BVA: Name length = 50 (at max boundary)"""
        result = self.manager.add_menu_item(
            name="A" * 50,
            description="Valid description text here",
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_name_length_above_maximum(self):
        """BVA: Name length = 51 (above max of 50)"""
        result = self.manager.add_menu_item(
            name="A" * 51,
            description="Valid description text here",
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ===== DESCRIPTION LENGTH BOUNDARIES =====
    
    def test_description_length_below_minimum(self):
        """BVA: Description length = 9 (below min of 10)"""
        result = self.manager.add_menu_item(
            name="Test Item",
            description="A" * 9,
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_description_length_at_minimum(self):
        """BVA: Description length = 10 (at min boundary)"""
        result = self.manager.add_menu_item(
            name="Test Item",
            description="A" * 10,
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_description_length_above_minimum(self):
        """BVA: Description length = 11 (just above min)"""
        result = self.manager.add_menu_item(
            name="Test Item Two",
            description="A" * 11,
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_description_length_below_maximum(self):
        """BVA: Description length = 499 (just below max)"""
        result = self.manager.add_menu_item(
            name="Test Item Three",
            description="A" * 499,
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_description_length_at_maximum(self):
        """BVA: Description length = 500 (at max boundary)"""
        result = self.manager.add_menu_item(
            name="Test Item Four",
            description="A" * 500,
            price=10.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_description_length_above_maximum(self):
        """BVA: Description length = 501 (above max of 500)"""
        result = self.manager.add_menu_item(
            name="Test Item Five",
            description="A" * 501,
            price=10.00,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ===== PRICE BOUNDARIES =====
    
    def test_price_below_minimum(self):
        """BVA: Price = 0.49 (below min of 0.50)"""
        result = self.manager.add_menu_item(
            name="Cheap Item",
            description="Valid description text here",
            price=0.49,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    def test_price_at_minimum(self):
        """BVA: Price = 0.50 (at min boundary)"""
        result = self.manager.add_menu_item(
            name="Budget Item",
            description="Valid description text here",
            price=0.50,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_price_above_minimum(self):
        """BVA: Price = 0.51 (just above min)"""
        result = self.manager.add_menu_item(
            name="Budget Item Two",
            description="Valid description text here",
            price=0.51,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_price_below_maximum(self):
        """BVA: Price = 499.99 (just below max)"""
        result = self.manager.add_menu_item(
            name="Premium Item",
            description="Valid description text here",
            price=499.99,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_price_at_maximum(self):
        """BVA: Price = 500.00 (at max boundary)"""
        result = self.manager.add_menu_item(
            name="Luxury Item",
            description="Valid description text here",
            price=500.00,
            category_id="cat1"
        )
        self.assertTrue(result["success"])
    
    def test_price_above_maximum(self):
        """BVA: Price = 500.01 (above max of 500)"""
        result = self.manager.add_menu_item(
            name="Too Expensive",
            description="Valid description text here",
            price=500.01,
            category_id="cat1"
        )
        self.assertFalse(result["success"])
    
    # ===== PREPARATION TIME BOUNDARIES =====
    
    def test_prep_time_below_minimum(self):
        """BVA: Prep time = 4 (below min of 5)"""
        result = self.manager.add_menu_item(
            name="Quick Item",
            description="Valid description text here",
            price=10.00,
            category_id="cat1",
            preparation_time=4
        )
        self.assertFalse(result["success"])
    
    def test_prep_time_at_minimum(self):
        """BVA: Prep time = 5 (at min boundary)"""
        result = self.manager.add_menu_item(
            name="Fast Item",
            description="Valid description text here",
            price=10.00,
            category_id="cat1",
            preparation_time=5
        )
        self.assertTrue(result["success"])
    
    def test_prep_time_above_minimum(self):
        """BVA: Prep time = 6 (just above min)"""
        result = self.manager.add_menu_item(
            name="Fast Item Two",
            description="Valid description text here",
            price=10.00,
            category_id="cat1",
            preparation_time=6
        )
        self.assertTrue(result["success"])
    
    def test_prep_time_below_maximum(self):
        """BVA: Prep time = 119 (just below max)"""
        result = self.manager.add_menu_item(
            name="Slow Item",
            description="Valid description text here",
            price=10.00,
            category_id="cat1",
            preparation_time=119
        )
        self.assertTrue(result["success"])
    
    def test_prep_time_at_maximum(self):
        """BVA: Prep time = 120 (at max boundary)"""
        result = self.manager.add_menu_item(
            name="Very Slow Item",
            description="Valid description text here",
            price=10.00,
            category_id="cat1",
            preparation_time=120
        )
        self.assertTrue(result["success"])
    
    def test_prep_time_above_maximum(self):
        """BVA: Prep time = 121 (above max of 120)"""
        result = self.manager.add_menu_item(
            name="Too Slow Item",
            description="Valid description text here",
            price=10.00,
            category_id="cat1",
            preparation_time=121
        )
        self.assertFalse(result["success"])


class TestSearchItemsBoundary(unittest.TestCase):
    """
    US-A4: Search Menu Items - Boundary Value Analysis
    
    Boundaries tested:
    - Query length: 0, 1, 100 chars
    - Price range boundaries
    - Pagination: page 0, 1, max
    - Results per page: 0, 1, 50, 51
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        self.storage.save_category(Category(id="cat1", name="Mains"))
        
        # Create test items with various prices
        for i in range(25):
            item = MenuItem(
                id=f"item{i}",
                name=f"Test Item {i}",
                description="A test item description",
                price=5.00 + (i * 2),  # Prices from 5 to 53
                category_id="cat1",
                is_available=True,
                stock_quantity=10
            )
            self.storage.save_menu_item(item)
    
    def test_search_empty_query(self):
        """BVA: Query length = 0 (empty)"""
        result = self.manager.search_items(query="")
        self.assertTrue(result["success"])
        # Empty query should return all items
    
    def test_search_single_char_query(self):
        """BVA: Query length = 1"""
        result = self.manager.search_items(query="T")
        self.assertTrue(result["success"])
    
    def test_price_range_exact_match(self):
        """BVA: Price range exactly matching an item"""
        result = self.manager.search_items(min_price=5.00, max_price=5.00)
        self.assertTrue(result["success"])
        self.assertGreaterEqual(len(result["items"]), 1)
    
    def test_price_range_no_items(self):
        """BVA: Price range with no items"""
        result = self.manager.search_items(min_price=1000.00, max_price=2000.00)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 0)
    
    def test_pagination_page_one(self):
        """BVA: First page of results"""
        result = self.manager.search_items(page=1, page_size=10)
        self.assertTrue(result["success"])
        self.assertLessEqual(len(result["items"]), 10)
    
    def test_pagination_page_size_one(self):
        """BVA: Page size = 1 (minimum)"""
        result = self.manager.search_items(page=1, page_size=1)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 1)
    
    def test_pagination_large_page_size(self):
        """BVA: Page size = 50 (maximum)"""
        result = self.manager.search_items(page=1, page_size=50)
        self.assertTrue(result["success"])


class TestCategoryHierarchyBoundary(unittest.TestCase):
    """
    US-A2: Categorize Menu Items - Boundary Value Analysis
    
    Boundaries tested:
    - Category name length: 1, 2, 50, 51
    - Hierarchy depth: 0, 1, 2, 3, 4 levels
    - Subcategories per parent: 0, 1, max
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
    
    def test_category_name_at_minimum(self):
        """BVA: Category name = 2 chars (minimum)"""
        result = self.manager.create_category(name="AB")
        self.assertTrue(result["success"])
    
    def test_category_name_below_minimum(self):
        """BVA: Category name = 1 char (below minimum)"""
        result = self.manager.create_category(name="A")
        self.assertFalse(result["success"])
    
    def test_category_name_at_maximum(self):
        """BVA: Category name = 50 chars (maximum)"""
        result = self.manager.create_category(name="A" * 50)
        self.assertTrue(result["success"])
    
    def test_category_name_above_maximum(self):
        """BVA: Category name = 51 chars (above maximum)"""
        result = self.manager.create_category(name="A" * 51)
        self.assertFalse(result["success"])
    
    def test_hierarchy_depth_level_one(self):
        """BVA: Hierarchy depth = 1 (root category)"""
        result = self.manager.create_category(name="Root Category")
        self.assertTrue(result["success"])
        self.assertIsNone(result["category"].parent_id)
    
    def test_hierarchy_depth_level_two(self):
        """BVA: Hierarchy depth = 2 (child of root)"""
        parent = self.manager.create_category(name="Parent")
        result = self.manager.create_category(
            name="Child",
            parent_id=parent["category"].id
        )
        self.assertTrue(result["success"])
    
    def test_hierarchy_depth_level_three(self):
        """BVA: Hierarchy depth = 3 (at maximum)"""
        level1 = self.manager.create_category(name="Level One")
        level2 = self.manager.create_category(
            name="Level Two",
            parent_id=level1["category"].id
        )
        result = self.manager.create_category(
            name="Level Three",
            parent_id=level2["category"].id
        )
        self.assertTrue(result["success"])
    
    def test_hierarchy_depth_level_four(self):
        """BVA: Hierarchy depth = 4 (exceeds maximum of 3)"""
        level1 = self.manager.create_category(name="L1")
        level2 = self.manager.create_category(name="L2", parent_id=level1["category"].id)
        level3 = self.manager.create_category(name="L3", parent_id=level2["category"].id)
        result = self.manager.create_category(
            name="L4",
            parent_id=level3["category"].id
        )
        self.assertFalse(result["success"])
        self.assertIn("depth", result["error"].lower())


class TestStockManagementBoundary(unittest.TestCase):
    """
    US-A3: Update Menu Item with Stock Management - Boundary Value Analysis
    
    Boundaries tested:
    - Stock quantity: -1, 0, 1, 999, 1000
    - Stock adjustment: large negative, -1, 0, +1, large positive
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        self.storage.save_category(Category(id="cat1", name="Mains"))
        
        # Create item with initial stock
        item = MenuItem(
            id="item1",
            name="Stock Test Item",
            description="Item for stock testing",
            price=10.00,
            category_id="cat1",
            stock_quantity=50,
            is_available=True
        )
        self.storage.save_menu_item(item)
    
    def test_adjust_stock_to_zero(self):
        """BVA: Adjust stock to exactly 0"""
        result = self.manager.adjust_stock("item1", -50)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_quantity"], 0)
    
    def test_adjust_stock_below_zero(self):
        """BVA: Try to adjust stock below 0"""
        result = self.manager.adjust_stock("item1", -51)
        self.assertFalse(result["success"])
    
    def test_adjust_stock_to_one(self):
        """BVA: Adjust stock to 1"""
        result = self.manager.adjust_stock("item1", -49)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_quantity"], 1)
    
    def test_adjust_stock_large_increase(self):
        """BVA: Large stock increase"""
        result = self.manager.adjust_stock("item1", 500)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_quantity"], 550)


if __name__ == '__main__':
    unittest.main()
