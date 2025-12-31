import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from config import Config
from models.db import mysql

# Import blueprints
from routes.auth import auth_bp
from routes.buyer import buyer_bp
from routes.seller import seller_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)

    # Load config (uses Clever Cloud env variables automatically)
    app.config.from_object(Config)

    # Init MySQL
    mysql.init_app(app)

    # Upload folder
    app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)

    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app


# Create app for Clever Cloud WSGI server
app = create_app()


# Local development mode
if __name__ == "__main__":
    app.run(debug=True)
