"""
Menu Management Module - Member A
Handles: Menu items, Categories, Search/Filter, Offers, Customization

User Stories:
- US-A1: Add Menu Item with Validation
- US-A2: Categorize Menu Items  
- US-A3: Update Menu Item with Stock Management
- US-A4: Search Menu Items
- US-A5: Filter by Dietary Requirements
- US-A6: Menu Item Availability Scheduling
- US-A7: Special Offers on Items
- US-A8: Item Customization Options
- US-A9: Menu Import/Export
"""

import re
import json
import csv
import io
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from models import (
    MenuItem, Category, ItemExtra, AvailabilitySchedule, SpecialOffer,
    ItemCustomization, DietaryTag, SpiceLevel, ItemSize, OfferType
)


class MenuManager:
    """Manages menu items, categories, and related operations."""
    
    def __init__(self, storage):
        """Initialize with storage backend."""
        self.storage = storage
    
    # ==================== US-A1: Add Menu Item with Validation ====================
    
    def add_menu_item(self, name: str, description: str, price: float, 
                      category_id: str, preparation_time: int = 15,
                      dietary_tags: list = None, stock_quantity: int = 100) -> dict:
        """
        Add a new menu item with comprehensive validation.
        
        Cyclomatic Complexity: >= 10 (multiple validation branches)
        """
        # Validate name (branch 1-4)
        name_validation = self._validate_item_name(name)
        if not name_validation["valid"]:
            return {"success": False, "item": None, "error": name_validation["error"]}
        
        # Validate description (branch 5-7)
        desc_validation = self._validate_description(description)
        if not desc_validation["valid"]:
            return {"success": False, "item": None, "error": desc_validation["error"]}
        
        # Validate price (branch 8-11)
        price_validation = self._validate_price(price)
        if not price_validation["valid"]:
            return {"success": False, "item": None, "error": price_validation["error"]}
        
        # Validate category exists (branch 12)
        if not self._category_exists(category_id):
            return {"success": False, "item": None, "error": "Category does not exist"}
        
        # Validate preparation time (branch 13)
        if not self._validate_preparation_time(preparation_time):
            return {"success": False, "item": None, 
                    "error": "Preparation time must be between 5 and 120 minutes"}
        
        # Check for duplicate items (branch 14)
        if self._item_name_exists(name, category_id):
            return {"success": False, "item": None, 
                    "error": "Item with this name already exists in this category"}
        
        # Validate dietary tags (branch 15-16)
        if dietary_tags:
            tags_validation = self._validate_dietary_tags(dietary_tags)
            if not tags_validation["valid"]:
                return {"success": False, "item": None, "error": tags_validation["error"]}
        
        # Create the menu item
        item = MenuItem(
            name=name.strip(),
            description=description.strip(),
            price=round(price, 2),
            category_id=category_id,
            preparation_time=preparation_time,
            dietary_tags=dietary_tags or [],
            stock_quantity=stock_quantity,
            is_available=stock_quantity > 0
        )
        
        self.storage.save_menu_item(item)
        return {"success": True, "item": item, "error": None}
    
    def _validate_item_name(self, name: str) -> dict:
        """Validate item name meets requirements."""
        if not name or not isinstance(name, str):
            return {"valid": False, "error": "Name is required"}
        
        name = name.strip()
        if len(name) < 2:
            return {"valid": False, "error": "Name must be at least 2 characters"}
        if len(name) > 50:
            return {"valid": False, "error": "Name must not exceed 50 characters"}
        if not re.match(r'^[a-zA-Z0-9\s\-\'\.]+$', name):
            return {"valid": False, "error": "Name contains invalid characters"}
        
        return {"valid": True, "error": None}
    
    def _validate_description(self, description: str) -> dict:
        """Validate item description meets requirements."""
        if not description or not isinstance(description, str):
            return {"valid": False, "error": "Description is required"}
        
        description = description.strip()
        if len(description) < 10:
            return {"valid": False, "error": "Description must be at least 10 characters"}
        if len(description) > 500:
            return {"valid": False, "error": "Description must not exceed 500 characters"}
        
        return {"valid": True, "error": None}
    
    def _validate_price(self, price: float) -> dict:
        """Validate price is within acceptable range and format."""
        if price is None:
            return {"valid": False, "error": "Price is required"}
        try:
            price = float(price)
        except (TypeError, ValueError):
            return {"valid": False, "error": "Price must be a number"}
        
        if price < 0.50:
            return {"valid": False, "error": "Price must be at least £0.50"}
        if price > 500:
            return {"valid": False, "error": "Price must not exceed £500"}
        if round(price, 2) != price:
            return {"valid": False, "error": "Price can have maximum 2 decimal places"}
        
        return {"valid": True, "error": None}
    
    def _validate_preparation_time(self, prep_time: int) -> bool:
        """Validate preparation time is within range."""
        try:
            prep_time = int(prep_time)
            return 5 <= prep_time <= 120
        except (TypeError, ValueError):
            return False
    
    def _category_exists(self, category_id: str) -> bool:
        """Check if category exists in storage."""
        return self.storage.get_category(category_id) is not None
    
    def _item_name_exists(self, name: str, category_id: str) -> bool:
        """Check if item with same name exists in category."""
        items = self.storage.get_items_by_category(category_id)
        return any(item.name.lower() == name.lower().strip() for item in items)
    
    def _validate_dietary_tags(self, tags: list) -> dict:
        """Validate dietary tags are valid."""
        valid_tags = [tag.value for tag in DietaryTag]
        for tag in tags:
            if isinstance(tag, DietaryTag):
                continue
            if tag not in valid_tags:
                return {"valid": False, "error": f"Invalid dietary tag: {tag}"}
        return {"valid": True, "error": None}
    
    # ==================== US-A2: Categorize Menu Items ====================
    
    def create_category(self, name: str, description: str = "", 
                        parent_id: str = None) -> dict:
        """
        Create a new category with hierarchy support (max 3 levels).
        
        Cyclomatic Complexity: >= 10
        """
        # Validate name (branches 1-3)
        if not name or len(name.strip()) < 2:
            return {"success": False, "category": None, 
                    "error": "Category name must be at least 2 characters"}
        if len(name) > 50:
            return {"success": False, "category": None,
                    "error": "Category name must not exceed 50 characters"}
        
        # Check hierarchy depth (branches 4-6)
        if parent_id:
            depth = self._get_category_depth(parent_id)
            if depth >= 3:
                return {"success": False, "category": None,
                        "error": "Maximum category depth (3 levels) exceeded"}
            if not self._category_exists(parent_id):
                return {"success": False, "category": None,
                        "error": "Parent category does not exist"}
        
        # Check name uniqueness at same level (branch 7)
        if self._category_name_exists_at_level(name, parent_id):
            return {"success": False, "category": None,
                    "error": "Category name already exists at this level"}
        
        category = Category(
            name=name.strip(),
            description=description.strip() if description else "",
            parent_id=parent_id
        )
        self.storage.save_category(category)
        return {"success": True, "category": category, "error": None}
    
    def update_category(self, category_id: str, name: str = None, 
                        description: str = None, display_order: int = None) -> dict:
        """Update an existing category."""
        category = self.storage.get_category(category_id)
        if not category:
            return {"success": False, "category": None, "error": "Category not found"}
        
        if name:
            if len(name.strip()) < 2:
                return {"success": False, "category": None,
                        "error": "Category name must be at least 2 characters"}
            if self._category_name_exists_at_level(name, category.parent_id, exclude_id=category_id):
                return {"success": False, "category": None,
                        "error": "Category name already exists at this level"}
            category.name = name.strip()
        
        if description is not None:
            category.description = description.strip()
        if display_order is not None:
            category.display_order = display_order
        
        category.updated_at = datetime.now()
        self.storage.save_category(category)
        return {"success": True, "category": category, "error": None}
    
    def delete_category(self, category_id: str, force: bool = False) -> dict:
        """Delete a category (prevents if has items unless force=True)."""
        category = self.storage.get_category(category_id)
        if not category:
            return {"success": False, "error": "Category not found"}
        
        items = self.storage.get_items_by_category(category_id)
        if items and not force:
            return {"success": False, 
                    "error": f"Category has {len(items)} items. Use force=True to delete anyway"}
        
        subcategories = self.storage.get_subcategories(category_id)
        if subcategories and not force:
            return {"success": False,
                    "error": f"Category has {len(subcategories)} subcategories"}
        
        self.storage.delete_category(category_id)
        return {"success": True, "error": None}
    
    def _get_category_depth(self, category_id: str) -> int:
        """Get the depth level of a category in hierarchy."""
        depth = 1
        category = self.storage.get_category(category_id)
        while category and category.parent_id:
            depth += 1
            category = self.storage.get_category(category.parent_id)
            if depth > 10:
                break
        return depth
    
    def _category_name_exists_at_level(self, name: str, parent_id: str = None, 
                                        exclude_id: str = None) -> bool:
        """Check if category name exists at the same hierarchy level."""
        categories = self.storage.get_categories_by_parent(parent_id)
        for cat in categories:
            if cat.id == exclude_id:
                continue
            if cat.name.lower() == name.lower().strip():
                return True
        return False
    
    # ==================== US-A3: Update Menu Item with Stock Management ====================
    
    def update_menu_item(self, item_id: str, **updates) -> dict:
        """
        Update a menu item with validation and change logging.
        
        Cyclomatic Complexity: >= 10 (multiple field validations)
        """
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "item": None, "error": "Item not found", "changes": []}
        
        changes = []
        
        # Validate and apply name update
        if "name" in updates:
            validation = self._validate_item_name(updates["name"])
            if not validation["valid"]:
                return {"success": False, "item": None, "error": validation["error"], "changes": []}
            if self._item_name_exists_excluding(updates["name"], item.category_id, item_id):
                return {"success": False, "item": None,
                        "error": "Item name already exists in this category", "changes": []}
            changes.append({"field": "name", "old": item.name, "new": updates["name"]})
            item.name = updates["name"].strip()
        
        # Validate and apply description update
        if "description" in updates:
            validation = self._validate_description(updates["description"])
            if not validation["valid"]:
                return {"success": False, "item": None, "error": validation["error"], "changes": []}
            changes.append({"field": "description", "old": item.description, "new": updates["description"]})
            item.description = updates["description"].strip()
        
        # Validate and apply price update
        if "price" in updates:
            validation = self._validate_price(updates["price"])
            if not validation["valid"]:
                return {"success": False, "item": None, "error": validation["error"], "changes": []}
            changes.append({"field": "price", "old": item.price, "new": updates["price"]})
            item.price = round(updates["price"], 2)
        
        # Handle stock quantity update
        if "stock_quantity" in updates:
            new_stock = updates["stock_quantity"]
            if not isinstance(new_stock, int) or new_stock < 0:
                return {"success": False, "item": None,
                        "error": "Stock quantity must be a non-negative integer", "changes": []}
            changes.append({"field": "stock_quantity", "old": item.stock_quantity, "new": new_stock})
            item.stock_quantity = new_stock
            if new_stock == 0 and item.is_available:
                item.is_available = False
                changes.append({"field": "is_available", "old": True, "new": False})
        
        # Handle availability update
        if "is_available" in updates:
            changes.append({"field": "is_available", "old": item.is_available, "new": updates["is_available"]})
            item.is_available = updates["is_available"]
        
        # Handle preparation time update
        if "preparation_time" in updates:
            if not self._validate_preparation_time(updates["preparation_time"]):
                return {"success": False, "item": None,
                        "error": "Preparation time must be between 5 and 120 minutes", "changes": []}
            changes.append({"field": "preparation_time", "old": item.preparation_time, "new": updates["preparation_time"]})
            item.preparation_time = updates["preparation_time"]
        
        # Handle category update
        if "category_id" in updates:
            if not self._category_exists(updates["category_id"]):
                return {"success": False, "item": None, "error": "Category does not exist", "changes": []}
            changes.append({"field": "category_id", "old": item.category_id, "new": updates["category_id"]})
            item.category_id = updates["category_id"]
        
        # Handle dietary tags update
        if "dietary_tags" in updates:
            validation = self._validate_dietary_tags(updates["dietary_tags"])
            if not validation["valid"]:
                return {"success": False, "item": None, "error": validation["error"], "changes": []}
            changes.append({"field": "dietary_tags", "old": item.dietary_tags, "new": updates["dietary_tags"]})
            item.dietary_tags = updates["dietary_tags"]
        
        item.updated_at = datetime.now()
        self.storage.save_menu_item(item)
        self.storage.log_item_changes(item_id, changes)
        return {"success": True, "item": item, "error": None, "changes": changes}
    
    def _item_name_exists_excluding(self, name: str, category_id: str, exclude_id: str) -> bool:
        """Check if item name exists, excluding specified item."""
        items = self.storage.get_items_by_category(category_id)
        for item in items:
            if item.id == exclude_id:
                continue
            if item.name.lower() == name.lower().strip():
                return True
        return False
    
    def adjust_stock(self, item_id: str, quantity_change: int, reason: str = "") -> dict:
        """Adjust stock quantity for an item."""
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "new_quantity": None, "error": "Item not found"}
        
        new_quantity = item.stock_quantity + quantity_change
        if new_quantity < 0:
            return {"success": False, "new_quantity": None,
                    "error": f"Insufficient stock. Current: {item.stock_quantity}"}
        
        item.stock_quantity = new_quantity
        if new_quantity == 0:
            item.is_available = False
        
        item.updated_at = datetime.now()
        self.storage.save_menu_item(item)
        self.storage.log_stock_adjustment(item_id, quantity_change, reason)
        return {"success": True, "new_quantity": new_quantity, "error": None}
    
    # ==================== US-A4: Search Menu Items ====================
    
    def search_items(self, query: str = None, category_id: str = None,
                     min_price: float = None, max_price: float = None,
                     dietary_tags: list = None, available_only: bool = True,
                     sort_by: str = "relevance", sort_order: str = "asc",
                     page: int = 1, page_size: int = 20,
                     combine_filters: str = "AND") -> dict:
        """
        Search menu items with multiple criteria.
        
        Cyclomatic Complexity: >= 15 (multiple filter combinations)
        """
        all_items = self.storage.get_all_menu_items()
        filtered_items = []
        
        for item in all_items:
            matches = []
            
            # Text search (branches 1-3)
            if query:
                query_lower = query.lower().strip()
                name_match = query_lower in item.name.lower()
                desc_match = query_lower in item.description.lower()
                matches.append(name_match or desc_match)
            
            # Category filter (branches 4-5)
            if category_id:
                cat_match = item.category_id == category_id
                if not cat_match:
                    cat_match = self._is_in_category_tree(item.category_id, category_id)
                matches.append(cat_match)
            
            # Price range filter (branches 6-7)
            if min_price is not None:
                matches.append(item.price >= min_price)
            if max_price is not None:
                matches.append(item.price <= max_price)
            
            # Dietary tags filter (branches 8-10)
            if dietary_tags:
                item_tags = [t.value if isinstance(t, DietaryTag) else t for t in item.dietary_tags]
                filter_tags = [t.value if isinstance(t, DietaryTag) else t for t in dietary_tags]
                if combine_filters == "AND":
                    tags_match = all(tag in item_tags for tag in filter_tags)
                else:
                    tags_match = any(tag in item_tags for tag in filter_tags)
                matches.append(tags_match)
            
            # Availability filter (branch 11)
            if available_only:
                matches.append(item.is_available and item.stock_quantity > 0)
            
            # Combine matches (branches 12-14)
            if not matches:
                filtered_items.append(item)
            elif combine_filters == "AND":
                if all(matches):
                    filtered_items.append(item)
            else:
                if any(matches):
                    filtered_items.append(item)
        
        # Calculate relevance scores
        if query and sort_by == "relevance":
            for item in filtered_items:
                item._relevance = self._calculate_relevance(item, query)
        
        # Sort results
        filtered_items = self._sort_items(filtered_items, sort_by, sort_order)
        
        # Pagination
        total = len(filtered_items)
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = filtered_items[start_idx:end_idx]
        
        return {
            "success": True, "items": paginated_items, "total": total,
            "page": page, "total_pages": total_pages, "error": None
        }
    
    def _is_in_category_tree(self, item_category_id: str, parent_category_id: str) -> bool:
        """Check if item's category is a descendant of given parent."""
        category = self.storage.get_category(item_category_id)
        while category and category.parent_id:
            if category.parent_id == parent_category_id:
                return True
            category = self.storage.get_category(category.parent_id)
        return False
    
    def _calculate_relevance(self, item: MenuItem, query: str) -> float:
        """Calculate relevance score for search result."""
        score = 0.0
        query_lower = query.lower()
        if item.name.lower() == query_lower:
            score += 100
        elif item.name.lower().startswith(query_lower):
            score += 50
        elif query_lower in item.name.lower():
            score += 25
        if query_lower in item.description.lower():
            score += 10
        return score
    
    def _sort_items(self, items: list, sort_by: str, sort_order: str) -> list:
        """Sort items by specified field."""
        reverse = sort_order.lower() == "desc"
        if sort_by == "price":
            return sorted(items, key=lambda x: x.price, reverse=reverse)
        elif sort_by == "name":
            return sorted(items, key=lambda x: x.name.lower(), reverse=reverse)
        elif sort_by == "relevance":
            return sorted(items, key=lambda x: getattr(x, '_relevance', 0), reverse=True)
        return items
    
    # ==================== US-A5: Filter by Dietary Requirements ====================
    
    def filter_by_dietary(self, tags: list, match_all: bool = True,
                          include_allergen_warning: bool = True) -> dict:
        """
        Filter items by dietary requirements.
        
        Cyclomatic Complexity: >= 10
        """
        if not tags:
            return {"success": False, "items": [], "warnings": [],
                    "error": "At least one dietary tag is required"}
        
        validation = self._validate_dietary_tags(tags)
        if not validation["valid"]:
            return {"success": False, "items": [], "warnings": [], "error": validation["error"]}
        
        filter_tags = [tag.value if isinstance(tag, DietaryTag) else tag for tag in tags]
        implied_tags = self._get_implied_tags(filter_tags)
        
        all_items = self.storage.get_all_menu_items()
        filtered_items = []
        warnings = []
        
        for item in all_items:
            if not item.is_available:
                continue
            
            item_tags = [t.value if isinstance(t, DietaryTag) else t for t in item.dietary_tags]
            
            if match_all:
                matches = all(tag in item_tags for tag in filter_tags)
            else:
                matches = any(tag in item_tags for tag in filter_tags)
            
            if matches:
                contradiction = self._check_dietary_contradictions(item_tags)
                if contradiction:
                    warnings.append(f"{item.name}: {contradiction}")
                if include_allergen_warning and item.allergen_info:
                    warnings.append(f"{item.name} - Allergens: {item.allergen_info}")
                filtered_items.append(item)
        
        return {"success": True, "items": filtered_items, "warnings": warnings, "error": None}
    
    def _get_implied_tags(self, tags: list) -> list:
        """Get tags implied by given tags."""
        implied = list(tags)
        if DietaryTag.VEGAN.value in tags and DietaryTag.VEGETARIAN.value not in implied:
            implied.append(DietaryTag.VEGETARIAN.value)
        return implied
    
    def _check_dietary_contradictions(self, tags: list) -> str:
        """Check for contradictory dietary tags."""
        if DietaryTag.VEGAN.value in tags and DietaryTag.VEGETARIAN.value not in tags:
            return "Item marked vegan should also be vegetarian"
        return None
    
    # ==================== US-A6: Menu Item Availability Scheduling ====================
    
    def set_availability_schedule(self, item_id: str, schedules: list) -> dict:
        """
        Set availability schedule for an item.
        
        Cyclomatic Complexity: >= 10
        """
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        for schedule in schedules:
            validation = self._validate_schedule(schedule)
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}
        
        conflicts = self._check_schedule_conflicts(schedules)
        if conflicts:
            return {"success": False, "error": f"Schedule conflicts: {conflicts}"}
        
        item.availability_schedule = schedules
        item.updated_at = datetime.now()
        self.storage.save_menu_item(item)
        return {"success": True, "error": None}
    
    def _validate_schedule(self, schedule: AvailabilitySchedule) -> dict:
        """Validate a single schedule entry."""
        if not isinstance(schedule.day_of_week, int) or not 0 <= schedule.day_of_week <= 6:
            return {"valid": False, "error": "Day of week must be 0-6 (Mon-Sun)"}
        if schedule.start_time >= schedule.end_time:
            return {"valid": False, "error": "Start time must be before end time"}
        return {"valid": True, "error": None}
    
    def _check_schedule_conflicts(self, schedules: list) -> str:
        """Check for overlapping time slots on same day."""
        by_day = {}
        for schedule in schedules:
            day = schedule.day_of_week
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(schedule)
        
        for day, day_schedules in by_day.items():
            sorted_schedules = sorted(day_schedules, key=lambda x: x.start_time)
            for i in range(len(sorted_schedules) - 1):
                current = sorted_schedules[i]
                next_slot = sorted_schedules[i + 1]
                if current.end_time > next_slot.start_time:
                    return f"Overlap on day {day}"
        return None
    
    def is_item_available_now(self, item_id: str) -> dict:
        """Check if item is available at current time."""
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"available": False, "reason": "Item not found"}
        if not item.is_available:
            return {"available": False, "reason": "Item is marked unavailable"}
        if item.stock_quantity <= 0:
            return {"available": False, "reason": "Item is out of stock"}
        
        if item.availability_schedule:
            now = datetime.now()
            current_day = now.weekday()
            current_time = now.time()
            
            is_scheduled_now = False
            for schedule in item.availability_schedule:
                if schedule.day_of_week == current_day:
                    if schedule.start_time <= current_time <= schedule.end_time:
                        is_scheduled_now = True
                        break
            
            if not is_scheduled_now:
                return {"available": False, "reason": "Item not available at this time"}
        
        return {"available": True, "reason": None}
    
    # ==================== US-A7: Special Offers on Items ====================
    
    def create_special_offer(self, name: str, offer_type: OfferType, value: float,
                             start_date: datetime, end_date: datetime = None,
                             max_uses_per_customer: int = 0, min_quantity: int = 1) -> dict:
        """
        Create a special offer.
        
        Cyclomatic Complexity: >= 10
        """
        # Validate offer type and value
        if offer_type == OfferType.PERCENTAGE_DISCOUNT:
            if value < 1 or value > 99:
                return {"success": False, "offer": None,
                        "error": "Percentage discount must be between 1 and 99"}
        elif offer_type == OfferType.FIXED_DISCOUNT:
            if value <= 0:
                return {"success": False, "offer": None,
                        "error": "Fixed discount must be positive"}
        elif offer_type == OfferType.BOGO:
            if min_quantity < 2:
                return {"success": False, "offer": None,
                        "error": "Buy-one-get-one requires minimum quantity of 2"}
        
        if end_date and end_date <= start_date:
            return {"success": False, "offer": None,
                    "error": "End date must be after start date"}
        
        offer = SpecialOffer(
            name=name, offer_type=offer_type, value=value,
            start_date=start_date, end_date=end_date,
            max_uses_per_customer=max_uses_per_customer,
            min_quantity=min_quantity, is_active=True
        )
        self.storage.save_special_offer(offer)
        return {"success": True, "offer": offer, "error": None}
    
    def apply_offer_to_item(self, item_id: str, offer_id: str) -> dict:
        """Apply a special offer to a menu item."""
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        offer = self.storage.get_special_offer(offer_id)
        if not offer:
            return {"success": False, "error": "Offer not found"}
        if not offer.is_active:
            return {"success": False, "error": "Offer is not active"}
        
        if offer.offer_type == OfferType.FIXED_DISCOUNT and offer.value >= item.price:
            return {"success": False, "error": "Offer discount exceeds item price"}
        
        item.special_offer_id = offer_id
        item.updated_at = datetime.now()
        self.storage.save_menu_item(item)
        return {"success": True, "error": None}
    
    def calculate_offer_price(self, item: MenuItem, quantity: int = 1,
                              customer_id: str = None) -> dict:
        """Calculate price after applying offer."""
        original_price = item.price * quantity
        
        if not item.special_offer_id:
            return {"original_price": original_price, "discounted_price": original_price,
                    "savings": 0, "offer_applied": False, "reason": "No offer on item"}
        
        offer = self.storage.get_special_offer(item.special_offer_id)
        if not offer or not offer.is_active:
            return {"original_price": original_price, "discounted_price": original_price,
                    "savings": 0, "offer_applied": False, "reason": "Offer not active"}
        
        now = datetime.now()
        if offer.start_date > now:
            return {"original_price": original_price, "discounted_price": original_price,
                    "savings": 0, "offer_applied": False, "reason": "Offer not yet started"}
        if offer.end_date and offer.end_date < now:
            return {"original_price": original_price, "discounted_price": original_price,
                    "savings": 0, "offer_applied": False, "reason": "Offer expired"}
        if quantity < offer.min_quantity:
            return {"original_price": original_price, "discounted_price": original_price,
                    "savings": 0, "offer_applied": False,
                    "reason": f"Minimum quantity {offer.min_quantity} required"}
        
        if customer_id and offer.max_uses_per_customer > 0:
            usage_count = self.storage.get_customer_offer_usage(customer_id, offer.id)
            if usage_count >= offer.max_uses_per_customer:
                return {"original_price": original_price, "discounted_price": original_price,
                        "savings": 0, "offer_applied": False, "reason": "Usage limit reached"}
        
        # Calculate discount
        if offer.offer_type == OfferType.PERCENTAGE_DISCOUNT:
            discount = original_price * (offer.value / 100)
        elif offer.offer_type == OfferType.FIXED_DISCOUNT:
            discount = offer.value * (quantity // offer.min_quantity)
        elif offer.offer_type == OfferType.BOGO:
            free_items = quantity // offer.min_quantity
            discount = item.price * free_items
        else:
            discount = 0
        
        discounted_price = max(0, original_price - discount)
        return {"original_price": round(original_price, 2),
                "discounted_price": round(discounted_price, 2),
                "savings": round(discount, 2), "offer_applied": True, "reason": None}
    
    # ==================== US-A8: Item Customization Options ====================
    
    def add_extra_option(self, item_id: str, name: str, price: float) -> dict:
        """Add an extra/addon option to a menu item."""
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "extra": None, "error": "Item not found"}
        if not name or len(name.strip()) < 2:
            return {"success": False, "extra": None,
                    "error": "Extra name must be at least 2 characters"}
        if price < 0:
            return {"success": False, "extra": None, "error": "Extra price cannot be negative"}
        if price > 50:
            return {"success": False, "extra": None, "error": "Extra price cannot exceed £50"}
        
        for extra in item.extras:
            if extra.name.lower() == name.lower().strip():
                return {"success": False, "extra": None,
                        "error": "Extra with this name already exists"}
        
        extra = ItemExtra(name=name.strip(), price=round(price, 2), is_available=True)
        item.extras.append(extra)
        item.updated_at = datetime.now()
        self.storage.save_menu_item(item)
        return {"success": True, "extra": extra, "error": None}
    
    def validate_customization(self, item_id: str, customization: ItemCustomization) -> dict:
        """Validate a customization for an item."""
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"valid": False, "errors": ["Item not found"], "final_price": 0}
        
        errors = []
        extra_cost = 0
        max_extras = 10
        
        if len(customization.extras) > max_extras:
            errors.append(f"Maximum {max_extras} extras allowed")
        
        item_extra_ids = [e.id for e in item.extras]
        for extra_id in customization.extras:
            if extra_id not in item_extra_ids:
                errors.append(f"Extra {extra_id} not available for this item")
            else:
                extra = next(e for e in item.extras if e.id == extra_id)
                if not extra.is_available:
                    errors.append(f"Extra {extra.name} is not available")
                else:
                    extra_cost += extra.price
        
        for ingredient in customization.removed_ingredients:
            if ingredient not in item.removable_ingredients:
                errors.append(f"Cannot remove {ingredient} from this item")
        
        size_adjustment = 0
        if customization.size != ItemSize.MEDIUM and item.size_prices:
            size_key = customization.size if customization.size in item.size_prices else customization.size.value
            if size_key in item.size_prices:
                size_adjustment = item.size_prices[size_key]
        
        final_price = item.price + extra_cost + size_adjustment
        
        if customization.special_instructions and len(customization.special_instructions) > 200:
            errors.append("Special instructions must be under 200 characters")
        
        return {"valid": len(errors) == 0, "errors": errors, "final_price": round(final_price, 2)}
    
    # ==================== US-A9: Menu Import/Export ====================
    
    def export_menu(self, format: str = "json", category_id: str = None) -> dict:
        """Export menu data to file format."""
        if format.lower() not in ["json", "csv"]:
            return {"success": False, "data": None, "error": "Format must be 'json' or 'csv'"}
        
        if category_id:
            items = self.storage.get_items_by_category(category_id)
        else:
            items = self.storage.get_all_menu_items()
        
        categories = self.storage.get_all_categories()
        
        if format.lower() == "json":
            data = self._export_to_json(items, categories)
        else:
            data = self._export_to_csv(items)
        
        return {"success": True, "data": data, "error": None}
    
    def _export_to_json(self, items: list, categories: list) -> str:
        """Export to JSON format."""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "categories": [{"id": c.id, "name": c.name, "description": c.description,
                           "parent_id": c.parent_id} for c in categories],
            "items": [{"id": i.id, "name": i.name, "description": i.description,
                      "price": i.price, "category_id": i.category_id,
                      "dietary_tags": [t.value if isinstance(t, DietaryTag) else t for t in i.dietary_tags],
                      "preparation_time": i.preparation_time, "stock_quantity": i.stock_quantity,
                      "is_available": i.is_available} for i in items]
        }
        return json.dumps(export_data, indent=2)
    
    def _export_to_csv(self, items: list) -> str:
        """Export items to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "name", "description", "price", "category_id",
                        "dietary_tags", "preparation_time", "stock_quantity", "is_available"])
        for item in items:
            writer.writerow([item.id, item.name, item.description, item.price,
                            item.category_id,
                            "|".join([t.value if isinstance(t, DietaryTag) else t for t in item.dietary_tags]),
                            item.preparation_time, item.stock_quantity, item.is_available])
        return output.getvalue()
    
    def import_menu(self, data: str, format: str = "json", mode: str = "merge") -> dict:
        """Import menu data from file format."""
        if format.lower() not in ["json", "csv"]:
            return {"success": False, "imported": 0, "skipped": 0, "errors": [],
                    "error": "Format must be 'json' or 'csv'"}
        if mode.lower() not in ["merge", "replace"]:
            return {"success": False, "imported": 0, "skipped": 0, "errors": [],
                    "error": "Mode must be 'merge' or 'replace'"}
        
        try:
            if format.lower() == "json":
                return self._import_from_json(data, mode)
            else:
                return self._import_from_csv(data, mode)
        except Exception as e:
            return {"success": False, "imported": 0, "skipped": 0,
                    "errors": [str(e)], "error": "Import failed"}
    
    def _import_from_json(self, data: str, mode: str) -> dict:
        """Import from JSON format."""
        try:
            import_data = json.loads(data)
        except json.JSONDecodeError as e:
            return {"success": False, "imported": 0, "skipped": 0,
                    "errors": [f"Invalid JSON: {e}"], "error": "Invalid JSON format"}
        
        imported, skipped, errors = 0, 0, []
        
        if mode == "replace":
            self.storage.clear_all_items()
            self.storage.clear_all_categories()
        
        for item_data in import_data.get("items", []):
            try:
                if mode == "merge" and self.storage.get_menu_item(item_data.get("id", "")):
                    skipped += 1
                    continue
                
                price = item_data.get("price", 0)
                if price < 0.50 or price > 500:
                    errors.append(f"Item {item_data.get('name')}: invalid price")
                    continue
                
                item = MenuItem(
                    id=item_data.get("id"), name=item_data.get("name"),
                    description=item_data.get("description", ""), price=price,
                    category_id=item_data.get("category_id"),
                    dietary_tags=item_data.get("dietary_tags", []),
                    preparation_time=item_data.get("preparation_time", 15),
                    stock_quantity=item_data.get("stock_quantity", 100),
                    is_available=item_data.get("is_available", True)
                )
                self.storage.save_menu_item(item)
                imported += 1
            except Exception as e:
                errors.append(f"Item {item_data.get('name', 'unknown')}: {e}")
        
        return {"success": imported > 0 or len(errors) == 0, "imported": imported,
                "skipped": skipped, "errors": errors, "error": None}
    
    def _import_from_csv(self, data: str, mode: str) -> dict:
        """Import items from CSV format."""
        reader = csv.DictReader(io.StringIO(data))
        imported, skipped, errors = 0, 0, []
        
        if mode == "replace":
            self.storage.clear_all_items()
        
        for row in reader:
            try:
                if mode == "merge" and row.get("id") and self.storage.get_menu_item(row["id"]):
                    skipped += 1
                    continue
                
                price = float(row.get("price", 0))
                if price < 0.50 or price > 500:
                    errors.append(f"Row {reader.line_num}: invalid price")
                    continue
                
                dietary_tags = row.get("dietary_tags", "").split("|") if row.get("dietary_tags") else []
                
                item = MenuItem(
                    id=row.get("id"), name=row.get("name", ""),
                    description=row.get("description", ""), price=price,
                    category_id=row.get("category_id", ""), dietary_tags=dietary_tags,
                    preparation_time=int(row.get("preparation_time", 15)),
                    stock_quantity=int(row.get("stock_quantity", 100)),
                    is_available=row.get("is_available", "True").lower() == "true"
                )
                self.storage.save_menu_item(item)
                imported += 1
            except Exception as e:
                errors.append(f"Row {reader.line_num}: {e}")
        
        return {"success": imported > 0, "imported": imported, "skipped": skipped,
                "errors": errors, "error": None}
