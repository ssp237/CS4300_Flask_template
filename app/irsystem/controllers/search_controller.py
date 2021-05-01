from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

project_name = "Pocket Esthetician"
net_id = "Em Gregoire: erg92 \nKriti Sinha: ks867 \nRaheel Yanful: ray37 \nShan Parikh: ssp237"

def adjust_sensitivity(ranking, sensitive):
    """Returns the ranking after adjusting scores based on skin sensiivity.
    
    Params: {ranking: Numpy Array,
             sensitive: Boolean}
    Returns: Numpy Array 
    """
    if sensitive:
        for prod in categories['abrasive/scrub']['products']:
            ranking[products_to_indices[prod]] *= 0.5
        for prod in categories['perfuming']['products']:
            ranking[products_to_indices[prod]] *= 0.5
            
        for prod in categories['soothing']['products']:
            ranking[products_to_indices[prod]] *= 1.5
    return ranking


def adjust_skin_type(ranking, s_type):
    """Returns the ranking after adjusting scores based on skin type.
    
    Params: {ranking: Numpy Array,
             s_type: String}
    Returns: Numpy Array 
    """
    if s_type == 'oily':
        ranking[product_types['face_oil_products']] *= 0.5
            
        for prod in categories['absorbent/mattifier']['products']:
            ranking[products_to_indices[prod]] *= 1.5
        ranking[product_types['bha_products']] *= 1.5
        ranking[product_types['oil_absorbing_products']] *= 1.5
    
    elif s_type == 'dry':
        for prod in categories['absorbent/mattifier']['products']:
            ranking[products_to_indices[prod]] *= 0.5
        ranking[product_types['oil_absorbing_products']] *= 0.5
            
        for prod in categories['soothing']['products']:
            ranking[products_to_indices[prod]] *= 1.5
    
    elif s_type == 'combo':
        pass
    
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


def concern_similarity(query, category_info, prod_to_idx, category_to_idx):
    """ Finds cosine similarity between input query (concerns) and each product category's concern list. 
        Returns a numpy array with each product's score, based on the categories they are in.
        
        Params: {query: (user input) String,
                 category_info: (category -> Dict) Dict,
                 prod_to_idx: (product -> index) Dict, 
                 category_to_idx: (category -> index) Dict}
        Returns: Numpy Array
    """
    result = np.zeros(len(prod_to_idx))
                      
    tfidf_vec = TfidfVectorizer(stop_words = 'english')
    lst = [category_info[k]['concerns'] for k in categories.keys()]
    lst.append(query)
    tfidf_mat = tfidf_vec.fit_transform(lst).toarray()
    
    for k,v in category_info.items():
        sim = cos_sim(k, tfidf_mat, category_to_idx)
        for p in v['products']:
            result[prod_to_idx[p]] += sim
            
        # added adjustments
        for category in relevant_product_types[k]['relevant']:
            result[product_types[category]] *= 1.5
        for category in relevant_product_types[k]['irrelevant']:
            result[product_types[category]] *= 0.1
        
    return result


def rank_products(query, category_info, prod_to_idx, idx_to_prod, product_info, category_to_idx,
                 product_types, price_ranges, product_type=None, skin_type=None, budget=None, sensitivity=None):
    """ Returns a ranked list of products, with the most relevant at index 0.
        
        Params: {query: (user input) String,
                 category_info: (category -> Dict) Dict,
                 prod_to_idx: (product -> index) Dict,
                 idx_to_prod: (index -> product) Dict
                 product_info: (product -> Dict) Dict
        Returns: List
    """
    scores = concern_similarity(query, category_info, prod_to_idx, category_to_idx)
    scores += 2 * claims_similarity(query, product_info, prod_to_idx)
    if sum(scores) == 0: return 'invalid query'
    
    # ranking adjustments
    if skin_type != None:
        scores = adjust_skin_type(scores, skin_type)
    if sensitivity != None:
        scores = adjust_sensitivity(scores, sensitivity)
    
    # strict filters
    if budget != None:
        scores[np.invert(price_ranges[budget])] = 0     
    if product_type != None:
        scores[np.invert(product_types[product_type])] = 0
    
    scores_idx = [(val,prod) for prod, val in enumerate(scores)]
    rank_idx = sorted(scores_idx, key = lambda x: (x[0], product_info[idx_to_prod[x[1]]]["num faves"], 
                                            product_info[idx_to_prod[x[1]]]["price"]), reverse = True)
    
    ranking = list(map(lambda x: (idx_to_prod[x[1]], 
                        product_info[idx_to_prod[x[1]]]["brand"], 
                        product_info[idx_to_prod[x[1]]]["price"]), rank_idx))
    return ranking


@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    
    product = request.args.get('product-type')
    if product == 'all': product = None
    skin = request.args.get('skin-type')
    if skin == 'all': skin = None
    budget_in = request.args.get('budget')
    if budget_in == 'all': budget_in = None
    sensitive = request.args.get('sensitivity')
    if sensitive == 'high': sensitive = True
    else: sensitive = None
    
    if not query:
        search_data = []
        output_message = ''
    else:
        output_message = "Here are the products we found for: " + query
        search_data = rank_products(query, categories, products_to_indices, indices_to_products, 
                                    data, category_to_index, product_types, price_ranges,
                                    product_type=product, skin_type=skin, budget=budget_in, sensitivity=sensitive)
        if search_data == 'invalid query':
            search_data = []
            output_message = 'Sorry, that query is invalid.'

    return render_template('search.html', name=project_name, netid=net_id,
                           output_message=output_message, data=search_data[:10], 
                           query=query, product_types=product_types, product_type=product, skin_type=skin,
                           budget=budget_in, sensitivity=sensitive)

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
