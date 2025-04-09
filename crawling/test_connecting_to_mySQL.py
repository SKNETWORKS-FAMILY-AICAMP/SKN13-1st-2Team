import pymysql

# MySQL 연결
conn = pymysql.connect(
    host='localhost',
    user='skn13_woo',
    password='1111',  # 여기에 너 비밀번호
    db='car_data',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
    
cursor = conn.cursor()
