from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()
driver.get('https://sc-nc-web.nict.go.jp/wsdb_osndisk/shareDirDownload/03ZzRnKS?lang=en')

wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)

checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.selectable.t8')))
actions.double_click(checkbox_element).perform()

checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.selectable.t4')))
actions.double_click(checkbox_element).perform()

checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.selectable.t2')))
actions.double_click(checkbox_element).perform()

time.sleep(2)

thumb_list = wait.until(EC.presence_of_element_located((By.ID, 'thumb_list')))
thumbnails = thumb_list.find_elements(By.CSS_SELECTOR, '.thumbnail')

with open('dates.txt', 'r') as file:
    date_list = [date.strip()[:7] + '/' for date in file.readlines()]

for thumbnail in thumbnails:
    try:
        time.sleep(2)
        name = thumbnail.find_element(By.XPATH, './/div[contains(@class, "select directory")]').get_attribute('name')
        time.sleep(2)
        if name in date_list:
            print("Match found:", name)
            actions.double_click(thumbnail).perform()
            time.sleep(2)
            checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.t0')))
            actions.double_click(checkbox_element).perform()
            time.sleep(2)
        else:
            print("No matching date for:", name)
    except Exception:
        continue

time.sleep(5)
driver.quit()
