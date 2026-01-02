"""
Order Management Module - Member C
User Stories: US-C1 to US-C9
"""

from datetime import datetime, timedelta
from typing import Optional, List
from models import (
    Cart, CartItem, Order, OrderStatus, OrderStatusHistory,
    ItemCustomization, MenuItem, Address
)


class OrderManager:
    """Manages shopping cart and order operations."""
    
    def __init__(self, storage):
        self.storage = storage
        self.MAX_CART_ITEMS = 50
        self.MAX_ITEM_QUANTITY = 99
        self.MIN_ORDER_AMOUNT = 10.00
        self.VAT_RATE = 0.20
        self.MAX_CANCELLATIONS_PER_MONTH = 3
    
    # ==================== US-C1: Add Items to Cart ====================
    
    def add_to_cart(self, cart_id: str, item_id: str, quantity: int = 1,
                    customization: ItemCustomization = None, notes: str = "") -> dict:
        """
        Add item to cart with validation. Complexity >= 10.
        """
        # Get or create cart
        cart = self.storage.get_cart(cart_id)
        if not cart:
            cart = Cart(id=cart_id)
        
        # Check cart size limit
        total_items = sum(ci.quantity for ci in cart.items)
        if total_items + quantity > self.MAX_CART_ITEMS:
            return {"success": False, "cart": None, "error": f"Max {self.MAX_CART_ITEMS} items"}
        
        # Validate quantity
        if quantity < 1 or quantity > self.MAX_ITEM_QUANTITY:
            return {"success": False, "cart": None, "error": "Invalid quantity (1-99)"}
        
        # Get and validate menu item
        item = self.storage.get_menu_item(item_id)
        if not item:
            return {"success": False, "cart": None, "error": "Item not found"}
        
        if not item.is_available:
            return {"success": False, "cart": None, "error": "Item not available"}
        
        if item.stock_quantity < quantity:
            return {"success": False, "cart": None, 
                    "error": f"Only {item.stock_quantity} in stock"}
        
        # Check item still available (price/status may have changed)
        availability = self._check_item_availability(item)
        if not availability["available"]:
            return {"success": False, "cart": None, "error": availability["reason"]}
        
        # Calculate price with customization
        unit_price = self._calculate_item_price(item, customization)
        line_total = unit_price * quantity
        
        # Check if item already in cart (update quantity)
        existing = next((ci for ci in cart.items if ci.menu_item_id == item_id 
                        and self._same_customization(ci.customization, customization)), None)
        
        if existing:
            new_qty = existing.quantity + quantity
            if new_qty > self.MAX_ITEM_QUANTITY:
                return {"success": False, "cart": None, "error": "Max quantity exceeded"}
            existing.quantity = new_qty
            existing.line_total = unit_price * new_qty
        else:
            cart_item = CartItem(
                menu_item_id=item_id,
                quantity=quantity,
                customization=customization or ItemCustomization(),
                unit_price=unit_price,
                line_total=line_total,
                notes=notes[:200] if notes else ""
            )
            cart.items.append(cart_item)
        
        # Recalculate totals
        self._recalculate_cart(cart)
        cart.updated_at = datetime.now()
        self.storage.save_cart(cart)
        
        return {"success": True, "cart": cart, "error": None}
    
    def _check_item_availability(self, item: MenuItem) -> dict:
        if not item.is_available:
            return {"available": False, "reason": "Item unavailable"}
        if item.stock_quantity <= 0:
            return {"available": False, "reason": "Out of stock"}
        
        # Check schedule if exists
        if item.availability_schedule:
            now = datetime.now()
            day = now.weekday()
            current_time = now.time()
            scheduled = any(
                s.day_of_week == day and s.start_time <= current_time <= s.end_time
                for s in item.availability_schedule
            )
            if not scheduled:
                return {"available": False, "reason": "Not available at this time"}
        
        return {"available": True, "reason": None}
    
    def _calculate_item_price(self, item: MenuItem, customization: ItemCustomization) -> float:
        price = item.price
        
        if customization:
            # Add extras
            for extra_id in customization.extras:
                extra = next((e for e in item.extras if e.id == extra_id), None)
                if extra:
                    price += extra.price
            
            # Size adjustment
            if customization.size and item.size_prices:
                size_key = customization.size.value if hasattr(customization.size, 'value') else customization.size
                if size_key in item.size_prices:
                    price += item.size_prices[size_key]
        
        return round(price, 2)
    
    def _same_customization(self, c1: ItemCustomization, c2: ItemCustomization) -> bool:
        if c1 is None and c2 is None:
            return True
        if c1 is None or c2 is None:
            return False
        return (set(c1.extras) == set(c2.extras) and
                set(c1.removed_ingredients) == set(c2.removed_ingredients) and
                c1.size == c2.size and c1.spice_level == c2.spice_level)
    
    # ==================== US-C2: Manage Cart Contents ====================
    
    def update_cart_item(self, cart_id: str, cart_item_id: str, 
                         quantity: int = None, notes: str = None) -> dict:
        """Update cart item quantity or notes. Complexity >= 10."""
        cart = self.storage.get_cart(cart_id)
        if not cart:
            return {"success": False, "cart": None, "error": "Cart not found"}
        
        cart_item = next((ci for ci in cart.items if ci.id == cart_item_id), None)
        if not cart_item:
            return {"success": False, "cart": None, "error": "Item not in cart"}
        
        if quantity is not None:
            if quantity < 1 or quantity > self.MAX_ITEM_QUANTITY:
                return {"success": False, "cart": None, "error": "Invalid quantity"}
            
            # Check stock availability
            item = self.storage.get_menu_item(cart_item.menu_item_id)
            if item and item.stock_quantity < quantity:
                return {"success": False, "cart": None,
                        "error": f"Only {item.stock_quantity} available"}
            
            cart_item.quantity = quantity
            cart_item.line_total = cart_item.unit_price * quantity
        
        if notes is not None:
            cart_item.notes = notes[:200]
        
        self._recalculate_cart(cart)
        cart.updated_at = datetime.now()
        self.storage.save_cart(cart)
        
        return {"success": True, "cart": cart, "error": None}
    
    def remove_from_cart(self, cart_id: str, cart_item_id: str) -> dict:
        """Remove item from cart."""
        cart = self.storage.get_cart(cart_id)
        if not cart:
            return {"success": False, "cart": None, "error": "Cart not found"}
        
        cart.items = [ci for ci in cart.items if ci.id != cart_item_id]
        self._recalculate_cart(cart)
        cart.updated_at = datetime.now()
        self.storage.save_cart(cart)
        
        return {"success": True, "cart": cart, "error": None}
    
    def clear_cart(self, cart_id: str) -> dict:
        """Clear all items from cart."""
        cart = self.storage.get_cart(cart_id)
        if not cart:
            return {"success": False, "error": "Cart not found"}
        
        cart.items = []
        cart.subtotal = 0
        cart.tax_amount = 0
        cart.total = 0
        cart.discount_amount = 0
        cart.updated_at = datetime.now()
        self.storage.save_cart(cart)
        
        return {"success": True, "cart": cart, "error": None}
    
    def merge_carts(self, guest_cart_id: str, customer_cart_id: str) -> dict:
        """Merge guest cart into customer cart on login."""
        guest_cart = self.storage.get_cart(guest_cart_id)
        customer_cart = self.storage.get_cart(customer_cart_id)
        
        if not guest_cart:
            return {"success": True, "cart": customer_cart, "error": None}
        
        if not customer_cart:
            guest_cart.id = customer_cart_id
            self.storage.save_cart(guest_cart)
            return {"success": True, "cart": guest_cart, "error": None}
        
        # Merge items
        for item in guest_cart.items:
            existing = next((ci for ci in customer_cart.items 
                           if ci.menu_item_id == item.menu_item_id), None)
            if existing:
                existing.quantity = min(existing.quantity + item.quantity, self.MAX_ITEM_QUANTITY)
                existing.line_total = existing.unit_price * existing.quantity
            else:
                customer_cart.items.append(item)
        
        self._recalculate_cart(customer_cart)
        self.storage.save_cart(customer_cart)
        self.storage.delete_cart(guest_cart_id)
        
        return {"success": True, "cart": customer_cart, "error": None}
    
    # ==================== US-C3: Cart Total Calculation ====================
    
    def _recalculate_cart(self, cart: Cart):
        """Recalculate all cart totals."""
        # Subtotal
        cart.subtotal = sum(ci.line_total for ci in cart.items)
        
        # Apply discount
        if cart.discount_code:
            discount = self.storage.get_discount_code(cart.discount_code)
            if discount and discount.is_active:
                cart.discount_amount = self._calculate_discount(cart.subtotal, discount)
            else:
                cart.discount_amount = 0
                cart.discount_code = None
        
        # Calculate tax (VAT on subtotal minus discount)
        taxable = cart.subtotal - cart.discount_amount
        cart.tax_amount = round(taxable * self.VAT_RATE, 2)
        
        # Total
        cart.total = round(
            cart.subtotal - cart.discount_amount + cart.tax_amount + 
            cart.delivery_fee + cart.tip_amount, 2
        )
    
    def _calculate_discount(self, subtotal: float, discount) -> float:
        from models import DiscountType
        
        if discount.min_order_amount and subtotal < discount.min_order_amount:
            return 0
        
        if discount.discount_type == DiscountType.PERCENTAGE:
            amount = subtotal * (discount.value / 100)
        elif discount.discount_type == DiscountType.FIXED_AMOUNT:
            amount = discount.value
        else:
            return 0
        
        if discount.max_discount_amount:
            amount = min(amount, discount.max_discount_amount)
        
        return round(amount, 2)
    
    def get_cart_summary(self, cart_id: str) -> dict:
        """Get detailed cart summary."""
        cart = self.storage.get_cart(cart_id)
        if not cart:
            return {"success": False, "error": "Cart not found"}
        
        # Check item availability
        warnings = []
        for ci in cart.items:
            item = self.storage.get_menu_item(ci.menu_item_id)
            if not item or not item.is_available:
                warnings.append(f"{ci.menu_item_id} is no longer available")
            elif item.stock_quantity < ci.quantity:
                warnings.append(f"Only {item.stock_quantity} of {item.name} available")
        
        return {
            "success": True,
            "summary": {
                "item_count": len(cart.items),
                "total_quantity": sum(ci.quantity for ci in cart.items),
                "subtotal": cart.subtotal,
                "discount": cart.discount_amount,
                "tax": cart.tax_amount,
                "delivery_fee": cart.delivery_fee,
                "tip": cart.tip_amount,
                "total": cart.total,
                "savings": cart.discount_amount
            },
            "warnings": warnings,
            "error": None
        }
    
    # ==================== US-C4: Place Order ====================
    
    def place_order(self, cart_id: str, customer_id: str, delivery_address: Address,
                    payment_method: str, loyalty_points_to_use: int = 0) -> dict:
        """
        Place order with comprehensive validation. Complexity >= 15.
        """
        cart = self.storage.get_cart(cart_id)
        if not cart or not cart.items:
            return {"success": False, "order": None, "error": "Cart is empty"}
        
        # Validate minimum order
        if cart.subtotal < self.MIN_ORDER_AMOUNT:
            return {"success": False, "order": None,
                    "error": f"Minimum order £{self.MIN_ORDER_AMOUNT}"}
        
        # Validate delivery address
        if not delivery_address:
            return {"success": False, "order": None, "error": "Delivery address required"}
        
        from models import DeliveryZone
        if delivery_address.delivery_zone == DeliveryZone.OUT_OF_RANGE:
            return {"success": False, "order": None, "error": "Outside delivery area"}
        
        # Validate all items still available
        for ci in cart.items:
            item = self.storage.get_menu_item(ci.menu_item_id)
            if not item:
                return {"success": False, "order": None,
                        "error": f"Item no longer exists"}
            if not item.is_available:
                return {"success": False, "order": None,
                        "error": f"{item.name} is no longer available"}
            if item.stock_quantity < ci.quantity:
                return {"success": False, "order": None,
                        "error": f"Insufficient stock for {item.name}"}
        
        # Check restaurant is open
        if not self._is_restaurant_open():
            return {"success": False, "order": None, "error": "Restaurant is closed"}
        
        # Handle loyalty points
        points_discount = 0
        if loyalty_points_to_use > 0:
            customer = self.storage.get_customer(customer_id)
            if customer and customer.loyalty_points.total_points >= loyalty_points_to_use:
                points_discount = min(loyalty_points_to_use * 0.01, cart.total * 0.5)
        
        # Generate order number
        order_number = self._generate_order_number()
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            items=list(cart.items),  # Snapshot
            delivery_address=delivery_address,
            subtotal=cart.subtotal,
            discount_amount=cart.discount_amount + points_discount,
            tax_amount=cart.tax_amount,
            delivery_fee=cart.delivery_fee,
            tip_amount=cart.tip_amount,
            total=round(cart.total - points_discount, 2),
            discount_code_used=cart.discount_code,
            loyalty_points_used=int(points_discount / 0.01),
            status=OrderStatus.PENDING,
            payment_method=payment_method
        )
        
        # Add initial status
        order.status_history.append(
            OrderStatusHistory(status=OrderStatus.PENDING)
        )
        
        # Reserve stock
        for ci in cart.items:
            self.storage.reserve_stock(ci.menu_item_id, ci.quantity)
        
        # Calculate estimated delivery time
        order.estimated_delivery_time = self._estimate_delivery_time(order)
        
        # Save order
        self.storage.save_order(order)
        
        # Clear cart
        self.clear_cart(cart_id)
        
        return {"success": True, "order": order, "error": None}
    
    def _is_restaurant_open(self) -> bool:
        """Check if restaurant is currently open."""
        now = datetime.now()
        hour = now.hour
        # Example: Open 11am - 11pm
        return 11 <= hour < 23
    
    def _generate_order_number(self) -> str:
        """Generate unique order number."""
        import random
        now = datetime.now()
        return f"ORD-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    def _estimate_delivery_time(self, order: Order) -> datetime:
        """Estimate delivery time based on order."""
        base_time = 30  # Base prep time in minutes
        
        # Add time for order size
        item_count = sum(ci.quantity for ci in order.items)
        base_time += (item_count // 3) * 5
        
        # Add time for delivery distance
        if order.delivery_address:
            from models import DeliveryZone
            zone_times = {
                DeliveryZone.ZONE_1: 10,
                DeliveryZone.ZONE_2: 20,
                DeliveryZone.ZONE_3: 30
            }
            base_time += zone_times.get(order.delivery_address.delivery_zone, 15)
        
        # Add peak time buffer
        hour = datetime.now().hour
        if 18 <= hour <= 21:
            base_time += 15
        
        return datetime.now() + timedelta(minutes=base_time)
    
    # ==================== US-C5: Order Status Tracking ====================
    
    def update_order_status(self, order_id: str, new_status: OrderStatus,
                            notes: str = "") -> dict:
        """
        Update order status with validation. Complexity >= 10.
        """
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "order": None, "error": "Order not found"}
        
        # Validate status transition
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.OUT_FOR_DELIVERY],
            OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: []
        }
        
        allowed = valid_transitions.get(order.status, [])
        if new_status not in allowed:
            return {"success": False, "order": None,
                    "error": f"Cannot change from {order.status.value} to {new_status.value}"}
        
        # Update status
        order.status = new_status
        order.status_history.append(
            OrderStatusHistory(status=new_status, notes=notes)
        )
        order.updated_at = datetime.now()
        
        # Handle delivery
        if new_status == OrderStatus.DELIVERED:
            order.actual_delivery_time = datetime.now()
        
        # Update delivery estimate
        if new_status in [OrderStatus.CONFIRMED, OrderStatus.PREPARING]:
            order.estimated_delivery_time = self._estimate_delivery_time(order)
        
        self.storage.save_order(order)
        
        return {"success": True, "order": order, "error": None}
    
    def get_order_status(self, order_id: str) -> dict:
        """Get current order status with timeline."""
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        
        return {
            "success": True,
            "status": order.status.value,
            "timeline": [
                {"status": sh.status.value, "time": sh.timestamp, "notes": sh.notes}
                for sh in order.status_history
            ],
            "estimated_delivery": order.estimated_delivery_time,
            "error": None
        }
    
    # ==================== US-C6: Cancel Order ====================
    
    def cancel_order(self, order_id: str, customer_id: str, reason: str = "") -> dict:
        """
        Cancel order with refund logic. Complexity >= 10.
        """
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "refund": 0, "error": "Order not found"}
        
        if order.customer_id != customer_id:
            return {"success": False, "refund": 0, "error": "Not authorized"}
        
        # Check cancellation limit
        recent_cancellations = self.storage.get_customer_cancellations(
            customer_id, days=30
        )
        if len(recent_cancellations) >= self.MAX_CANCELLATIONS_PER_MONTH:
            return {"success": False, "refund": 0,
                    "error": "Monthly cancellation limit reached"}
        
        # Calculate refund based on status
        if order.status == OrderStatus.PENDING:
            refund_percentage = 100
        elif order.status == OrderStatus.CONFIRMED:
            refund_percentage = 100
        elif order.status == OrderStatus.PREPARING:
            refund_percentage = 50
        else:
            return {"success": False, "refund": 0,
                    "error": f"Cannot cancel order in {order.status.value} status"}
        
        refund_amount = round(order.total * (refund_percentage / 100), 2)
        
        # Update order
        order.status = OrderStatus.CANCELLED
        order.status_history.append(
            OrderStatusHistory(status=OrderStatus.CANCELLED, notes=reason)
        )
        order.cancellation_reason = reason
        order.refund_amount = refund_amount
        order.updated_at = datetime.now()
        
        # Restore stock
        for ci in order.items:
            self.storage.release_stock(ci.menu_item_id, ci.quantity)
        
        # Restore loyalty points
        if order.loyalty_points_used > 0:
            customer = self.storage.get_customer(customer_id)
            if customer:
                customer.loyalty_points.total_points += order.loyalty_points_used
                self.storage.save_customer(customer)
        
        self.storage.save_order(order)
        self.storage.log_cancellation(order_id, customer_id, reason)
        
        return {
            "success": True,
            "refund": refund_amount,
            "refund_percentage": refund_percentage,
            "error": None
        }
    
    # ==================== US-C7: Schedule Order ====================
    
    def schedule_order(self, cart_id: str, customer_id: str, delivery_address: Address,
                       scheduled_time: datetime, payment_method: str) -> dict:
        """
        Schedule order for future delivery. Complexity >= 10.
        """
        now = datetime.now()
        
        # Validate scheduled time
        min_advance = timedelta(hours=1)
        max_advance = timedelta(days=7)
        
        if scheduled_time < now + min_advance:
            return {"success": False, "order": None,
                    "error": "Must schedule at least 1 hour in advance"}
        
        if scheduled_time > now + max_advance:
            return {"success": False, "order": None,
                    "error": "Cannot schedule more than 7 days in advance"}
        
        # Check restaurant will be open
        scheduled_hour = scheduled_time.hour
        if not (11 <= scheduled_hour < 23):
            return {"success": False, "order": None,
                    "error": "Restaurant not open at scheduled time"}
        
        # Check items available at scheduled time
        cart = self.storage.get_cart(cart_id)
        if not cart or not cart.items:
            return {"success": False, "order": None, "error": "Cart is empty"}
        
        for ci in cart.items:
            item = self.storage.get_menu_item(ci.menu_item_id)
            if item and item.availability_schedule:
                day = scheduled_time.weekday()
                time_check = scheduled_time.time()
                available = any(
                    s.day_of_week == day and s.start_time <= time_check <= s.end_time
                    for s in item.availability_schedule
                )
                if not available:
                    return {"success": False, "order": None,
                            "error": f"{item.name} not available at scheduled time"}
        
        # Place order as scheduled
        result = self.place_order(cart_id, customer_id, delivery_address, payment_method)
        
        if result["success"]:
            order = result["order"]
            order.is_scheduled = True
            order.scheduled_for = scheduled_time
            order.estimated_delivery_time = scheduled_time
            self.storage.save_order(order)
        
        return result
    
    def modify_scheduled_order(self, order_id: str, customer_id: str,
                               new_time: datetime = None, **item_changes) -> dict:
        """Modify scheduled order before cutoff time."""
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        
        if order.customer_id != customer_id:
            return {"success": False, "error": "Not authorized"}
        
        if not order.is_scheduled:
            return {"success": False, "error": "Not a scheduled order"}
        
        # Check cutoff (30 min before)
        cutoff = order.scheduled_for - timedelta(minutes=30)
        if datetime.now() > cutoff:
            return {"success": False, "error": "Modification cutoff passed"}
        
        if new_time:
            order.scheduled_for = new_time
            order.estimated_delivery_time = new_time
        
        order.updated_at = datetime.now()
        self.storage.save_order(order)
        
        return {"success": True, "order": order, "error": None}
    
    # ==================== US-C8: Reorder Previous Order ====================
    
    def reorder(self, order_id: str, customer_id: str) -> dict:
        """
        Reorder a previous order. Complexity >= 10.
        """
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "cart": None, "error": "Order not found"}
        
        if order.customer_id != customer_id:
            return {"success": False, "cart": None, "error": "Not authorized"}
        
        # Create new cart
        cart = Cart(customer_id=customer_id)
        
        unavailable_items = []
        price_changes = []
        
        for ci in order.items:
            item = self.storage.get_menu_item(ci.menu_item_id)
            
            if not item:
                unavailable_items.append(ci.menu_item_id)
                continue
            
            if not item.is_available:
                unavailable_items.append(item.name)
                continue
            
            if item.stock_quantity < ci.quantity:
                unavailable_items.append(f"{item.name} (insufficient stock)")
                continue
            
            # Note price changes
            current_price = self._calculate_item_price(item, ci.customization)
            if current_price != ci.unit_price:
                price_changes.append({
                    "item": item.name,
                    "old_price": ci.unit_price,
                    "new_price": current_price
                })
            
            # Add to cart with current prices
            new_cart_item = CartItem(
                menu_item_id=ci.menu_item_id,
                quantity=ci.quantity,
                customization=ci.customization,
                unit_price=current_price,
                line_total=current_price * ci.quantity,
                notes=ci.notes
            )
            cart.items.append(new_cart_item)
        
        if not cart.items:
            return {"success": False, "cart": None,
                    "error": "No items available to reorder"}
        
        self._recalculate_cart(cart)
        self.storage.save_cart(cart)
        
        return {
            "success": True,
            "cart": cart,
            "unavailable_items": unavailable_items,
            "price_changes": price_changes,
            "error": None
        }
    
    # ==================== US-C9: Order Notes ====================
    
    def add_order_notes(self, order_id: str, notes: str) -> dict:
        """Add general notes to order."""
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        
        if len(notes) > 500:
            return {"success": False, "error": "Notes max 500 characters"}
        
        # Filter inappropriate content
        filtered = self._filter_content(notes)
        if filtered != notes:
            return {"success": False, "error": "Notes contain inappropriate content"}
        
        # Check for contact info
        if self._contains_contact_info(notes):
            return {"success": False, "error": "Notes cannot contain contact information"}
        
        order.order_notes = notes
        order.updated_at = datetime.now()
        self.storage.save_order(order)
        
        return {"success": True, "error": None}
    
    def add_item_notes(self, cart_id: str, cart_item_id: str, notes: str) -> dict:
        """Add notes to specific cart item."""
        cart = self.storage.get_cart(cart_id)
        if not cart:
            return {"success": False, "error": "Cart not found"}
        
        cart_item = next((ci for ci in cart.items if ci.id == cart_item_id), None)
        if not cart_item:
            return {"success": False, "error": "Item not in cart"}
        
        if len(notes) > 200:
            return {"success": False, "error": "Notes max 200 characters"}
        
        filtered = self._filter_content(notes)
        if filtered != notes:
            return {"success": False, "error": "Notes contain inappropriate content"}
        
        cart_item.notes = notes
        cart.updated_at = datetime.now()
        self.storage.save_cart(cart)
        
        return {"success": True, "error": None}
    
    def _filter_content(self, text: str) -> str:
        """Filter inappropriate content from notes."""
        # Simple profanity filter (would be more comprehensive in production)
        bad_words = ['spam', 'offensive']  # Example list
        filtered = text
        for word in bad_words:
            filtered = filtered.replace(word, '***')
        return filtered
    
    def _contains_contact_info(self, text: str) -> bool:
        """Check if text contains contact information."""
        import re
        # Check for phone numbers
        if re.search(r'\d{10,}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', text):
            return True
        # Check for emails
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            return True
        return False
