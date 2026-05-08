"""Functions for an indexer."""
import string
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

# move these to main.py (run once)


def retrieve_tokens(text):
    """Retrieve significant words from provided text."""
    # Lowercase + removes/replaces apostrophes, double quotes, and hyphens
    text = text.lower()
    replace = str.maketrans({"'": "", '"': " ", "”": " ", "“": " ", "-": " "})
    text = text.translate(replace)

    # Tokenizes the text
    tokens = word_tokenize(text, 'english')

    # Removes stopwords and single punctuation marks
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and token not in string.punctuation]
    
    # Performs stemming
    stemmer = SnowballStemmer('english')
    stems = []
    [stems.append(stemmer.stem(token)) for token in tokens]
    
    # Creates dictionary of stems and their positions (list) in the document
    stem_dict = dict()
    for i, token in enumerate(stems):
        if token in stem_dict: stem_dict[token].append(i)
        else: stem_dict[token] = [i]

    return stem_dict


def index(html, page_number, inverted_index):
    """Indexes the html page onto the inverted index."""
    soup = BeautifulSoup(html, 'html.parser')
    # Ignores footer content
    for footer in soup.find_all("footer"):
        footer.decompose()

    tokens = retrieve_tokens(soup.get_text())
    
    for token in tokens:
        if token in inverted_index:
            inverted_index[token][page_number] = tokens[token]
        else: inverted_index[token] = {page_number: tokens[token]}

    return len(tokens)
