import asyncio
import aiohttp
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


async def fetch_kakao_map(session, store_name):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 헤드리스 모드 활성화
    # options.add_argument("--disable-gpu")  # GPU 사용 비활성화
    driver_kakao = webdriver.Chrome(options=options)

    driver_kakao.set_window_size(1280, 1024)
    driver_kakao.get("https://map.kakao.com/?nil_profile=title&nil_src=local")
    driver_kakao.implicitly_wait(30)

    search_element = driver_kakao.find_element(By.ID, "search.keyword.query")
    search_element.send_keys(store_name)
    search_element.send_keys(Keys.ENTER)

    # 예시: 여러 개의 업체 정보 가져오기
    store_elements = driver_kakao.find_elements(By.CSS_SELECTOR, "li.PlaceItem")
    kakao_results = []  # 결과를 저장할 리스트
    for store_element in store_elements:
        # 업체 이름 가져오기
        store_name_element = store_element.find_element(By.CSS_SELECTOR, "a.link_name")
        store_name = store_name_element.text

        # 업체 주소 링크 가져오기
        address_link_element = store_element.find_element(By.CSS_SELECTOR, "a.moreview")
        kakao_detail_url = address_link_element.get_attribute("href")

        # 평점 정보 가져오기
        score_element = store_element.find_element(By.CSS_SELECTOR, "em.num")
        score = score_element.text

        # 리뷰 개수 가져오기
        review_count_element = store_element.find_element(
            By.CSS_SELECTOR, "a.numberofscore"
        )
        review_count = review_count_element.text

        # 영업 시간 가져오기
        operating_hours_element = store_element.find_element(
            By.CSS_SELECTOR, "span.openhourTitle"
        )
        operating_hours_status = operating_hours_element.text
        operating_hours_text_element = store_element.find_element(
            By.CSS_SELECTOR, "a[data-id='periodTxt']"
        )
        operating_hours = operating_hours_text_element.text

        # 가게이름 요소 클릭
        driver_kakao.execute_script("arguments[0].click();", store_element)

        button_element = driver_kakao.find_element(By.CSS_SELECTOR, "button.expand")
        # 버튼 요소 클릭
        driver_kakao.execute_script("arguments[0].click();", button_element)
        img_element = driver_kakao.find_element(By.CSS_SELECTOR, "img.placeimg")

        # 이미지의 src 속성 가져오기
        img_src = img_element.get_attribute("src")
        if img_src:
            print("이미지 URL:", img_src)
        else:
            img_src = "이미지없음"
            print(img_src)

        print("업체 이름:", store_name)
        print("평점:", score)
        print("리뷰 개수:", review_count)
        print("영업 상태:", operating_hours_status)
        print("영업 시간:", operating_hours)
        print("url:", kakao_detail_url)
        print("img_src:", img_src)
        print("=" * 30)

        # 브라우저 닫기
        kakao_results.append(
            {
                "store_name": store_name,
                "grade": score,
                "review_count": review_count,
                "operating_hours": operating_hours,
                "detail_url": kakao_detail_url,  # 이 부분은 여러분이 가져와야 할 링크입니다.
                "img_src:": img_src,
            }
        )
    driver_kakao.quit()

    return kakao_results


if __name__ == "__main__":
    store_name = "남해 카페"  # 검색하고자 하는 키워드

    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_kakao_map(None, store_name))
