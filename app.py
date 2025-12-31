import pymysql
pymysql.install_as_MySQLdb()

import os
from flask import Flask
from config import Config
from models.db import mysql

# Blueprints
from routes.auth import auth_bp
from routes.buyer import buyer_bp
from routes.seller import seller_bp
from routes.admin import admin_bp


def create_app():
    """Application factory for both local and Clever Cloud deployment."""
    
    app = Flask(__name__)

    # Load Config (automatically uses environment vars on Clever Cloud)
    app.config.from_object(Config)


    #  INITIALIZE MYSQL DATABASE
    mysql.init_app(app)

    # Upload folder
    app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER


    # REGISTER ROUTES/BLUEPRINTS
    app.register_blueprint(auth_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)


    # DISABLE CACHING
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app


#  CREATE APP INSTANCE FOR WSGI SERVER
app = create_app()


#  LOCAL DEVELOPMENT ENTRY POINT
if __name__ == "__main__":
    app.run(debug=True)
