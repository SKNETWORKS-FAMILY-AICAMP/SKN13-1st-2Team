import re
import time
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By



# MySQL 연결 설정
conn = pymysql.connect(
    host='localhost',
    user = 'skn13_woo', # 본인의 sql id 입력
    password = '1111', # 본인의 sql password 입력
    database='car_data',
    charset='utf8mb4',
    autocommit=True
)
cursor = conn.cursor()

url_list = [f"https://auto.danawa.com/newcar/?&page={i}" for i in range(1,15)]

car_type_list = ["경차", "SUV", "MPV", "소형",
                 "중형", "준중형", "대형", "상용",
                 "스포츠카", "승합","픽업/밴", "경트럭"]

fuel_type_list = ["가솔린", "디젤", "하이브리드", 
                  "전기", "LPG", "수소", "바이퓨얼"]


def get_price(text):
    # 줄 단위로 나눔
    lines = text.split('\n')

    # 할인가 또는 출고가가 있는 줄 찾기
    price_line = None
    for line in lines:
        if '할인가' in line:
            price_line = line
            break
    if not price_line:
        for line in lines:
            if '출고가' in line:
                price_line = line
                break
    if not price_line:
        return None, None

    # 숫자 추출
    def parse_price(s):
        s = s.replace(',', '').replace(' ', '')
        eok_match = re.search(r'(\d+)억', s)
        man_match = re.search(r'(\d+)(?=만원)', s)
        eok = int(eok_match.group(1)) * 10000 if eok_match else 0
        man = int(man_match.group(1)) if man_match else 0
        return eok + man if (eok or man) else None

    # ~ 있으면 범위
    if '~' in price_line:
        parts = price_line.split('~')
        price_min = parse_price(parts[0])
        price_max = parse_price(parts[1])
    else:
        price_min = parse_price(price_line)
        price_max = None

    return price_min



# Selenium 설정
driver = webdriver.Chrome()
for url in url_list:
    driver.get(url)
    print("selecting url: \n", url)
    time.sleep(3)
    
    car_elements = driver.find_elements(By.CSS_SELECTOR, "li > div.info")

    for car in car_elements:
        try:
            # 공통 정보 추출
            img_tag = car.find_element(By.CSS_SELECTOR, "a.image > img")
            img_url = img_tag.get_attribute("src")
            name = img_tag.get_attribute("alt")
            model_id = int(car.find_element(By.CSS_SELECTOR, "a.image").get_attribute("model"))
            brand = name.split()[0]

                        
            brand_img = None
            try:
                brand_img_tag = car.find_element(By.CSS_SELECTOR, ".detail_middle .name img")
                brand_img = brand_img_tag.get_attribute("src")
            except:
                print(f"⚠️ brand_img 태그 못 찾음: {name}")

            # 브랜드 이름 정리
            if "르노" in brand:
                brand = "르노"
            elif brand == "랜드로버":
                brand = "재규어랜드로버"
            
            # 상세 페이지 URL과 가격 추출
            detail_url = price = None
            try:
                right_box = car.find_element(By.XPATH, "../div[@class='right']")
                #print(right_box.text)
                price = get_price(right_box.text)
                detail_url_tag = right_box.find_element(By.CSS_SELECTOR, ".action > a")
                detail_url = detail_url_tag.get_attribute("href") if detail_url_tag else None
            except:
                pass

            # 스펙 처리
            specs = car.find_elements(By.CSS_SELECTOR, ".spec span")
            car_type = fuel_type = release_date = engine_displacement = efficiency = delivery_period = None
            efficiency_km_per_kwh = total_range_km = battery_capacity_kwh = battery_manufacturer = None

            for spec in specs:
                text = spec.text.strip()

                if "출시" in text:
                    release_date = text.replace("출시", "").strip()
                elif "㎞/ℓ" in text:
                    efficiency = text
                elif "cc" in text:
                    engine_displacement = text
                elif any(x in text for x in car_type_list):
                    car_type = text
                elif any(x in text for x in fuel_type_list):
                    fuel_type = text
                elif "㎞/kWh" in text:
                    efficiency_km_per_kwh = text
                elif "총주행거리" in text:
                    total_range_km = text
                elif "배터리 용량" in text:
                    battery_capacity_kwh = text
                elif "배터리 제조사" in text:
                    battery_manufacturer = text
                elif "출고 대기기간" in text:
                    delivery_period = text.replace("출고 대기기간 :", "").strip()


            cursor.execute("SELECT 1 FROM car_brands WHERE brand = %s", (brand,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute("""
                    INSERT INTO car_brands (brand, brand_img)
                    VALUES (%s, %s)
                """, (brand, brand_img))
            else:
                cursor.execute("""
                    UPDATE car_brands SET brand_img = %s WHERE brand = %s
                """, (brand_img, brand))
            # cars 테이블 삽입
            cursor.execute("""
                INSERT INTO cars (model_id, name, brand, car_type, fuel_type, release_date, price, image_url, detail_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name=VALUES(name), brand=VALUES(brand),
                    car_type=VALUES(car_type), fuel_type=VALUES(fuel_type),
                    release_date=VALUES(release_date), price=VALUES(price),
                    image_url=VALUES(image_url), detail_url=VALUES(detail_url)
            """, (model_id, name, brand, car_type, fuel_type, release_date, price, img_url, detail_url))

            # 전기차 or 일반차
            if fuel_type and "전기" in fuel_type:
                cursor.execute("""
                    INSERT INTO ev_specs (model_id, efficiency_km_per_kwh, total_range_km, battery_capacity_kwh, battery_manufacturer, delivery_period)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        efficiency_km_per_kwh=VALUES(efficiency_km_per_kwh),
                        total_range_km=VALUES(total_range_km),
                        battery_capacity_kwh=VALUES(battery_capacity_kwh),
                        battery_manufacturer=VALUES(battery_manufacturer),
                        delivery_period=VALUES(delivery_period)
                """, (model_id, efficiency_km_per_kwh, total_range_km, battery_capacity_kwh, battery_manufacturer, delivery_period))
            else:
                cursor.execute("""
                    INSERT INTO engine_specs (model_id, engine_displacement, efficiency, delivery_period)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        engine_displacement=VALUES(engine_displacement),
                        efficiency=VALUES(efficiency),
                        delivery_period=VALUES(delivery_period)
                """, (model_id, engine_displacement, efficiency, delivery_period))

            print(f"✅ 저장 완료: {name} ({model_id})")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")

# 종료 처리
driver.quit()
conn.close()
