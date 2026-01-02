"""
Storage Module - Data Persistence Layer
Handles serialized file storage for all entities.
"""

import json
import os
from datetime import datetime, date
from typing import Optional, List
from models import (
    MenuItem, Category, Customer, Order, Cart, DiscountCode,
    SpecialOffer, Refund, OrderStatus
)


class Storage:
    """
    File-based storage for the Takeaway Menu System.
    Uses JSON serialization for data persistence.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_directories()
        
        # In-memory caches
        self._menu_items = {}
        self._categories = {}
        self._customers = {}
        self._orders = {}
        self._carts = {}
        self._discount_codes = {}
        self._special_offers = {}
        self._refunds = {}
        self._sessions = {}
        self._reset_tokens = {}
        self._blocked_emails = {}
        self._item_change_logs = {}
        self._stock_adjustments = {}
        self._login_logs = {}
        self._cancellation_logs = {}
        
        # Load existing data
        self._load_all_data()
    
    def _ensure_directories(self):
        """Ensure data directories exist."""
        dirs = [
            self.data_dir,
            os.path.join(self.data_dir, "menu"),
            os.path.join(self.data_dir, "customers"),
            os.path.join(self.data_dir, "orders"),
            os.path.join(self.data_dir, "logs")
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def _load_all_data(self):
        """Load all data from files."""
        self._load_menu_items()
        self._load_categories()
        self._load_customers()
        self._load_orders()
        self._load_carts()
        self._load_discount_codes()
    
    def _serialize_datetime(self, obj):
        """JSON serializer for datetime objects."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def _save_to_file(self, filename: str, data: dict):
        """Save data to JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, default=self._serialize_datetime, indent=2)
    
    def _load_from_file(self, filename: str) -> dict:
        """Load data from JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    # ==================== Menu Items ====================
    
    def save_menu_item(self, item: MenuItem):
        """Save or update a menu item."""
        self._menu_items[item.id] = item
        self._persist_menu_items()
    
    def get_menu_item(self, item_id: str) -> Optional[MenuItem]:
        """Get a menu item by ID."""
        return self._menu_items.get(item_id)
    
    def get_all_menu_items(self) -> List[MenuItem]:
        """Get all menu items."""
        return list(self._menu_items.values())
    
    def get_items_by_category(self, category_id: str) -> List[MenuItem]:
        """Get all items in a category."""
        return [i for i in self._menu_items.values() if i.category_id == category_id]
    
    def delete_menu_item(self, item_id: str):
        """Delete a menu item."""
        if item_id in self._menu_items:
            del self._menu_items[item_id]
            self._persist_menu_items()
    
    def clear_all_items(self):
        """Clear all menu items."""
        self._menu_items = {}
        self._persist_menu_items()
    
    def _load_menu_items(self):
        """Load menu items from file."""
        # Implementation for loading - simplified for now
        pass
    
    def _persist_menu_items(self):
        """Persist menu items to file."""
        data = {k: self._item_to_dict(v) for k, v in self._menu_items.items()}
        self._save_to_file("menu/items.json", data)
    
    def _item_to_dict(self, item: MenuItem) -> dict:
        """Convert MenuItem to dictionary."""
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "category_id": item.category_id,
            "dietary_tags": [t.value if hasattr(t, 'value') else t for t in item.dietary_tags],
            "preparation_time": item.preparation_time,
            "stock_quantity": item.stock_quantity,
            "is_available": item.is_available,
            "created_at": item.created_at,
            "updated_at": item.updated_at
        }
    
    # ==================== Categories ====================
    
    def save_category(self, category: Category):
        """Save or update a category."""
        self._categories[category.id] = category
        self._persist_categories()
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID."""
        return self._categories.get(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        return list(self._categories.values())
    
    def get_categories_by_parent(self, parent_id: str = None) -> List[Category]:
        """Get categories by parent ID."""
        return [c for c in self._categories.values() if c.parent_id == parent_id]
    
    def get_subcategories(self, parent_id: str) -> List[Category]:
        """Get subcategories of a category."""
        return self.get_categories_by_parent(parent_id)
    
    def delete_category(self, category_id: str):
        """Delete a category."""
        if category_id in self._categories:
            del self._categories[category_id]
            self._persist_categories()
    
    def clear_all_categories(self):
        """Clear all categories."""
        self._categories = {}
        self._persist_categories()
    
    def _load_categories(self):
        pass
    
    def _persist_categories(self):
        data = {k: {"id": v.id, "name": v.name, "description": v.description,
                    "parent_id": v.parent_id} for k, v in self._categories.items()}
        self._save_to_file("menu/categories.json", data)
    
    # ==================== Customers ====================
    
    def save_customer(self, customer: Customer):
        """Save or update a customer."""
        self._customers[customer.id] = customer
        self._persist_customers()
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get a customer by ID."""
        return self._customers.get(customer_id)
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get a customer by email."""
        email = email.lower().strip()
        for c in self._customers.values():
            if c.email.lower() == email:
                return c
        return None
    
    def get_customer_order_count(self, customer_id: str) -> int:
        """Get number of orders for a customer."""
        return len([o for o in self._orders.values() if o.customer_id == customer_id])
    
    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get all orders for a customer."""
        return [o for o in self._orders.values() if o.customer_id == customer_id]
    
    def get_active_orders(self, customer_id: str) -> List[Order]:
        """Get active (non-completed) orders."""
        active_statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, 
                         OrderStatus.PREPARING, OrderStatus.READY, 
                         OrderStatus.OUT_FOR_DELIVERY]
        return [o for o in self._orders.values() 
                if o.customer_id == customer_id and o.status in active_statuses]
    
    def _load_customers(self):
        pass
    
    def _persist_customers(self):
        # Simplified - would serialize customer objects
        pass
    
    # ==================== Orders ====================
    
    def save_order(self, order: Order):
        """Save or update an order."""
        self._orders[order.id] = order
        self._persist_orders()
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        return self._orders.get(order_id)
    
    def get_orders_in_range(self, start_date: date, end_date: date) -> List[Order]:
        """Get orders within a date range."""
        return [o for o in self._orders.values() 
                if start_date <= o.created_at.date() <= end_date]
    
    def _load_orders(self):
        pass
    
    def _persist_orders(self):
        pass
    
    # ==================== Carts ====================
    
    def save_cart(self, cart: Cart):
        """Save or update a cart."""
        self._carts[cart.id] = cart
    
    def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Get a cart by ID."""
        return self._carts.get(cart_id)
    
    def delete_cart(self, cart_id: str):
        """Delete a cart."""
        if cart_id in self._carts:
            del self._carts[cart_id]
    
    def _load_carts(self):
        pass
    
    # ==================== Discount Codes ====================
    
    def save_discount_code(self, code: DiscountCode):
        """Save or update a discount code."""
        self._discount_codes[code.code] = code
    
    def get_discount_code(self, code: str) -> Optional[DiscountCode]:
        """Get a discount code."""
        return self._discount_codes.get(code.upper())
    
    def has_customer_used_code(self, customer_id: str, code: str) -> bool:
        """Check if customer has used a discount code."""
        for order in self._orders.values():
            if order.customer_id == customer_id and order.discount_code_used == code.upper():
                return True
        return False
    
    def _load_discount_codes(self):
        pass
    
    # ==================== Special Offers ====================
    
    def save_special_offer(self, offer: SpecialOffer):
        """Save or update a special offer."""
        self._special_offers[offer.id] = offer
    
    def get_special_offer(self, offer_id: str) -> Optional[SpecialOffer]:
        """Get a special offer by ID."""
        return self._special_offers.get(offer_id)
    
    def get_customer_offer_usage(self, customer_id: str, offer_id: str) -> int:
        """Get how many times customer has used an offer."""
        count = 0
        for order in self._orders.values():
            if order.customer_id == customer_id:
                for item in order.items:
                    menu_item = self.get_menu_item(item.menu_item_id)
                    if menu_item and menu_item.special_offer_id == offer_id:
                        count += 1
        return count
    
    # ==================== Refunds ====================
    
    def save_refund(self, refund: Refund):
        """Save a refund."""
        if refund.order_id not in self._refunds:
            self._refunds[refund.order_id] = []
        self._refunds[refund.order_id].append(refund)
    
    def get_order_refunds(self, order_id: str) -> List[Refund]:
        """Get all refunds for an order."""
        return self._refunds.get(order_id, [])
    
    # ==================== Sessions ====================
    
    def create_session(self, customer_id: str, token: str, expires_at: datetime):
        """Create a new session."""
        self._sessions[token] = {
            "customer_id": customer_id,
            "expires_at": expires_at
        }
    
    def get_session(self, token: str) -> Optional[dict]:
        """Get a session by token."""
        return self._sessions.get(token)
    
    def invalidate_session(self, token: str):
        """Invalidate a session."""
        if token in self._sessions:
            del self._sessions[token]
    
    # ==================== Password Reset ====================
    
    def save_reset_token(self, token):
        """Save a password reset token."""
        self._reset_tokens[token.token] = token
    
    def get_reset_token(self, token: str):
        """Get a reset token."""
        return self._reset_tokens.get(token)
    
    def get_recent_reset_requests(self, customer_id: str, hours: int = 1) -> list:
        """Get recent reset requests for a customer."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [t for t in self._reset_tokens.values() 
                if t.customer_id == customer_id and t.created_at > cutoff]
    
    def invalidate_reset_tokens(self, customer_id: str):
        """Invalidate all reset tokens for a customer."""
        self._reset_tokens = {k: v for k, v in self._reset_tokens.items() 
                             if v.customer_id != customer_id}
    
    # ==================== Email Blocking ====================
    
    def block_email(self, email: str, until: datetime):
        """Block an email from registration."""
        self._blocked_emails[email.lower()] = {"blocked_until": until}
    
    def get_blocked_email(self, email: str) -> Optional[dict]:
        """Check if email is blocked."""
        return self._blocked_emails.get(email.lower())
    
    def unblock_email(self, email: str):
        """Unblock an email."""
        if email.lower() in self._blocked_emails:
            del self._blocked_emails[email.lower()]
    
    # ==================== Logging ====================
    
    def log_item_changes(self, item_id: str, changes: list):
        """Log changes to a menu item."""
        if item_id not in self._item_change_logs:
            self._item_change_logs[item_id] = []
        self._item_change_logs[item_id].append({
            "timestamp": datetime.now(),
            "changes": changes
        })
    
    def log_stock_adjustment(self, item_id: str, change: int, reason: str):
        """Log a stock adjustment."""
        if item_id not in self._stock_adjustments:
            self._stock_adjustments[item_id] = []
        self._stock_adjustments[item_id].append({
            "timestamp": datetime.now(),
            "change": change,
            "reason": reason
        })
    
    def log_login(self, customer_id: str, timestamp: datetime, is_suspicious: bool):
        """Log a login attempt."""
        if customer_id not in self._login_logs:
            self._login_logs[customer_id] = []
        self._login_logs[customer_id].append({
            "timestamp": timestamp,
            "suspicious": is_suspicious
        })
    
    def get_recent_logins(self, customer_id: str, limit: int = 10) -> list:
        """Get recent login logs."""
        logs = self._login_logs.get(customer_id, [])
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def log_cancellation(self, order_id: str, customer_id: str, reason: str):
        """Log an order cancellation."""
        if customer_id not in self._cancellation_logs:
            self._cancellation_logs[customer_id] = []
        self._cancellation_logs[customer_id].append({
            "order_id": order_id,
            "timestamp": datetime.now(),
            "reason": reason
        })
    
    def get_customer_cancellations(self, customer_id: str, days: int = 30) -> list:
        """Get recent cancellations for a customer."""
        cutoff = datetime.now() - timedelta(days=days)
        logs = self._cancellation_logs.get(customer_id, [])
        return [l for l in logs if l["timestamp"] > cutoff]
    
    # ==================== Stock Management ====================
    
    def reserve_stock(self, item_id: str, quantity: int):
        """Reserve stock for an order."""
        item = self.get_menu_item(item_id)
        if item:
            item.stock_quantity -= quantity
            if item.stock_quantity <= 0:
                item.is_available = False
            self.save_menu_item(item)
    
    def release_stock(self, item_id: str, quantity: int):
        """Release reserved stock (e.g., on cancellation)."""
        item = self.get_menu_item(item_id)
        if item:
            item.stock_quantity += quantity
            self.save_menu_item(item)
    
    # ==================== Account Deletion ====================
    
    def schedule_deletion(self, customer_id: str, delete_at: datetime):
        """Schedule account deletion."""
        customer = self.get_customer(customer_id)
        if customer:
            customer._scheduled_deletion = delete_at
            self.save_customer(customer)
    
    def get_scheduled_deletion(self, customer_id: str) -> Optional[dict]:
        """Get scheduled deletion info."""
        customer = self.get_customer(customer_id)
        if customer and hasattr(customer, '_scheduled_deletion'):
            return {"delete_at": customer._scheduled_deletion}
        return None
    
    def cancel_deletion(self, customer_id: str):
        """Cancel scheduled deletion."""
        customer = self.get_customer(customer_id)
        if customer and hasattr(customer, '_scheduled_deletion'):
            delattr(customer, '_scheduled_deletion')
            self.save_customer(customer)
    
    def anonymize_customer_orders(self, customer_id: str):
        """Anonymize orders for deleted customer."""
        for order in self._orders.values():
            if order.customer_id == customer_id:
                order.customer_id = "DELETED_USER"
                self.save_order(order)
    
    # ==================== Notifications ====================
    
    def create_notification(self, customer_id: str, message: str):
        """Create a notification for a customer."""
        # Would integrate with notification system
        print(f"Notification for {customer_id}: {message}")


# Singleton instance
_storage_instance = None

def get_storage(data_dir: str = "data") -> Storage:
    """Get the storage singleton."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = Storage(data_dir)
    return _storage_instance
