"""
Takeaway Menu System - Main Application
CO3095 Group Assignment - Project 19

A text-based takeaway ordering system.
"""

import sys
from datetime import datetime, date

from storage import get_storage
from menu_manager import MenuManager
from customer_manager import CustomerManager
from order_manager import OrderManager
from payment_delivery_manager import PaymentDeliveryManager
from models import DietaryTag, ItemSize, SpiceLevel, ItemCustomization, DeliveryZone


class TakeawayApp:
    """Main application class for the Takeaway Menu System."""
    
    def __init__(self):
        self.storage = get_storage()
        self.menu_manager = MenuManager(self.storage)
        self.customer_manager = CustomerManager(self.storage)
        self.order_manager = OrderManager(self.storage)
        self.payment_manager = PaymentDeliveryManager(self.storage)
        
        self.current_customer = None
        self.current_cart_id = None
        self._setup_sample_data()
    
    def _setup_sample_data(self):
        """Set up sample menu data for testing."""
        # Create categories
        categories = [
            ("cat1", "Starters", "Appetizers and small plates"),
            ("cat2", "Main Courses", "Main dishes"),
            ("cat3", "Desserts", "Sweet treats"),
            ("cat4", "Drinks", "Beverages")
        ]
        
        from models import Category
        for cat_id, name, desc in categories:
            if not self.storage.get_category(cat_id):
                cat = Category(id=cat_id, name=name, description=desc)
                self.storage.save_category(cat)
        
        # Create sample menu items
        items = [
            ("item1", "Spring Rolls", "Crispy vegetable spring rolls", 5.50, "cat1", [DietaryTag.VEGETARIAN]),
            ("item2", "Chicken Satay", "Grilled chicken skewers with peanut sauce", 6.50, "cat1", []),
            ("item3", "Pad Thai", "Classic Thai noodles with prawns", 12.00, "cat2", []),
            ("item4", "Green Curry", "Spicy Thai green curry with vegetables", 11.50, "cat2", [DietaryTag.VEGETARIAN, DietaryTag.VEGAN, DietaryTag.GLUTEN_FREE]),
            ("item5", "Mango Sticky Rice", "Sweet coconut rice with fresh mango", 6.00, "cat3", [DietaryTag.VEGETARIAN, DietaryTag.VEGAN]),
            ("item6", "Thai Iced Tea", "Sweet creamy Thai tea", 3.50, "cat4", [DietaryTag.VEGETARIAN]),
        ]
        
        from models import MenuItem
        for item_id, name, desc, price, cat_id, tags in items:
            if not self.storage.get_menu_item(item_id):
                item = MenuItem(
                    id=item_id, name=name, description=desc, price=price,
                    category_id=cat_id, dietary_tags=tags, stock_quantity=50
                )
                self.storage.save_menu_item(item)
    
    def run(self):
        """Run the main application loop."""
        print("\n" + "="*50)
        print("  WELCOME TO THAI TAKEAWAY")
        print("  Takeaway Menu System")
        print("="*50)
        
        while True:
            self._show_main_menu()
            choice = input("\nEnter choice: ").strip()
            
            if choice == "1":
                self._browse_menu()
            elif choice == "2":
                self._search_menu()
            elif choice == "3":
                self._view_cart()
            elif choice == "4":
                self._checkout()
            elif choice == "5":
                self._customer_menu()
            elif choice == "6":
                self._admin_menu()
            elif choice == "0":
                print("\nThank you for visiting! Goodbye.")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please try again.")
    
    def _show_main_menu(self):
        """Display the main menu."""
        print("\n--- MAIN MENU ---")
        print("1. Browse Menu")
        print("2. Search Menu")
        print("3. View Cart")
        print("4. Checkout")
        print("5. Customer Account")
        print("6. Admin Panel")
        print("0. Exit")
        
        if self.current_customer:
            print(f"\n[Logged in as: {self.current_customer.first_name}]")
        if self.current_cart_id:
            cart = self.storage.get_cart(self.current_cart_id)
            if cart and cart.items:
                print(f"[Cart: {len(cart.items)} items - £{cart.total:.2f}]")
    
    def _browse_menu(self):
        """Browse menu by category."""
        categories = self.storage.get_all_categories()
        
        print("\n--- MENU CATEGORIES ---")
        for i, cat in enumerate(categories, 1):
            items_count = len(self.storage.get_items_by_category(cat.id))
            print(f"{i}. {cat.name} ({items_count} items)")
        print("0. Back")
        
        choice = input("\nSelect category: ").strip()
        if choice == "0":
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                self._show_category_items(categories[idx])
        except ValueError:
            print("Invalid choice.")
    
    def _show_category_items(self, category):
        """Show items in a category."""
        items = self.storage.get_items_by_category(category.id)
        
        print(f"\n--- {category.name.upper()} ---")
        if not items:
            print("No items in this category.")
            return
        
        for i, item in enumerate(items, 1):
            status = "✓" if item.is_available else "✗"
            tags = ", ".join([t.value if hasattr(t, 'value') else t for t in item.dietary_tags])
            tags_str = f" [{tags}]" if tags else ""
            print(f"{i}. {status} {item.name} - £{item.price:.2f}{tags_str}")
            print(f"   {item.description[:50]}...")
        print("0. Back")
        
        choice = input("\nSelect item to add to cart (or 0 to go back): ").strip()
        if choice == "0":
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                self._add_item_to_cart(items[idx])
        except ValueError:
            print("Invalid choice.")
    
    def _add_item_to_cart(self, item):
        """Add an item to cart."""
        if not item.is_available:
            print(f"\nSorry, {item.name} is not available.")
            return
        
        print(f"\n--- ADD {item.name.upper()} ---")
        print(f"Price: £{item.price:.2f}")
        
        # Get quantity
        qty = input("Quantity (1-10): ").strip()
        try:
            quantity = int(qty)
            if quantity < 1 or quantity > 10:
                print("Quantity must be between 1 and 10.")
                return
        except ValueError:
            quantity = 1
        
        # Create or get cart
        if not self.current_cart_id:
            import uuid
            self.current_cart_id = str(uuid.uuid4())
        
        # Add to cart
        result = self.order_manager.add_to_cart(
            self.current_cart_id, item.id, quantity
        )
        
        if result["success"]:
            print(f"\n✓ Added {quantity}x {item.name} to cart")
            print(f"  Cart total: £{result['cart'].total:.2f}")
        else:
            print(f"\n✗ Error: {result['error']}")
    
    def _search_menu(self):
        """Search menu items."""
        print("\n--- SEARCH MENU ---")
        query = input("Search term: ").strip()
        
        if not query:
            print("Please enter a search term.")
            return
        
        result = self.menu_manager.search_items(query=query)
        
        if result["success"] and result["items"]:
            print(f"\nFound {result['total']} items:")
            for i, item in enumerate(result["items"], 1):
                print(f"{i}. {item.name} - £{item.price:.2f}")
            
            choice = input("\nSelect item to add (or 0 to go back): ").strip()
            if choice != "0":
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(result["items"]):
                        self._add_item_to_cart(result["items"][idx])
                except ValueError:
                    pass
        else:
            print("No items found.")
    
    def _view_cart(self):
        """View and manage cart."""
        if not self.current_cart_id:
            print("\nYour cart is empty.")
            return
        
        cart = self.storage.get_cart(self.current_cart_id)
        if not cart or not cart.items:
            print("\nYour cart is empty.")
            return
        
        print("\n--- YOUR CART ---")
        for i, item in enumerate(cart.items, 1):
            menu_item = self.storage.get_menu_item(item.menu_item_id)
            name = menu_item.name if menu_item else "Unknown"
            print(f"{i}. {item.quantity}x {name} - £{item.line_total:.2f}")
        
        print(f"\nSubtotal: £{cart.subtotal:.2f}")
        if cart.discount_amount > 0:
            print(f"Discount: -£{cart.discount_amount:.2f}")
        print(f"VAT (20%): £{cart.tax_amount:.2f}")
        print(f"Delivery: £{cart.delivery_fee:.2f}")
        print(f"TOTAL: £{cart.total:.2f}")
        
        print("\nOptions:")
        print("1. Remove item")
        print("2. Clear cart")
        print("3. Apply discount code")
        print("0. Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            item_num = input("Item number to remove: ").strip()
            try:
                idx = int(item_num) - 1
                if 0 <= idx < len(cart.items):
                    self.order_manager.remove_from_cart(
                        self.current_cart_id, cart.items[idx].id
                    )
                    print("Item removed.")
            except ValueError:
                pass
        elif choice == "2":
            self.order_manager.clear_cart(self.current_cart_id)
            print("Cart cleared.")
        elif choice == "3":
            code = input("Enter discount code: ").strip()
            result = self.payment_manager.validate_discount_code(
                code, cart.subtotal
            )
            if result["valid"]:
                cart.discount_code = code.upper()
                cart.discount_amount = result["discount"]
                self.storage.save_cart(cart)
                print(f"✓ Code applied! You save £{result['discount']:.2f}")
            else:
                print(f"✗ {result['error']}")
    
    def _checkout(self):
        """Process checkout."""
        if not self.current_cart_id:
            print("\nYour cart is empty.")
            return
        
        cart = self.storage.get_cart(self.current_cart_id)
        if not cart or not cart.items:
            print("\nYour cart is empty.")
            return
        
        print("\n--- CHECKOUT ---")
        
        # Check if logged in
        if not self.current_customer:
            print("Please login or register to checkout.")
            self._customer_menu()
            if not self.current_customer:
                return
        
        # Get delivery address
        print("\nDelivery Address:")
        if self.current_customer.addresses:
            print("Your saved addresses:")
            for i, addr in enumerate(self.current_customer.addresses, 1):
                default = " (default)" if addr.is_default else ""
                print(f"{i}. {addr.line1}, {addr.postcode}{default}")
            print(f"{len(self.current_customer.addresses) + 1}. Enter new address")
            
            choice = input("Select address: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.current_customer.addresses):
                    delivery_address = self.current_customer.addresses[idx]
                else:
                    delivery_address = self._get_new_address()
            except ValueError:
                delivery_address = self._get_new_address()
        else:
            delivery_address = self._get_new_address()
        
        if not delivery_address:
            print("Checkout cancelled.")
            return
        
        # Calculate delivery fee
        fee_result = self.payment_manager.calculate_delivery_fee(
            delivery_address.postcode, cart.subtotal
        )
        if not fee_result["success"]:
            print(f"✗ {fee_result['error']}")
            return
        
        cart.delivery_fee = fee_result["fee"]
        
        # Update cart totals
        from order_manager import OrderManager
        self.order_manager._recalculate_cart(cart)
        
        # Show order summary
        print("\n--- ORDER SUMMARY ---")
        print(f"Subtotal: £{cart.subtotal:.2f}")
        print(f"Delivery: £{cart.delivery_fee:.2f}")
        print(f"VAT: £{cart.tax_amount:.2f}")
        print(f"TOTAL: £{cart.total:.2f}")
        
        # Confirm order
        confirm = input("\nConfirm order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
        
        # Place order
        result = self.order_manager.place_order(
            self.current_cart_id,
            self.current_customer.id,
            delivery_address,
            "card"
        )
        
        if result["success"]:
            order = result["order"]
            print("\n" + "="*40)
            print("  ORDER PLACED SUCCESSFULLY!")
            print("="*40)
            print(f"Order Number: {order.order_number}")
            print(f"Total: £{order.total:.2f}")
            print(f"Estimated Delivery: {order.estimated_delivery_time.strftime('%H:%M')}")
            print("="*40)
            
            # Award loyalty points
            if self.current_customer:
                self.customer_manager.earn_points(
                    self.current_customer.id, order.total, order.id
                )
            
            self.current_cart_id = None
        else:
            print(f"\n✗ Order failed: {result['error']}")
    
    def _get_new_address(self):
        """Get a new delivery address from user."""
        print("\nEnter delivery address:")
        line1 = input("Address line 1: ").strip()
        line2 = input("Address line 2 (optional): ").strip()
        city = input("City: ").strip()
        postcode = input("Postcode: ").strip()
        
        if not line1 or not city or not postcode:
            return None
        
        from models import Address
        address = Address(
            line1=line1, line2=line2, city=city,
            postcode=postcode.upper()
        )
        
        # Determine delivery zone
        address.delivery_zone = self.payment_manager._get_delivery_zone(
            postcode.upper().replace(' ', '')
        )
        
        return address
    
    def _customer_menu(self):
        """Customer account menu."""
        print("\n--- CUSTOMER ACCOUNT ---")
        
        if self.current_customer:
            print(f"Logged in as: {self.current_customer.first_name} {self.current_customer.last_name}")
            print(f"Loyalty Points: {self.current_customer.loyalty_points.total_points}")
            print("\n1. View Order History")
            print("2. Manage Addresses")
            print("3. Logout")
            print("0. Back")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                self._view_order_history()
            elif choice == "2":
                self._manage_addresses()
            elif choice == "3":
                self.current_customer = None
                print("Logged out successfully.")
        else:
            print("1. Login")
            print("2. Register")
            print("0. Back")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                self._login()
            elif choice == "2":
                self._register()
    
    def _login(self):
        """Login a customer."""
        print("\n--- LOGIN ---")
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        result = self.customer_manager.login(email, password)
        
        if result["success"]:
            self.current_customer = result["customer"]
            print(f"\n✓ Welcome back, {self.current_customer.first_name}!")
        else:
            print(f"\n✗ {result['error']}")
    
    def _register(self):
        """Register a new customer."""
        print("\n--- REGISTER ---")
        email = input("Email: ").strip()
        password = input("Password (min 8 chars, upper, lower, number, special): ").strip()
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        phone = input("Phone (UK format): ").strip()
        
        result = self.customer_manager.register_customer(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            terms_accepted=True
        )
        
        if result["success"]:
            self.current_customer = result["customer"]
            print(f"\n✓ Welcome, {self.current_customer.first_name}! Account created.")
        else:
            print(f"\n✗ {result['error']}")
    
    def _view_order_history(self):
        """View customer order history."""
        if not self.current_customer:
            return
        
        result = self.customer_manager.get_order_history(self.current_customer.id)
        
        if result["success"] and result["orders"]:
            print("\n--- ORDER HISTORY ---")
            for order in result["orders"]:
                print(f"\n{order.order_number} - {order.created_at.strftime('%d/%m/%Y %H:%M')}")
                print(f"  Status: {order.status.value}")
                print(f"  Total: £{order.total:.2f}")
        else:
            print("\nNo orders found.")
    
    def _manage_addresses(self):
        """Manage customer addresses."""
        if not self.current_customer:
            return
        
        print("\n--- YOUR ADDRESSES ---")
        if self.current_customer.addresses:
            for i, addr in enumerate(self.current_customer.addresses, 1):
                default = " (default)" if addr.is_default else ""
                print(f"{i}. {addr.line1}, {addr.city}, {addr.postcode}{default}")
        else:
            print("No saved addresses.")
        
        print("\n1. Add new address")
        print("0. Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            addr = self._get_new_address()
            if addr:
                self.customer_manager.add_address(
                    self.current_customer.id,
                    addr.line1, addr.line2, addr.city, addr.postcode
                )
                print("Address added.")
    
    def _admin_menu(self):
        """Admin panel."""
        print("\n--- ADMIN PANEL ---")
        print("1. View Sales Report")
        print("2. View Popular Items")
        print("3. Add Menu Item")
        print("4. Create Discount Code")
        print("0. Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            self._view_sales_report()
        elif choice == "2":
            self._view_popular_items()
        elif choice == "3":
            self._add_menu_item()
        elif choice == "4":
            self._create_discount()
    
    def _view_sales_report(self):
        """View sales report."""
        today = date.today()
        start = today.replace(day=1)
        
        result = self.payment_manager.generate_sales_report(start, today)
        
        if result["success"]:
            report = result["report"]
            print("\n--- SALES REPORT ---")
            print(f"Period: {report.start_date} to {report.end_date}")
            print(f"Total Orders: {report.total_orders}")
            print(f"Total Revenue: £{report.total_revenue:.2f}")
            print(f"Net Revenue: £{report.net_revenue:.2f}")
            print(f"Average Order: £{report.average_order_value:.2f}")
    
    def _view_popular_items(self):
        """View popular items."""
        result = self.payment_manager.get_popular_items()
        
        if result["success"] and result["items"]:
            print("\n--- POPULAR ITEMS ---")
            for i, item in enumerate(result["items"], 1):
                print(f"{i}. {item.item_name}")
                print(f"   Sold: {item.quantity_sold} | Revenue: £{item.revenue:.2f}")
    
    def _add_menu_item(self):
        """Add a new menu item."""
        print("\n--- ADD MENU ITEM ---")
        
        # Show categories
        categories = self.storage.get_all_categories()
        print("Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.name}")
        
        name = input("\nItem name: ").strip()
        description = input("Description: ").strip()
        price = input("Price (£): ").strip()
        cat_idx = input("Category number: ").strip()
        
        try:
            price_float = float(price)
            cat_id = categories[int(cat_idx) - 1].id
            
            result = self.menu_manager.add_menu_item(
                name=name,
                description=description,
                price=price_float,
                category_id=cat_id
            )
            
            if result["success"]:
                print(f"\n✓ Added {name} to menu.")
            else:
                print(f"\n✗ {result['error']}")
        except (ValueError, IndexError) as e:
            print(f"\n✗ Invalid input: {e}")
    
    def _create_discount(self):
        """Create a discount code."""
        print("\n--- CREATE DISCOUNT CODE ---")
        code = input("Code: ").strip()
        value = input("Discount % (e.g., 10 for 10%): ").strip()
        
        try:
            from models import DiscountType
            result = self.payment_manager.create_discount_code(
                code=code,
                discount_type=DiscountType.PERCENTAGE,
                value=float(value)
            )
            
            if result["success"]:
                print(f"\n✓ Created code: {code.upper()}")
            else:
                print(f"\n✗ {result['error']}")
        except ValueError:
            print("\n✗ Invalid value.")


def main():
    """Main entry point."""
    app = TakeawayApp()
    app.run()


if __name__ == "__main__":
    main()
