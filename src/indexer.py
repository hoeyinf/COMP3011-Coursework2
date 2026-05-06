"""Functions for an indexer."""
import string
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

# move these to main.py (run once)
nltk.download('punkt_tab')
nltk.download('stopwords')

def retrieve_tokens(text):
    """Retrieve significant words from provided text."""
    
    # Removes apostrophes: e.g. can't -> cant
    text = text.replace("'", "")
    # Replaces hyphens with spaces: e.g. hand-drawn -> hand drawn
    text = text.replace("-", " ")

    # Tokenizes the text
    tokens = word_tokenize(text, 'english')

    # Removes stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Performs stemming
    stemmer = SnowballStemmer('english')
    stems = set()
    [stems.add(stemmer.stem(token)) for token in tokens]
    
    # Removes single punctuation marks
    [stems.discard(punc) for punc in string.punctuation]

    return stems


def index(html, page_number, inverted_index):
    """Indexes the html page onto the inverted index."""
    soup = BeautifulSoup(html, 'html.parser')
    tokens = retrieve_tokens(soup.text)
    
    for token in tokens:
        if token in inverted_index:
            inverted_index[token].add(page_number)
        else:
            inverted_index[token] = {page_number}

    return inverted_index
