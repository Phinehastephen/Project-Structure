import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecretkey123")

    MYSQL_ADDON_DB="bwnpzqcu6wxwiwysgjfj"
    MYSQL_ADDON_HOST="bwnpzqcu6wxwiwysgjfj-mysql.services.clever-cloud.com"
    MYSQL_ADDON_PASSWORD="KokQmeOczwRowRaihSh5"
    MYSQL_ADDON_PORT="3306"
    MYSQL_ADDON_URI="mysql://uefgl8bfwgzw275l:KokQmeOczwRowRaihSh5@bwnpzqcu6wxwiwysgjfj-mysql.services.clever-cloud.com:3306/bwnpzqcu6wxwiwysgjfj"
    MYSQL_ADDON_USER="uefgl8bfwgzw275l"
    MYSQL_ADDON_VERSION="8.0"

    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
