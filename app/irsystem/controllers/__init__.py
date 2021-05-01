# Import flask deps
from flask import request, render_template, \
    flash, g, session, redirect, url_for, jsonify, abort

# For decorators around routes
from functools import wraps

# Import for pass / encryption 
from werkzeug import check_password_hash, generate_password_hash

# Import the db object from main app module
from app import db

# Marshmallow 
from marshmallow import ValidationError

# Import socketio for socket creation in this module 
from app import socketio

# Import module models 
# from app.irsystem import search

# IMPORT THE BLUEPRINT APP OBJECT 
from app.irsystem import irsystem

# Import module models
from app.accounts.models.user import *
from app.accounts.models.session import *

# Import json (TODO should this be loaded here???)
# TODO: wrap in helper function
import numpy as np
import json
import glob
import re


def getProducts(i_list, p_data):
    """
    Return a list of the products that contain at least one ingredient
    in the given list.
    :param i_list: List of ingredients to search for
    :param p_data: Product data to search in
    :return: List of products that contain at least one ingredient in i_list
    """
    i_set = set(i_list)
    out = []
    for k, v in p_data.items():
        i = 0
        found = False
        while i < len(v['ingredients']) and not found:
            found = v['ingredients'][i] in i_set
            i += 1
        if found:
            out.append(k)

    return out


with open("finaldata.json", "r") as f:
    data = json.loads("\n".join(f.readlines()))

with open("ingredients.json", "r", errors='ignore') as f:
    u_ingredients = json.loads("\n".join(f.readlines()))

with open("concerns.json", "r") as f:
    u_concerns = json.loads("\n".join(f.readlines()))
    
with open("relevant_types.json", "r") as f:
    relevant_product_types = json.loads("\n".join(f.readlines()))
    

# Cleaning ingredients
for _, v in data.items():
    i_string = v['ingredients']
    if i_string[-1] == '.': i_string = i_string[:len(i_string) - 1]
    i_list = re.split(", |\. ", i_string)
    v['ingredients'] = [(re.sub(r".*:", "", s)).strip() for s in i_list]

categories = {}

for k, v in u_concerns.items():
    d = {
        "concerns": ", ".join(v),
        "products": getProducts(u_ingredients[k], data)
    }
    categories[k.lower()] = d

# Construct auxiliary data structures
num_products = len(data)
category_to_index = {name: index for index, name in enumerate(categories)}
products_to_indices = {k: v for k, v in zip(data.keys(), range(num_products))}
indices_to_products = {v: k for k, v in products_to_indices.items()}

def create_product_types_dict():
    """Returns a dictionary to map product types to Boolean arrays 
    (True if index corresponds to a product of that type).
    
    Params: {}
    Returns: (String -> Numpy Array) Dict 
    """
    product_types = {}
    product_files = glob.glob("./product_types_lists/*.json")
    if len(product_files) == 0: 
        print('can\'t read')  
    
    for p_file in product_files:
        name = p_file[22:-5]
        with open(p_file) as json_file:
            data = json.load(json_file)
        p_arr = np.full(num_products, False)
        for p in data:
            if p not in products_to_indices.keys():
                continue
            p_arr[products_to_indices[p]] = True
        product_types[name] = p_arr
    
    return product_types

def create_price_ranges():
    """Returns a dictionary to map price ranges to Boolean arrays 
    (True if index corresponds to a product within the budget).
    
    Params: {}
    Returns: (String -> Numpy Array) Dict 
    """
    price_ranges = dict([('under $15', np.full(num_products, False)), ('$15-30', np.full(num_products, False)),
                         ('$30-50', np.full(num_products, False)), ('$50-75', np.full(num_products, False)), 
                         ('$75+', np.full(num_products, False))])
    for k,v in data.items():
        if v['price'] < 15:
            price_ranges['under $15'][products_to_indices[k]] = True
        elif v['price'] < 30:
            price_ranges['$15-30'][products_to_indices[k]] = True
        elif v['price'] < 30:
            price_ranges['$30-50'][products_to_indices[k]] = True
        elif v['price'] < 30:
            price_ranges['$50-75'][products_to_indices[k]] = True
        else :
            price_ranges['$75+'][products_to_indices[k]] = True
    
    return price_ranges

product_types = create_product_types_dict()
price_ranges = create_price_ranges()

