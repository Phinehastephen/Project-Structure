from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import mysql

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")


# -------------------- LOGIN --------------------
@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, name, email, password, role, active, approved 
            FROM users WHERE email=%s
        """, [email])
        user = cur.fetchone()
        cur.close()

        if not user:
            flash("Invalid email or password")
            return render_template("auth/login.html")

        # Extract user data properly
        user_id       = user[0]
        user_name     = user[1]
        user_email    = user[2]
        stored_pass   = user[3]
        user_role     = user[4]
        user_active   = user[5]
        user_approved = user[6]

        # -------------------- ACCOUNT CHECKS --------------------

        # Suspended users cannot login
        if user_active == 0:
            flash("Your account is suspended. Contact admin.")
            return render_template("auth/login.html")

        # Sellers must be approved first
        if user_role == "seller" and user_approved == 0:
            flash("Your seller account is awaiting approval.")
            return render_template("auth/login.html")

        # -------------------- PASSWORD VALIDATION --------------------

        valid_password = False

        # Try hashed password
        try:
            if check_password_hash(stored_pass, password):
                valid_password = True
        except:
            pass

        # Try plain password (for manually created admin/seller accounts)
        if stored_pass == password:
            valid_password = True

        if not valid_password:
            flash("Invalid email or password")
            return render_template("auth/login.html")

        # -------------------- LOGIN SUCCESS --------------------

        session['user_id'] = user_id
        session['role'] = user_role

        # Redirect based on role
        if user_role == "buyer":
            return redirect("/buyer/products")
        elif user_role == "seller":
            return redirect("/seller/dashboard")
        elif user_role == "admin":
            return redirect("/admin/dashboard")

    return render_template("auth/login.html")


# -------------------- LOGOUT --------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/auth/login")


# -------------------- REGISTER --------------------
@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        name = request.form['fullname']  # your template uses 'fullname'
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (name, email, password, role, active, approved)
            VALUES (%s, %s, %s, %s, 1, 0)
        """, (name, email, password, "buyer"))

        mysql.connection.commit()
        cur.close()

        flash("Registration successful! Please login.")
        return redirect("/auth/login")

    return render_template("auth/register.html")
