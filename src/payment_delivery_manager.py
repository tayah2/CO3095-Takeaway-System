"""
Payment, Delivery & Reports Module - Member D
User Stories: US-D1 to US-D9
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from collections import Counter
from models import (
    DeliveryZone, PaymentDetails, CardType, DiscountCode, DiscountType,
    Order, OrderStatus, Refund, SalesReport, ItemAnalytics
)


class PaymentDeliveryManager:
    """Manages payments, delivery fees, and reporting."""
    
    def __init__(self, storage):
        self.storage = storage
        self.ZONE_FEES = {
            DeliveryZone.ZONE_1: 2.00,
            DeliveryZone.ZONE_2: 3.50,
            DeliveryZone.ZONE_3: 5.00
        }
        self.FREE_DELIVERY_THRESHOLD = 30.00
        self.PEAK_SURCHARGE = 1.50
        self.BAD_WEATHER_SURCHARGE = 1.00
        self.TIP_PRESETS = [10, 15, 20]
        self.MIN_TIP = 0.50
        self.MAX_TIP_PERCENTAGE = 100
    
    # ==================== US-D1: Calculate Delivery Fee ====================
    
    def calculate_delivery_fee(self, postcode: str, order_subtotal: float,
                               is_peak_time: bool = None, bad_weather: bool = False) -> dict:
        """Calculate delivery fee based on multiple factors. Complexity >= 10."""
        if not postcode:
            return {"success": False, "fee": 0, "error": "Postcode required"}
        
        postcode = postcode.upper().replace(' ', '')
        zone = self._get_delivery_zone(postcode)
        
        if zone == DeliveryZone.OUT_OF_RANGE:
            return {"success": False, "fee": 0, "error": "Outside delivery area"}
        
        base_fee = self.ZONE_FEES.get(zone, 0)
        breakdown = {"base_fee": base_fee, "zone": zone.value}
        
        # Free delivery check
        if order_subtotal >= self.FREE_DELIVERY_THRESHOLD:
            return {"success": True, "fee": 0, "breakdown": {
                "base_fee": base_fee, "free_delivery": True,
                "reason": f"Free on orders over £{self.FREE_DELIVERY_THRESHOLD}"
            }, "error": None}
        
        total_fee = base_fee
        
        # Peak surcharge
        if is_peak_time is None:
            is_peak_time = self._is_peak_time()
        if is_peak_time:
            total_fee += self.PEAK_SURCHARGE
            breakdown["peak_surcharge"] = self.PEAK_SURCHARGE
        
        # Weather surcharge
        if bad_weather:
            total_fee += self.BAD_WEATHER_SURCHARGE
            breakdown["weather_surcharge"] = self.BAD_WEATHER_SURCHARGE
        
        breakdown["total"] = round(total_fee, 2)
        return {"success": True, "fee": round(total_fee, 2), "breakdown": breakdown, "error": None}
    
    def _get_delivery_zone(self, postcode: str) -> DeliveryZone:
        if postcode.startswith('LE1') or postcode.startswith('LE2'):
            return DeliveryZone.ZONE_1
        elif postcode.startswith(('LE3', 'LE4', 'LE5')):
            return DeliveryZone.ZONE_2
        elif postcode.startswith('LE'):
            return DeliveryZone.ZONE_3
        return DeliveryZone.OUT_OF_RANGE
    
    def _is_peak_time(self) -> bool:
        return 18 <= datetime.now().hour < 21
    
    # ==================== US-D2: Apply Discount Codes ====================
    
    def validate_discount_code(self, code: str, order_subtotal: float,
                               customer_id: str = None, is_first_order: bool = False) -> dict:
        """Validate and calculate discount. Complexity >= 10."""
        if not code:
            return {"valid": False, "discount": 0, "error": "Code required"}
        
        code = code.upper().strip()
        discount = self.storage.get_discount_code(code)
        
        if not discount:
            return {"valid": False, "discount": 0, "error": "Invalid code"}
        if not discount.is_active:
            return {"valid": False, "discount": 0, "error": "Code inactive"}
        
        now = datetime.now()
        if discount.valid_from > now:
            return {"valid": False, "discount": 0, "error": "Code not yet valid"}
        if discount.valid_until and discount.valid_until < now:
            return {"valid": False, "discount": 0, "error": "Code expired"}
        
        if discount.usage_limit > 0 and discount.times_used >= discount.usage_limit:
            return {"valid": False, "discount": 0, "error": "Usage limit reached"}
        
        if customer_id and discount.is_single_use_per_customer:
            if self.storage.has_customer_used_code(customer_id, code):
                return {"valid": False, "discount": 0, "error": "Already used this code"}
        
        if discount.is_first_order_only and not is_first_order:
            return {"valid": False, "discount": 0, "error": "First order only"}
        
        if discount.min_order_amount and order_subtotal < discount.min_order_amount:
            return {"valid": False, "discount": 0,
                    "error": f"Min order £{discount.min_order_amount}"}
        
        # Calculate discount
        if discount.discount_type == DiscountType.PERCENTAGE:
            amount = order_subtotal * (discount.value / 100)
        elif discount.discount_type == DiscountType.FIXED_AMOUNT:
            amount = discount.value
        elif discount.discount_type == DiscountType.FREE_DELIVERY:
            return {"valid": True, "discount": 0, "free_delivery": True, "error": None}
        else:
            amount = 0
        
        if discount.max_discount_amount:
            amount = min(amount, discount.max_discount_amount)
        
        return {"valid": True, "discount": round(amount, 2),
                "discount_type": discount.discount_type.value, "error": None}
    
    def create_discount_code(self, code: str, discount_type: DiscountType, value: float,
                             min_order: float = 0, usage_limit: int = 0,
                             valid_days: int = 30, first_order_only: bool = False) -> dict:
        """Create a new discount code."""
        if not code or len(code) < 4:
            return {"success": False, "error": "Code must be 4+ characters"}
        
        code = code.upper().strip()
        if self.storage.get_discount_code(code):
            return {"success": False, "error": "Code exists"}
        if value <= 0:
            return {"success": False, "error": "Value must be positive"}
        if discount_type == DiscountType.PERCENTAGE and value > 100:
            return {"success": False, "error": "Max 100%"}
        
        discount = DiscountCode(
            code=code, discount_type=discount_type, value=value,
            min_order_amount=min_order, usage_limit=usage_limit,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=valid_days),
            is_first_order_only=first_order_only, is_active=True
        )
        self.storage.save_discount_code(discount)
        return {"success": True, "discount_code": discount, "error": None}
    
    # ==================== US-D3: Payment Validation ====================
    
    def validate_payment(self, card_number: str, expiry_month: int, expiry_year: int,
                         cvv: str, card_holder: str, amount: float) -> dict:
        """Validate payment details using Luhn algorithm. Complexity >= 10."""
        errors = []
        
        card_clean = card_number.replace(' ', '').replace('-', '')
        if not self._validate_luhn(card_clean):
            errors.append("Invalid card number")
        
        card_type = self._detect_card_type(card_clean)
        if card_type == CardType.UNKNOWN:
            errors.append("Unsupported card type")
        
        # Length validation
        lengths = {CardType.VISA: [13, 16], CardType.MASTERCARD: [16], CardType.AMEX: [15]}
        if card_type in lengths and len(card_clean) not in lengths[card_type]:
            errors.append("Invalid card number length")
        
        # Expiry validation
        now = datetime.now()
        if expiry_year < now.year or (expiry_year == now.year and expiry_month < now.month):
            errors.append("Card expired")
        if expiry_year > now.year + 10:
            errors.append("Invalid expiry year")
        if not 1 <= expiry_month <= 12:
            errors.append("Invalid expiry month")
        
        # CVV validation
        cvv_clean = cvv.strip()
        expected_len = 4 if card_type == CardType.AMEX else 3
        if len(cvv_clean) != expected_len or not cvv_clean.isdigit():
            errors.append(f"Invalid CVV ({expected_len} digits required)")
        
        if not card_holder or len(card_holder.strip()) < 2:
            errors.append("Card holder name required")
        if amount <= 0:
            errors.append("Invalid amount")
        
        if errors:
            return {"valid": False, "errors": errors, "card_type": None}
        
        return {"valid": True, "errors": [], "card_type": card_type.value,
                "masked_card": '*' * (len(card_clean) - 4) + card_clean[-4:],
                "last_four": card_clean[-4:]}
    
    def _validate_luhn(self, card_number: str) -> bool:
        if not card_number.isdigit():
            return False
        digits = [int(d) for d in card_number]
        odd = digits[-1::-2]
        even = digits[-2::-2]
        checksum = sum(odd) + sum(sum(divmod(d * 2, 10)) for d in even)
        return checksum % 10 == 0
    
    def _detect_card_type(self, card_number: str) -> CardType:
        if card_number.startswith('4'):
            return CardType.VISA
        if card_number.startswith(('51', '52', '53', '54', '55', '2221', '2720')):
            return CardType.MASTERCARD
        if card_number.startswith(('34', '37')):
            return CardType.AMEX
        return CardType.UNKNOWN
    
    # ==================== US-D4: Process Refunds ====================
    
    def process_refund(self, order_id: str, amount: float, reason: str,
                       processed_by: str) -> dict:
        """Process refund with validation. Complexity >= 10."""
        order = self.storage.get_order(order_id)
        if not order:
            return {"success": False, "refund": None, "error": "Order not found"}
        if order.payment_status != "paid":
            return {"success": False, "refund": None, "error": "Order not paid"}
        if amount <= 0:
            return {"success": False, "refund": None, "error": "Invalid amount"}
        
        existing = self.storage.get_order_refunds(order_id)
        total_refunded = sum(r.amount for r in existing)
        
        if total_refunded + amount > order.total:
            return {"success": False, "refund": None,
                    "error": f"Exceeds paid amount. Max: £{order.total - total_refunded:.2f}"}
        if total_refunded >= order.total:
            return {"success": False, "refund": None, "error": "Already fully refunded"}
        
        # Calculate points to restore
        points_restore = 0
        if order.loyalty_points_used > 0 and total_refunded == 0:
            points_restore = int(order.loyalty_points_used * (amount / order.total))
        
        refund = Refund(
            order_id=order_id, amount=round(amount, 2), reason=reason,
            is_partial=amount < (order.total - total_refunded),
            loyalty_points_restored=points_restore, processed_by=processed_by
        )
        self.storage.save_refund(refund)
        
        # Restore points
        if points_restore > 0:
            customer = self.storage.get_customer(order.customer_id)
            if customer:
                customer.loyalty_points.total_points += points_restore
                self.storage.save_customer(customer)
        
        order.refund_amount = total_refunded + amount
        self.storage.save_order(order)
        
        return {"success": True, "refund": refund,
                "total_refunded": round(total_refunded + amount, 2),
                "points_restored": points_restore, "error": None}
    
    # ==================== US-D5: Delivery Time Estimation ====================
    
    def estimate_delivery_time(self, order_size: int, delivery_zone: DeliveryZone,
                               current_queue: int = 0) -> dict:
        """Estimate delivery time. Complexity >= 10."""
        # Base prep time
        if order_size <= 3:
            prep = 15
        elif order_size <= 6:
            prep = 25
        elif order_size <= 10:
            prep = 35
        else:
            prep = 45
        
        # Travel time
        travel = {DeliveryZone.ZONE_1: 10, DeliveryZone.ZONE_2: 20, DeliveryZone.ZONE_3: 30}
        travel_time = travel.get(delivery_zone, 20)
        
        # Queue and adjustments
        queue_time = current_queue * 5
        peak_adj = 15 if self._is_peak_time() else 0
        weather_adj = 10 if self._is_bad_weather() else 0
        
        total_min = prep + travel_time + queue_time + peak_adj + weather_adj
        total_max = total_min + 15
        
        return {
            "success": True,
            "min_minutes": total_min,
            "max_minutes": total_max,
            "display": f"{total_min}-{total_max} mins",
            "estimated_arrival": datetime.now() + timedelta(minutes=total_min),
            "breakdown": {"prep": prep, "travel": travel_time, "queue": queue_time,
                         "peak": peak_adj, "weather": weather_adj},
            "error": None
        }
    
    def _is_bad_weather(self) -> bool:
        return False  # Would integrate with weather API
    
    # ==================== US-D6: Tip Calculation ====================
    
    def calculate_tip(self, subtotal: float, percentage: int = None,
                      custom_amount: float = None, round_up: bool = False) -> dict:
        """Calculate tip amount. Complexity >= 10."""
        if percentage is None and custom_amount is None:
            return {"success": False, "tip": 0, "error": "Specify percentage or amount"}
        
        if percentage is not None:
            if percentage < 0 or percentage > self.MAX_TIP_PERCENTAGE:
                return {"success": False, "tip": 0, "error": "Invalid percentage"}
            tip = subtotal * (percentage / 100)
        else:
            tip = custom_amount
        
        if tip > 0 and tip < self.MIN_TIP:
            return {"success": False, "tip": 0, "error": f"Min tip £{self.MIN_TIP}"}
        
        max_tip = subtotal * (self.MAX_TIP_PERCENTAGE / 100)
        if tip > max_tip:
            return {"success": False, "tip": 0, "error": f"Max tip £{max_tip:.2f}"}
        
        if round_up and tip > 0:
            tip = round(tip + 0.05, 1)
        
        return {"success": True, "tip": round(tip, 2),
                "percentage": round((tip / subtotal) * 100, 1) if subtotal > 0 else 0,
                "error": None}
    
    def get_tip_presets(self, subtotal: float) -> dict:
        presets = [{"percentage": p, "amount": round(subtotal * p / 100, 2),
                   "label": f"{p}% (£{subtotal * p / 100:.2f})"} for p in self.TIP_PRESETS]
        presets.append({"percentage": 0, "amount": 0, "label": "No tip"})
        return {"success": True, "presets": presets, "error": None}
    
    # ==================== US-D7: Sales Report Generation ====================
    
    def generate_sales_report(self, start_date: date, end_date: date,
                              category_filter: str = None) -> dict:
        """Generate sales report. Complexity >= 15."""
        if start_date > end_date:
            return {"success": False, "report": None, "error": "Invalid date range"}
        
        orders = self.storage.get_orders_in_range(start_date, end_date)
        delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
        
        if not delivered:
            return {"success": True, "report": SalesReport(
                start_date=start_date, end_date=end_date), "error": None}
        
        total_revenue = sum(o.total for o in delivered)
        total_tax = sum(o.tax_amount for o in delivered)
        total_delivery = sum(o.delivery_fee for o in delivered)
        total_tips = sum(o.tip_amount for o in delivered)
        total_discounts = sum(o.discount_amount for o in orders)
        
        # Refunds
        total_refunds = 0
        for o in orders:
            refunds = self.storage.get_order_refunds(o.id)
            total_refunds += sum(r.amount for r in refunds)
        
        net_revenue = total_revenue - total_refunds
        avg_order = total_revenue / len(delivered) if delivered else 0
        
        # Status counts
        status_counts = {}
        for status in OrderStatus:
            count = len([o for o in orders if o.status == status])
            if count > 0:
                status_counts[status.value] = count
        
        # Payment method counts
        payment_counts = {}
        for o in delivered:
            m = o.payment_method.value
            payment_counts[m] = payment_counts.get(m, 0) + 1
        
        # Top items
        item_sales = {}
        for o in delivered:
            for ci in o.items:
                iid = ci.menu_item_id
                if iid not in item_sales:
                    mi = self.storage.get_menu_item(iid)
                    item_sales[iid] = {"name": mi.name if mi else "Unknown",
                                       "quantity": 0, "revenue": 0}
                item_sales[iid]["quantity"] += ci.quantity
                item_sales[iid]["revenue"] += ci.line_total
        top_items = sorted(item_sales.values(), key=lambda x: x["revenue"], reverse=True)[:10]
        
        # Category revenue
        cat_revenue = {}
        for o in delivered:
            for ci in o.items:
                mi = self.storage.get_menu_item(ci.menu_item_id)
                if mi:
                    cat = self.storage.get_category(mi.category_id)
                    name = cat.name if cat else "Other"
                    cat_revenue[name] = cat_revenue.get(name, 0) + ci.line_total
        
        report = SalesReport(
            start_date=start_date, end_date=end_date,
            total_orders=len(orders), total_revenue=round(total_revenue, 2),
            total_tax=round(total_tax, 2), total_delivery_fees=round(total_delivery, 2),
            total_tips=round(total_tips, 2), total_discounts=round(total_discounts, 2),
            total_refunds=round(total_refunds, 2), net_revenue=round(net_revenue, 2),
            average_order_value=round(avg_order, 2), orders_by_status=status_counts,
            orders_by_payment_method=payment_counts, top_items=top_items,
            revenue_by_category=cat_revenue
        )
        return {"success": True, "report": report, "error": None}
    
    def export_report_csv(self, report: SalesReport) -> str:
        import io, csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Sales Report", f"{report.start_date} to {report.end_date}"])
        writer.writerow(["Total Orders", report.total_orders])
        writer.writerow(["Total Revenue", f"£{report.total_revenue:.2f}"])
        writer.writerow(["Net Revenue", f"£{report.net_revenue:.2f}"])
        writer.writerow(["Avg Order Value", f"£{report.average_order_value:.2f}"])
        return output.getvalue()
    
    # ==================== US-D8: Popular Items Analytics ====================
    
    def get_popular_items(self, start_date: date = None, end_date: date = None,
                          limit: int = 10, sort_by: str = "quantity") -> dict:
        """Get popular items. Complexity >= 10."""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        orders = self.storage.get_orders_in_range(start_date, end_date)
        delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
        
        item_data = {}
        for o in delivered:
            for ci in o.items:
                iid = ci.menu_item_id
                if iid not in item_data:
                    mi = self.storage.get_menu_item(iid)
                    if not mi:
                        continue
                    item_data[iid] = {"name": mi.name, "qty": 0, "revenue": 0,
                                      "orders": 0, "hours": []}
                item_data[iid]["qty"] += ci.quantity
                item_data[iid]["revenue"] += ci.line_total
                item_data[iid]["orders"] += 1
                item_data[iid]["hours"].append(o.created_at.hour)
        
        analytics = []
        for iid, d in item_data.items():
            avg_qty = d["qty"] / d["orders"] if d["orders"] > 0 else 0
            popularity = d["qty"] * 0.4 + d["revenue"] * 0.3 + d["orders"] * 0.3
            peak_hours = [h for h, _ in Counter(d["hours"]).most_common(3)] if d["hours"] else []
            
            analytics.append(ItemAnalytics(
                item_id=iid, item_name=d["name"], quantity_sold=d["qty"],
                revenue=round(d["revenue"], 2), order_count=d["orders"],
                average_quantity_per_order=round(avg_qty, 2),
                popularity_score=round(popularity, 2), peak_hours=peak_hours
            ))
        
        if sort_by == "quantity":
            analytics.sort(key=lambda x: x.quantity_sold, reverse=True)
        elif sort_by == "revenue":
            analytics.sort(key=lambda x: x.revenue, reverse=True)
        
        return {"success": True, "items": analytics[:limit],
                "period": {"start": start_date, "end": end_date}, "error": None}
    
    # ==================== US-D9: Revenue Analytics Dashboard ====================
    
    def get_revenue_dashboard(self, period: str = "daily") -> dict:
        """Get revenue dashboard. Complexity >= 10."""
        today = date.today()
        
        if period == "daily":
            start, end = today, today
            prev_start, prev_end = today - timedelta(1), today - timedelta(1)
        elif period == "weekly":
            start = today - timedelta(days=today.weekday())
            end = today
            prev_start = start - timedelta(7)
            prev_end = start - timedelta(1)
        elif period == "monthly":
            start = today.replace(day=1)
            end = today
            prev = start - timedelta(1)
            prev_start, prev_end = prev.replace(day=1), prev
        else:
            return {"success": False, "error": "Invalid period"}
        
        orders = self.storage.get_orders_in_range(start, end)
        delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
        
        revenue = sum(o.total for o in delivered)
        order_count = len(delivered)
        tax = sum(o.tax_amount for o in delivered)
        delivery = sum(o.delivery_fee for o in delivered)
        tips = sum(o.tip_amount for o in delivered)
        
        # Previous period
        prev_orders = self.storage.get_orders_in_range(prev_start, prev_end)
        prev_del = [o for o in prev_orders if o.status == OrderStatus.DELIVERED]
        prev_rev = sum(o.total for o in prev_del)
        
        change = ((revenue - prev_rev) / prev_rev * 100) if prev_rev > 0 else (100 if revenue else 0)
        avg = revenue / order_count if order_count else 0
        
        # By payment
        by_payment = {}
        for o in delivered:
            m = o.payment_method.value
            by_payment[m] = by_payment.get(m, 0) + o.total
        
        # By category
        by_cat = {}
        for o in delivered:
            for ci in o.items:
                mi = self.storage.get_menu_item(ci.menu_item_id)
                if mi:
                    cat = self.storage.get_category(mi.category_id)
                    name = cat.name if cat else "Other"
                    by_cat[name] = by_cat.get(name, 0) + ci.line_total
        
        return {
            "success": True,
            "dashboard": {
                "period": period,
                "revenue": {"total": round(revenue, 2), "change": round(change, 1)},
                "orders": {"total": order_count, "avg_value": round(avg, 2)},
                "breakdown": {"tax": round(tax, 2), "delivery": round(delivery, 2),
                             "tips": round(tips, 2)},
                "by_payment": {k: round(v, 2) for k, v in by_payment.items()},
                "by_category": {k: round(v, 2) for k, v in by_cat.items()}
            },
            "error": None
        }
