"""
White-Box Tests: Symbolic Execution & Concolic Testing
Member A: Menu Management

Test File: studentid_test_whitebox_symbolic.py
Replace 'studentid' with your actual student ID.

This file demonstrates symbolic execution and concolic testing
as required by the research component.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from menu_manager import MenuManager
from models import MenuItem, Category, DietaryTag, OfferType
from datetime import datetime, timedelta


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


class TestAddMenuItemSymbolic(unittest.TestCase):
    """
    Symbolic Execution Tests for US-A1: add_menu_item
    
    SYMBOLIC EXECUTION ANALYSIS:
    ============================
    
    Function: add_menu_item(name, description, price, category_id, preparation_time, 
                            dietary_tags, stock_quantity)
    
    SYMBOLIC TREE:
    
                            START
                              |
                    [name_validation]
                    /              \
                T (valid)      F (invalid)
                   |              |
          [desc_validation]    RETURN error
          /              \
       T (valid)      F (invalid)
          |              |
    [price_validation]  RETURN error
    /              \
    T (valid)    F (invalid)
       |              |
    [cat_exists]   RETURN error
    /          \
    T (exists)  F (not exists)
       |              |
    [prep_valid]   RETURN error
    /          \
    T (valid)   F (invalid)
       |              |
    [name_unique] RETURN error
    /          \
    T (unique)  F (duplicate)
       |              |
    [tags_valid] RETURN error
    /          \
    T (valid)  F (invalid)
       |              |
    CREATE ITEM  RETURN error
       |
    RETURN success
    
    PATH CONDITIONS:
    ================
    Path 1: name_valid ∧ desc_valid ∧ price_valid ∧ cat_exists ∧ prep_valid ∧ name_unique ∧ tags_valid → SUCCESS
    Path 2: ¬name_valid → ERROR (name validation)
    Path 3: name_valid ∧ ¬desc_valid → ERROR (description validation)
    Path 4: name_valid ∧ desc_valid ∧ ¬price_valid → ERROR (price validation)
    Path 5: name_valid ∧ desc_valid ∧ price_valid ∧ ¬cat_exists → ERROR (category not found)
    Path 6: name_valid ∧ desc_valid ∧ price_valid ∧ cat_exists ∧ ¬prep_valid → ERROR (prep time)
    Path 7: name_valid ∧ desc_valid ∧ price_valid ∧ cat_exists ∧ prep_valid ∧ ¬name_unique → ERROR (duplicate)
    Path 8: name_valid ∧ desc_valid ∧ price_valid ∧ cat_exists ∧ prep_valid ∧ name_unique ∧ ¬tags_valid → ERROR (tags)
    
    CONCOLIC TEST INPUTS (derived from path conditions):
    ====================================================
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        
        # Set up valid category
        cat = Category(id="cat1", name="Main")
        self.storage.save_category(cat)
    
    # PATH 1: All conditions TRUE - Success path
    def test_path1_all_valid(self):
        """
        Path 1: All validations pass
        
        Symbolic values:
        - name: SYM_NAME where len(SYM_NAME) >= 2 ∧ len(SYM_NAME) <= 50 ∧ valid_chars(SYM_NAME)
        - description: SYM_DESC where len(SYM_DESC) >= 10 ∧ len(SYM_DESC) <= 500
        - price: SYM_PRICE where SYM_PRICE >= 0.50 ∧ SYM_PRICE <= 500
        - category_id: SYM_CAT where exists(SYM_CAT)
        - preparation_time: SYM_PREP where SYM_PREP >= 5 ∧ SYM_PREP <= 120
        
        Concrete values (satisfying constraints):
        """
        result = self.manager.add_menu_item(
            name="Valid Item",               # len=10, satisfies 2<=len<=50
            description="A valid description text",  # len=24, satisfies 10<=len<=500
            price=15.00,                     # satisfies 0.50<=price<=500
            category_id="cat1",              # exists in storage
            preparation_time=30              # satisfies 5<=prep<=120
        )
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["item"])
        self.assertIsNone(result["error"])
    
    # PATH 2: Name validation fails
    def test_path2_name_invalid_short(self):
        """
        Path 2: ¬name_valid (name too short)
        
        Symbolic constraint: len(SYM_NAME) < 2
        Concrete value: "A" (len=1)
        """
        result = self.manager.add_menu_item(
            name="A",
            description="A valid description text",
            price=15.00,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("2 characters", result["error"])
    
    def test_path2_name_invalid_empty(self):
        """
        Path 2 variant: ¬name_valid (empty name)
        
        Symbolic constraint: len(SYM_NAME) == 0
        Concrete value: ""
        """
        result = self.manager.add_menu_item(
            name="",
            description="A valid description text",
            price=15.00,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
    
    def test_path2_name_invalid_chars(self):
        """
        Path 2 variant: ¬name_valid (invalid characters)
        
        Symbolic constraint: ¬valid_chars(SYM_NAME)
        Concrete value: "Test@#$"
        """
        result = self.manager.add_menu_item(
            name="Test@#$",
            description="A valid description text",
            price=15.00,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("invalid characters", result["error"])
    
    # PATH 3: Description validation fails
    def test_path3_description_invalid(self):
        """
        Path 3: name_valid ∧ ¬desc_valid
        
        Symbolic constraints:
        - len(SYM_NAME) >= 2 ∧ len(SYM_NAME) <= 50 (satisfied)
        - len(SYM_DESC) < 10 (violated)
        
        Concrete values:
        - name: "Valid" (len=5)
        - description: "Short" (len=5)
        """
        result = self.manager.add_menu_item(
            name="Valid",
            description="Short",
            price=15.00,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("10 characters", result["error"])
    
    # PATH 4: Price validation fails
    def test_path4_price_invalid_low(self):
        """
        Path 4: name_valid ∧ desc_valid ∧ ¬price_valid (too low)
        
        Symbolic constraint: SYM_PRICE < 0.50
        Concrete value: 0.25
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="A valid description text",
            price=0.25,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("0.50", result["error"])
    
    def test_path4_price_invalid_high(self):
        """
        Path 4 variant: SYM_PRICE > 500
        Concrete value: 501.00
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="A valid description text",
            price=501.00,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("500", result["error"])
    
    # PATH 5: Category doesn't exist
    def test_path5_category_not_exists(self):
        """
        Path 5: ... ∧ ¬cat_exists
        
        Symbolic constraint: ¬exists(SYM_CAT)
        Concrete value: "nonexistent"
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="A valid description text",
            price=15.00,
            category_id="nonexistent"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Category", result["error"])
    
    # PATH 6: Preparation time invalid
    def test_path6_prep_time_invalid_low(self):
        """
        Path 6: ... ∧ ¬prep_valid (too low)
        
        Symbolic constraint: SYM_PREP < 5
        Concrete value: 4
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="A valid description text",
            price=15.00,
            category_id="cat1",
            preparation_time=4
        )
        
        self.assertFalse(result["success"])
        self.assertIn("5", result["error"])
    
    def test_path6_prep_time_invalid_high(self):
        """
        Path 6 variant: SYM_PREP > 120
        Concrete value: 121
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="A valid description text",
            price=15.00,
            category_id="cat1",
            preparation_time=121
        )
        
        self.assertFalse(result["success"])
        self.assertIn("120", result["error"])
    
    # PATH 7: Duplicate name
    def test_path7_duplicate_name(self):
        """
        Path 7: ... ∧ ¬name_unique
        
        Requires: existing item with same name in category
        """
        # First, add an item
        self.manager.add_menu_item(
            name="Duplicate Item",
            description="First item description",
            price=10.00,
            category_id="cat1"
        )
        
        # Try to add with same name
        result = self.manager.add_menu_item(
            name="Duplicate Item",
            description="Second item description",
            price=12.00,
            category_id="cat1"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])
    
    # PATH 8: Invalid dietary tags
    def test_path8_invalid_dietary_tag(self):
        """
        Path 8: ... ∧ ¬tags_valid
        
        Symbolic constraint: ∃t ∈ SYM_TAGS: ¬valid_tag(t)
        Concrete value: ["invalid_tag"]
        """
        result = self.manager.add_menu_item(
            name="Valid Item",
            description="A valid description text",
            price=15.00,
            category_id="cat1",
            dietary_tags=["invalid_tag"]
        )
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid dietary tag", result["error"])


class TestSearchItemsSymbolic(unittest.TestCase):
    """
    Symbolic Execution Tests for US-A4: search_items
    
    SYMBOLIC TREE (Simplified):
    
                START
                  |
            [has_query?]
            /         \
          T            F
          |            |
    [check_match]   [no query filter]
          |            |
    [has_category?]   ...
          ...
    
    PATH CONDITIONS:
    - Path 1: query ∧ match_found ∧ available → return matching items
    - Path 2: query ∧ ¬match_found → return empty
    - Path 3: ¬query ∧ category → return category items
    - Path 4: price_filter ∧ in_range → return filtered
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        
        # Setup test data
        cat = Category(id="cat1", name="Main")
        self.storage.save_category(cat)
        
        items = [
            MenuItem(id="1", name="Chicken Curry", price=12.00,
                    description="Spicy chicken", category_id="cat1",
                    is_available=True, stock_quantity=10),
            MenuItem(id="2", name="Veg Curry", price=10.00,
                    description="Mild vegetables", category_id="cat1",
                    is_available=True, stock_quantity=5),
        ]
        for item in items:
            self.storage.save_menu_item(item)
    
    def test_search_path1_query_match(self):
        """
        Path 1: query ∧ match_found
        
        Symbolic: SYM_QUERY where match(SYM_QUERY, items)
        Concrete: "Chicken"
        """
        result = self.manager.search_items(query="Chicken")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 1)
    
    def test_search_path2_query_no_match(self):
        """
        Path 2: query ∧ ¬match_found
        
        Symbolic: SYM_QUERY where ¬match(SYM_QUERY, items)
        Concrete: "Pizza"
        """
        result = self.manager.search_items(query="Pizza")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 0)
    
    def test_search_path3_price_filter(self):
        """
        Path 3: price_filter with items in range
        
        Symbolic: SYM_MIN <= item.price <= SYM_MAX
        Concrete: min=10, max=11
        """
        result = self.manager.search_items(min_price=10.00, max_price=11.00)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 1)


class TestCalculateOfferPriceSymbolic(unittest.TestCase):
    """
    Symbolic Execution Tests for calculate_offer_price
    
    SYMBOLIC TREE:
    
                    START
                      |
                [has_offer?]
                /          \
              F              T
              |              |
        RETURN original  [offer_active?]
                         /          \
                       F              T
                       |              |
                 RETURN original  [not_expired?]
                                  /          \
                                F              T
                                |              |
                          RETURN original  [min_qty_met?]
                                           /          \
                                         F              T
                                         |              |
                                   RETURN original  [calc_discount]
                                                        |
                                                  RETURN discounted
    
    PATH CONDITIONS:
    - P1: ¬has_offer → original_price
    - P2: has_offer ∧ ¬active → original_price
    - P3: has_offer ∧ active ∧ expired → original_price
    - P4: has_offer ∧ active ∧ ¬expired ∧ qty < min → original_price
    - P5: has_offer ∧ active ∧ ¬expired ∧ qty >= min → discounted_price
    """
    
    def setUp(self):
        self.storage = MockStorage()
        self.manager = MenuManager(self.storage)
        
        cat = Category(id="cat1", name="Main")
        self.storage.save_category(cat)
    
    def test_path1_no_offer(self):
        """
        Path 1: Item has no offer
        
        Constraint: item.special_offer_id == None
        """
        item = MenuItem(
            id="1", name="Test", description="Test item",
            price=10.00, category_id="cat1",
            special_offer_id=None
        )
        self.storage.save_menu_item(item)
        
        result = self.manager.calculate_offer_price(item, quantity=1)
        
        self.assertFalse(result["offer_applied"])
        self.assertEqual(result["original_price"], 10.00)
        self.assertEqual(result["discounted_price"], 10.00)
    
    def test_path5_offer_applied(self):
        """
        Path 5: All conditions met, discount applied
        
        Constraints satisfied:
        - has_offer
        - offer.is_active
        - offer.start_date <= now <= offer.end_date
        - quantity >= offer.min_quantity
        """
        from models import SpecialOffer
        
        offer = SpecialOffer(
            id="offer1",
            name="10% Off",
            offer_type=OfferType.PERCENTAGE_DISCOUNT,
            value=10,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            min_quantity=1,
            is_active=True
        )
        self.storage.save_special_offer(offer)
        
        item = MenuItem(
            id="1", name="Test", description="Test item",
            price=10.00, category_id="cat1",
            special_offer_id="offer1"
        )
        self.storage.save_menu_item(item)
        
        result = self.manager.calculate_offer_price(item, quantity=1)
        
        self.assertTrue(result["offer_applied"])
        self.assertEqual(result["original_price"], 10.00)
        self.assertEqual(result["discounted_price"], 9.00)
        self.assertEqual(result["savings"], 1.00)


if __name__ == '__main__':
    unittest.main()
