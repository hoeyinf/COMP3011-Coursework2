"""Tests for src/indexer.py"""

import pytest
from src.indexer import *


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
                              ("multiple significant words used precisely", 5),
                              ("paragraphs\n\nnecessarily\nwork properly", 4),
                              ("however, punctuation exists everywhere!", 4),
                              ("John Doe Leeds United Kingdom", 5),
                              ("Ms. Tan www.google.com p.m e.g.", 5)])
    def test_words_in_strings(self, string, expected):
        """Identify the correct number of tokens in a variety of strings.
        
        Specifically: no words, one word, multiple words, paragraphs,
        general punctuation, capitalization, and periods.
        """
        words = retrieve_tokens(string)
        assert len(words) == expected, words
        
    @pytest.mark.parametrize("string,expected",
                             [("t-shirt", 1),
                              ("hand-drawn", 2),
                              ("em-dash", 2)])
    def test_hyphens(self, string, expected):
        """Identify the correct number of tokens in words with hyphens."""
        words = retrieve_tokens(string)
        assert len(words) == expected, words
        
    def test_apostrophes(self):
        """Identify the correct tokens in a string with apostrophes."""
        words = retrieve_tokens("don't can't Michael's people's "
                                "2000's womens' o'donnell")
        assert len(words) == 7, words
        
    @pytest.mark.parametrize("string,expected",
                             [("1 256 987654", 3),
                              ("3.1415", 1),
                              ("3.000 12,345  1,024.20480 678.901,24", 4)])
    def test_numbers(self, string, expected):
        """Identify numbers correctly."""
        numbers = set()
        [numbers.add(number) for number in string.split()]
        words = retrieve_tokens(string)
        assert len(words) == expected, words
        assert words == numbers
    
    @pytest.mark.parametrize("string,expected",
                             [("this is a sentence", 1),
                              ("this string contains a few stopwords", 3),
                              ("to be or not to be", 0)])
    def test_stopwords(self, string, expected):
        """Perform correct stopword removal."""
        stopwords = ["this", "is", "a", "few", "to", "be", "or", "not"]

        words = retrieve_tokens(string)
        assert [word not in words for word in stopwords]
        assert len(words) == expected, words

    @pytest.mark.parametrize("string,count",
                             [("write wrote written writes", 4),
                              ("book books", 2),
                              ("stare stared staring stares", 4),])
    def test_stemming(self, string, count):
        """Perform reasonable stemming."""
        words = retrieve_tokens(string)
        assert len(words) < count, words

    def test_unicode(self):
        """Unicode text"""
        
        assert False


def test_index(html_page):
    """index() updates the inverted index correctly."""
    ii = {"internet": {0, 1}, "googl": {1}}
    
    index(html_page, 2, ii)
    assert ii["internet"] == {0, 1, 2} and ii["googl"] == {1, 2}