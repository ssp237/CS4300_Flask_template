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
driver.get('https://www.beautypedia.com/skin-care/')
products = driver.find_elements_by_xpath('//a[@class="review-product"]')
product_list = []
for p in range(len(products)):
    product_list.append(products[p].text)
prices = driver.find_elements_by_xpath('//div[@class="review-price"]')
price_list = []
for p in range(len(prices)):
    #turns the string dollar amount into a number
    price_list.append(float((prices[p].text).replace('$', '')))
links = [None] * len(product_list)
for i, product in enumerate(product_list) :
    lst = []
    #tokenize the product name
    tokes = product.split(' ')
    #join all tokens by a hyphen
    str1 = '-'.join(tokes)
    #remove the percent symbols
    str1 = str1.replace('%', '')
    #put into link structure
    links[i] = "https://www.beautypedia.com/products/" +str1+ "/?archive_search=%2Fskin-care%2F"
more_data = [None] * len(product_list)
for i, site in enumerate(links) :
    temp = {}
    driver.get(site)
    #this is to manually close ads because i can't find code to do it
    #if you run it and an ad comes up you have to close it or it'll break
    time.sleep(5)
    faves = driver.find_elements_by_xpath('//div[@class="faves"]')
    temp['num faves'] = int(faves[0].text)
    brand = driver.find_elements_by_xpath('//a[@class="brand-name"]')
    temp['brand'] = brand[0].text
    #clicks on the claims tab
    button =driver.find_element_by_xpath('//h3[@class="tab-title claims"]')
    button.click()
    claims = driver.find_elements_by_xpath('//div[@id="claims"]')
    temp['claims'] = claims[0].text
    #clicks on the ingredients tab
    button2 = driver.find_element_by_xpath('//h3[@class="tab-title ingredients"]')
    button2.click()
    ingredients = driver.find_elements_by_xpath('//div[@id="ingredients"]')
    temp['ingredients'] = ingredients[0].text
    more_data[i] =temp
data = {}
#put all data into a dictionary
for i, product in enumerate(product_list):
    temp = {'price':price_list[i], 'link':links[i]}
    temp.update(more_data[i])
    data[product_list[i]] = temp
#put dictionary into a json
with open('data.txt', 'w') as outfile:
    json.dump(data, outfile, indent = 7)
#close the browser
driver.quit()