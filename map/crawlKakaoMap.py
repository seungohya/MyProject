import asyncio
import re
import aiohttp
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    UnexpectedAlertPresentException,
)


async def fetch_kakao_map(session, store_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    # options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--disable-gpu")  # GPU 사용 비활성화
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
    for idx, store_element in enumerate(store_elements):
        # 업체 이름 가져오기
        store_name_element = store_element.find_element(By.CSS_SELECTOR, "a.link_name")
        store_name = store_name_element.text

        # 업체 주소 링크 가져오기
        address_link_element = store_element.find_element(By.CSS_SELECTOR, "a.moreview")
        kakao_detail_url = address_link_element.get_attribute("href")

        # 평점 정보 가져오기
        score_element = store_element.find_element(By.CSS_SELECTOR, "em.num")
        score = score_element.text
        # 주소 정보 추출
        address_element = store_element.find_element(By.CSS_SELECTOR, "div.addr")
        address = address_element.text
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
        # 현재 탭의 핸들 저장
        original_tab = driver_kakao.current_window_handle
        # 상세보기 링크 요소 찾기
        link_elements = driver_kakao.find_elements(By.CSS_SELECTOR, "a.moreview")
        link_element = link_elements[idx]

        # 링크 요소 자바스크립트로 클릭
        driver_kakao.execute_script("arguments[0].click();", link_element)

        # 새 탭으로 전환
        new_tab_handle = None
        WebDriverWait(driver_kakao, 10).until(EC.number_of_windows_to_be(2))
        for handle in driver_kakao.window_handles:
            if handle != original_tab:
                new_tab_handle = handle
                break
        driver_kakao.switch_to.window(new_tab_handle)
        try:
            driver_kakao.find_element(By.CSS_SELECTOR, "span.frame_g").click()

            try:
                img_element = WebDriverWait(driver_kakao, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "#photoViewer > div.layer_body > div.view_photo > div.view_image > img",
                        )
                    )
                )
                img_src = img_element.get_attribute("src")
            except (TimeoutException, UnexpectedAlertPresentException):
                img_src = "이미지 없음"
                pass

            try:
                WebDriverWait(driver_kakao, 10).until(EC.alert_is_present())
                alert = driver_kakao.switch_to.alert
                alert.accept()
            except TimeoutException:
                pass

        except NoSuchElementException:
            img_src = "이미지 없음"
        finally:
            driver_kakao.close()
            driver_kakao.switch_to.window(original_tab)

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
                "detail_url": kakao_detail_url,
                "img_src": img_src,
                "address": address,
            }
        )
    driver_kakao.quit()

    return kakao_results


async def fetch_naver_map(session, store_name):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")  # GPU 사용 비활성화
    driver_naver = webdriver.Chrome(options=options)
    driver_naver.set_window_size(1280, 1024)
    driver_naver.get("https://map.naver.com/")
    driver_naver.implicitly_wait(10)

    search_element = driver_naver.find_element(By.CLASS_NAME, "input_search")
    search_element.send_keys(store_name)
    search_element.send_keys(Keys.RETURN)

    image_link = None
    ad_results = []
    naver_results = []
    time.sleep(1)
    try:
        driver_naver.find_element(By.CSS_SELECTOR, "iframe#entryIframe")

    except NoSuchElementException:
        # If iframe is not present, it's a search results page
        print("This is a search results page")
        time.sleep(1)
        search_iframe = WebDriverWait(driver_naver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe"))
        )
        driver_naver.switch_to.frame(search_iframe)
        print("Switching to search iframe")
        time.sleep(0.5)
        results = driver_naver.find_elements(
            By.CSS_SELECTOR, "li.UEzoS.rTjJo, li.VLTHu.OW9LQ"
        )
        if results:
            print("Found search results:")
        else:
            print("No search results found")

        for index, result in enumerate(results):
            if index >= 1:  # 두 번째 인덱스부터 프레임 변경 실행
                driver_naver.switch_to.default_content()
                time.sleep(2)

                driver_naver.switch_to.frame(search_iframe)
                print("Switching to search iframe")

            link_text = result.text
            print("Found search result:", link_text)

            if "cZnHG" in result.get_attribute("class"):
                ad_results.append(link_text)
            else:
                link = result.find_element(
                    By.CSS_SELECTOR,
                    "span.place_bluelink.TYaxT, span.place_bluelink.YwYLL",
                )
                # 자바스크립트를 사용하여 요소 클릭
                driver_naver.execute_script("arguments[0].click();", link)
                time.sleep(0.5)  # 클릭 후 잠시 대기
                link_text = result.find_element(
                    By.CSS_SELECTOR,
                    "span.place_bluelink.TYaxT, span.place_bluelink.YwYLL",
                ).text
                driver_naver.switch_to.default_content()
                driver_naver.switch_to.frame(
                    driver_naver.find_element(By.CSS_SELECTOR, "iframe#entryIframe")
                )
                detail_url = driver_naver.current_url
                print("Detail URL:", detail_url)
                # 주소 정보 요소 찾기
                address_element = driver_naver.find_element(
                    By.CSS_SELECTOR, "div.vV_z_ a.PkgBl span.LDgIH"
                )

                # 주소 정보 추출
                address = address_element.text
                try:
                    # 새로운 요소 찾기
                    image_element = WebDriverWait(driver_naver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[id='ibu_1'],div[id='ugc_1']")
                        )
                    )
                    print("image_element", image_element)
                    style_value = image_element.get_attribute("style")
                    print("style_value", style_value)

                    prefix = 'url("'
                    suffix = '")'
                    if prefix in style_value and suffix in style_value:
                        start_index = style_value.index(prefix) + len(prefix)
                        end_index = style_value.index(suffix)
                        image_link = style_value[start_index:end_index]
                        print("이미지 링크:", image_link)
                    else:
                        print("이미지 링크를 찾을 수 없음")
                        image_link = "이미지없음"
                except UnexpectedAlertPresentException:
                    alert = driver_naver.switch_to.alert
                    print(f"경고창 발생: {alert.text}")
                    alert.accept()
                except Exception as e:
                    print("이미지 링크를 찾을 수 없음")
                    print(f"예외 발생: {e}")
                    image_link = "이미지없음"
                try:
                    star_element = driver_naver.find_element(
                        By.CSS_SELECTOR,
                        "div.place_section.OP4V8 span.PXMot.LXIwF > em",
                    )
                    detail_star_rating = star_element.text
                except:
                    detail_star_rating = "별점 없음"
                print("Detail Star Rating:", detail_star_rating)

                try:
                    review_count_element = driver_naver.find_element(
                        By.CSS_SELECTOR, "a.place_bluelink em"
                    )
                    review_count = review_count_element.text
                    print("네이버지도 리뷰 개수:", review_count)
                except:
                    review_count = "리뷰 없음"

                try:
                    business_hours_element = driver_naver.find_element(
                        By.CSS_SELECTOR, "div.A_cdD time"
                    )
                    business_hours = business_hours_element.get_attribute("textContent")
                    print("네이버지도 영업 시간:", business_hours)
                except:
                    business_hours = "영업 시간 정보 없음"

                # try:
                #     # 영업시간 정보 추출

                # except:

                naver_results.append(
                    {
                        "detail_name": link_text,
                        "detail_star_rating": detail_star_rating,
                        "business_hours": business_hours,
                        "review_count": review_count,
                        "detail_url": detail_url,
                        "image_link": image_link,
                        "address": address,
                    }
                )

    else:
        # If iframe is present, it's a detail page
        print("This is a detail page")
        driver_naver.switch_to.frame(
            driver_naver.find_element(By.CSS_SELECTOR, "iframe#entryIframe")
        )
        time.sleep(1)
        detail_name_element = WebDriverWait(driver_naver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.Fc1rA"))
        )
        detail_url = driver_naver.current_url
        detail_name = detail_name_element.text
        print("Detail name:", detail_name)
        # 주소 정보 요소 찾기
        address_element = driver_naver.find_element(
            By.CSS_SELECTOR, "div.vV_z_ a.PkgBl span.LDgIH"
        )

        # 주소 정보 추출
        address = address_element.text
        review_count_element = driver_naver.find_element(
            By.CSS_SELECTOR,
            "#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm.f7aZ0 > div.dAsGb > span:nth-child(2) > a > em",
        )
        review_count = review_count_element.text
        try:
            image_element = WebDriverWait(driver_naver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[id='ibu_1'],div[id='ugc_1']")
                )
            )
            print("image_element", image_element)
            style_value = image_element.get_attribute("style")
            print("style_value", style_value)

            prefix = 'url("'
            suffix = '")'
            if prefix in style_value and suffix in style_value:
                start_index = style_value.index(prefix) + len(prefix)
                end_index = style_value.index(suffix)
                image_link = style_value[start_index:end_index]
                print("이미지 링크:", image_link)
            else:
                print("이미지 링크를 찾을 수 없음")

        except UnexpectedAlertPresentException:
            alert = driver_naver.switch_to.alert
            print(f"경고창 발생: {alert.text}")
            alert.accept()
        except Exception as e:
            print("이미지 링크를 찾을 수 없음")
            print(f"예외 발생: {e}")
            image_link = "이미지없음"
        try:
            # 별점 정보 얻기
            star_element = driver_naver.find_element(
                By.CSS_SELECTOR,
                "#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm.f7aZ0 > div.dAsGb > span.PXMot.LXIwF > em",
            )
            detail_star_rating = star_element.text.replace("별점", "").strip()
        except:
            detail_star_rating = "별점 없음"

        try:
            # 영업시간 정보 추출

            business_hours_element = WebDriverWait(driver_naver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.y6tNq time"))
            )

            business_hours = business_hours_element.get_attribute("textContent")
        except:
            business_hours = "영업 시간 정보 없음"

        naver_results.append(
            {
                "detail_name": detail_name,
                "detail_star_rating": detail_star_rating,
                "business_hours": business_hours,
                "review_count": review_count,
                "detail_url": detail_url,
                "image_link": image_link,
                "address": address,
            }
        )

    driver_naver.quit()
    return naver_results


def crawl_kakao(store_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    session = aiohttp.ClientSession()
    kakao_results = loop.run_until_complete(fetch_kakao_map(session, store_name))
    session.close()
    loop.close()
    return kakao_results


def crawl_naver(store_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    session = aiohttp.ClientSession()
    naver_results = loop.run_until_complete(fetch_naver_map(session, store_name))
    session.close()
    loop.close()
    return naver_results  # 결과 반환
