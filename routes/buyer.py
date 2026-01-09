from flask import Blueprint, render_template, session, redirect, request, flash
from models.db import mysql
from models.notifications import add_notification 

buyer_bp = Blueprint('buyer', __name__, url_prefix="/buyer")


# -------------------- BUYER DASHBOARD --------------------
@buyer_bp.route("/dashboard")
def dashboard():
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")
    return render_template("buyer/dashboard.html")


# -------------------- VIEW PRODUCTS --------------------
@buyer_bp.route("/products")
def products():
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    keyword = request.args.get("search", "")
    category = request.args.get("category", "")

    cur = mysql.connection.cursor()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if keyword:
        query += " AND (name LIKE %s OR description LIKE %s)"
        params.append(f"%{keyword}%")
        params.append(f"%{keyword}%")

    if category:
        query += " AND category = %s"
        params.append(category)

    cur.execute(query, params)
    items = cur.fetchall()
    cur.close()

    return render_template(
        "buyer/products.html",
        products=items,
        search=keyword,
        category=category
    )


# -------------------- PRODUCT DETAILS --------------------
@buyer_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    if "role" not in session or session["role"] != "buyer":
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", [product_id])
    product = cur.fetchone()
    cur.close()

    return render_template("buyer/product_detail.html", product=product)


# -------------------- ADD TO CART --------------------
@buyer_bp.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id, quantity FROM cart 
        WHERE user_id = %s AND product_id = %s
    """, (user_id, product_id))
    existing = cur.fetchone()

    if existing:
        cur.execute("UPDATE cart SET quantity=%s WHERE id=%s",
                    (existing[1] + 1, existing[0]))
    else:
        cur.execute("""
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (%s, %s, 1)
        """, (user_id, product_id))

    mysql.connection.commit()
    cur.close()

    flash("Item added to cart!")
    return redirect("/buyer/products")


# -------------------- VIEW CART --------------------
@buyer_bp.route("/cart")
def cart():
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT cart.id, products.name, products.price, cart.quantity, products.id
        FROM cart 
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = %s
    """, [user_id])

    items = cur.fetchall()
    cur.close()

    total = sum(item[2] * item[3] for item in items)

    return render_template("buyer/cart.html", cart_items=items, total=total)


# -------------------- UPDATE CART QUANTITY --------------------
@buyer_bp.route("/cart/update/<int:cart_id>", methods=["POST"])
def update_cart(cart_id):
    qty = int(request.form['quantity'])

    cur = mysql.connection.cursor()
    cur.execute("UPDATE cart SET quantity=%s WHERE id=%s", (qty, cart_id))
    mysql.connection.commit()
    cur.close()

    flash("Cart updated!")
    return redirect("/buyer/cart")


# -------------------- DELETE FROM CART --------------------
@buyer_bp.route("/cart/delete/<int:cart_id>")
def delete(cart_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE id=%s", [cart_id])
    mysql.connection.commit()
    cur.close()

    flash("Item removed!")
    return redirect("/buyer/cart")


# -------------------- CHECKOUT --------------------
@buyer_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # ---------------- GET: show checkout page ----------------
    if request.method == "GET":
        cur.execute("""
            SELECT products.name, products.image, products.price, cart.quantity
            FROM cart
            JOIN products ON cart.product_id = products.id
            WHERE cart.user_id = %s
        """, [user_id])

        items = cur.fetchall()
        cur.close()

        if not items:
            flash("Your cart is empty!")
            return redirect("/buyer/cart")

        return render_template("buyer/checkout.html", items=items)

    # ---------------- POST: place order ----------------
    address = request.form["address"]

    cur.execute("""
        SELECT cart.product_id, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = %s
    """, [user_id])

    cart_items = cur.fetchall()

    if not cart_items:
        cur.close()
        flash("Your cart is empty!")
        return redirect("/buyer/cart")

    total = sum(item[1] * item[2] for item in cart_items)

    # Create order
    cur.execute("""
        INSERT INTO orders (buyer_id, total, status, address)
        VALUES (%s, %s, %s, %s)
    """, (user_id, total, "pending", address))
    order_id = cur.lastrowid

    # Insert order items + notify sellers
    for item in cart_items:
        product_id, price, qty = item

        cur.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, product_id, qty, price))

        cur.execute("SELECT seller_id FROM products WHERE id=%s", [product_id])
        seller = cur.fetchone()

        if seller:
            add_notification(
                seller[0],
                f"You received a new order (Order #{order_id})."
            )

    # Notify admin (safe)
    try:
        add_notification(1, f"A new order (Order #{order_id}) has been placed.")
    except:
        pass

    # Clear cart
    cur.execute("DELETE FROM cart WHERE user_id=%s", [user_id])

    mysql.connection.commit()
    cur.close()

    return redirect(f"/buyer/order-success/{order_id}")


# -------------------- ORDER SUCCESS --------------------
@buyer_bp.route("/order-success/<int:order_id>")
def order_success(order_id):
    return render_template("buyer/order_success.html", order_id=order_id)


# -------------------- VIEW ALL ORDERS --------------------
@buyer_bp.route("/orders")
def orders():
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            id,
            total,
            status,
            created_at,
            estimated_delivery
        FROM orders
        WHERE buyer_id = %s
        ORDER BY id DESC
    """, [user_id])

    orders = cur.fetchall()
    cur.close()

    return render_template("buyer/orders.html", orders=orders)



# -------------------- VIEW SINGLE ORDER --------------------
@buyer_bp.route("/order/<int:order_id>")
def view_single_order(order_id):
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # FIXED column names
    cur.execute("""
        SELECT id, total, status, address, created_at, estimated_delivery
        FROM orders
        WHERE id=%s AND buyer_id=%s
    """, (order_id, user_id))
    order = cur.fetchone()

    cur.execute("""
        SELECT products.name, order_items.price, order_items.quantity
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id=%s
    """, [order_id])
    items = cur.fetchall()

    cur.close()

    return render_template("buyer/order.html", order=order, items=items)


# -------------------- CANCEL ORDER --------------------
@buyer_bp.route("/order/cancel/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    if 'role' not in session or session['role'] != "buyer":
        return redirect("/auth/login")

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Check ownership and status
    cur.execute("""
        SELECT status FROM orders
        WHERE id=%s AND buyer_id=%s
    """, (order_id, user_id))
    result = cur.fetchone()

    if not result:
        flash("Order not found!")
        return redirect("/buyer/orders")

    if result[0] != "pending":
        flash("Only pending orders can be cancelled.")
        return redirect(f"/buyer/order/{order_id}")

    # Update status
    cur.execute("""
        UPDATE orders 
        SET status='cancelled'
        WHERE id=%s
    """, [order_id])

    mysql.connection.commit()
    cur.close()

    flash("Order cancelled!")
    return redirect("/buyer/orders")
