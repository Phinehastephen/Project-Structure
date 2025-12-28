from flask import Blueprint, render_template, session, redirect, request, flash, current_app
from werkzeug.utils import secure_filename
from models.db import mysql
from models.notifications import add_notification
import os


seller_bp = Blueprint('seller', __name__, url_prefix="/seller")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}


# -------------------- SELLER DASHBOARD --------------------
@seller_bp.route("/dashboard")
def dashboard():
    if 'role' not in session or session['role'] != "seller":
        return redirect("/auth/login")

    seller_id = session['user_id']
    cur = mysql.connection.cursor()

    # Total products
    cur.execute("SELECT COUNT(*) FROM products WHERE seller_id=%s", [seller_id])
    total_products = cur.fetchone()[0]

    # Total orders
    cur.execute("""
        SELECT COUNT(*)
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE p.seller_id=%s
    """, [seller_id])
    total_orders = cur.fetchone()[0]

    # Fetch unread notifications
    cur.execute("""
        SELECT message, created_at 
        FROM notifications 
        WHERE user_id=%s AND is_read=0
        ORDER BY created_at DESC
    """, [seller_id])
    notifications = cur.fetchall()

    cur.close()

    return render_template("seller/dashboard.html",
                           total_products=total_products,
                           total_orders=total_orders,
                           notifications=notifications)



# -------------------- PRODUCT LIST --------------------
@seller_bp.route("/products")
def products():
    if 'role' not in session or session['role'] != "seller":
        return redirect("/auth/login")

    seller_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE seller_id=%s", [seller_id])
    items = cur.fetchall()
    cur.close()

    return render_template("seller/products.html", products=items)


# -------------------- ADD PRODUCT --------------------
@seller_bp.route("/add-product", methods=["GET", "POST"])
def add_product():
    if 'role' not in session or session['role'] != "seller":
        return redirect("/auth/login")

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]
        seller_id = session['user_id']

        # HANDLE IMAGE
        image = request.files.get("image")
        filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename) # type: ignore
            image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename)) # type: ignore

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products (name, description, price, stock, seller_id, image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, description, price, stock, seller_id, filename))

        mysql.connection.commit()
        cur.close()

        return redirect("/seller/products")

    return render_template("seller/add_product.html")


# -------------------- EDIT PRODUCT --------------------
@seller_bp.route("/edit-product/<int:product_id>", methods=['GET', 'POST'])
def edit_product(product_id):
    if 'role' not in session or session['role'] != "seller":
        return redirect("/auth/login")

    cur = mysql.connection.cursor()

    # Get product details
    cur.execute("SELECT * FROM products WHERE id=%s", [product_id])
    product = cur.fetchone()

    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']

        cur.execute("""
            UPDATE products 
            SET name=%s, description=%s, price=%s, stock=%s 
            WHERE id=%s
        """, (name, description, price, stock, product_id))

        mysql.connection.commit()
        cur.close()

        flash("Product updated successfully!")
        return redirect("/seller/products")

    cur.close()
    return render_template("seller/edit_product.html", product=product)


# -------------------- DELETE PRODUCT --------------------
@seller_bp.route("/delete-product/<int:product_id>")
def delete_product(product_id):
    if 'role' not in session or session['role'] != "seller":
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", [product_id])
    mysql.connection.commit()
    cur.close()

    flash("Product deleted!")
    return redirect("/seller/products")


# -------------------- Orders --------------------
@seller_bp.route("/orders")
def seller_orders():
    if "role" not in session or session["role"] != "seller":
        return redirect("/auth/login")

    seller_id = session["user_id"]

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT o.id, o.user_id, o.total_amount, o.order_status, o.created_at
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE p.seller_id = %s
        GROUP BY o.id
        ORDER BY o.id DESC
    """, [seller_id])

    orders = cur.fetchall()
    cur.close()

    return render_template("seller/orders.html", orders=orders)


# --------------------Approve ORDER -----------------
@seller_bp.route("/orders/approve/<int:order_id>", methods=["POST"])
def approve_order(order_id):
    if "role" not in session or session["role"] != "seller":
        return redirect("/auth/login")

    seller_id = session["user_id"]

    cur = mysql.connection.cursor()

    # Update status
    cur.execute("""
        UPDATE orders SET order_status='approved'
        WHERE id=%s
    """, [order_id])

    mysql.connection.commit()
    cur.close()

    flash("Order approved!")
    return redirect("/seller/orders")


# --------------------Mark Order as Shipped -----------------
@seller_bp.route("/orders/shipped/<int:order_id>", methods=["POST"])
def mark_shipped(order_id):
    if "role" not in session or session["role"] != "seller":
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET order_status='shipped' WHERE id=%s", [order_id])
    mysql.connection.commit()
    cur.close()

    flash("Order marked as shipped!")
    return redirect("/seller/orders")


# -------------------- Mark Order as Delivered -----------------
@seller_bp.route("/orders/delivered/<int:order_id>", methods=["POST"])
def mark_delivered(order_id):
    if "role" not in session or session["role"] != "seller":
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET order_status='delivered' WHERE id=%s", [order_id])
    mysql.connection.commit()
    cur.close()

    flash("Order delivered!")
    return redirect("/seller/orders")


# --------------------- Cancel Order --------------------
@seller_bp.route("/orders/cancel/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    if "role" not in session or session["role"] != "seller":
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET order_status='cancelled' WHERE id=%s", [order_id])
    mysql.connection.commit()
    cur.close()

    flash("Order cancelled.")
    return redirect("/seller/orders")


# -------------------- Dashboard --------------------
@seller_bp.route("/sales-data")
def sales_data():
    if 'role' not in session or session['role'] != "seller":
        return {"error": "Unauthorized"}

    seller_id = session['user_id']
    cur = mysql.connection.cursor()

    # Monthly sales (sum of order_items.price * quantity)
    cur.execute("""
        SELECT 
            MONTH(o.created_at) AS month_num,
            SUM(oi.price * oi.quantity) AS total_sales
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE p.seller_id = %s
        GROUP BY MONTH(o.created_at)
        ORDER BY MONTH(o.created_at)
    """, [seller_id])

    result = cur.fetchall()
    cur.close()

    months = [row[0] for row in result]
    totals = [float(row[1]) for row in result]

    return {"months": months, "totals": totals}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}
