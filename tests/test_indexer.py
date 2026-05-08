"""Tests for src/indexer.py"""

import pytest
from indexer import *


@pytest.fixture(scope='function')
def html_page():
    """Fixture for an HTML page."""
    page = """<!doctype html><html lang="en">
              <head><meta charset="UTF-8"><title>Mock HTML Page</title>
              <link rel="stylesheet" href="/static/bootstrap.min.css"></head>
              
              <body><h1>This is an HTML Page for testing</h1>
              <div class="container">
              <h2>I am a subheading</h2>
              <p>This is example text for a sentence on an HTML page. Multiple
              sentences will create a paragraph. This should be enough.</p>
              
              <h2>Google Links Example</h2>
              <p>The indexer should also be able to identify words inside a
              link. Click <a href="https://www.google.com">Google</a>.
              Google is a search engine for the internet.</p>
              </div></body></html>"""
    return page


class TestRetrieveTokens:
    """"Tests for retrieve_tokens()"""

    @pytest.mark.parametrize("string,expected",
                             [("", 0),
                              ("single", 1),
                              ("multiple types   whitespace\tused  example", 5),
                              ("paragraphs\n\nnecessarily\nwork properly", 4),
                              ("however, punctuation exists everywhere!", 4),
                              ("Ms. Tan www.google.com p.m e.g.", 5),
                              ('"sentence double quotation marks"', 4)])
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_token_count(self, benchmark, string, expected):
        """Identify the correct number of tokens in a variety of strings,
        including varying punctuation and whitespace.
        """
        tokens = benchmark(retrieve_tokens, string)

        assert len(tokens) == expected, tokens
    
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_capitals(self, benchmark):
        """Identify correct tokens from a sentence with capital letters."""
        words = ["John", "Doe", "London", "England", "UK", "RSVP"]
        tokens = benchmark(retrieve_tokens, " ".join(words))
        
        assert list(tokens.keys()) == [word.casefold() for word in words]
        
        
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_unicode(self, benchmark):
        """Normalizes different unicode correctly."""
        words = ['"áéíóú"', '“a\u0301e\u0301i\u0301o\u0301u\u0301”']
        tokens = benchmark(retrieve_tokens, " ".join(words))
        
        assert list(tokens.keys()) == ["aeiou"], tokens

    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_diacritics_and_symbols(self, benchmark):
        """Folds diacritics and symbols correctly."""
        words = ["áéíóúçñ²³", "äeiöücn23", "åeioucn23", "aeioucn23"]
        tokens = benchmark(retrieve_tokens, " ".join(words))
        
        assert list(tokens.keys()) == ["aeioucn23"], tokens
        
    @pytest.mark.parametrize("string,expected",
                             [("t-shirt", 1),
                              ("hand-drawn", 2),
                              ("em-dash", 2)])
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_hyphens(self, benchmark, string, expected):
        """Identify the correct number of tokens in words with hyphens."""
        tokens = benchmark(retrieve_tokens, string)

        assert len(tokens) == expected, tokens
    
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_apostrophes(self, benchmark):
        """Identify the correct tokens in a string with apostrophes."""
        tokens = benchmark(retrieve_tokens,"don't can't Michael's people's "
                                          "2000's womens' o'donnell")
        assert len(tokens) == 7, tokens
        
    @pytest.mark.parametrize("string,expected",
                             [("1 256 987654", 3),
                              ("3.1415", 1),
                              ("3.000 12,345  1,024.20480 678.901,24", 4)])
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_numbers(self, benchmark, string, expected):
        """Identify numbers correctly."""
        # Build the correct dictionary
        num_list = string.split()
        num_dict = dict()
        for i, num in enumerate(num_list): num_dict[num] = [i]
        
        tokens = benchmark(retrieve_tokens, string)
        
        assert len(tokens) == expected, tokens
        assert tokens == num_dict
    
    @pytest.mark.benchmark(group="retrieve_tokens()")
    @pytest.mark.parametrize("string,expected",
                             [("this is a sentence", 1),
                              ("this string contains a few stopwords", 3),
                              ("to be or not to be", 0)])
    def test_stopwords(self, benchmark, string, expected):
        """Perform correct stopword removal."""
        stopwords = ["this", "is", "a", "few", "to", "be", "or", "not"]

        tokens = benchmark(retrieve_tokens, string)

        assert [word not in tokens for word in stopwords]
        assert len(tokens) == expected, tokens

    @pytest.mark.benchmark(group="retrieve_tokens()")
    @pytest.mark.parametrize("string,count",
                             [("write wrote written writes", 4),
                              ("book books", 2),
                              ("stare stared staring stares", 4),])
    def test_stemming(self, benchmark, string, count):
        """Perform reasonable stemming."""
        tokens = benchmark(retrieve_tokens, string)

        assert len(tokens) < count, tokens
        
    @pytest.mark.benchmark(group="retrieve_tokens()")
    def test_positions(self, benchmark):
        """Correct token position in document."""
        tokens = benchmark(retrieve_tokens, "dog chased cat chases rat rats cat")
        dict = {"dog": [0], "chase": [1, 3], "cat": [2, 6], "rat": [4, 5]}
        assert tokens == dict

"""
def test_index(html_page):
    index() updates the inverted index correctly.
    ii = {"internet": {0, 1}, "googl": {1}}
    
    index(html_page, 2, ii)
    assert ii["internet"] == {0, 1, 2} and ii["googl"] == {1, 2}"""
