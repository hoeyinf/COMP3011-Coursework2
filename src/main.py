import pickle
import nltk
from itertools import islice

import os.path
from crawler import crawl

if __name__=="__main__":
    
    nltk.download('punkt_tab')
    nltk.download('stopwords')

    visited, inverted_index = crawl("https://quotes.toscrape.com")

    # Remember to implement file handling errors later
    with open(os.path.dirname(__file__) +
              '/../data/inverted_index.p', "wb") as f:
        pickle.dump(visited, f)
        pickle.dump(inverted_index, f)
        
    dicts = []
    with open(os.path.dirname(__file__) +
              '/../data/inverted_index.p', "rb") as f:
        while True:
            try:
                dicts.append(pickle.load(f))
            except EOFError:
                break
    dicts[1].keys
    print(dict(islice(dicts[1].items(), 10)))
