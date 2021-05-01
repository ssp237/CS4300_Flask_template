from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import json
import time
import random
import re
import os
import csv
import math
import time
driver = webdriver.Chrome(executable_path="C:/Users/ergre/Downloads/chromedriver_win32/chromedriver.exe")
driver.get('https://www.crueltyfreekitty.com/list-of-cruelty-free-brands/')
brands = driver.find_elements_by_xpath('//a[@class="heading heading--secondary brand-list__list__title"]')
brands_names = [];
for bnd in brands :
    brands_names.append(bnd.text)
with open('crueltyfree.json', 'w') as outfile:
    json.dump(brands_names, outfile, indent = 7)