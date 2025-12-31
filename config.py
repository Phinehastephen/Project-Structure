import os

class Config:
    MYSQL_HOST = os.environ.get("MYSQL_ADDON_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_ADDON_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_ADDON_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_ADDON_DB", "users")
    MYSQL_PORT = int(os.environ.get("MYSQL_ADDON_PORT", 3306))

    SECRET_KEY = os.environ.get("SECRET_KEY", "development-secret")

    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
