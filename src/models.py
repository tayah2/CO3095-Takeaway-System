"""
Takeaway Menu System - Data Models
CO3095 Group Assignment - Project 19
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum
from typing import Optional
import uuid


# ============== ENUMS ==============

class DietaryTag(Enum):
    """Dietary requirement tags for menu items."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    HALAL = "halal"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"


class SpiceLevel(Enum):
    """Spice level options for items."""
    NONE = 0
    MILD = 1
    MEDIUM = 2
    HOT = 3
    EXTRA_HOT = 4


class ItemSize(Enum):
    """Size variations for menu items."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class OrderStatus(Enum):
    """Status progression for orders."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    """Supported payment methods."""
    CARD = "card"
    CASH = "cash"
    LOYALTY_POINTS = "loyalty_points"


class DiscountType(Enum):
    """Types of discounts."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_DELIVERY = "free_delivery"
    BUY_ONE_GET_ONE = "bogo"


class DeliveryZone(Enum):
    """Delivery zones based on distance."""
    ZONE_1 = 1  # 0-2 miles
    ZONE_2 = 2  # 2-5 miles
    ZONE_3 = 3  # 5-8 miles
    OUT_OF_RANGE = 4  # >8 miles


class CardType(Enum):
    """Credit/debit card types."""
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    UNKNOWN = "unknown"


class OfferType(Enum):
    """Types of special offers."""
    PERCENTAGE_DISCOUNT = "percentage"
    FIXED_DISCOUNT = "fixed"
    BOGO = "buy_one_get_one"


# ============== DATA CLASSES ==============

@dataclass
class Category:
    """Menu category with hierarchy support."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    parent_id: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ItemExtra:
    """Extra/addon for menu items."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    price: float = 0.0
    is_available: bool = True


@dataclass
class ItemCustomization:
    """Customization applied to a cart item."""
    extras: list = field(default_factory=list)  # List of ItemExtra ids
    removed_ingredients: list = field(default_factory=list)
    spice_level: SpiceLevel = SpiceLevel.MEDIUM
    size: ItemSize = ItemSize.MEDIUM
    special_instructions: str = ""


@dataclass
class AvailabilitySchedule:
    """Availability time slot for menu items."""
    day_of_week: int = 0  # 0=Monday, 6=Sunday
    start_time: time = field(default_factory=lambda: time(0, 0))
    end_time: time = field(default_factory=lambda: time(23, 59))


@dataclass
class SpecialOffer:
    """Special offer on menu items."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    offer_type: OfferType = OfferType.PERCENTAGE_DISCOUNT
    value: float = 0.0  # percentage or fixed amount
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    max_uses_per_customer: int = 0  # 0 = unlimited
    min_quantity: int = 1
    is_active: bool = True


@dataclass
class MenuItem:
    """Menu item with all attributes."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    price: float = 0.0
    category_id: str = ""
    dietary_tags: list = field(default_factory=list)  # List of DietaryTag
    preparation_time: int = 15  # minutes
    stock_quantity: int = 100
    is_available: bool = True
    extras: list = field(default_factory=list)  # List of ItemExtra
    removable_ingredients: list = field(default_factory=list)
    size_prices: dict = field(default_factory=dict)  # {ItemSize: price_adjustment}
    availability_schedule: list = field(default_factory=list)  # List of AvailabilitySchedule
    special_offer_id: Optional[str] = None
    allergen_info: str = ""
    calories: int = 0
    image_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Address:
    """Customer delivery address."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    line1: str = ""
    line2: str = ""
    city: str = ""
    postcode: str = ""
    country: str = "UK"
    is_default: bool = False
    delivery_zone: DeliveryZone = DeliveryZone.ZONE_1
    delivery_instructions: str = ""


@dataclass
class LoyaltyPoints:
    """Customer loyalty points tracking."""
    total_points: int = 0
    points_history: list = field(default_factory=list)  # List of point transactions
    lifetime_earned: int = 0
    lifetime_redeemed: int = 0


@dataclass
class PointTransaction:
    """Individual loyalty point transaction."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    points: int = 0  # positive for earn, negative for redeem
    reason: str = ""
    order_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class Customer:
    """Customer account."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    date_of_birth: Optional[date] = None
    addresses: list = field(default_factory=list)  # List of Address
    loyalty_points: LoyaltyPoints = field(default_factory=LoyaltyPoints)
    dietary_preferences: list = field(default_factory=list)  # List of DietaryTag
    favorite_items: list = field(default_factory=list)  # List of MenuItem ids
    is_active: bool = True
    is_verified: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    terms_accepted_at: Optional[datetime] = None
    communication_preferences: dict = field(default_factory=dict)


@dataclass
class PasswordResetToken:
    """Password reset token."""
    token: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    is_used: bool = False


@dataclass
class CartItem:
    """Item in shopping cart."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    menu_item_id: str = ""
    quantity: int = 1
    customization: ItemCustomization = field(default_factory=ItemCustomization)
    unit_price: float = 0.0
    line_total: float = 0.0
    notes: str = ""
    added_at: datetime = field(default_factory=datetime.now)


@dataclass
class Cart:
    """Shopping cart."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: Optional[str] = None  # None for guest carts
    items: list = field(default_factory=list)  # List of CartItem
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    delivery_fee: float = 0.0
    tip_amount: float = 0.0
    total: float = 0.0
    discount_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DiscountCode:
    """Discount/promo code."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    code: str = ""
    discount_type: DiscountType = DiscountType.PERCENTAGE
    value: float = 0.0
    min_order_amount: float = 0.0
    max_discount_amount: Optional[float] = None
    usage_limit: int = 0  # 0 = unlimited
    times_used: int = 0
    is_single_use_per_customer: bool = False
    is_first_order_only: bool = False
    is_combinable: bool = True
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    is_active: bool = True


@dataclass
class OrderStatusHistory:
    """Status change record for order."""
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


@dataclass
class Order:
    """Customer order."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str = ""
    customer_id: str = ""
    items: list = field(default_factory=list)  # List of CartItem (snapshot)
    delivery_address: Optional[Address] = None
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    delivery_fee: float = 0.0
    tip_amount: float = 0.0
    total: float = 0.0
    discount_code_used: Optional[str] = None
    loyalty_points_used: int = 0
    loyalty_points_earned: int = 0
    status: OrderStatus = OrderStatus.PENDING
    status_history: list = field(default_factory=list)  # List of OrderStatusHistory
    payment_method: PaymentMethod = PaymentMethod.CARD
    payment_status: str = "pending"
    is_scheduled: bool = False
    scheduled_for: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    order_notes: str = ""
    cancellation_reason: Optional[str] = None
    refund_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PaymentDetails:
    """Payment card details (for validation only, not storage)."""
    card_number: str = ""
    card_holder_name: str = ""
    expiry_month: int = 1
    expiry_year: int = 2025
    cvv: str = ""
    billing_address: Optional[Address] = None
    card_type: CardType = CardType.UNKNOWN


@dataclass
class Refund:
    """Order refund record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = ""
    amount: float = 0.0
    reason: str = ""
    is_partial: bool = False
    loyalty_points_restored: int = 0
    processed_at: datetime = field(default_factory=datetime.now)
    processed_by: str = ""  # admin id


@dataclass
class SalesReport:
    """Sales report data."""
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)
    total_orders: int = 0
    total_revenue: float = 0.0
    total_tax: float = 0.0
    total_delivery_fees: float = 0.0
    total_tips: float = 0.0
    total_discounts: float = 0.0
    total_refunds: float = 0.0
    net_revenue: float = 0.0
    average_order_value: float = 0.0
    orders_by_status: dict = field(default_factory=dict)
    orders_by_payment_method: dict = field(default_factory=dict)
    top_items: list = field(default_factory=list)
    revenue_by_category: dict = field(default_factory=dict)


@dataclass
class ItemAnalytics:
    """Analytics for a single menu item."""
    item_id: str = ""
    item_name: str = ""
    quantity_sold: int = 0
    revenue: float = 0.0
    order_count: int = 0
    average_quantity_per_order: float = 0.0
    popularity_score: float = 0.0
    trend: str = "stable"  # increasing, decreasing, stable
    peak_hours: list = field(default_factory=list)
