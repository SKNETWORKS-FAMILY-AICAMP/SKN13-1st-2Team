import pymysql

# WOOZ Local DB Connection
def get_connection():
    return pymysql.connect(
        host="192.168.0.41",
        user="skn13_woo",
        password="1111",
        db="car_data",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )