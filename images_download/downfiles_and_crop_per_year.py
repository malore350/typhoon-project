from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from urllib.parse import urljoin
import time
import requests
import os

from PIL import Image

# Define your main target directory
main_target_dir = r"C:\Users\kamra\DataspellProjects\images"

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Base URL of the site
base_url = 'http://agora.ex.nii.ac.jp'

# Go to your outer page
outer_url = 'http://agora.ex.nii.ac.jp/digital-typhoon/year/wsp/2023.html.en' # replace with the URL of the outer page
driver.get(outer_url)

# Get the HTML of the outer page
outer_html = driver.page_source

# Parse the HTML with BeautifulSoup
outer_soup = BeautifulSoup(outer_html, 'html.parser')

# Find the table and extract all rows
table = outer_soup.find('table', {'class': 'TABLELIST'})
table_rows = table.find_all('tr')

# Iterate over each row (skip the first one)
for row in table_rows[1:]:
    # Find the link in the current row
    link = row.find('a')

    if link is not None:
        # Build the full URL
        url1 = urljoin(base_url, link.get('href'))

        # Go to your target URL
        driver.get(url1)

        # Get the HTML of the page
        html = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all links with class 'IMGLINK'
        links = soup.find_all('a', {'class': 'IMGLINK'})

        # Iterate through the links
        for link in links:
            # Build the full URL (you might need to adjust this based on your site)
            url = urljoin(base_url, link.get('href'))

            # Navigate to the URL
            driver.get(url)

            # Wait for the page to load and the 'ul' element with class 'LISTITEM' to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.LISTITEM")))

            # Get the HTML of the new page
            html = driver.page_source

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Find the '35 kt' value
            all_meta_elements = soup.find_all('td', {'class': 'META'})
            max_wind_speed = all_meta_elements[8].text.strip()
            max_wind_speed = int(max_wind_speed[:-2])

            # Categorizing the wind
            if max_wind_speed < 34:
                category = '2'
            elif max_wind_speed < 48:
                category = '3'
            elif max_wind_speed < 64:
                category = '4'
            else:
                category = '5'

            # Get the folder name
            folder_name = soup.find('td', {'class': 'CURRENT'}).text.replace(":", "_").replace(" ", "_") + f"_{category}"
            folder_cropped_name = soup.find('td', {'class': 'CURRENT'}).text.replace(":", "_").replace(" ", "_") + "_cropped" + f"_{category}"

            # Create a new directory for this link if it doesn't exist
            target_dir = os.path.join(main_target_dir, folder_name)
            target_dir_cropped = os.path.join(main_target_dir, folder_cropped_name)
            os.makedirs(target_dir, exist_ok=True)
            os.makedirs(target_dir_cropped, exist_ok=True)

            #Find Longitude/Latitude information
            latitude = float(all_meta_elements[4].text.strip())
            longitude = float(all_meta_elements[5].text.strip())

            # Find all 'td' elements with class 'META' that contain 'ul' elements with class 'LISTITEM'
            all_meta_elems = soup.find_all('td', {'class': 'META'})
            listitem_links = [elem.find('ul', {'class': 'LISTITEM'}).find('a') for elem in all_meta_elems if elem.find('ul', {'class': 'LISTITEM'}) is not None]

            # Select the correct 'a' element based on the index
            listitem_link = listitem_links[3]

            # If the link is not found, skip to the next iteration
            if listitem_link is None:
                print(f"No link found in <ul> tag on {url}, skipping.")
                continue

            # Build the full URL
            listitem_url = urljoin(base_url, listitem_link.get('href'))

            # Navigate to the URL
            driver.get(listitem_url)

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

                # OPTIONAL Cropping the image
                image = Image.open(f'{target_dir}/image_{index}.jpg')
                width, height = image.size

                # left (longitude) and top (latitude) of the image
                left = 76.65
                top = 90

                # right (longitude) and bottom (latitude) of the image
                right = 225
                bottom = -90

                # conversion to pixel coordinates
                x = (longitude - left) / (right - left) * width
                y = (top - latitude) / (top - bottom) * height

                # cropping the image
                cropped_image = image.crop((x-1000, y-1000, x+1000, y+1000))
                cropped_image.save(f'{target_dir_cropped}/image_{index}.jpg')


# Close the browser
driver.quit()
