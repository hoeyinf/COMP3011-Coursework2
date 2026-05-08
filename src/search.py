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


def relevant_documents(tokens, inverted_index):
    """Find documents that only contain all the tokens."""
    
    # Finds token in the least documents
    min_n = len(inverted_index[tokens[0]])
    min_token = tokens[0]
    sets = []
    for token in tokens[1:]:
        if min_n > len(inverted_index[token]):
            min_n = len(inverted_index[token])
            min_token = token
        
        # Builds list of documents
        sets.append(inverted_index[token].values())
    
    # Finds matching documents
    documents = set(sets[min_n])
    for i in range(len(tokens)):
        if i == min_n: continue
        documents = documents.intersection(sets[i])
    
    return documents


def tfidf(term, document, document_index):
    """Calculate the TF-IDF score for a term in a document"""
    tf = len(term[document]) / document_index[document][1]
    idf = math.log(len(document_index)/len(term))
    
    return tf * idf


def rank_documents(query, inverted_index, document_index):
    """Rank document relevance for a given query."""
    
    tokens = query_tokens(query)
    documents = relevant_documents(tokens, inverted_index)
    
    # Calculates the tfidf for each document for each term
    scores = []
    for i, document in enumerate(documents):
        scores.append([])
        for token in tokens:
            scores[i].append(tfidf(token, document, document_index))
    
    # Sorts by score
    ranks = [score for _, score in sorted(zip(scores, documents))]
    ranks = ranks.reverse()
    
    results = []
    [results.append(document_index[document][0]) for document in ranks]
    
    return results
    
    