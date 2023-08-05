from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Replace 'path_to_chromedriver' with the path to your downloaded ChromeDriver executable
driver = webdriver.Chrome()

# Replace 'your_website_url' with the URL of your website
driver.get('https://sc-nc-web.nict.go.jp/wsdb_osndisk/shareDirDownload/03ZzRnKS?lang=en')

# We get to choose HIMAWARI-8 from list
wait = WebDriverWait(driver, 4)
checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.selectable.t8')))

actions = ActionChains(driver)
actions.double_click(checkbox_element).perform()

# We get to choose HISD from list
wait = WebDriverWait(driver, 4)
checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.selectable.t4')))

actions.double_click(checkbox_element).perform()

# We get to choose Full Disk from list
wait = WebDriverWait(driver, 4)
checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.selectable.t2')))

actions.double_click(checkbox_element).perform()


time.sleep(2)
# We get to choose the date from list
wait = WebDriverWait(driver, 4)

# Locate the thumb_list element
thumb_list = wait.until(EC.presence_of_element_located((By.ID, 'thumb_list')))

# Find all the div elements with the class "thumbnail" within thumb_list
thumbnails = thumb_list.find_elements(By.CSS_SELECTOR, '.thumbnail')

# Using an index to track current thumbnail
i = 0

# Loop until all thumbnails are processed
while i < len(thumbnails):
    # Need to re-fetch thumbnails as the page state has changed
    thumb_list = wait.until(EC.presence_of_element_located((By.ID, 'thumb_list')))
    thumbnails = thumb_list.find_elements(By.CSS_SELECTOR, '.thumbnail')
    thumbnail = thumbnails[i]

    # Perform a double-click action on the thumbnail
    class_name = thumbnail.get_attribute('class')

    # Check if the current thumbnail has the class "thumbnail selectable t2"
    if 'thumbnail t0' in class_name or 'thumbnail nodisp t1' in class_name:
        i += 1
        continue

    actions.double_click(thumbnail).perform()
    # Wait 2 seconds
    time.sleep(2)
    checkbox_element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumbnail.t0')))
    actions.double_click(checkbox_element).perform()
    # Wait for the page to return to the previous state
    time.sleep(2)

    # Increment index to process the next thumbnail
    i += 1



# Add a delay of 5 seconds to observe the subsequent behavior
time.sleep(5)

# Close the browser
driver.quit()
