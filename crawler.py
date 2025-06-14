import os
import random
import sys
import time
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils_db import connect_db, check_url_exist, save_url, save_data

load_dotenv()

conn = connect_db()

driver = uc.Chrome(headless=False)
wait = WebDriverWait(driver, 1)
DOMAIN = os.getenv("DOMAIN")


def init_driver():
    cookies_str = os.getenv("COOKIES")
    cookies = []
    for pair in cookies_str.split("; "):
        name, value = pair.split("=", 1)
        cookies.append({"name": name, "value": value})
    driver.get(f"https://www.{DOMAIN}/")
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)
    time.sleep(random.uniform(5, 7))
    driver.refresh()


def crawl_main_page(page_num: int = 1):
    url = f"https://www.{DOMAIN}/listing?options=&page={page_num}&sortBy=firstOnlineDateDesc"
    driver.get(url)

    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//a[contains(@data-testid, 'vehicleCardV2')]")
    ))
    cards = driver.find_elements(By.XPATH, "//a[contains(@data-testid, 'vehicleCardV2')]")
    hrefs = [card.get_attribute("href") for card in cards]

    num_fails = 0
    for i, href in enumerate(hrefs):
        print(f"{i + 1}/{len(hrefs)} for page {page_num}.")

        if check_url_exist(conn, href):
            print("Crawled.")
            continue

        print("Sleeping...")
        time.sleep(random.uniform(7, 15))
        if i % 5 == 0:
            time.sleep(random.uniform(7, 15))
        if num_fails == 1:
            time.sleep(100)
        elif num_fails == 5:
            sys.exit(1)

        try:
            crawl_detail_page(href)
            num_fails = 0
        except Exception as e:
            print("Crawling failed!")
            save_url(conn, href, page_num)
            num_fails += 1


def crawl_detail_page(url: str):
    driver.get(url)

    data = {"url": url}

    print(f"Crawling info...")
    span_brand = driver.find_element(By.XPATH, "//a[contains(@href, 'occasion-voiture-marque')]/span")
    data["Marque"] = span_brand.text.replace("occasion", "").strip()

    span_title = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//span[contains(@class, 'CardContainer_CardContainer_title')]")
    ))
    data["Titre"] = span_title.text

    div_price = driver.find_element(By.XPATH, "//div[contains(@class, 'PriceInformation_price__VTbf2')]")
    data["Prix"] = div_price.text

    try:
        div_location = driver.find_element(By.XPATH, "//div[contains(@class, 'LocationMap_location__Tis0t')]")
        data["Code Postal"] = div_location.text
    except Exception as e:
        data["Code Postal"] = ""
        pass

    print(f"Waiting button...")
    button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-tracking-click-id, 'voirTout')]"))
    )
    time.sleep(random.uniform(7, 15))
    button.click()

    print("Waiting div...")
    div = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[contains(@class, 'ReactModal__Content')]")
    ))

    lis = div.find_elements(By.XPATH, ".//ul[contains(@class, 'LabelItems_grid__p4gcl')]/li")
    for li in lis:
        label = li.find_element(By.XPATH, ".//span[contains(@class, 'LabelItems_itemLabelName__KxJ28')]").text
        value = ""
        try:
            if label == "Volume de coffre":
                value = li.find_element(By.XPATH, ".//a").text
            elif label == "Emission de CO2":
                value = li.find_element(By.XPATH, ".//button/span").text
            else:
                value = li.find_element(By.XPATH, ".//span[contains(@class, 'LabelItems_itemValue__SHPV0')]").text
        except Exception as e:
            pass
        data[label] = value

    print(data)

    save_data(conn, data)



if __name__ == '__main__':
    begin = 66
    init_driver()
    time.sleep(random.uniform(1, 3))

    for i in range(begin, 300):
        crawl_main_page(page_num=i)
        time.sleep(random.uniform(7, 15))
