from flask import Blueprint, render_template, request, redirect, session, flash
from models.db import mysql

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -------------------- SECURITY --------------------
def admin_only():
    return "role" in session and session["role"] == "admin"


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
            o.total,
            o.status,
            o.created_at,
            o.estimated_delivery
        FROM orders o
        JOIN users u ON o.buyer_id = u.id
        ORDER BY o.id DESC
    """)

    orders = cur.fetchall()
    cur.close()

    return render_template("admin/orders.html", orders=orders)


# -------------------- VIEW SINGLE ORDER --------------------
@admin_bp.route("/orders/view/<int:order_id>")
def view_order(order_id):
    if not admin_only():
        return redirect("/auth/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            o.id,
            o.total,
            o.status,
            o.address,
            o.created_at,
            u.name,
            u.email,
            o.estimated_delivery
        FROM orders o
        JOIN users u ON o.buyer_id = u.id
        WHERE o.id = %s
    """, [order_id])

    order = cur.fetchone()

    cur.execute("""
        SELECT p.name, oi.price, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, [order_id])

    items = cur.fetchall()
    cur.close()

    return render_template("admin/order_view.html", order=order, items=items)


# -------------------- UPDATE ORDER --------------------
@admin_bp.route("/orders/update/<int:order_id>", methods=["POST"])
def update_order(order_id):
    if not admin_only():
        return redirect("/auth/login")

    status = request.form.get("status")
    estimated_delivery = request.form.get("estimated_delivery")

    cur = mysql.connection.cursor()

    if estimated_delivery:
        cur.execute("""
            UPDATE orders
            SET status=%s, estimated_delivery=%s
            WHERE id=%s
        """, (status, estimated_delivery, order_id))
    else:
        cur.execute("""
            UPDATE orders
            SET status=%s
            WHERE id=%s
        """, (status, order_id))

    mysql.connection.commit()
    cur.close()

    flash("Order updated successfully.")
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

    flash("Order deleted.")
    return redirect("/admin/orders")
