from selenium import webdriver
import time
from selenium.webdriver.common.by import By


def google_maps_crawler(location, zoom_level=15):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")  # GPU 사용 비활성화
    driver_google = webdriver.Chrome(options=options)
    driver_google.set_window_size(1280, 1024)
    driver_google.get("https://www.google.co.kr/maps")
    driver_google.implicitly_wait(10)

    # 일정 시간 동안 페이지를 로드할 시간을 줍니다
    time.sleep(5)

    # 지도에서 필요한 정보 수집
    # 이 예제에서는 지도의 제목(장소 이름)을 수집합니다
    searchbar = driver_google.find_element(By.CSS_SELECTOR, "#searchboxinput")
    search_query = "창동 맛집"
    searchbar.send_keys(search_query)
    search_button = driver_google.find_element(
        by=By.CSS_SELECTOR, value="#searchbox-searchbutton"
    )
    search_button.click()
    # 업체 이름 요소를 CSS 선택자를 사용하여 찾습니다.
    company_elements = driver_google.find_elements(by=By.CSS_SELECTOR, value="a.hfpxzc")

    # 업체 이름을 리스트로 수집합니다.
    company_names = [
        element.get_attribute("aria-label") for element in company_elements
    ]
    print(company_names)
    # 드라이버 종료 및 결과 반환
    driver_google.quit()
    return


# 함수 테스트 (위도, 경도 형식의 튜플 사용)
location = (37.5665, 126.9780)  # 서울시청 위도, 경도
result = google_maps_crawler(location)
print(result)
