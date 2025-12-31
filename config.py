import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecretkey123")

    MYSQL_HOST = os.getenv("MYSQL_ADDON_HOST")
    MYSQL_USER = os.getenv("MYSQL_ADDON_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_ADDON_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_ADDON_DB")
    MYSQL_PORT = int(os.getenv("MYSQL_ADDON_PORT", 3306))

    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
