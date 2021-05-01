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
with open('finaldata.json') as json_file:
    data = json.load(json_file)
productrate= []
for key, dic in data.items() :
    link = dic['link']
    try:
        driver.get(link)
    except:
        pass
    rate = 0
    try:
        faves = driver.find_elements_by_xpath('//div[@class="product-rating rating stars-1"]')
        productrate.append({'product': key,'rate': 1})
    except:
        pass
    try:
        faves = driver.find_elements_by_xpath('//div[@class="product-rating rating stars-2"]')
        productrate.append({'product': key,'rate': 2})
    except:
        pass
    try:
        faves = driver.find_elements_by_xpath('//div[@class="product-rating rating stars-3"]')
        productrate.append({'product': key,'rate': 3})
    except:
        pass
    try:
        faves = driver.find_elements_by_xpath('//div[@class="product-rating rating stars-4"]')
        productrate.append({'product': key,'rate':4})
    except:
        pass
    try:
        faves = driver.find_elements_by_xpath('//div[@class="product-rating rating stars-5"]')
        productrate.append({'product':key,'rate':5})
    except:
        pass
with open('reviews.json', 'w') as outfile:
    json.dump(productrate, outfile, indent = 7)
