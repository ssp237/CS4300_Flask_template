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
from config import Config
from ..models.products import Product

# IMPORT THE BLUEPRINT APP OBJECT 
from app.irsystem import irsystem

# Import module models
from app.accounts.models.user import *
from app.accounts.models.session import *

# Import json (TODO should this be loaded here???)
# TODO: wrap in helper function
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
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


def dicToNumpy(dic):
    """
    Convert Dictionary d representing a JSON of tips and keywords to
    a matrix representation - rows are tips, columns are keywords. Also
    returns a dict of tips to inds and keywords to inds
    :param dic: Dictionary to convert, must be of form
    { tips : {terms: {term : count}} }
    :return: Tuple of numpy array, tip_ind dict, keyword_ind dict
    """
    terms = set()
    for _, v in dic.items():
        terms = terms | set(v["terms"].keys())
    n_tips, n_terms = len(dic), len(terms)
    arr = np.zeros((n_tips, n_terms))
    tip_ind = {t: i for (t, i) in zip(dic, range(n_tips))}
    key_ind = {key: i for (key, i) in zip(terms, range(n_terms))}
    for k, v in dic.items():
        for w, c in v["terms"].items():
            arr[tip_ind[k], key_ind[w]] = c
    return arr, tip_ind, key_ind


def numpyToDic(arr, tip_ind, key_ind, dic):
    """
    Update the counts in dic to reflect the counts stored in
    numpy array arr.
    :param arr: Numpy array where rows are tips and columns are
    counts of relevant terms
    :param tip_ind: Dictionary of tips to indices
    :param key_ind: Dictionary of terms to indices
    :param dic: Dictionary to update, must be of form
    { tips : {terms: {term : count}} }
    """
    tip_rev = {v: k for (k, v) in tip_ind.items()}
    key_rev = {v: k for (k, v) in key_ind.items()}
    m, n = arr.shape
    for i in range(m):
        for j in range(n):
            if arr[i, j] > 0:
                dic[tip_rev[i]]["terms"][key_rev[j]] = arr[i, j]


data_file = "finaldata.json"
ingredients_file = "ingredients.json"
concerns_file = "concerns.json"
tip_file = "skincare_tips.json"

with open(data_file, "r") as f:
    data = json.loads("\n".join(f.readlines()))

with open(ingredients_file, "r") as f:
    u_ingredients = json.loads("\n".join(f.readlines()))

with open(concerns_file, "r") as f:
    u_concerns = json.loads("\n".join(f.readlines()))

with open("relevant_types.json", "r") as f:
    relevant_product_types = json.loads("\n".join(f.readlines()))

with open(tip_file, "r") as f:
    tips = json.loads("\n".join(f.readlines()))

with open("reviews.json", "r") as f:
    reviews_lst = json.loads("\n".join(f.readlines()))

with open("product_type_names.json", "r") as f:
    product_file_to_type = json.loads("\n".join(f.readlines()))

for _, v in data.items():
    i_string = v['ingredients']
    if i_string[-1] == '.': i_string = i_string[:len(i_string) - 1]
    i_list = list(filter(lambda x: (x is not None) and (x.strip() != ","),
                         re.split(r"(, |\.)|(\(and\)) ", i_string)))
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

tips_arr, tips_to_ind, terms_to_ind = dicToNumpy(tips)


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
        with open(p_file) as json_file:
            data = json.load(json_file)
        p_arr = np.full(num_products, False)
        for p in data:
            if p not in products_to_indices.keys():
                continue
            p_arr[products_to_indices[p]] = True
        product_types[product_file_to_type[p_file[22:-5]]] = p_arr

    return product_types


def create_prices():
    prices = np.array(np.ndarray.flatten(np.indices((1,num_products))[1]), dtype=float)
    for x in prices:
        prices[int(x)] = data[indices_to_products[int(x)]]['price']
    return prices


def create_ratings():
    """Returns a Numpy Array where each product index stores its rating.
    
    Params: {}
    Returns: Numpy Array
    """
    ratings = np.zeros(num_products)

    for prod in reviews_lst:
        ratings[products_to_indices[prod['product']]] = prod['rate']

    return ratings


product_types = create_product_types_dict()
prices = create_prices()
ratings = create_ratings()

# Add to db
if Config.LOAD_DB:
    for name, d in data.items():
        i = products_to_indices[name]
        types = [k for k, v in product_types.items() if v[i]]
        info = Product(name=name, link=d["link"], brand=d["brand"],
                       claims=d["claims"], num_faves=d["num faves"],
                       ingredients=d["ingredients"], price=d["price"],
                       types=types)
        db.session.merge(info)

    db.session.commit()
    #
    # p = Product.query.with_entities(Product.brand, Product.name).filter_by(brand="La Prairie").all()
    # print(p)


# del data
