
# Member 2 – Cart and Customization

A standalone Flask web application for managing a shopping cart, customizing individual food items and building meal combos.

## Features
- Browse a small food menu.
- Add items to the cart with optional extras.
- Increase/decrease item quantities and remove cart lines.
- Build a meal combo with one main item, one side and one drink.
- View the cart subtotal.
- Cart data is stored in the Flask session.

## Design patterns
1. **Command – `commands.py`:** Add, remove and quantity changes are represented as command objects. `CartInvoker` executes them. Add and remove commands also support undo.
2. **Decorator – `decorators.py` and `customization.py`:** add-ons wrap a basic food object and change its description and price without modifying the original food class.
3. **Builder – `meal_builder.py`:** constructs a meal combo step by step and validates that it contains one main, one side and one drink.
=======
# Member 1 – Authentication and Restaurant Menu

A standalone Flask application for customer registration/login and restaurant menu browsing/management.

## Features
- Customer registration and login with hashed passwords.
- Session-based login and logout.
- Restaurant menu grouped by food category.
- Admin-only menu management: add and remove menu items.
- SQLite database.
- Unit tests for the three assigned design patterns.

## Design patterns
1. **Singleton – `DatabaseManager`:** ensures the application uses one shared database manager configuration.
2. **Factory Method – `MenuItemFactory`:** creates menu items after validating their category and details.
3. **Proxy – `MenuManagementProxy`:** checks administrator permissions before allowing menu changes.


## Run on Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5002.

Open http://127.0.0.1:5001.

The SQLite database is created automatically on first run.

## Demo administrator account
- Email: `admin@goodbite.local`
- Password: `Admin123!`

Change the demo password before using this application beyond local coursework testing. New registrations receive the customer role; the registration form cannot grant administrator access.


## Run tests
```powershell
pytest -v
```

## GitHub (independent repository)

Create a separate repository, for example `Member2-Cart-Customization`, then:
```powershell
git init
git add .
git commit -m "Implement cart and customization design patterns"
git branch -M feature/cart-customization
git remote add origin https://github.com/USERNAME/Member2-Cart-Customization.git
git push -u origin feature/cart-customization

Create a new repository, for example `Member1-Authentication-RestaurantMenu`, then:
```powershell
git init
git add .
git commit -m "Implement authentication and restaurant menu"
git branch -M feature/auth-restaurant-menu
git remote add origin https://github.com/USERNAME/Member1-Authentication-RestaurantMenu.git
git push -u origin feature/auth-restaurant-menu

```
Replace `USERNAME` with your GitHub username.
