import time
import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


## brand 정제하는 코드?

# ✅ 브랜드 매핑 딕셔너리
valid_brands = {
    "GS글로벌", "기아", "닛산", "다임러트럭", "디암러트럭", "람보르기니", "롤스로이스", "루트17",
    "르노", "르노삼성", "르노자동차", "르노코리아", "마세라티", "만트럭", "모빌리티네트웍스",
    "벤츠", "벤츠코리아", "벤틀리", "볼보", "볼보코리아", "볼보트럭", "비엠더블유", "쌍용",
    "쌍용자동차", "애스턴마틴", "이비온", "재규어랜드로버", "재규어랜드로보", "제이스모빌리티",
    "지에스글로벌", "지엠아시아", "지엠코리아", "케이지모빌리티", "케이지엠커머셜", "테슬라",
    "토요타", "포드", "포르쉐", "포르쉐코리아", "폭스바겐그룹", "한국닛산", "현대", "현대자동차",
    "혼다", "혼다코리아"
}

brand_mapping = {
    "GS글로벌": "BYD",
    "KR모터스": None,
    "기아": "기아",
    "기흥": None,           # 수입사
    "기흥모터스": None,     # 수입사
    "기흥인터내셔널": None, # 수입사
    "노바스": "대창모터스",
    "닛산": None,
    "다임러트럭": "벤츠",
    "대전기계공업": None,
    "더좋은사람": None,
    "두카티": None,
    "람보르기니": "람보르기니",
    "롤스로이스": "롤스로이스",
    "루트17": None,
    "르노": "르노",
    "르노자동차": "르노",
    "르노코리아": "르노",
    "마세라티": "마세라티",
    "만트럭": None,
    "모빌리티네트웍스": "모빌리티네트웍스",
    "바이드": "BYD",
    "바이크원": None,
    "바이크코리아": None,
    "범한자동차": "자일자동차",
    "벤츠": "벤츠",
    "벤틀리": "벤틀리",
    "볼보": "볼보",
    "볼보트럭": "볼보",
    "블루샤크": None,
    "비바모빌리티": None,
    "비엠더블유": "BMW",
    "스즈키씨엠씨": None,
    "스카니아": None,
    "스텔란티스": None,
    "아이씨피": None,
    "애스턴마틴": "애스턴마틴",
    "야마하": None,
    "에스에스라이트": "에스에스라이트",
    "에프엠케이": "마세라티",  # 또는 페라리. 상황 따라 다르게 가능
    "오토스원": None,
    "이누리": None,
    "이비온": "이비온",
    "인에이블인터내셔널": None,
    "재규어랜드로버": "랜드로버",
    "재규어랜드로보": "랜드로버",
    "제이스모빌리티": "제이스모빌리티",
    "제이에스얼라이언스": None,
    "지에스글로벌": None,
    "지엠아시아": "쉐보레",
    "지엠코리아": "쉐보레",
    "케이지모빌리티": "쎄보모빌리티",
    "케이지엠커머셜": "KGM",
    "킹콩이브이코리아": None,
    "타타대우": None,
    "테슬라": "테슬라",
    "텐핑": None,
    "토요타": "토요타",
    "티에스모터스": None,
    "포드": "포드",
    "포르쉐": "포르쉐",
    "폭스바겐그룹": "폭스바겐",
    "피라인모터스": None,
    "한국닛산": None,
    "한국모터스": None,
    "한국모터트레이딩": None,
    "한국지엠": "쉐보레",
    "한솜바이크": None,
    "현대": "현대",
    "혼다": "혼다",
    "화창상사": None,
}


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

conn = pymysql.connect(
    host='localhost',
    user='skn13_woo',
    password='1111',
    database='car_data',
    charset='utf8mb4',
    autocommit=True
)
cursor = conn.cursor()

url_list = [f'https://www.consumer.go.kr/user/ftc/consumer/recallInfo/629/selectRecallInfoInternalList.do?searchCondition1=0301&page={i}' for i in range(1, 95)]

# def normalize_brand(raw_brand):
#     return brand_mapping.get(raw_brand, None)

for url in url_list:
    driver.get(url)
    print(f'🛜 현재 페이지: {url}')

    for i in range(1, 11):
        try:
            image_xpath = f'//*[@id="goodsList"]/ul/li[{i}]/div[1]/a/p/img'
            image = wait.until(EC.element_to_be_clickable((By.XPATH, image_xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", image)
            image.click()

            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "goodsViewDesc")))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            container = soup.select_one("div.rightArea.goodsViewDesc.goodsViewDescNI")

            brand = product_name = manufacturer = production_period = model_name = None
            recall_type = announcement_start = announcement_end = source = defect_description = None

            if container:
                title_tag = container.find("h3", class_="title")
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    if title_text.startswith('['):
                        brand = title_text.split(']')[0][1:]
                        product_name = title_text.split(']')[1].split('-')[0].strip()
            
            goods_info = container.select("div.goodsInfo dl")
            for row in goods_info:
                key = row.find('dt').get_text(strip=True)
                value = row.find('dd').get_text(strip=True)
                if key == "제조사":
                    manufacturer = value
                elif key == "제조연월일":
                    production_period = value
                elif key == "모델명":
                    model_name = value

            recall_info = soup.select("div.goodsViewUi dl")
            for row in recall_info:
                key = row.find('dt').get_text(strip=True)
                dd = row.find('dd')
                value = '\n'.join(p.get_text(strip=True) for p in dd.find_all('p')) if dd.find_all('p') else dd.get_text(strip=True)
                if key == "리콜구분":
                    recall_type = value
                elif key == "리콜공표기간":
                    if '~' in value:
                        parts = value.split('~')
                        announcement_start = parts[0].strip() or None
                        announcement_end = parts[1].strip() or None
                    else:
                        announcement_start = value.strip() or None
                        announcement_end = None
                elif key == "출처":
                    source = value
                elif key == "결함의 내용":
                    defect_description = value

            # brand = normalize_brand(brand)
            model_list = [m.strip() for m in (model_name or '').split(',') if m.strip()]
            release_start = production_period.split('~')[0].strip() if production_period else None
            release_end = production_period.split('~')[1].strip() if production_period and '~' in production_period else None

            # ✅ 브랜드명 매핑 적용
            #  brand = brand_mapping.get(brand, brand)

            for name in model_list or [None]:
                cursor.execute("""
                    INSERT INTO recalls (brand, name, release_start, release_end, recall_type, announcement_start, announcement_end, source, defect_description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        brand=VALUES(brand), name=VALUES(name), release_start=VALUES(release_start),
                        release_end=VALUES(release_end), recall_type=VALUES(recall_type),
                        announcement_start=VALUES(announcement_start), announcement_end=VALUES(announcement_end),
                        source=VALUES(source), defect_description=VALUES(defect_description)
                """, (brand, name, release_start, release_end, recall_type, announcement_start, announcement_end, source, defect_description))

            driver.back()
            wait.until(EC.presence_of_element_located((By.ID, "goodsList")))

        except Exception as e:
            print(f"[❌ ERROR] Page: {url}, Item: {i} - {e}")
            driver.back()
            continue

driver.quit()
