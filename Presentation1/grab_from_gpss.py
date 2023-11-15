"""
從https://gpss3.tipo.gov.tw/，抓取專利號碼、專利名稱
"""

import time
import requests
import json
import re
import os
import unicodedata
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


# 從Global Patent Search專利搜索查詢專利ID
def get_patent_data_from_gpss(query):
    # Initialize the Selenium webdriver
    driver = webdriver.Chrome()

    # Navigate to the website
    driver.get("https://gpss3.tipo.gov.tw/")

    try:
        # Click "檢索空欄"
        keywords_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "term1")))
        actions = ActionChains(driver)
        actions.move_to_element(keywords_element).perform()

        # Fill the textarea
        keywords_element.send_keys(query)

        # Click the input button to submit
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button")))
        submit_button.click()

        # # 移動到"家族合并"icon and click
        # family_element = WebDriverWait(driver, 30).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "btnchk")))
        # actions = ActionChains(driver)
        # actions.move_to_element(family_element).perform()
        # actions.click().perform()
        # input("瀏覽器已暫停，按下 Enter 鍵繼續...")

        # 移動到"家族去重"icon and click
        family_element = WebDriverWait(driver, 30).until(
            # EC.presence_of_element_located((By.CLASS_NAME, "btnchk")))
            EC.presence_of_element_located((By.CSS_SELECTOR,"input[type='submit'][name='BUTTON'][value='家族去重']")))
        actions = ActionChains(driver)
        actions.move_to_element(family_element).perform()
        actions.click().perform()
        # input("瀏覽器已暫停，按下 Enter 鍵繼續...")

        # 移動到"數量"icon ， 選擇 50 and click
        select_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select[onchange='instback(this)']")))

        actions = ActionChains(driver)
        actions.move_to_element(select_element).perform()

        select = Select(select_element)
        select.select_by_visible_text('50')
        # input("瀏覽器已暫停，按下 Enter 鍵繼續...")

        patent_ids_all = []
        patent_titles_all = []

        pages_ttl = driver.find_elements(By.CLASS_NAME, "numfmt")[2].text if \
            len(driver.find_elements(By.CLASS_NAME, "numfmt")) > 2 else None
        pages_ttl = int(pages_ttl)

        progress_bar = tqdm(total = pages_ttl)
        condition = True
        iteration = 0

        while condition and iteration < pages_ttl:
            progress_bar.update(1)
            iteration += 1
            # 檢查頁碼 找到所有帶有 'numfmt' 類別的 <span> 標籤
            numfmt_elements = driver.find_elements(By.CLASS_NAME,"numfmt")
            # 提取和打印所有找到的數字
            numbers = [element.text for element in numfmt_elements]
            # print(f"{numbers[1]} / {numbers[2]}")

            # 找到所有帶有特定class=sumtd2_PN的元素
            application_element = driver.find_elements(By.CLASS_NAME, "sumtd2_PN")
            patent_ids = [element.text for element in application_element]
            # 找到所有帶有特定class=sumtd2_TI的元素
            application_element = driver.find_elements(By.CLASS_NAME, "sumtd2_TI")
            patent_titles = [element.text for element in application_element]
            # patent_titles = [element.text for element in application_element if not contains_chinese(element.text)]

            patent_ids_all.extend(patent_ids)
            patent_titles_all.extend(patent_titles)
            # input("瀏覽器已暫停，按下 Enter 鍵繼續...")

            if int(numbers[1])>= pages_ttl:  #最後一頁:
                condition = 0
            else:
                # 翻到下一頁
                next_page_button = driver.find_element(By.NAME, "_IMG_次頁")
                next_page_button.click()
                time.sleep(1)

        progress_bar.close()
        driver.quit()
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pass

    return patent_ids_all, patent_titles_all


# 從GPSS抓取專利號碼和專利名稱
query = '((drone OR uav))@AB NOT ((ice OR engine))@AB AND ID=20200101:'
patent_ids_all, patent_titles_all = get_patent_data_from_gpss(query)

# 儲存檔案
patent_ids_file_path = os.path.join('dataset', 'patent_ids.txt')
patent_titles_file_path = os.path.join('dataset', 'patent_titles.txt')
# 創建或取代檔案
with open(patent_ids_file_path, 'w', encoding='utf-8') as f:
    for patent_id in patent_ids_all:
        f.write(patent_id + "\n")

with open(patent_titles_file_path, 'w', encoding='utf-8') as f:
    for patent_title in patent_titles_all:
        f.write(patent_title + "\n")

print(f'ID quantity={len(patent_ids_all)}, Title quantity={len(patent_titles_all)}')
