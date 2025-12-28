from models.db import mysql

def add_notification(user_id, message):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, message)
        VALUES (%s, %s)
    """, (user_id, message))
    mysql.connection.commit()
    cur.close()
