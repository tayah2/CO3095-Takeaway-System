"""
Customer Management Module - Member B
User Stories: US-B1 to US-B9
"""

import re
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from models import (
    Customer, Address, LoyaltyPoints, PointTransaction, PasswordResetToken,
    DietaryTag, DeliveryZone
)


class CustomerManager:
    """Manages customer accounts and related operations."""
    
    def __init__(self, storage):
        self.storage = storage
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOCKOUT_DURATION_MINUTES = 30
        self.MAX_ADDRESSES = 5
        self.MIN_POINTS_TO_REDEEM = 500
        self.MAX_FAVORITES = 50
    
    # ==================== US-B1: Customer Registration ====================
    
    def register_customer(self, email: str, password: str, first_name: str,
                          last_name: str, phone: str, date_of_birth: date = None,
                          terms_accepted: bool = False) -> dict:
        """Register with comprehensive validation. Complexity >= 10."""
        # Validate email
        email_validation = self._validate_email(email)
        if not email_validation["valid"]:
            return {"success": False, "customer": None, "error": email_validation["error"]}
        
        if self.storage.get_customer_by_email(email.lower().strip()):
            return {"success": False, "customer": None, "error": "Email already registered"}
        
        # Validate password
        pwd_validation = self._validate_password(password)
        if not pwd_validation["valid"]:
            return {"success": False, "customer": None, "error": pwd_validation["error"]}
        
        # Validate phone
        phone_validation = self._validate_phone(phone)
        if not phone_validation["valid"]:
            return {"success": False, "customer": None, "error": phone_validation["error"]}
        
        # Validate names
        if not first_name or len(first_name.strip()) < 2 or len(first_name) > 50:
            return {"success": False, "customer": None, "error": "Invalid first name"}
        if not last_name or len(last_name.strip()) < 2 or len(last_name) > 50:
            return {"success": False, "customer": None, "error": "Invalid last name"}
        
        # Validate age
        if date_of_birth:
            age = (date.today() - date_of_birth).days // 365
            if age < 16:
                return {"success": False, "customer": None, "error": "Must be at least 16"}
        
        if not terms_accepted:
            return {"success": False, "customer": None, "error": "Must accept terms"}
        
        customer = Customer(
            email=email.lower().strip(),
            password_hash=self._hash_password(password),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=self._format_phone(phone),
            date_of_birth=date_of_birth,
            terms_accepted_at=datetime.now(),
            loyalty_points=LoyaltyPoints()
        )
        self.storage.save_customer(customer)
        return {"success": True, "customer": customer, "error": None}
    
    def _validate_email(self, email: str) -> dict:
        if not email:
            return {"valid": False, "error": "Email required"}
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email.strip()):
            return {"valid": False, "error": "Invalid email format"}
        disposable = ['tempmail.com', 'throwaway.com', 'mailinator.com']
        if email.split('@')[1] in disposable:
            return {"valid": False, "error": "Disposable emails not allowed"}
        return {"valid": True, "error": None}
    
    def _validate_password(self, password: str) -> dict:
        if not password or len(password) < 8:
            return {"valid": False, "error": "Password must be 8+ characters"}
        if not re.search(r'[A-Z]', password):
            return {"valid": False, "error": "Need uppercase letter"}
        if not re.search(r'[a-z]', password):
            return {"valid": False, "error": "Need lowercase letter"}
        if not re.search(r'\d', password):
            return {"valid": False, "error": "Need number"}
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return {"valid": False, "error": "Need special character"}
        return {"valid": True, "error": None}
    
    def _validate_phone(self, phone: str) -> dict:
        if not phone:
            return {"valid": False, "error": "Phone required"}
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        if not re.match(r'^(\+44|0044|0)7\d{9}$', phone):
            return {"valid": False, "error": "Invalid UK phone"}
        return {"valid": True, "error": None}
    
    def _hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        try:
            salt, stored = password_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == stored
        except:
            return False
    
    def _format_phone(self, phone: str) -> str:
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        if phone.startswith('0'):
            phone = '+44' + phone[1:]
        return phone
    
    # ==================== US-B2: Customer Login ====================
    
    def login(self, email: str, password: str, remember_me: bool = False) -> dict:
        """Authenticate with security measures. Complexity >= 10."""
        if not email or not password:
            return {"success": False, "customer": None, "error": "Credentials required"}
        
        customer = self.storage.get_customer_by_email(email.lower().strip())
        if not customer:
            return {"success": False, "customer": None, "error": "Invalid credentials"}
        
        if not customer.is_active:
            return {"success": False, "customer": None, "error": "Account deactivated"}
        
        # Check lockout
        if customer.locked_until and customer.locked_until > datetime.now():
            mins = (customer.locked_until - datetime.now()).seconds // 60
            return {"success": False, "customer": None, "error": f"Locked for {mins} min"}
        
        if not self._verify_password(password, customer.password_hash):
            customer.failed_login_attempts += 1
            if customer.failed_login_attempts >= self.MAX_LOGIN_ATTEMPTS:
                customer.locked_until = datetime.now() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
            self.storage.save_customer(customer)
            return {"success": False, "customer": None, "error": "Invalid credentials"}
        
        # Success
        customer.failed_login_attempts = 0
        customer.locked_until = None
        customer.last_login = datetime.now()
        token = secrets.token_urlsafe(32)
        self.storage.save_customer(customer)
        return {"success": True, "customer": customer, "session_token": token, "error": None}
    
    def logout(self, session_token: str) -> dict:
        self.storage.invalidate_session(session_token)
        return {"success": True, "error": None}
    
    # ==================== US-B3: Manage Delivery Addresses ====================
    
    def add_address(self, customer_id: str, line1: str, line2: str, city: str,
                    postcode: str, is_default: bool = False) -> dict:
        """Add delivery address. Complexity >= 10."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "address": None, "error": "Customer not found"}
        
        if len(customer.addresses) >= self.MAX_ADDRESSES:
            return {"success": False, "address": None, "error": f"Max {self.MAX_ADDRESSES} addresses"}
        
        if not line1 or len(line1.strip()) < 5:
            return {"success": False, "address": None, "error": "Address line 1 required"}
        if not city or len(city.strip()) < 2:
            return {"success": False, "address": None, "error": "City required"}
        
        # Validate postcode
        postcode_clean = postcode.upper().replace(' ', '')
        if not re.match(r'^[A-Z]{1,2}[0-9][0-9A-Z]?[0-9][A-Z]{2}$', postcode_clean):
            return {"success": False, "address": None, "error": "Invalid UK postcode"}
        
        # Check delivery zone
        zone = self._get_delivery_zone(postcode_clean)
        if zone == DeliveryZone.OUT_OF_RANGE:
            return {"success": False, "address": None, "error": "Outside delivery area"}
        
        # Check duplicate
        formatted_pc = postcode_clean[:-3] + ' ' + postcode_clean[-3:]
        for addr in customer.addresses:
            if addr.postcode == formatted_pc and addr.line1.lower() == line1.lower().strip():
                return {"success": False, "address": None, "error": "Address exists"}
        
        address = Address(
            line1=line1.strip(), line2=line2.strip() if line2 else "",
            city=city.strip(), postcode=formatted_pc, delivery_zone=zone, is_default=is_default
        )
        
        if is_default:
            for a in customer.addresses:
                a.is_default = False
        elif not customer.addresses:
            address.is_default = True
        
        customer.addresses.append(address)
        self.storage.save_customer(customer)
        return {"success": True, "address": address, "error": None}
    
    def update_address(self, customer_id: str, address_id: str, **updates) -> dict:
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        address = next((a for a in customer.addresses if a.id == address_id), None)
        if not address:
            return {"success": False, "error": "Address not found"}
        
        for key, value in updates.items():
            if hasattr(address, key):
                setattr(address, key, value)
        
        self.storage.save_customer(customer)
        return {"success": True, "address": address, "error": None}
    
    def delete_address(self, customer_id: str, address_id: str) -> dict:
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        customer.addresses = [a for a in customer.addresses if a.id != address_id]
        if customer.addresses and not any(a.is_default for a in customer.addresses):
            customer.addresses[0].is_default = True
        
        self.storage.save_customer(customer)
        return {"success": True, "error": None}
    
    def _get_delivery_zone(self, postcode: str) -> DeliveryZone:
        if postcode.startswith('LE1') or postcode.startswith('LE2'):
            return DeliveryZone.ZONE_1
        elif postcode.startswith('LE'):
            return DeliveryZone.ZONE_2
        elif postcode.startswith(('NG', 'DE', 'CV')):
            return DeliveryZone.ZONE_3
        return DeliveryZone.OUT_OF_RANGE
    
    # ==================== US-B4: Profile Management ====================
    
    def update_profile(self, customer_id: str, current_password: str = None, **updates) -> dict:
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        if "first_name" in updates:
            if len(updates["first_name"].strip()) < 2:
                return {"success": False, "error": "Invalid first name"}
            customer.first_name = updates["first_name"].strip()
        
        if "last_name" in updates:
            if len(updates["last_name"].strip()) < 2:
                return {"success": False, "error": "Invalid last name"}
            customer.last_name = updates["last_name"].strip()
        
        if "new_password" in updates:
            if not current_password or not self._verify_password(current_password, customer.password_hash):
                return {"success": False, "error": "Current password incorrect"}
            validation = self._validate_password(updates["new_password"])
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}
            customer.password_hash = self._hash_password(updates["new_password"])
        
        if "dietary_preferences" in updates:
            customer.dietary_preferences = updates["dietary_preferences"]
        
        customer.updated_at = datetime.now()
        self.storage.save_customer(customer)
        return {"success": True, "customer": customer, "error": None}
    
    # ==================== US-B5: Loyalty Points ====================
    
    def earn_points(self, customer_id: str, order_amount: float, order_id: str,
                    bonus_multiplier: float = 1.0) -> dict:
        """Award loyalty points. Complexity >= 10."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "points_earned": 0, "error": "Customer not found"}
        if order_amount <= 0:
            return {"success": False, "points_earned": 0, "error": "Invalid amount"}
        
        base_points = int(order_amount)
        total_points = int(base_points * bonus_multiplier)
        
        # First order bonus
        if self.storage.get_customer_order_count(customer_id) == 0:
            total_points += 100
        
        # Birthday bonus
        if customer.date_of_birth:
            today = date.today()
            if customer.date_of_birth.month == today.month and customer.date_of_birth.day == today.day:
                total_points *= 2
        
        transaction = PointTransaction(
            points=total_points, reason=f"Order #{order_id}", order_id=order_id,
            expires_at=datetime.now() + timedelta(days=365)
        )
        customer.loyalty_points.total_points += total_points
        customer.loyalty_points.lifetime_earned += total_points
        customer.loyalty_points.points_history.append(transaction)
        self.storage.save_customer(customer)
        return {"success": True, "points_earned": total_points, "error": None}
    
    def redeem_points(self, customer_id: str, points: int, order_total: float) -> dict:
        """Redeem points for discount. Complexity >= 10."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "discount": 0, "error": "Customer not found"}
        if points < self.MIN_POINTS_TO_REDEEM:
            return {"success": False, "discount": 0, "error": f"Min {self.MIN_POINTS_TO_REDEEM} points"}
        if customer.loyalty_points.total_points < points:
            return {"success": False, "discount": 0, "error": "Insufficient points"}
        
        discount = points * 0.01  # 1p per point
        max_discount = order_total * 0.5  # 50% max
        if discount > max_discount:
            points = int(max_discount / 0.01)
            discount = max_discount
        
        customer.loyalty_points.total_points -= points
        customer.loyalty_points.lifetime_redeemed += points
        customer.loyalty_points.points_history.append(
            PointTransaction(points=-points, reason="Redemption")
        )
        self.storage.save_customer(customer)
        return {"success": True, "discount": round(discount, 2), "points_redeemed": points, "error": None}
    
    def restore_points(self, customer_id: str, points: int, order_id: str) -> dict:
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        customer.loyalty_points.total_points += points
        customer.loyalty_points.points_history.append(
            PointTransaction(points=points, reason=f"Refund #{order_id}", order_id=order_id)
        )
        self.storage.save_customer(customer)
        return {"success": True, "error": None}
    
    # ==================== US-B6: Password Reset ====================
    
    def request_password_reset(self, email: str) -> dict:
        """Request password reset. Complexity >= 10."""
        customer = self.storage.get_customer_by_email(email.lower().strip())
        if not customer:
            return {"success": True, "error": None}  # Don't reveal if email exists
        
        # Rate limit
        recent = self.storage.get_recent_reset_requests(customer.id, hours=1)
        if len(recent) >= 3:
            return {"success": False, "error": "Too many requests. Try later"}
        
        # Invalidate existing tokens
        self.storage.invalidate_reset_tokens(customer.id)
        
        token = PasswordResetToken(
            customer_id=customer.id,
            expires_at=datetime.now() + timedelta(hours=1)
        )
        self.storage.save_reset_token(token)
        return {"success": True, "token": token.token, "error": None}
    
    def reset_password(self, token: str, new_password: str) -> dict:
        """Reset password with token. Complexity >= 10."""
        reset_token = self.storage.get_reset_token(token)
        if not reset_token:
            return {"success": False, "error": "Invalid token"}
        if reset_token.is_used:
            return {"success": False, "error": "Token already used"}
        if reset_token.expires_at < datetime.now():
            return {"success": False, "error": "Token expired"}
        
        validation = self._validate_password(new_password)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}
        
        customer = self.storage.get_customer(reset_token.customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        customer.password_hash = self._hash_password(new_password)
        reset_token.is_used = True
        self.storage.save_customer(customer)
        self.storage.save_reset_token(reset_token)
        return {"success": True, "error": None}
    
    # ==================== US-B7: Order History ====================
    
    def get_order_history(self, customer_id: str, page: int = 1, page_size: int = 10,
                          status_filter: str = None, date_from: date = None,
                          date_to: date = None, sort_by: str = "date") -> dict:
        """Get paginated order history. Complexity >= 10."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "orders": [], "error": "Customer not found"}
        
        orders = self.storage.get_customer_orders(customer_id)
        
        # Apply filters
        if status_filter:
            orders = [o for o in orders if o.status.value == status_filter]
        if date_from:
            orders = [o for o in orders if o.created_at.date() >= date_from]
        if date_to:
            orders = [o for o in orders if o.created_at.date() <= date_to]
        
        # Sort
        if sort_by == "date":
            orders.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "amount":
            orders.sort(key=lambda x: x.total, reverse=True)
        
        # Paginate
        total = len(orders)
        start = (page - 1) * page_size
        orders = orders[start:start + page_size]
        
        # Calculate total spent
        all_orders = self.storage.get_customer_orders(customer_id)
        total_spent = sum(o.total for o in all_orders if o.status.value == "delivered")
        
        return {
            "success": True, "orders": orders, "total": total,
            "total_pages": (total + page_size - 1) // page_size,
            "total_spent": round(total_spent, 2), "error": None
        }
    
    # ==================== US-B8: Favorite Items ====================
    
    def add_favorite(self, customer_id: str, item_id: str) -> dict:
        """Add item to favorites. Complexity >= 10."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        if len(customer.favorite_items) >= self.MAX_FAVORITES:
            return {"success": False, "error": f"Max {self.MAX_FAVORITES} favorites"}
        
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "error": "Item not found"}
        
        if item_id in customer.favorite_items:
            return {"success": False, "error": "Already in favorites"}
        
        customer.favorite_items.append(item_id)
        self.storage.save_customer(customer)
        return {"success": True, "error": None}
    
    def remove_favorite(self, customer_id: str, item_id: str) -> dict:
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        customer.favorite_items = [i for i in customer.favorite_items if i != item_id]
        self.storage.save_customer(customer)
        return {"success": True, "error": None}
    
    def get_favorites(self, customer_id: str) -> dict:
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "items": [], "error": "Customer not found"}
        
        items = []
        for item_id in customer.favorite_items:
            item = self.storage.get_menu_item(item_id)
            if item:
                items.append({"item": item, "available": item.is_available})
        
        return {"success": True, "items": items, "error": None}
    
    # ==================== US-B9: Account Deletion ====================
    
    def delete_account(self, customer_id: str, password: str, reason: str = "") -> dict:
        """Delete customer account. Complexity >= 10."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        if not self._verify_password(password, customer.password_hash):
            return {"success": False, "error": "Password incorrect"}
        
        # Check active orders
        active_orders = self.storage.get_active_orders(customer_id)
        if active_orders:
            return {"success": False, "error": "Cannot delete with active orders"}
        
        # Handle pending points
        if customer.loyalty_points.total_points > 0:
            customer.loyalty_points.points_history.append(
                PointTransaction(points=-customer.loyalty_points.total_points,
                                reason="Account deletion")
            )
        
        # Schedule deletion
        customer.is_active = False
        customer.updated_at = datetime.now()
        
        # Block email reuse
        self.storage.block_email(
            customer.email,
            datetime.now() + timedelta(days=90)
        )
        
        # Anonymize orders
        self.storage.anonymize_customer_orders(customer_id)
        
        # Schedule permanent deletion
        self.storage.schedule_deletion(customer_id, datetime.now() + timedelta(days=30))
        
        self.storage.save_customer(customer)
        return {"success": True, "grace_period_days": 30, "error": None}
    
    def recover_account(self, customer_id: str, password: str) -> dict:
        """Recover account within grace period."""
        customer = self.storage.get_customer(customer_id)
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        if customer.is_active:
            return {"success": False, "error": "Account is already active"}
        
        if not self._verify_password(password, customer.password_hash):
            return {"success": False, "error": "Password incorrect"}
        
        deletion = self.storage.get_scheduled_deletion(customer_id)
        if not deletion or deletion["delete_at"] < datetime.now():
            return {"success": False, "error": "Recovery period expired"}
        
        customer.is_active = True
        self.storage.cancel_deletion(customer_id)
        self.storage.unblock_email(customer.email)
        self.storage.save_customer(customer)
        return {"success": True, "error": None}
