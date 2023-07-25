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

import subprocess
import time

import cv2
import numpy as np
from scipy.spatial import Delaunay


# Define your main target directory
main_target_dir = "/lustre/home/sasha/typhoon/images/2021"
main_projected_dir = "/lustre/home/sasha/typhoon/projected/2021"
main_cropped_dir = "/lustre/home/sasha/typhoon/cropped/2021"
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Base URL of the site
base_url = 'http://agora.ex.nii.ac.jp'

# Go to your outer page
outer_url = 'http://agora.ex.nii.ac.jp/digital-typhoon/year/wsp/2021.html.en' # replace with the URL of the outer page
driver.get(outer_url)

# Get the HTML of the outer page
outer_html = driver.page_source

# Parse the HTML with BeautifulSoup
outer_soup = BeautifulSoup(outer_html, 'html.parser')

# Find the table and extract all rows
table = outer_soup.find('table', {'class': 'TABLELIST'})
table_rows = table.find_all('tr')

# # OPTIONAL: FOR CROPPING:
# CONVERT LAN/LON TO PIXEL COORDINATES
# List of latitude/longitude points
latlon_points = np.array([
    [-11.9, 92.6],
    [-14, 117.5],
    [-14.7, 153.6],
    [-28.2, 166.2],
    [-9.8, 101.0], 
    [-10.5, 156.3]
], dtype=np.float32)

# List of corresponding pixel points
pixel_points = np.array([
    [1160, 6690],
    [3040, 6977],
    [6816, 7025],
    [7792, 8358],
    [1648, 6652], 
    [7236,6824]
], dtype=np.float32)

# Find the transformation matrix
M_geo_to_pix, mask = cv2.findHomography(latlon_points, pixel_points)

# Define a function that uses the matrix to transform lat/lon coordinates to pixel coordinates
def latlon_to_pixel(lat, lon):
    # Use the transformation matrix to convert lat/lon to pixel
    latlon = np.array([[[lat, lon]]], dtype=np.float32)
    pixel = cv2.perspectiveTransform(latlon, M_geo_to_pix)
    return pixel[0][0]

# CONVERT PIXEL COORDINATES TO PROJECTED COORDINATES

# List of projected points (replace with your actual points)
projected_points = np.array([
    [800, 4532],
    [2340, 4650],
    [4537, 4660],
    [5357, 5544],
    [1277, 4488],
    [4737, 4552]
], dtype=np.float32)

# Find the transformation matrix
M, mask = cv2.findHomography(pixel_points, projected_points)

def transform_points(points):

    # Now you can use this matrix to convert points from the original image to the projected image
    # For example, let's transform the original point (150, 150)
    original_point = np.array([[[points[0], points[1]]]], dtype=np.float32)
    projected_point = cv2.perspectiveTransform(original_point, M)
    return projected_point[0][0]


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
            folder_name = folder_name[2:4] + folder_name[5:7] + folder_name[8:10] + "_" + folder_name[11:13] + folder_name[14:16] + f"_{category}"
            print(folder_name)
            folder_cropped_name = soup.find('td', {'class': 'CURRENT'}).text.replace(":", "_").replace(" ", "_") + "_cropped" + f"_{category}"

            # Create a new directory for this link if it doesn't exist
            target_dir = os.path.join(main_target_dir, folder_name)
            target_dir_cropped = os.path.join(main_cropped_dir, folder_cropped_name)
            projected_dir = os.path.join(main_projected_dir, folder_name)
            
            if not os.path.isdir(target_dir) and not os.path.isdir(target_dir_cropped):
                os.makedirs(target_dir, exist_ok=True)
                os.makedirs(target_dir_cropped, exist_ok=True)
                os.makedirs(projected_dir, exist_ok=True)

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
                    with open(f'{target_dir}/{folder_name[:-1]}1.jpg', 'wb') as out_file:
                        out_file.write(response.content)

                    # APPLY PROJECTION TO THE IMAGE
                    start_time = time.time()
                    command = ["typhoon/sanchez-v1.0.24-linux-x64/Sanchez", "reproject", "-s", f'{target_dir}/{folder_name[:-1]}1.jpg', "-o", f'{projected_dir}/image_{index}_{category}.jpg', "-ULa", "-r", "1"] # "--lon", f'{longitude-5}:{longitude+5}', "--lat", f'{latitude+5}:{latitude-5}'
                    subprocess.run(command)
                    end_time = time.time()
                    print(f"Time taken to reproject image {index}: {end_time - start_time}")

                    output = latlon_to_pixel(latitude, longitude)
                    output_project = transform_points(output)
                    image = Image.open(f'{projected_dir}/image_{index}_{category}.jpg')
                    width, height = image.size

                    # Define the cropping size
                    crop_size = 1000

                    # Calculate the proposed crop box
                    left = output_project[0]-crop_size
                    top = output_project[1]-crop_size
                    right = output_project[0]+crop_size
                    bottom = output_project[1]+crop_size

                    # Make sure the proposed crop box doesn't exceed the image's dimensions
                    if left < 0:
                        right -= left  # shift right boundary to the right
                        left = 0
                    if top < 0:
                        bottom -= top  # shift bottom boundary down
                        top = 0
                    if right > width:
                        left -= right - width  # shift left boundary to the left
                        right = width
                    if bottom > height:
                        top -= bottom - height  # shift top boundary up
                        bottom = height

                    # cropping the image
                    cropped_image = image.crop((left, top, right, bottom))
                    cropped_image.save(f'{target_dir_cropped}/{folder_name[:-1]}{index}_{category}.jpg')

                    # # OPTIONAL Cropping the image
                    # output = latlon_to_pixel(latitude, longitude)
                    # image = Image.open(f'{target_dir}/image_{index}.jpg')
                    # width, height = image.size

                    # # cropping the image
                    # cropped_image = image.crop((output[0]-1000, output[1]-1000, output[0]+1000, output[1]+1000))
                    # cropped_image.save(f'{target_dir_cropped}/image_{index}.jpg')
            else:
                # if number of items in folder doesn't match number of files in the dropdown,
                # write a code to pick up from where it is left based on the number of files in folder
                # serving as index
                continue


# Close the browser
driver.quit()
