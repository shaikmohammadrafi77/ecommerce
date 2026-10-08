from flask import Blueprint, render_template, request, redirect, session, url_for
from .models import Product, User, Order

main = Blueprint("main", __name__)


# ---------------- HOME ----------------
@main.route("/")
def index():
    products = Product.get_all()
    return render_template("index.html", products=products)


# ---------------- LOGIN ----------------
@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "login.html",
                error="Email and password are required."
            )

        user = User.login(email, password)

        if user:
            session["user"] = user["id"]
            session["user_name"] = user["name"]

            if "cart" not in session:
                session["cart"] = []

            return redirect(url_for("main.index"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@main.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("user_name", None)
    session.pop("cart", None)

    return redirect(url_for("main.index"))


# ---------------- REGISTER ----------------
@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template(
                "register.html",
                error="All fields are required."
            )

        try:
            User.register(name, email, password)

        except Exception:
            return render_template(
                "register.html",
                error="Registration failed. Email may already exist."
            )

        return redirect(url_for("main.login"))

    return render_template("register.html")


# ---------------- ADD TO CART ----------------
@main.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    product_id = request.form.get("product_id")

    if not product_id:
        return redirect(url_for("main.index"))

    cart = session.get("cart", [])

    cart.append(product_id)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("main.cart"))


# ---------------- REMOVE FROM CART ----------------
@main.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():

    try:
        index = int(request.form.get("index", -1))
    except ValueError:
        index = -1

    cart = session.get("cart", [])

    if 0 <= index < len(cart):
        cart.pop(index)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("main.cart"))


# ---------------- VIEW CART ----------------
@main.route("/cart")
def cart():

    cart_ids = session.get("cart", [])

    items = []
    total = 0.0

    all_products = Product.get_all()

    for item_id in cart_ids:

        for product in all_products:

            if str(product["id"]) == str(item_id):

                items.append(product)
                total += float(product["price"])

                break

    return render_template(
        "cart.html",
        items=items,
        total=total
    )


# ---------------- CHECKOUT ----------------
@main.route("/checkout", methods=["POST"])
def checkout():

    # User must be logged in
    if "user" not in session:
        return redirect(url_for("main.login"))

    cart_ids = session.get("cart", [])

    # Empty cart
    if not cart_ids:
        return redirect(url_for("main.cart"))

    items = []

    all_products = Product.get_all()

    for item_id in cart_ids:

        for product in all_products:

            if str(product["id"]) == str(item_id):

                items.append(product)
                break

    if not items:
        return redirect(url_for("main.cart"))

    try:

        order_id = Order.create(
            session["user"],
            items
        )

    except Exception:

        return render_template(
            "cart.html",
            items=items,
            total=sum(float(p["price"]) for p in items),
            error="Unable to create order. Please try again."
        )

    # Clear cart after successful order
    session["cart"] = []
    session.modified = True

    user_name = session.get("user_name")

    return render_template(
        "order_success.html",
        order_id=order_id,
        user_name=user_name
    )