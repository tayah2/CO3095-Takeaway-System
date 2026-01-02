# Takeaway Menu System - Project Plan

## Team Structure (4 Members)

| Member | Role | Responsibility Area |
|--------|------|---------------------|
| Member A | Menu Manager | Menu, Categories, Items, Search/Filter |
| Member B | Customer Manager | Customer accounts, Authentication, Addresses |
| Member C | Order Manager | Cart, Orders, Order Processing, Status Tracking |
| Member D | Payment & Delivery Manager | Payments, Discounts, Delivery, Reports |

---

## Sprint Overview

| Sprint | Duration | Focus |
|--------|----------|-------|
| Sprint 1 | Weeks 1-2 | Core entities & basic CRUD operations |
| Sprint 2 | Weeks 3-4 | Business logic & validations |
| Sprint 3 | Weeks 5-6 | Advanced features & integration |

---

## User Stories by Member (9 per member = 36 total)

### MEMBER A: Menu & Item Management

#### Sprint 1
**US-A1: Add Menu Item with Validation**
- As a restaurant owner, I want to add menu items with comprehensive validation so that only valid items are added to the menu.
- Acceptance Criteria:
  - Validate item name (2-50 chars, no special characters except spaces)
  - Validate price (positive, max 2 decimal places, within range £0.50-£500)
  - Validate category exists
  - Validate description length (10-500 chars)
  - Check for duplicate items
  - Validate preparation time (5-120 minutes)
- Story Points: 8
- Complexity: High (multiple validation branches)

**US-A2: Categorize Menu Items**
- As a restaurant owner, I want to organize items into categories with hierarchy support so customers can browse easily.
- Acceptance Criteria:
  - Create/edit/delete categories
  - Support parent-child category relationships (max 3 levels)
  - Validate category names unique within same level
  - Prevent deletion of categories with items
  - Handle category reordering
- Story Points: 8
- Complexity: High (hierarchy management)

**US-A3: Update Menu Item with Stock Management**
- As a restaurant owner, I want to update items including stock levels so I can manage availability.
- Acceptance Criteria:
  - Update any item field with validation
  - Track stock quantity
  - Auto-mark unavailable when stock = 0
  - Log all changes with timestamps
  - Validate stock doesn't go negative
  - Handle concurrent update scenarios
- Story Points: 5
- Complexity: Medium

#### Sprint 2
**US-A4: Search Menu Items**
- As a customer, I want to search for items using multiple criteria so I can find what I want quickly.
- Acceptance Criteria:
  - Search by name (partial match, case-insensitive)
  - Search by category
  - Search by price range
  - Search by dietary requirements
  - Search by availability
  - Combine multiple search criteria (AND/OR)
  - Sort results by relevance/price/name
  - Paginate results
- Story Points: 13
- Complexity: Very High (multiple filter combinations)

**US-A5: Filter by Dietary Requirements**
- As a customer with dietary restrictions, I want to filter items by dietary tags so I can find suitable food.
- Acceptance Criteria:
  - Support tags: vegetarian, vegan, gluten-free, halal, dairy-free, nut-free
  - Items can have multiple tags
  - Filter by single or multiple tags
  - Show allergen warnings
  - Validate tag combinations (e.g., vegan implies vegetarian)
  - Display dietary info prominently
- Story Points: 8
- Complexity: High

**US-A6: Menu Item Availability Scheduling**
- As a restaurant owner, I want to schedule item availability so items only show during appropriate times.
- Acceptance Criteria:
  - Set available days (Mon-Sun)
  - Set available time ranges
  - Support multiple time slots per day
  - Handle timezone considerations
  - Override for special dates
  - Validate time slot conflicts
- Story Points: 8
- Complexity: High

#### Sprint 3
**US-A7: Special Offers on Items**
- As a restaurant owner, I want to create special offers so I can promote items.
- Acceptance Criteria:
  - Percentage discount (1-99%)
  - Fixed amount discount
  - Buy-one-get-one offers
  - Time-limited offers with start/end dates
  - Validate offer doesn't exceed item price
  - Limit offers per customer
  - Priority handling when multiple offers apply
- Story Points: 13
- Complexity: Very High

**US-A8: Item Customization Options**
- As a customer, I want to customize items with extras and modifications so I can personalize my order.
- Acceptance Criteria:
  - Add extras with prices (e.g., extra cheese £0.50)
  - Remove ingredients
  - Set spice levels
  - Size variations with price adjustments
  - Validate combinations (e.g., can't remove base ingredient)
  - Calculate final price with all modifications
  - Maximum extras limit
- Story Points: 13
- Complexity: Very High

**US-A9: Menu Import/Export**
- As a restaurant owner, I want to import/export menu data so I can backup and transfer menus.
- Acceptance Criteria:
  - Export to JSON/CSV format
  - Import with validation
  - Handle duplicate detection
  - Merge vs replace options
  - Validate file format and size
  - Report import errors without failing entire import
  - Support partial imports
- Story Points: 8
- Complexity: High

---

### MEMBER B: Customer Management

#### Sprint 1
**US-B1: Customer Registration with Validation**
- As a new customer, I want to register an account so I can place orders.
- Acceptance Criteria:
  - Validate email format and uniqueness
  - Validate password strength (min 8 chars, uppercase, lowercase, number, special char)
  - Validate phone number format (UK format)
  - Validate name (2-50 chars)
  - Age verification (must be 16+)
  - Terms acceptance required
  - Prevent registration with disposable emails
- Story Points: 8
- Complexity: High

**US-B2: Customer Login with Security**
- As a customer, I want to securely log in so I can access my account.
- Acceptance Criteria:
  - Validate credentials
  - Lock account after 5 failed attempts
  - Unlock after 30 minutes or admin reset
  - Track login history
  - Detect suspicious login patterns
  - Session timeout after inactivity
  - Support remember me functionality
- Story Points: 8
- Complexity: High

**US-B3: Manage Delivery Addresses**
- As a customer, I want to manage multiple delivery addresses so I can order to different locations.
- Acceptance Criteria:
  - Add up to 5 addresses
  - Validate postcode format (UK)
  - Set default address
  - Validate address completeness
  - Check delivery zone eligibility
  - Edit/delete addresses
  - Validate address doesn't duplicate existing
- Story Points: 8
- Complexity: High

#### Sprint 2
**US-B4: Customer Profile Management**
- As a customer, I want to manage my profile so my information stays current.
- Acceptance Criteria:
  - Update personal details with validation
  - Change password (require current password)
  - Update communication preferences
  - Set dietary preferences
  - View account creation date and order count
  - Validate changes don't conflict with orders in progress
- Story Points: 5
- Complexity: Medium

**US-B5: Customer Loyalty Points**
- As a customer, I want to earn and spend loyalty points so I get rewards for ordering.
- Acceptance Criteria:
  - Earn 1 point per £1 spent
  - Redeem 100 points = £1 discount
  - Points expire after 12 months
  - Minimum 500 points to redeem
  - Maximum redemption per order (50% of total)
  - Track points history
  - Handle points refund on order cancellation
  - Bonus points for first order/birthday
- Story Points: 13
- Complexity: Very High

**US-B6: Password Reset Flow**
- As a customer, I want to reset my password if I forget it so I can regain access.
- Acceptance Criteria:
  - Generate secure reset token
  - Token expires in 1 hour
  - Validate email exists
  - One active token at a time
  - Invalidate token after use
  - Validate new password strength
  - Notify user of password change
  - Rate limit reset requests (max 3 per hour)
- Story Points: 8
- Complexity: High

#### Sprint 3
**US-B7: Customer Order History**
- As a customer, I want to view my order history so I can track past orders and reorder.
- Acceptance Criteria:
  - List all past orders with pagination
  - Filter by date range
  - Filter by status
  - Sort by date/amount
  - View full order details
  - Quick reorder functionality
  - Calculate total spent in period
- Story Points: 8
- Complexity: High

**US-B8: Favorite Items**
- As a customer, I want to save favorite items so I can quickly find items I like.
- Acceptance Criteria:
  - Add/remove favorites
  - Maximum 50 favorites
  - Show availability status
  - Notify when favorite item on offer
  - Sort favorites by frequency ordered
  - Handle removed items gracefully
  - Quick add to cart from favorites
- Story Points: 5
- Complexity: Medium

**US-B9: Customer Account Deletion**
- As a customer, I want to delete my account so my data is removed if I choose.
- Acceptance Criteria:
  - Require password confirmation
  - Check no active orders
  - Handle pending loyalty points
  - Anonymize order history (keep for records)
  - 30-day grace period to recover
  - Permanent deletion after grace period
  - Cannot reuse email for 90 days
  - Send confirmation email
- Story Points: 8
- Complexity: High

---

### MEMBER C: Order Management

#### Sprint 1
**US-C1: Add Items to Cart**
- As a customer, I want to add items to my cart so I can build my order.
- Acceptance Criteria:
  - Add available items only
  - Set quantity (1-99)
  - Validate item still available when adding
  - Include customizations
  - Calculate line item total
  - Check maximum cart size (50 items)
  - Handle item price changes
  - Cart persists across sessions
- Story Points: 8
- Complexity: High

**US-C2: Manage Cart Contents**
- As a customer, I want to modify my cart so I can adjust my order before checkout.
- Acceptance Criteria:
  - Update quantity
  - Remove items
  - Clear entire cart
  - Validate stock availability on changes
  - Recalculate totals automatically
  - Show item unavailable warnings
  - Save cart for later
  - Merge carts on login
- Story Points: 8
- Complexity: High

**US-C3: Cart Total Calculation**
- As a customer, I want to see accurate cart totals so I know what I'll pay.
- Acceptance Criteria:
  - Calculate subtotal
  - Apply item discounts
  - Calculate tax (VAT 20%)
  - Show savings
  - Handle rounding correctly (to penny)
  - Update on any cart change
  - Show breakdown of charges
- Story Points: 5
- Complexity: Medium

#### Sprint 2
**US-C4: Place Order with Validation**
- As a customer, I want to place an order so I can receive my food.
- Acceptance Criteria:
  - Validate cart not empty
  - Validate minimum order amount (£10)
  - Validate delivery address in zone
  - Validate all items still available
  - Validate restaurant is open
  - Reserve stock on order placement
  - Generate unique order number
  - Send order confirmation
  - Handle payment failure gracefully
- Story Points: 13
- Complexity: Very High

**US-C5: Order Status Tracking**
- As a customer, I want to track my order status so I know when to expect delivery.
- Acceptance Criteria:
  - Statuses: Pending, Confirmed, Preparing, Ready, Out for Delivery, Delivered, Cancelled
  - Validate status transitions (can't skip statuses)
  - Timestamp each status change
  - Estimate delivery time based on status
  - Handle delayed orders
  - Notify customer on status change
- Story Points: 8
- Complexity: High

**US-C6: Cancel Order**
- As a customer, I want to cancel my order if needed so I'm not charged for unwanted food.
- Acceptance Criteria:
  - Can only cancel if status is Pending or Confirmed
  - Full refund if cancelled before Preparing
  - Partial refund during Preparing (50%)
  - No refund after Ready
  - Restore stock on cancellation
  - Restore loyalty points used
  - Record cancellation reason
  - Limit cancellations (max 3 per month)
- Story Points: 13
- Complexity: Very High

#### Sprint 3
**US-C7: Schedule Order for Later**
- As a customer, I want to schedule an order for later so I can plan ahead.
- Acceptance Criteria:
  - Select future date/time
  - Minimum 1 hour in advance
  - Maximum 7 days in advance
  - Validate restaurant open at scheduled time
  - Validate items available at scheduled time
  - Allow modification until 30 min before
  - Handle item unavailability at order time
  - Send reminder 1 hour before
- Story Points: 8
- Complexity: High

**US-C8: Reorder Previous Order**
- As a customer, I want to quickly reorder a previous order so I can save time.
- Acceptance Criteria:
  - Select from order history
  - Check all items still exist
  - Check all items available
  - Apply current prices (not historical)
  - Handle removed items
  - Allow modifications before placing
  - Show price difference if any
  - Maintain original customizations
- Story Points: 8
- Complexity: High

**US-C9: Order Notes and Special Instructions**
- As a customer, I want to add notes to my order so the restaurant knows my preferences.
- Acceptance Criteria:
  - Add general order notes
  - Add per-item notes
  - Character limit (500 for order, 200 per item)
  - Filter inappropriate content
  - Validate notes don't contain contact info
  - Save common notes for reuse
  - Handle special characters safely
  - Make notes visible to restaurant
- Story Points: 5
- Complexity: Medium

---

### MEMBER D: Payment, Delivery & Reports

#### Sprint 1
**US-D1: Calculate Delivery Fee**
- As a system, I want to calculate delivery fees accurately so customers are charged correctly.
- Acceptance Criteria:
  - Base fee by distance zones
  - Zone 1 (0-2 miles): £2.00
  - Zone 2 (2-5 miles): £3.50
  - Zone 3 (5-8 miles): £5.00
  - Free delivery over £30
  - Peak time surcharge (£1.50 during 6-9pm)
  - Bad weather surcharge
  - Validate postcode in delivery area
  - Handle edge cases (boundary postcodes)
- Story Points: 8
- Complexity: High

**US-D2: Apply Discount Codes**
- As a customer, I want to apply discount codes so I can save money.
- Acceptance Criteria:
  - Validate code exists and not expired
  - Validate usage limit not exceeded
  - Validate minimum order amount met
  - Types: percentage, fixed amount, free delivery
  - One code per order
  - Validate not combinable with other offers (configurable)
  - First-order only codes
  - Handle case-insensitive codes
- Story Points: 8
- Complexity: High

**US-D3: Payment Validation**
- As a system, I want to validate payment details so transactions are secure.
- Acceptance Criteria:
  - Validate card number (Luhn algorithm)
  - Validate expiry date (not expired, not >10 years future)
  - Validate CVV format (3 or 4 digits)
  - Validate billing address
  - Detect card type (Visa, Mastercard, Amex)
  - Handle different card number lengths
  - Mask card number in storage
  - Validate payment amount matches order
- Story Points: 8
- Complexity: High

#### Sprint 2
**US-D4: Process Refunds**
- As an admin, I want to process refunds so customers are compensated for issues.
- Acceptance Criteria:
  - Full or partial refund
  - Validate order exists and paid
  - Validate refund doesn't exceed paid amount
  - Multiple partial refunds allowed up to total
  - Record refund reason
  - Restore loyalty points proportionally
  - Notify customer of refund
  - Generate refund reference
  - Handle already refunded orders
- Story Points: 8
- Complexity: High

**US-D5: Delivery Time Estimation**
- As a customer, I want to see estimated delivery time so I can plan accordingly.
- Acceptance Criteria:
  - Base preparation time by order size
  - Add travel time by distance
  - Factor in current order queue
  - Adjust for peak hours (+15 min)
  - Adjust for weather conditions
  - Show range (e.g., 30-45 mins)
  - Update estimate as order progresses
  - Handle delays with new estimates
- Story Points: 8
- Complexity: High

**US-D6: Tip Calculation**
- As a customer, I want to add a tip so I can reward good service.
- Acceptance Criteria:
  - Preset percentages (10%, 15%, 20%)
  - Custom amount option
  - Tip on subtotal (not including delivery/tax)
  - Minimum tip £0.50
  - Maximum tip 100% of subtotal
  - Round to nearest 10p option
  - No tip option
  - Track tips separately for reporting
- Story Points: 5
- Complexity: Medium

#### Sprint 3
**US-D7: Sales Report Generation**
- As an admin, I want to generate sales reports so I can analyze business performance.
- Acceptance Criteria:
  - Filter by date range
  - Filter by category
  - Filter by payment method
  - Calculate total revenue
  - Calculate total orders
  - Calculate average order value
  - Show top selling items
  - Compare to previous period
  - Export to CSV
  - Handle large data sets efficiently
- Story Points: 13
- Complexity: Very High

**US-D8: Popular Items Analytics**
- As an admin, I want to see popular items so I can make business decisions.
- Acceptance Criteria:
  - Rank by quantity sold
  - Rank by revenue generated
  - Filter by time period
  - Show trend (increasing/decreasing)
  - Category breakdown
  - Show with/without promotions
  - Peak ordering times per item
  - Calculate popularity score
- Story Points: 8
- Complexity: High

**US-D9: Revenue Analytics Dashboard**
- As an admin, I want a revenue dashboard so I can monitor business health.
- Acceptance Criteria:
  - Daily/weekly/monthly revenue
  - Compare periods
  - Revenue by payment type
  - Revenue by category
  - Profit margin calculation
  - Tax collected summary
  - Delivery fee revenue
  - Tips collected
  - Average order value trends
  - Handle data aggregation efficiently
- Story Points: 13
- Complexity: Very High

---

## Story Points Summary

### By Member
| Member | Sprint 1 | Sprint 2 | Sprint 3 | Total |
|--------|----------|----------|----------|-------|
| A | 21 | 29 | 34 | 84 |
| B | 24 | 26 | 21 | 71 |
| C | 21 | 34 | 21 | 76 |
| D | 24 | 21 | 34 | 79 |

### By Sprint
| Sprint | Total Points |
|--------|--------------|
| Sprint 1 | 90 |
| Sprint 2 | 110 |
| Sprint 3 | 110 |
| **Total** | **310** |

---

## Planning Poker Evidence

Story points were estimated using Planning Poker with the following scale:
- 1, 2, 3, 5, 8, 13, 21

### Estimation Criteria:
- **5 points**: Simple CRUD with basic validation (3-4 conditions)
- **8 points**: Moderate complexity with multiple validations (5-7 conditions)
- **13 points**: High complexity with many branches and edge cases (8+ conditions)

### Example Planning Poker Session (Document with screenshots in report):
- Each member reveals estimate simultaneously
- Discuss if estimates differ by more than 2 levels
- Re-vote until consensus

---

## PERT Diagram Activities

### Sprint 1 Activities
| ID | Activity | Duration (days) | Dependencies |
|----|----------|-----------------|--------------|
| A1 | Setup project structure | 1 | - |
| A2 | US-A1: Add Menu Item | 3 | A1 |
| A3 | US-A2: Categorize Items | 3 | A1 |
| A4 | US-A3: Update Menu Item | 2 | A2 |
| B1 | US-B1: Registration | 3 | A1 |
| B2 | US-B2: Login | 3 | B1 |
| B3 | US-B3: Manage Addresses | 3 | B1 |
| C1 | US-C1: Add to Cart | 3 | A2 |
| C2 | US-C2: Manage Cart | 3 | C1 |
| C3 | US-C3: Cart Total | 2 | C1 |
| D1 | US-D1: Delivery Fee | 3 | A1 |
| D2 | US-D2: Discount Codes | 3 | A1 |
| D3 | US-D3: Payment Validation | 3 | A1 |
| T1 | Sprint 1 Testing | 2 | All above |

### Critical Path Analysis
Will be calculated based on dependencies - see PERT diagram in report.

---

## COCOMO Estimation

### COCOMO I (Basic)
Estimated KLOC: 4-5 KLOC (Python)
Project Type: Semi-detached

E = a × (KLOC)^b
- a = 3.0, b = 1.12
- E = 3.0 × (4.5)^1.12 = 16.8 person-months

### COCOMO II
Will use detailed cost drivers for more accurate estimation.

---

## Velocity Tracking

### Expected Velocity
- Sprint 1: 90 points / 2 weeks = 45 points/week
- Sprint 2: 110 points / 2 weeks = 55 points/week
- Sprint 3: 110 points / 2 weeks = 55 points/week

Velocity will be tracked and adjusted based on actual completion.

---

## Burndown Chart Tracking

For each sprint:
- Record daily/every-other-day progress
- Plot ideal burndown line
- Plot actual burndown
- Identify blockers and adjustments

---

## Earned Value Management (EVM)

Will track:
- Planned Value (PV)
- Earned Value (EV)
- Actual Cost (AC)
- Schedule Variance (SV = EV - PV)
- Cost Variance (CV = EV - AC)
- Schedule Performance Index (SPI = EV/PV)
- Cost Performance Index (CPI = EV/AC)
