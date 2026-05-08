"""Functions for query processing."""
import string
import unicodedata
import math
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


def query_tokens(query):
    """Reduce query into tokens."""
    # Uses the same process as retrieve_tokens() in indexer.py
    text = unicodedata.normalize("NFKD", query)
    text = "".join(c for c in text if not unicodedata.combining(c)).casefold()
    replace = str.maketrans({"'": "", '"': " ", "”": " ", "“": " ", "-": " "})
    text = text.translate(replace)
    tokens = word_tokenize(text, 'english')
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and token not in string.punctuation]
    stemmer = SnowballStemmer('english')
    stems = []
    [stems.append(stemmer.stem(token)) for token in tokens]
    
    return stems


def tfidf(term, document, document_index):
    """Calculate the TF-IDF score for a term in a document"""
    tf = len(term[document]) / document_index[document][1]
    
    idf = math.log(len(document_index)/len(term))
    return tf * idf

