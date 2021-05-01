import numpy as np

from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import random


project_name = "Pocket Esthetician"
net_id = "Em Gregoire: erg92 \nKriti Sinha: ks867 \nRaheel Yanful: ray37 \nShan Parikh: ssp237"


def cos_sim(c, tfidf_mat, category_to_idx):
    """Returns the cosine similarity of the query and a concern list.

    Params: {c: String,
             tfidf_mat: np.ndarray,
             concern_to_index: Dict}
    Returns: Float
    """
    # query is last row
    v1 = tfidf_mat[-1]
    v2 = tfidf_mat[category_to_idx[c]]
    if np.linalg.norm(v2) == 0:
        return 0
    num = np.dot(v1, v2)
    return num / (np.linalg.norm(v1) * np.linalg.norm(v2))


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

    lst = [category_info[k]['concerns'] for k in categories.keys()]
    lst.append(query)
    tfidf_vec = TfidfVectorizer(stop_words='english')
    tfidf_mat = tfidf_vec.fit_transform(lst).toarray()

    for k, v in category_info.items():
        sim = cos_sim(k, tfidf_mat, category_to_idx)
        for p in v['products']:
            result[prod_to_idx[p]] += sim

    # for invalid query
    if sum(result) == 0:
        return 'invalid query'
    return result


def rank_products(query, category_info, prod_to_idx, idx_to_prod, product_info, category_to_idx):
    """ Returns a ranked list of products, with the most relevant at index 0.

        Params: {query: (user input) String,
                 category_info: (category -> Dict) Dict,
                 prod_to_idx: (product -> index) Dict,
                 idx_to_prod: (index -> product) Dict
                 product_info: (product -> Dict) Dict
        Returns: List
    """
    scores = concern_similarity(query, category_info, prod_to_idx, category_to_idx)

    scores_idx = [(val, prod) for prod, val in enumerate(scores)]
    rank_idx = sorted(scores_idx, key=lambda x: (x[0], product_info[idx_to_prod[x[1]]]["num faves"],
                                                 product_info[idx_to_prod[x[1]]]["price"]), reverse=True)
    ranking = list(map(lambda x: (idx_to_prod[x[1]], product_info[idx_to_prod[x[1]]]["brand"], product_info[idx_to_prod[x[1]]]["price"]), rank_idx))
    return ranking


@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        search_data = []
        output_message = ''
        tip = ''
        tip_data = {}
    else:
        output_message = "Here are the products we found for: " + query
        search_data = rank_products(query, categories, products_to_indices,
                                    indices_to_products, data, category_to_index)
        tip = getTip(query, tips_arr, tips_to_ind, terms_to_ind)
        tip_data = tips[tip]
        print(tip)

    return render_template('search.html', name=project_name, netid=net_id,
                           output_message=output_message, data=search_data[:10],
                           tip=tip, tip_data=tip_data)
