import pymysql
pymysql.install_as_MySQLdb()

import os
from flask import Flask, redirect, url_for
from config import Config
from models.db import mysql

# Import blueprints
from routes.auth import auth_bp
from routes.buyer import buyer_bp
from routes.seller import seller_bp
from routes.admin import admin_bp


def create_app():
    """Application factory for both local and Clever Cloud deployment."""
    
    app = Flask(__name__)

    # Load config (local or Clever Cloud)
    app.config.from_object(Config)

    # Initialize MySQL
    mysql.init_app(app)

    # Upload folder
    app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)

    # ROOT REDIRECT (STEP 1)
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # DISABLE CACHING
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app


# Create WSGI app for Clever Cloud
app = create_app()


# TEST DATABASE CONNECTION
@app.route("/test-db")
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        return "MySQL connected successfully!"
    except Exception as e:
        return f"Database Error: {str(e)}"


# Local development
if __name__ == "__main__":
    app.run(debug=True)
