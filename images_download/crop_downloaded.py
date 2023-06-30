# THIS IS USED IN CASE IMAGES ARE DOWNLOADED, BUT CROP IS NOT DONE
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
import numpy as np
from scipy.optimize import curve_fit
from pyproj import Proj, transform

# Define your main target directory
main_target_dir = "TyphoonProject/typhoon-project/images/2022"

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Base URL of the site
base_url = 'http://agora.ex.nii.ac.jp'

# Go to your outer page
outer_url = 'http://agora.ex.nii.ac.jp/digital-typhoon/year/wsp/2022.html.en' # replace with the URL of the outer page
driver.get(outer_url)

# Get the HTML of the outer page
outer_html = driver.page_source

# Parse the HTML with BeautifulSoup
outer_soup = BeautifulSoup(outer_html, 'html.parser')

# Find the table and extract all rows
table = outer_soup.find('table', {'class': 'TABLELIST'})
table_rows = table.find_all('tr')

# OPTIONAL: FOR CROPPING:
# Define the projection
p1 = Proj(proj='latlong', datum='WGS84')
p2 = Proj('+proj=geos +lon_0=140.7 +h=35785831.0 +x_0=0 +y_0=0 +a=6378169.0 +b=6356583.8 +units=m +no_defs')

# Define the calibration points
latlon_points = [(-11.9, 92.6), (-14, 117.5), (-14.7, 153.6), (-9.8, 101.0), (-10.5, 156.3)]
pixel_points = [(1122, 6696), (3040, 6977), (6816, 7025), (1648, 6652), (7236,6824)]

# Convert lat/lon to projected coordinates
proj_points = [transform(p1, p2, lon, lat) for lat, lon in latlon_points]

# Define the transformation functions
def func_x(x, a, b):
    return a * x + b
def func_y(y, a, b):
    return a * y + b

# Determine the parameters for the transformation functions
params_x, _ = curve_fit(func_x, [point[0] for point in proj_points], [point[0] for point in pixel_points])
params_y, _ = curve_fit(func_y, [point[1] for point in proj_points], [point[1] for point in pixel_points])

# Now you can use these transformation functions to convert any lat/lon to pixel coordinates
def latlon_to_pixel(lat, lon):
    x, y = transform(p1, p2, lon, lat)
    return func_x(x, *params_x), func_y(y, *params_y)

def count_files_in_directory(directory):
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])



# Iterate over each row (skip the first one)
for row in table_rows[1:]:
    # Find all 'td' elements in the row
    tds = row.find_all('td')

    # Check if any 'td' contains 'noname'
    if any('noname' in td.text.lower() or 'unnamed' in td.text.lower() for td in tds):
        # If so, skip this iteration
        continue

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
            print(url)

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

            if not os.path.isdir(target_dir) or not os.path.isdir(target_dir_cropped):
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
                    output = latlon_to_pixel(latitude, longitude)
                    image = Image.open(f'{target_dir}/image_{index}.jpg')
                    width, height = image.size

                    # cropping the image
                    cropped_image = image.crop((output[0]-1000, output[1]-1000, output[0]+1000, output[1]+1000))
                    cropped_image.save(f'{target_dir_cropped}/image_{index}.jpg')
            else:
                #Find Longitude/Latitude information
                latitude = float(all_meta_elements[4].text.strip())
                longitude = float(all_meta_elements[5].text.strip())

                # Find all 'td' elements with class 'META' that contain 'ul' elements with class 'LISTITEM'
                all_meta_elems = soup.find_all('td', {'class': 'META'})
                listitem_links = [elem.find('ul', {'class': 'LISTITEM'}).find('a') for elem in all_meta_elems if elem.find('ul', {'class': 'LISTITEM'}) is not None]

                # Select the correct 'a' element based on the index
                listitem_link = listitem_links[3]

                # Build the full URL
                listitem_url = urljoin(base_url, listitem_link.get('href'))

                # Navigate to the URL
                driver.get(listitem_url)

                # Wait for the page to load completely
                time.sleep(2)

                # Find the dropdown element
                dropdown = Select(driver.find_element(By.CLASS_NAME, 'nav_select'))


                for index in range(count_files_in_directory(target_dir)):
                    output = latlon_to_pixel(latitude, longitude)
                    image = Image.open(f'{target_dir}/image_{index}.jpg')
                    width, height = image.size

                    # cropping the image
                    cropped_image = image.crop((output[0]-1000, output[1]-1000, output[0]+1000, output[1]+1000))
                    cropped_image.save(f'{target_dir_cropped}/image_{index}.jpg')

                continue


# Close the browser
driver.quit()