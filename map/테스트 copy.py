import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import asyncio
import aiohttp


async def fetch_naver_map(session, store_name):
    options = webdriver.ChromeOptions()
    driver_naver = webdriver.Chrome(options=options)

    driver_naver.get("https://map.naver.com/")
    driver_naver.implicitly_wait(10)

    search_element = driver_naver.find_element(By.CLASS_NAME, "input_search")
    search_element.send_keys(store_name)
    search_element.send_keys(Keys.RETURN)

    ad_results = []
    naver_results = []

    try:
        driver_naver.find_element(By.CSS_SELECTOR, "iframe#entryIframe")
    except NoSuchElementException:
        # If iframe is not present, it's a search results page
        print("This is a search results page")
        search_iframe = driver_naver.find_element(
            By.CSS_SELECTOR, "iframe#searchIframe"
        )
        driver_naver.switch_to.frame(search_iframe)

        results = driver_naver.find_elements(By.CSS_SELECTOR, "li.UEzoS")

        for result in results:
            link_element = result.find_element(
                By.CSS_SELECTOR, "span.place_bluelink.TYaxT"
            )
            link_text = link_element.text
            print("Found search result:", link_text)

            if "cZnHG" in result.get_attribute("class"):
                ad_results.append(link_text)
            else:
                # Assign values to variables for detail page
                detail_name = link_text
                review_count_element = result.find_element(
                    By.XPATH,
                    './/span[contains(@class, "h69bs") and contains(text(), "리뷰")]',
                )
                review_count = review_count_element.text.replace("리뷰", "").strip()

                link_element.click()
                time.sleep(0.05)
                detail_url = driver_naver.current_url

                try:
                    time.sleep(1)
                    star_element = WebDriverWait(driver_naver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "span.h69bs.a2RFq")
                        )
                    )
                    detail_star_rating = star_element.text.replace("별점", "").strip()
                except:
                    detail_star_rating = "별점 없음"

                try:
                    # 영업시간 정보 추출
                    driver_naver.switch_to.default_content()
                    wait = WebDriverWait(driver_naver, 10)
                    wait.until(
                        EC.frame_to_be_available_and_switch_to_it(
                            (By.CSS_SELECTOR, "iframe#entryIframe")
                        )
                    )
                    time.sleep(1)
                    business_hours_element = WebDriverWait(driver_naver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div.y6tNq time")
                        )
                    )

                    business_hours = business_hours_element.get_attribute("textContent")
                except:
                    business_hours = "영업 시간 정보 없음"

                driver_naver.switch_to.default_content()
                driver_naver.switch_to.frame(search_iframe)

                naver_results.append(
                    {
                        "detail_name": detail_name,
                        "detail_star_rating": detail_star_rating,
                        "business_hours": business_hours,
                        "review_count": review_count,
                        "detail_url": detail_url,
                    }
                )

    else:
        # If iframe is present, it's a detail page
        print("This is a detail page")
        wait = WebDriverWait(driver_naver, 10)
        wait.until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe#entryIframe")
            )
        )

        detail_url = driver_naver.current_url
        detail_name_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.Fc1rA"))
        )
        detail_name = detail_name_element.text
        print("Detail name:", detail_name)

        review_count_element = driver_naver.find_element(
            By.CSS_SELECTOR,
            "span._3ocDE",
        )
        review_count = review_count_element.text

        try:
            # 별점 정보 얻기
            star_element = driver_naver.find_element(
                By.CSS_SELECTOR,
                "span.h69bs.a2RFq",
            )
            detail_star_rating = star_element.text.replace("별점", "").strip()
        except:
            detail_star_rating = "별점 없음"

        try:
            # 영업시간 정보 추출
            driver_naver.switch_to.default_content()
            wait = WebDriverWait(driver_naver, 10)
            wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe#entryIframe")
                )
            )
            time.sleep(0.2)
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
            }
        )

    driver_naver.quit()
    return naver_results


store_name = "건대 맛집"
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
session = aiohttp.ClientSession()
result = loop.run_until_complete(fetch_naver_map(session, store_name))
session.close()
loop.close()

print(result)
