from flask import (
    Blueprint, render_template, request,
    redirect, session, flash
)
from models.db import mysql

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -------------------- SECURITY --------------------
def admin_only():
    return "role" in session and session["role"] == "admin"


# -------------------- DASHBOARD --------------------
@admin_bp.route("/dashboard")
def dashboard():
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users WHERE role='buyer'")
    total_buyers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role='seller'")
    total_sellers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    cur.close()

    return render_template(
        "admin/dashboard.html",
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_orders=total_orders
    )


# -------------------- VIEW ALL ORDERS --------------------
@admin_bp.route("/orders")
def orders():
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            o.id,
            u.name,
            o.total_amount,
            o.order_status,
            o.created_at,
            o.estimated_delivery
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
    """)
    all_orders = cur.fetchall()
    cur.close()

    return render_template("admin/orders.html", orders=all_orders)


# -------------------- VIEW FULL ORDER DETAILS --------------------
@admin_bp.route("/orders/view/<int:order_id>")
def view_order(order_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            o.id,
            o.total_amount,
            o.order_status,
            o.address,
            o.created_at,
            u.name,
            u.email,
            o.estimated_delivery
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = %s
    """, [order_id])
    order = cur.fetchone()

    cur.execute("""
        SELECT p.name, p.price, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, [order_id])
    items = cur.fetchall()

    cur.close()

    return render_template("admin/order_view.html", order=order, items=items)


# -------------------- UPDATE ORDER STATUS --------------------
@admin_bp.route("/orders/update/<int:order_id>", methods=["POST"])
def admin_update_order(order_id):
    if not admin_only():
        return redirect("/auth/login")

    new_status = request.form.get("status")

    
    estimate = request.form.get("estimated_delivery", None)

    cur = mysql.connection.cursor()

    if estimate:
        cur.execute("""
            UPDATE orders 
            SET order_status=%s, estimated_delivery=%s
            WHERE id=%s
        """, (new_status, estimate, order_id))
    else:
        cur.execute("""
            UPDATE orders 
            SET order_status=%s
            WHERE id=%s
        """, (new_status, order_id))

    mysql.connection.commit()
    cur.close()

    flash("Order status updated!")
    return redirect("/admin/orders")


# -------------------- DELETE ORDER --------------------
@admin_bp.route("/orders/delete/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM order_items WHERE order_id=%s", [order_id])
    cur.execute("DELETE FROM orders WHERE id=%s", [order_id])
    mysql.connection.commit()
    cur.close()

    flash("Order deleted!")
    return redirect("/admin/orders")


# -------------------- VIEW USERS --------------------
@admin_bp.route("/users")
def users():
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, email, role, active, approved, created_at
        FROM users
    """)
    all_users = cur.fetchall()
    cur.close()

    return render_template("admin/users.html", users=all_users)


# -------------------- APPROVE SELLER ONLY --------------------
@admin_bp.route("/approve-seller/<int:user_id>", methods=["POST"])
def approve_seller(user_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET approved=1 WHERE id=%s", [user_id])
    mysql.connection.commit()
    cur.close()

    flash("Seller approved successfully!")
    return redirect("/admin/users")


# -------------------- ACTIVATE USER --------------------
@admin_bp.route("/activate/<int:user_id>", methods=["POST"])
def activate_user(user_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET active=1 WHERE id=%s", [user_id])
    mysql.connection.commit()
    cur.close()

    flash("User activated!")
    return redirect("/admin/users")


# -------------------- SUSPEND USER --------------------
@admin_bp.route("/suspend/<int:user_id>", methods=["POST"])
def suspend_user(user_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET active=0 WHERE id=%s", [user_id])
    mysql.connection.commit()
    cur.close()

    flash("User suspended!")
    return redirect("/admin/users")


# -------------------- VIEW PRODUCTS --------------------
@admin_bp.route("/products")
def products():
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id, p.name, p.price, p.stock, u.name
        FROM products p
        JOIN users u ON p.seller_id = u.id
    """)
    items = cur.fetchall()
    cur.close()

    return render_template("admin/products.html", products=items)


# -------------------- DELETE PRODUCT --------------------
@admin_bp.route("/products/delete/<int:product_id>")
def delete_product(product_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", [product_id])
    mysql.connection.commit()
    cur.close()

    flash("Product deleted!")
    return redirect("/admin/products")
