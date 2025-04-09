import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1111",
        db="project",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )