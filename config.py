import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret")

    MYSQL_HOST = os.environ.get("MYSQL_ADDON_HOST")
    MYSQL_USER = os.environ.get("MYSQL_ADDON_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_ADDON_PASSWORD")
    MYSQL_DB = os.environ.get("MYSQL_ADDON_DB")
    MYSQL_PORT = int(os.environ.get("MYSQL_ADDON_PORT", 3306))

    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
