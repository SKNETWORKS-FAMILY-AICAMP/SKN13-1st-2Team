import time
import pymysql
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains

# WebDriver 초기화 및 암시적 대기 시간 설정
driver = webdriver.Chrome()
driver.implicitly_wait(10)

conn = pymysql.connect(
    host='localhost',
    user = 'skn13_woo', # 본인의 sql id 입력
    password = '1111', # 본인의 sql password 입력
    database='car_data',
    charset='utf8mb4',
    autocommit=True
)
cursor = conn.cursor()

# 대상 웹 페이지 접속
url_list = [f'https://www.consumer.go.kr/user/ftc/consumer/recallInfo/629/selectRecallInfoInternalList.do?searchCondition1=0301&page={i}' for i in range(30, 95)]
for url in url_list:
    driver.get(url)
    print(f'🛜 현재 페이지: {url}')

    # 이미지 XPATH 동적으로 생성
    image_xpaths = [
        f'//*[@id="goodsList"]/ul/li[{i}]/div[1]/a/p/img' for i in range(1, 11)
    ]

    data = []

    # 각 이미지 클릭 → 정보 수집
    for xpath in image_xpaths:
        try:
            image = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].scrollIntoView();", image)
            time.sleep(1)
            ActionChains(driver).move_to_element(image).click().perform()
            time.sleep(2)

            # 전체 HTML 파싱
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # 리콜 상세 정보 영역 찾기
            container = soup.find("div", class_="rightArea goodsViewDesc goodsViewDescNI")
            # 초기 변수 선언
            company_name = product_name = manufacturer = production_period = model_name = None
            recall_type = announcement_date = defect_description = None

            if container:
                # 제목에서 회사명, 제품명 추출
                title_tag = container.find("h3", class_="title")
                if title_tag:
                    title_text = title_tag.get_text(strip=True)
                    if title_text.startswith('['):
                        try:
                            brand = title_text.split(']')[0][1:]
                            product_name = title_text.split(']')[1].split('-')[0].strip()
                        except IndexError:
                            print("제목 파싱 오류")

                # 표 항목 추출
                goods_info = container.find("div", class_="goodsInfo")
                if goods_info:
                    rows = goods_info.find_all('dl')
                    for row in rows:
                        key_tag = row.find('dt').find('span', class_='tit')
                        value_tag = row.find('dd')
                        if key_tag and value_tag:
                            key = key_tag.get_text(strip=True)
                            value = value_tag.get_text(strip=True)

                            if key == "제조사":
                                manufacturer = value
                            elif key == "제조연월일":
                                production_period = value
                            elif key == "모델명":
                                model_name = value
                            # elif key == "리콜구분":
                            #     recall_type = value
                            # elif key == "리콜공표일":
                            #     announcement_date = value
                            # elif key == "결함내용":
                            #     defect_description = value
                else:
                    print("goodsInfo 영역을 찾을 수 없습니다.")
            else:
                print("rightArea 영역을 찾을 수 없습니다.")

            # 리콜 정보가 담긴 테이블 추출
            table = driver.find_element(By.XPATH, '//*[@id="m_page_top"]/div[2]/div[2]')
            soup = BeautifulSoup(table.get_attribute("innerHTML"), 'html.parser')
            recall_table = soup.find("div", class_="goodsViewUi")

            if recall_table:
                rows = recall_table.find_all('dl')
                for row in rows:
                    key = row.find('dt').get_text(strip=True)
                    value = '\n'.join(p.get_text(strip=True) for p in row.find('dd').find_all('p')) if row.find('dd').find_all('p') else row.find('dd').get_text(strip=True)
                    if key == "리콜구분":
                        recall_type = value
                    elif key == "리콜공표기간":
                        if '~' in value:
                            parts = value.split('~')
                            announcement_start = parts[0].strip() or None
                            announcement_end = parts[1].strip() or None if len(parts) > 1 and parts[1].strip() else None
                        else:
                            announcement_start = value.strip() or None
                            announcement_end = None

                    elif key == "출처":
                        source = value
                    elif key == "결함의 내용":
                        defect_description = value

            print(brand, product_name, manufacturer, production_period, model_name, recall_type, announcement_start, announcement_end, source, defect_description)
            print("------------------------------------------------")

            model_list = model_name.split(',') if model_name else []
            model_list = [m.strip() for m in model_list]  # 공백 제거
            release_start = production_period.split('~')[0].strip() if production_period else None
            release_end = production_period.split('~')[1].strip() if production_period and '~' in production_period else None


            for name in model_list:
            # recall 테이블 삽입
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
            time.sleep(2)

        except Exception as e:
            print(f'오류 발생: {e}')
            print(f'url_page: {url}')
            continue

# 브라우저 종료
driver.quit()
