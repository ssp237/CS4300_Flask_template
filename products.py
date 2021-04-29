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
#open browser, have to give it path to the chromedriver
driver = webdriver.Chrome(executable_path="C:/Users/ergre/Downloads/chromedriver_win32/chromedriver.exe")
#go to website
product_list = []
driver.get('https://www.beautypedia.com/skin-care/?size=96&skincare_group[0]=water-resistant-sunscreen-reviews')
time.sleep(5)
for i in range(0,2):
    products = driver.find_elements_by_xpath('//a[@class="review-product"]')
    for p in range(0,len(products)):
        product=products[p].text
        product_list.append(product)
    print("done")
    time.sleep(10)
with open('water_resistant_sunscreen_products.json', 'w') as outfile:
    json.dump(product_list, outfile, indent = 7)