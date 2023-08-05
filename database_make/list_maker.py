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

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Base URL of the site
base_url = 'http://agora.ex.nii.ac.jp'

# Go to your outer page
outer_url = 'http://agora.ex.nii.ac.jp/digital-typhoon/year/wsp/2021.html.en'
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
    tds = row.find_all('td')
    if any('noname' in td.text.lower() or 'unnamed' in td.text.lower() for td in tds):
        continue

    link = row.find('a')

    if link is not None:
        url1 = urljoin(base_url, link.get('href'))

        driver.get(url1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', {'class': 'IMGLINK'})

        for link in links:
            url = urljoin(base_url, link.get('href'))

            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.LISTITEM")))
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            folder_name = soup.find('td', {'class': 'CURRENT'}).text.replace(":", "_").replace(" ", "_")
            folder_name = folder_name[0:4] + folder_name[5:7] + folder_name[8:10] +'/'

            with open('database_make/output.txt', 'a+') as f:
                # Move to the beginning of the file to read it
                f.seek(0)
                # Read all lines in the file
                lines = f.readlines()

                # Check if the folder name is already in the file
                if folder_name + '\n' not in lines:
                    # If not, write it to the file
                    f.write(folder_name + '\n')

driver.quit()

#TODO: Add typhoon's category, latitude and longitude information in the written txt file