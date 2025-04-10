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
    "GS글로벌", "기아", "기흥인터내셔널", 
    #"닛산", 
    "다임러트럭",
    "디암러트럭", "람보르기니", "롤스로이스", "루트17", "르노", 
    "르노삼성", "르노자동차", "르노코리아", "마세라티", # "만트럭",
    "모빌리티네트웍스", "벤츠", "벤츠코리아", "벤틀리", "볼보",
    "볼보코리아", "볼보트럭", "비엠더블유", #"스즈키씨엠씨", "스즈키코리아",
    #"스텔란티스", 
    "쌍용", "쌍용자동차", "애스턴마틴", "에프엠케이","에스에스라이트",
    "이비온","자일대우", "재규어랜드로버", "재규어랜드로보", "제이스모빌리티", "지에스글로벌",
    "지엠아시아", "지엠코리아", "케이지모빌리티", "케이지엠커머셜", "테슬라",
    "토요타", "포드", "포르쉐", "포르쉐코리아", "폭스바겐그룹",
    # "한국닛산", 
    "한국지엠", "한불", "한불모터스", "현대",
    "현대자동차", "혼다", "혼다코리아"
    }
brand_map = {
    "GS글로벌": "BYD",
    "기아": "기아",
    # "기흥인터내셔널": None,
    # "닛산": "닛산",
    "다임러트럭": "벤츠",
    "디암러트럭": "벤츠",
    "람보르기니": "람보르기니",
    "롤스로이스": "롤스로이스",
    "루트17": "대창모터스",
    "르노": "르노",
    "르노삼성": "르노",
    "르노자동차": "르노",
    "르노코리아": "르노",
    "마세라티": "마세라티",
    # "만트럭": "폭스바겐그룹",
    "모빌리티네트웍스": "모빌리티네트웍스",
    "벤츠": "벤츠",
    "벤츠코리아": "벤츠",
    "벤틀리": "벤틀리",
    "볼보": "볼보",
    "볼보코리아": "볼보",
    "볼보트럭": "볼보",
    # "스즈키씨엠씨": "스즈키",
    # "스즈키코리아": "스즈키",
    # "스텔란티스": None,
    "쌍용": "KGM",
    "쌍용자동차": "KGM",
    "애스턴마틴": "애스턴마틴",
    "에스에스라이트": "에스에스라이트",
    # "에프엠케이": None,
    "이비온": "이비온",
    "자일대우": "자일자동차",
    "재규어랜드로버": "재규어랜드로버",
    "재규어랜드로보": "재규어랜드로버",
    "제이스모빌리티": "제이스모빌리티",
    "지에스글로벌": "BYD",
    # "지엠아시아": "GMC",
    # "지엠코리아": "GMC",
    "케이지모빌리티": "KGM",
    "케이지엠커머셜": "KGM",
    "테슬라": "테슬라",
    "토요타": "토요타",
    "포드": "포드",
    "포르쉐": "포르쉐",
    "포르쉐코리아": "포르쉐",
    # "폭스바겐그룹": "폭스바겐그룹", 
    # "한국지엠": "쉐보레",
    # "한국닛산": "닛산",
    # "한불": None,
    # "한불모터스": None,
    "혼다": "혼다",
    "혼다코리아": "혼다"
}
cadillac_models = ["CT4", "CT5", "CT6", "XT4", "XT5", "XT6", "ATS", "CTS", "STS", "에스컬레이드", "리릭"]
lexus_models = [
    "ES300h",
    "RX450h",
    "RZ450e",
    "UX300h 2WD",
    "UX250h 2WD",
    "UX250h AWD",
    "NX350h",
    "NX450h+",
    "RX350h",
    "RX450h+",
    "RX500h",
    "LS500h AWD",
    "LS500 AWD",
    "LS500h 2WD",
    "LS500h",
    "CT200h",
    "SC430"
]
audi_models = [
        "A3", "A7", "A8", "Q3", "Q4", "Q6", "Q7", "Q8",
        "RS", "S8", "SQ", "e-tron", "R8"
        ]
volkswagen_models = [
        "Golf", "ID.4", "ID.5", "Jetta", "The Beetle", "Touareg", "Tiguan"
        ]
ford_models = [
            "Mustang", "Bronco", "Explorer", "Exp", "Ranger"
        ]
lincorln_models = [
            "Nautilus", "Aviator", "Corsair", "Navigator", "MKC", "MKX"
        ]
def map_brand(brand: str, name) -> str | None:
    # 여러 항목을 다루는 brand 처리
    ## 기흥인터내셔널널
    if brand == "기흥인터내셔널":
        if "McL" in name or "Art" in name or "Spi" in name:
            return "맥라렌"
    ## 스텔란티스 or 한불, 한불모터스스
    elif brand == "스텔란티스" or "한불" in brand:
        if "짚" in name:
            return "지프"
        elif "Peu" in name:
            return "푸조"
        elif "DS" in name:
            return "DS"
        elif "Cit" in name:
            return "시트로엥"
        else:
            return None

    ## 에프엠케이   
    elif brand == "에프엠케이":
        if "페라리" in name:
            return "페라리"
        else:
            return "마세라티"
    # ## 한불, 한불 모터스
    # elif "한불" in brand:
    #     if "DS" in name:
    #         return "DS"
    #     elif "Peu" in name:
    #         return "푸조"
    #     else:
    #         return "시트로엥"
    ## 비엠더블유
    elif brand == "비엠더블유":
        if "MINI" in name:
            return "미니"
        else:
            return "BMW"
    elif "현대" in brand:
        if name[0] =='G':
            return "제네시스"
        else:
            return "현대"
    elif "지엠" in brand :
        if name in cadillac_models:
            return "캐딜락"
        elif '시에라' in name:
            return "GMC"
        else:
            return "쉐보레"
    elif brand=="토요타" and name in lexus_models:
        return "렉서스"
    elif brand == "폭스바겐그룹":
        if any(keyword in name for keyword in audi_models):
            return "아우디"
        elif any(keyword in name for keyword in volkswagen_models):
            return "폭스바겐"
        return None
    elif brand=='포드':
        if any(keyword in name for keyword in ford_models):
            return "포드"
        
        elif any(keyword in name for keyword in lincorln_models):
            return "링컨"

    
    return brand_map.get(brand) if brand in valid_brands else None


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
            temp_brand = brand
            for name in model_list or [None]:
                # ✅ 브랜드명 매핑 적용
                brand = map_brand(temp_brand,name)
                print(brand, name)
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
