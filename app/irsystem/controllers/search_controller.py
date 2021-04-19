from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

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

    tfidf_vec = TfidfVectorizer(stop_words='english')
    lst = [category_info[k]['concerns'] for k in categories.keys()]
    lst.append(query)
    tfidf_mat = tfidf_vec.fit_transform(lst).toarray()

    for k, v in category_info.items():
        sim = cos_sim(k, tfidf_mat, category_to_idx)
        for p in v['products']:
            result[prod_to_idx[p]] += sim

    # for invalid query
    if sum(result) == 0: return 'invalid query'
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
    ranking = list(map(lambda x: idx_to_prod[x[1]], rank_idx))
    return ranking


@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        search_data = []
        output_message = ''
    else:
        output_message = "Your search: " + query
        search_data = rank_products(query, categories, products_to_indices,
                                    indices_to_products, data, category_to_index)

    return render_template('search.html', name=project_name, netid=net_id,
                           output_message=output_message, data=search_data[:10])
