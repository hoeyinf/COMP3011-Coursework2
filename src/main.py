import json
import nltk

import os.path
from crawler import crawl

if __name__=="__main__":
    
    nltk.download('punkt_tab')
    nltk.download('stopwords')

    visited, inverted_index = crawl("https://quotes.toscrape.com")
    
    # Remember to implement file handling errors later
    with open(os.path.dirname(__file__) + '/../data/inverted_index.json', "w") as f:
        json.dump(visited, f)
        json.dump(inverted_index, f)
        
