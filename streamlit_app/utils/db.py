# import pymysql
# sqlalchemy로 연결 변경
from sqlalchemy import create_engine


# WOOZ Local DB Connection
# def get_connection():
#     return pymysql.connect(
#         host="192.168.0.41",
#         user="skn13_woo",
#         password="1111",
#         db="car_data",
#         charset="utf8mb4",
#         cursorclass=pymysql.cursors.DictCursor
#     )

def get_connection():
    return create_engine("mysql+pymysql://skn13_woo:1111@192.168.0.41:3306/car_data")