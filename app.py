import pymysql
pymysql.install_as_MySQLdb()  

from flask import Flask
from config import Config
from models.db import mysql

# Routes
from routes.auth import auth_bp
from routes.buyer import buyer_bp
from routes.seller import seller_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(admin_bp)

app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER

if __name__ == "__main__":
    app.run(debug=True)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
