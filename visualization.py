import json
import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from collections import Counter


def read_data(infile):
    """
    Parse infile and return a json representation
    :param infile: File to parse
    :return: JSON representation of infile
    """
    with open(infile) as f:
        data = json.loads("\n".join(f.readlines()))

    # Separate list of ingredients
    for _, v in data.items():
        v['ingredients'] = v['ingredients'].split(",")
    return data


def run():
    """ Print out some form of data visualization
    """
    data = read_data("data.txt")

    print(f"There are {len(data.items())} different products")

    # print(data)
    ingredient_cts = np.array([len(v['ingredients']) for _, v in data.items()])
    plt.hist(ingredient_cts)
    plt.title("Ingredients per product")
    plt.xlabel("Number of products")
    plt.ylabel("Number of ingredients")
    plt.show()

    prices = np.array([v['price'] for _, v in data.items()])
    plt.hist(prices)
    plt.title("Prices per product")
    plt.xlabel("Number of products")
    plt.ylabel("Price")
    plt.show()

    plt.plot(ingredient_cts, prices, '.')
    plt.title("Price by number of ingredients")
    plt.xlabel("Number of ingredients")
    plt.ylabel("Price")
    plt.show()

    all_ingredients = reduce(lambda s, x: s | set(x[1]['ingredients']),
                             data.items(), set())
    print(f"There are {len(all_ingredients)} unique ingredients in these products")

    common_ingredients = reduce(lambda s, x: s & set(x[1]['ingredients']),
                                data.items(), set(list(data.items())[0][1]['ingredients']))
    print(f"There are {len(common_ingredients)} ingredients that are in every product")

    ingredient_count = Counter()
    for _, v in data.items():
        ingredient_count.update(v['ingredients'])
    counts = np.array(list(ingredient_count.values()))
    plt.hist(counts)
    plt.title("No. of products to use each ingredient")
    plt.ylabel("No ingredients")
    plt.xlabel("No. Products")
    plt.show()
    print(f"The most common ingredients are {ingredient_count.most_common(10)}")


if __name__ == "__main__":
    run()
