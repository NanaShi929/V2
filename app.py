
from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, session, flash

from catalog import FOOD_ITEMS
from cart import ShoppingCart
from commands import AddItemCommand, RemoveItemCommand, ChangeQuantityCommand, CartInvoker
from customization import build_customized_food, ADD_ONS
from meal_builder import MealComboBuilder

app = Flask(__name__)
app.secret_key = "member-two-development-secret"
invoker = CartInvoker()


def get_cart():
    return ShoppingCart.from_list(session.get("cart_items", []))


def save_cart(cart):
    session["cart_items"] = cart.to_list()
    session.modified = True


@app.get("/")
def index():
    cart = get_cart()
    return render_template(
        "index.html",
        foods=FOOD_ITEMS,
        addons=ADD_ONS,
        cart=cart.items,
        subtotal=cart.total,
    )


@app.post("/cart/add/<int:food_id>")
def add_food(food_id):
    food_data = next((item for item in FOOD_ITEMS if item["id"] == food_id), None)
    if not food_data:
        flash("That food item is not available.", "error")
        return redirect(url_for("index"))

    selected_addons = request.form.getlist("addons")
    customized_food = build_customized_food(food_data, selected_addons)

    cart = get_cart()
    cart_line = {
        "line_id": uuid4().hex,
        "name": customized_food.get_description(),
        "price": round(customized_food.get_cost(), 2),
        "quantity": 1,
        "kind": "food",
    }
    invoker.execute(AddItemCommand(cart, cart_line))
    save_cart(cart)
    flash(f'{cart_line["name"]} added to your cart.', "success")
    return redirect(url_for("index"))


@app.post("/cart/combo")
def add_combo():
    main_name = request.form.get("main_item", "").strip()
    side_name = request.form.get("side_item", "").strip()
    drink_name = request.form.get("drink_item", "").strip()

    main_item = next((x for x in FOOD_ITEMS if x["name"] == main_name), None)
    side_item = next((x for x in FOOD_ITEMS if x["name"] == side_name), None)
    drink_item = next((x for x in FOOD_ITEMS if x["name"] == drink_name), None)

    if not main_item or not side_item or not drink_item:
        flash("Choose one main, one side and one drink to build a combo.", "error")
        return redirect(url_for("index"))

    combo = (
        MealComboBuilder()
        .set_name("Your Meal Combo")
        .add_main(main_item)
        .add_side(side_item)
        .add_drink(drink_item)
        .build()
    )

    cart = get_cart()
    cart_line = {
        "line_id": uuid4().hex,
        "name": combo["name"] + ": " + ", ".join(combo["items"]),
        "price": combo["price"],
        "quantity": 1,
        "kind": "combo",
    }
    invoker.execute(AddItemCommand(cart, cart_line))
    save_cart(cart)
    flash("Your meal combo has been added.", "success")
    return redirect(url_for("index"))


@app.post("/cart/quantity/<line_id>/<int:delta>")
def change_quantity(line_id, delta):
    if delta not in (-1, 1):
        return redirect(url_for("index"))
    cart = get_cart()
    invoker.execute(ChangeQuantityCommand(cart, line_id, delta))
    save_cart(cart)
    return redirect(url_for("index"))


@app.post("/cart/remove/<line_id>")
def remove_item(line_id):
    cart = get_cart()
    invoker.execute(RemoveItemCommand(cart, line_id))
    save_cart(cart)
    flash("Item removed from your cart.", "success")
    return redirect(url_for("index"))


@app.post("/cart/clear")
def clear_cart():
    session["cart_items"] = []
    session.modified = True
    flash("Your cart is now empty.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5002)

from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import DatabaseManager
from menu_factory import MenuItemFactory
from menu_proxy import MenuManagementProxy

app = Flask(__name__)
app.secret_key = "member-one-development-secret"
db = DatabaseManager()
menu_proxy = MenuManagementProxy(db)


def current_user():
    user_id = session.get("user_id")
    return db.get_user_by_id(user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        if user["role"] != "admin":
            flash("Only an administrator can manage the menu.", "error")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


@app.get("/")
def index():
    return render_template("index.html", foods=db.get_menu(), user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password of at least 8 characters.", "error")
            return redirect(url_for("register"))
        if db.get_user_by_email(email):
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register"))
        db.create_user(name, email, generate_password_hash(password))
        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("auth.html", mode="register", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Email or password is incorrect.", "error")
            return redirect(url_for("login"))
        session.clear()
        session["user_id"] = user["id"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("index"))
    return render_template("auth.html", mode="login", user=current_user())


@app.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.get("/admin/menu")
@admin_required
def admin_menu():
    return render_template("admin_menu.html", foods=db.get_menu(), user=current_user())


@app.post("/admin/menu/add")
@admin_required
def add_menu_item():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    price_text = request.form.get("price", "").strip()
    try:
        price = float(price_text)
        if price <= 0:
            raise ValueError
    except ValueError:
        flash("Enter a valid price greater than zero.", "error")
        return redirect(url_for("admin_menu"))
    if not name or not description or category not in MenuItemFactory.CATEGORIES:
        flash("Complete all fields and choose a valid category.", "error")
        return redirect(url_for("admin_menu"))
    item = MenuItemFactory.create(category, name, description, price)
    menu_proxy.add_item(item, current_user())
    flash("Menu item added.", "success")
    return redirect(url_for("admin_menu"))


@app.post("/admin/menu/delete/<int:item_id>")
@admin_required
def delete_menu_item(item_id):
    menu_proxy.delete_item(item_id, current_user())
    flash("Menu item removed.", "success")
    return redirect(url_for("admin_menu"))


if __name__ == "__main__":
    db.initialize()
    app.run(debug=True, port=5001)

