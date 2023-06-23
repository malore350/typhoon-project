import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

# Define the URL and target directory to save images
url = 'http://agora.ex.nii.ac.jp/digital-typhoon/himawari-3g/iiif/Hsfd/index.html?timeline=/digital-typhoon/himawari-3g/iiif/Hsfd/timeline.json&cursorIndex=1618023600&lang=en'
target_dir = "images_download/20210410_3"

# Create target directory if not already exists
os.makedirs(target_dir, exist_ok=True)

# Initialize the Chrome driver
driver = webdriver.Chrome()

# Go to the URL
driver.get(url)

# Wait for the page to load completely
time.sleep(2)

# Find the dropdown element
dropdown = Select(driver.find_element(By.CLASS_NAME, 'nav_select'))

# Loop over each option in the dropdown
for index in range(len(dropdown.options)):
    # Find the dropdown again to get the fresh element
    dropdown = Select(driver.find_element(By.CLASS_NAME, 'nav_select'))

    # Select the option by its index
    dropdown.select_by_index(index)

    # Get the image URL
    image_url = driver.find_element(By.ID, "image_download").get_attribute('href')

    # Download the image using requests
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    with open(f'{target_dir}/image_{index}.jpg', 'wb') as out_file:
        out_file.write(response.content)

# Close the driver after looping through all dropdown options
driver.quit()

# Path: images_download\downfiles.py