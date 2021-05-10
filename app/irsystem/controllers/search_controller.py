import numpy as np

from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import random
from sqlalchemy import and_


project_name = ["Pocket", "Esthetician"]
net_id = "Em (erg92), Kriti(ks867), Raheel (ray37), Shan (ssp237)"
tip = ''
query = {}
changed_mat = False

def adjust_sensitivity(ranking, sensitive, products_to_indices):
    """Returns the ranking after adjusting scores based on skin sensiivity.
    
    Params: {ranking: Numpy Array,
             sensitive: Boolean}
    Returns: Numpy Array 
    """
    products = set(products_to_indices.keys())
    if sensitive:
        scrubs = products.intersection(set(categories['abrasive/scrub']['products']))
        perfuming = products.intersection(set(categories['perfuming']['products']))
        for prod in scrubs:
            ranking[products_to_indices[prod]] *= 0.25
        for prod in perfuming:
            ranking[products_to_indices[prod]] *= 0.25
        
        soothing = products.intersection(set(categories['soothing']['products']))
        for prod in soothing:
            ranking[products_to_indices[prod]] *= 1.75
    return ranking


def adjust_skin_type(ranking, s_type, product_types, products_to_indices, categories):
    """Returns the ranking after adjusting scores based on skin type.
    
    Params: {ranking: Numpy Array,
             s_type: String}
    Returns: Numpy Array 
    """
    products = set(products_to_indices.keys())
    if s_type == 'oily':
        
        ranking[product_types['Face Oils']] *= 0.1
        
        absorbent = products.intersection(set(categories['absorbent/mattifier']['products']))
        for prod in absorbent:
            ranking[products_to_indices[prod]] *= 1.5
        ranking[product_types['BHA Products']] *= 1.5
        ranking[product_types['Oil Absorbing Products']] *= 1.75
    
    elif s_type == 'dry':
        absorbent = products.intersection(set(categories['absorbent/mattifier']['products']))
        for prod in absorbent:
            ranking[products_to_indices[prod]] *= 0.1
        ranking[product_types['Oil Absorbing Products']] *= 0.1
        
        soothing = products.intersection(set(categories['soothing']['products']))
        for prod in soothing:
            ranking[products_to_indices[prod]] *= 1.5
    
    elif s_type == 'combo':
        pass
    
    return ranking


def adjust_rating(ranking, ratings):
    """Returns the ranking after adjusting scores based on product ratings.
    
    Params: {ranking: Numpy Array,
             ratings: Numpy Array}
    Returns: Numpy Array 
    """
    r1 = ratings == 1
    ranking[r1] *= 0.5
    
    r2 = ratings == 2
    ranking[r2] *= 0.75
    
#     r3 = ratings == 3
#     ranking[r3] *= 1
    
    r4 = ratings == 4
    ranking[r4] *= 1.25
    
    r5 = ratings == 5
    ranking[r5] *= 1.5
    
    return ranking


def cos_sim(c, tfidf_mat, category_to_idx):
    """Returns the cosine similarity of the query and a concern list.
    
    Params: {c: String,
             tfidf_mat: np.ndarray,
             category_to_idx: Dict}
    Returns: Float 
    """
    # query is last row
    v1 = tfidf_mat[len(tfidf_mat)-1]
    v2 = tfidf_mat[category_to_idx[c]]
    num = np.dot(v1, v2)
    
    denom = max((np.linalg.norm(v1)*np.linalg.norm(v2)), 1e-7)
    return num/denom


def claims_similarity(query, product_info, prod_to_idx):
    """ Finds cosine similarity between input query (concerns) and each product's claims. 
        Returns a numpy array with each product's score.
        
        Params: {query: (user input) String,
                 product_info: (product -> Dict) Dict,
                 prod_to_idx: (product -> index) Dict}
        Returns: Numpy Array
    """
    result = np.zeros(len(prod_to_idx))
                      
    tfidf_vec = TfidfVectorizer(stop_words = 'english')
    lst = [product_info[k]['claims'] for k in product_info.keys()]
    lst.append(query)
    tfidf_mat = tfidf_vec.fit_transform(lst).toarray()
    
    for k,v in product_info.items():
        sim = cos_sim(k, tfidf_mat, prod_to_idx)
        result[prod_to_idx[k]] += sim
        
    return result


def cos_sim_row(query, mat, term_ind):
    """
    Compute cosine similarity between query and mat
    :param query: indices of terms in the query
    :param mat: tip - term count matrix
    :param term_ind: Index of tip to find similarity of
    :return: cosine similarity of query and term
    """
    n1 = np.sqrt(len(query))
    v2 = mat[term_ind, :][query]
    if np.linalg.norm(v2) == 0:
        return 0
    return np.sum(v2) / (n1 * np.linalg.norm(v2))


def getTip(query_string, mat, tip_ind, key_ind):
    """
    Return a random tip within the 5 most similar to the given query
    :param query_string: Text of query
    :param mat: tip-term frequency matrix
    :param tip_ind: tip to index dict
    :param key_ind: keyword to index dict
    :return: tip to display
    """
    count_vec = CountVectorizer(stop_words='english')
    query_list = count_vec.fit_transform([query_string]).toarray()
    query = [key_ind[w]
             for w in list(count_vec.vocabulary_.keys())
             if w in key_ind]
    tip_ranking = [(k, cos_sim_row(query, mat, i)) for (k, i) in tip_ind.items()]
    tip_sorted = sorted(tip_ranking, key=lambda x: x[1], reverse=True)
    return tip_sorted[random.randint(0, min(len(tip_sorted), 5))][0]


def updateTip(query_string, mat, tip_ind, key_to_ind, inc):
    """
    Update the count of each term in query in mat
    :param query_string: text of query
    :param mat: tip-term frequency mat
    :param tip_ind: index of tip
    :param key_to_ind: keyword to index dictionary
    :param inc: If true, increase count. If false, decrease
    :return: Modified array
    """
    count_vec = CountVectorizer(stop_words='english')
    query_list = count_vec.fit_transform([query_string]).toarray()
    n_terms = len(key_to_ind)
    diff = 1.0 if inc else -0.5
    for q in list(count_vec.vocabulary_.keys()):
        if q in key_to_ind:
            mat[tip_ind, key_to_ind[q]] = max(mat[tip_ind, key_to_ind[q]] + diff, 0)
        else:
            key_to_ind[q] = n_terms
            col = np.zeros((mat.shape[0], 1))
            col[tip_ind] = max(diff, 0)
            mat = np.append(mat, col, axis=1)

    return mat


def concern_similarity(query, category_info, prod_to_idx, category_to_idx, product_types):
    """ Finds cosine similarity between input query (concerns) and each product category's concern list. 
        Returns a numpy array with each product's score, based on the categories they are in.
        
        Params: {query: (user input) String,
                 category_info: (category -> Dict) Dict,
                 prod_to_idx: (product -> index) Dict, 
                 category_to_idx: (category -> index) Dict}
        Returns: Numpy Array
    """
    result = np.zeros(len(prod_to_idx))

    lst = [category_info[k]['concerns'] for k in categories.keys()]
    lst.append(query)
    tfidf_vec = TfidfVectorizer(stop_words='english')
    tfidf_mat = tfidf_vec.fit_transform(lst).toarray()
    
    for k,v in category_info.items():
        sim = cos_sim(k, tfidf_mat, category_to_idx)
        for p in v['products']:
            if p in prod_to_idx:
                result[prod_to_idx[p]] += sim

            
        # added adjustments
        for category in relevant_product_types[k]['relevant']:
            result[product_types[product_file_to_type[category]]] *= 1.5
        for category in relevant_product_types[k]['irrelevant']:
            result[product_types[product_file_to_type[category]]] *= 0.1
    return result


# def rank_products(query, category_info, prod_to_idx, idx_to_prod, product_info, category_to_idx,
#                  product_types, ratings, product_type=None, skin_type=None, price_min=None, price_max=None,
#                   sensitivity=None):
def rank_products(query, category_info, prod_to_idx, idx_to_prod, product_info, category_to_idx, product_types, 
                  ratings, product_type=None, skin_type=None, sensitivity=None):
    """ Returns a ranked list of products, with the most relevant at index 0.
        
        Params: {query: (user input) String,
                 category_info: (category -> Dict) Dict,
                 prod_to_idx: (product -> index) Dict,
                 idx_to_prod: (index -> product) Dict,
                 product_info: (product -> Dict) Dict
                 product_types: (product type -> Numpy Array) Dict,
                 ratings: Numpy Array,
                 skin_type: String,
                 sensitivity: Boolean,
        Returns: List
    """
    scores = 2 * claims_similarity(query, product_info, prod_to_idx)
    scores += concern_similarity(query, category_info, prod_to_idx, category_to_idx, product_types)
    if sum(scores) == 0: return 'invalid query'
    
    # ranking adjustments
    scores = adjust_rating(scores, ratings)
    if skin_type is not None:
        scores = adjust_skin_type(scores, skin_type, product_types, prod_to_idx, category_info)
    if sensitivity is not None:
        scores = adjust_sensitivity(scores, sensitivity, prod_to_idx)
    
    # strict filters
#     if price_min is not None:
#         m1 = prices < price_min
#         scores[m1] = 0
#     if price_max is not None:
#         m2 = prices > price_max
#         scores[m2] = 0
    if product_type is not None:
        scores[np.invert(product_types[product_type])] = 0
    
    len_rank = np.count_nonzero(scores)
    scores_idx = [(val,prod) for prod, val in enumerate(scores)]
    rank_idx = sorted(scores_idx, key = lambda x: (x[0], ratings[x[1]], product_info[idx_to_prod[x[1]]]["num faves"]),
                      reverse = True)
    
    ranking = list(map(lambda x: (idx_to_prod[x[1]], product_info[idx_to_prod[x[1]]], 
    int(ratings[x[1]]), imagelinks[idx_to_prod[x[1]]]["image link"]), rank_idx))[:len_rank]
    return ranking


def get_data(product_type=None, budget=(0, 1000)):
    """
    Get data dictionary and product-index dictionary for products
    matching given parameters
    :param product_type: Type of product (string)
    :param budget: Budget to stay within (tuple of numbers)
    :return: Tuple of dictionary of data, product index dictionary,
            index product dictionary, ranking info, and new product types dict.
    """
    data = {}
    i = 0
    p_to_ind, ind_to_p = {}, {}
    filters = and_(Product.price >= budget[0], Product.price <= budget[1])
    if product_type:
        filters = and_(filters, Product.ptype.any(product_type))
    query_data = Product.query.with_entities(
        Product.name, Product.num_faves,
        Product.claims, Product.ingredients, Product.ptype).filter(filters).all()
    num_products = len(query_data)
    ptypes = {}
    
    for k,v in product_file_to_type.items():
        ptypes[v] = np.full(num_products, False)
        
    for prod in query_data:
        data[prod.name] = {
            "num faves": prod.num_faves,
            "claims": prod.claims,
            # "ingredients": prod.ingredients
        }
        for t in prod.ptype:
#             if t in ptypes:
            ptypes[t][i] = True
#             else:
#                 ptypes[t] = np.full(num_products, False)
#                 ptypes[t][i] = True
        p_to_ind[prod.name] = i
        ind_to_p[i] = prod.name
        i += 1

    ratings = np.zeros(len(data))
    for prod in reviews_lst:
        if prod["product"] in data:
            ratings[p_to_ind[prod["product"]]] = prod['rate']
    return data, p_to_ind, ind_to_p, ratings, ptypes


def get_price_and_link(name):
    """
    Get the price and link of a product given a name
    """
    prod = Product.query.with_entities(Product.price, Product.link, Product.brand).filter_by(name=name).first()
    return prod.price, prod.link, prod.brand


@irsystem.route('/increase')
def inc_query():
    """
    Increase the weight of the current query in the last returned tip
    """
    global changed_mat, tips_arr
    if not query or changed_mat:
        return "data"
    tips_arr = updateTip(query, tips_arr, tips_to_ind[tip], terms_to_ind, True)
    numpyToDic(tips_arr, tips_to_ind, terms_to_ind, tips)
    with open(tip_file, "w") as file:
        json.dump(tips, file, indent=7)
    changed_mat = True
    return "data"


@irsystem.route('/decrease')
def dec_query():
    """
    Decrease the weight of the current query in the last returned tip
    """
    global changed_mat, tips_arr
    if not query or changed_mat:
        return "nothing"
    tips_arr = updateTip(query, tips_arr, tips_to_ind[tip], terms_to_ind, False)
    numpyToDic(tips_arr, tips_to_ind, terms_to_ind, tips)
    with open(tip_file, "w") as file:
        json.dump(tips, file, indent=7)
    changed_mat = True
    return "nothing"


@irsystem.route('/', methods=['GET'])
def search():
    global tip, query, changed_mat
    query = request.args.get('search')

    changed_mat = False

    #Get Filter Values from frontend
    product = request.args.get('product-type')
    if product == 'all': product = None
    skin = request.args.get('skin-type')
    if skin == 'all': skin = None
    price_min = parse_for_int(request.args.get('price-min'), 0)
    price_min = 0 if price_min < 0 else price_min
    price_max = parse_for_int(request.args.get('price-max'), 1000)
    price_max = 1000 if price_max > 1000 else price_max  


    sensitive = request.args.get('sensitivity')
    if sensitive == 'high': sensitive = True
    elif sensitive == 'low': sensitive = False
    else: sensitive = None

    if not query:
        search_data = []
        output_message = ''
        tip = ''
        tip_data = {}
    else:
        tip = getTip(query, tips_arr, tips_to_ind, terms_to_ind)
        tip_data = tips[tip]
        new_data, p_to_ind, ind_to_p, new_rates, new_p_types = \
            get_data(product_type=product, budget=(price_min, price_max))
        search_data = rank_products(query, categories, p_to_ind, ind_to_p,
                                    new_data, category_to_index, new_p_types, new_rates,
                                    product_type=None, skin_type=skin,
                                    sensitivity=sensitive)
        output_message = "Top " + str(min(len(search_data), 10)) + " products for: " + query
        
        # invalid concerns query
        if search_data == 'invalid query':
            search_data = []
            output_message = 'Sorry, that query is invalid. Please check spelling or try different keywords! \n For example: "acne"'
        
        # no results (due to advanced search filtering)
        elif len(search_data) == 0:
            output_message = 'Sorry, there are no results matching your preferences.'

        else:
            search_data = search_data[:min(10, len(search_data))]
            for tup in search_data:
                dat = get_price_and_link(tup[0])
                tup[1]["price"] = dat[0]
                tup[1]["link"] = dat[1]
                tup[1]["brand"] = dat[2]

    return render_template('search.html', name=project_name, netid=net_id,
                           output_message=output_message, data=search_data,
                           tip=tip, tip_data=tip_data, 
                           query=query, product_types=product_types, product_type=product, 
                           price_min=price_min, price_max=price_max,
                           skin_type=skin, sensitive=sensitive)


def parse_for_int(request, value_if_none):
  return int(request if request else value_if_none)

# @irsystem.route('/filter', methods=['POST'])
# def filter():
#     product_type = str(request.form.get('product-type'))
#     skin_type = str(request.form.get('skin-type'))
#     query = str(request.args.get('search'))
    
#     search_data = rank_products(query, categories, products_to_indices,
#                               indices_to_products, data, category_to_index,
#                               product_types, price_ranges, 
#                               product_type=product_type, skin_type=skin_type)
#     output_message = "We found " + str(len(search_data)) + " products for: " + query
    
#     return render_template('search.html', name=project_name, netid=net_id,
#                            output_message=output_message, data=search_data[:10], query=query)