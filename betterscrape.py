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
links = []
#was on 201
#max is 746
for i in range(81,199):
    if i == 1 :
        driver.get('https://www.beautypedia.com/products/')
    else :
        driver.get('https://www.beautypedia.com/products/page/' + str(i) +'/')
    products = driver.find_elements_by_xpath('//div[@class="card-product-name"]')
    for p in range(0,len(products)):
        product=products[p].text
        product_list.append(product)
        lst = []
        #tokenize the product name
        tokes = product.split(' ')
        #join all tokens by a hyphen
        str1 = '-'.join(tokes)
        #remove the percent symbols
        str1 = str1.replace('%', '')
        str1= str1.replace('è', 'e')
        str1 = str1.replace('é', 'e')
        str1 = str1.replace('#', '')
        str1 = str1.replace('.','-')
        str1 = str1.replace('"','')
        str1 = str1.replace("'",'')
        str1 = str1.replace("’",'')
        str1 = str1.replace('”','')
        str1 = str1.replace('“','')
        #str1 = str1.replace('+', '2')
        #if str1 == "Super-Glow-Vitamin-C-+-Magnesium-Serum/":
            #str1 = "super-glow"
        #put into link structure
        links.append("https://www.beautypedia.com/products/" +str1+ "/?archive_search=%2Fskin-care%2F")
    

    
more_data = []
for site in links:
    temp = {}
    driver.get(site)
    #this is to manually close ads because i can't find code to do it
    #if you run it and an ad comes up you have to close it or it'll break
    #time.sleep(2)
    try:
        faves = driver.find_elements_by_xpath('//div[@class="faves"]')
        temp['num faves'] = int(faves[0].text)
    except:
        temp['num faves'] = ''
    try :
        brand = driver.find_elements_by_xpath('//a[@class="brand-name"]')
        temp['brand'] = brand[0].text
    except:
        temp['brand'] = ''
    try:
        #clicks on the claims tab
        button =driver.find_element_by_xpath('//h3[@class="tab-title claims"]')
        button.click()
        claims = driver.find_elements_by_xpath('//div[@id="claims"]')
        temp['claims'] = claims[0].text
    except:
        temp['claims'] = ''
        #clicks on the ingredients tab
    try:
        button2 = driver.find_element_by_xpath('//h3[@class="tab-title ingredients"]')
        button2.click()
        ingredients = driver.find_elements_by_xpath('//div[@id="ingredients"]')
        temp['ingredients'] = ingredients[0].text
    except:
        temp['ingredients'] = ''
    try :
        prices = driver.find_elements_by_xpath('//span[@class="price"]')
        price=(prices[0].text)
        if len(price.replace('$', '')) > 0 :
            temp['price'] = (float(price.replace('$', '')))
        else:
            temp['price'] = 0
    except:
        temp['price'] = 0
    more_data.append(temp)
    
    
data = {}
#put all data into a dictionary
for i, product in enumerate(product_list):
    temp = {'link':links[i]}
    temp.update(more_data[i])
    data[product_list[i]] = temp
#put dictionary into a json
with open('bigdata2.json', 'w') as outfile:
    json.dump(data, outfile, indent = 7)
#close the browser
driver.quit()