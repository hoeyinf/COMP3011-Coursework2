"""Functions for a token indexer."""

import string
import unicodedata
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


def retrieve_tokens(text: str) -> dict:
    """Retrieve significant words from provided text.

    Args:
        text(str): the (HTML) text to be parsed.

    Returns:
        stem_dict (dict): dictionary of tokens, which documents they appear in
        and their positions in each document.
    """
    # Normalizes unicode, folds diacritics, and lowercases
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c)).casefold()
    # Removes/replaces apostrophes, double quotes, and hyphens
    replace = str.maketrans({"'": "", '"': " ", "”": " ", "“": " ", "-": " "})
    text = text.translate(replace)

    # Tokenizes the text
    tokens = word_tokenize(text, 'english')

    # Removes stopwords and single punctuation marks
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens
              if token not in stop_words and token not in string.punctuation]

    # Performs stemming
    stemmer = SnowballStemmer('english')
    stems = [stemmer.stem(token) for token in tokens]

    # Creates dictionary of stems and their positions (list) in the document
    stem_dict = dict()
    for i, token in enumerate(stems):
        if token in stem_dict:
            stem_dict[token].append(i)
        else:
            stem_dict[token] = [i]

    return stem_dict


def index(html: str, page_number: int, inverted_index: dict) -> int:
    """Indexes the html page onto the inverted index.

    Args:
        html (str): the HTML page to index.
        page_number (int): the document number associated with the page.
        inverted_index (dict): index to store tokens and their locations.

    Returns:
        token_n (int): the number of tokens found in the HTML page.
    """
    soup = BeautifulSoup(html, 'html.parser')
    # Ignores footer content
    for footer in soup.find_all("footer"):
        footer.decompose()

    tokens = retrieve_tokens(soup.get_text())

    for token in tokens:
        if token in inverted_index:
            inverted_index[token][page_number] = tokens[token]
        else:
            inverted_index[token] = {page_number: tokens[token]}

    return len(tokens)
