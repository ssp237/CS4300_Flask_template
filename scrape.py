from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import random
import re
import os
import csv
import math
driver = webdriver.Chrome(executable_path="C:/Users/ergre/Downloads/chromedriver_win32/chromedriver.exe")
driver.get('https://www.beautypedia.com/skin-care/')
products = driver.find_elements_by_xpath('//a[@class="review-product"]')
product_list = []
for p in range(len(products)):
    product_list.append(products[p].text)
prices = driver.find_elements_by_xpath('//div[@class="review-price"]')
price_list = []
for p in range(len(prices)):
    price_list.append(prices[p].text)
links = [None] * len(product_list)
for i, product in enumerate(product_list) :
    lst = []
    tokes = product.split(' ') 
    str1 = '-'.join(tokes) 
    str1 = str1.replace('%', '')
    links[i] = "https://www.beautypedia.com/products/" +str1+ "/?archive_search=%2Fskin-care%2F"
more_data = [None] * len(product_list)
for i, site in enumerate(links) :
    temp = {}
    driver.get(site)
    faves = driver.find_elements_by_xpath('//div[@class="faves"]')
    temp['num faves'] = faves[0].text
    brand = driver.find_elements_by_xpath('//a[@class="brand-name"]')
    temp['brand'] = brand[0].text
    #these don't woek yet
    #animal_tested = driver.find_elements_by_xpath('//span[contains(@class,"value")]')
    #temp['animal tested?'] = animal_tested[0]
    #claim = driver.find_elements_by_xpath('//div[@id="claims"]') 
    #temp['claims'] = claim[0].text
    #ingredients = driver.find_elements_by_xpath('//div[@id="ingredients"]')
    #temp['ingredients'] = ingredients[0].text
    more_data[i] =temp
data = []
for i, product in enumerate(product_list):
    temp = {'name':product_list[i], 'price':price_list[i], 'link':links[i]}
    temp.update(more_data[i])
    data.append(temp)
print(data)