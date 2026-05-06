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


class TestRetrieveWords:
    """"Tests for retrieve_is()"""

    @pytest.mark.parametrize("string,expected",
                             [("", 0),
                              ("single", 1),
                              ("multiple significant words used precisely", 5),
                              ("paragraphs\n\nnecessarily\nwork properly", 4),
                              ("however, punctuation exists everywhere!", 4)])
    def test_words_in_strings(self, string, expected):
        """Identify correct number of words in a variety of strings.
        
        Specifically: no words, one word, multiple words, paragraphs,
        and a sentence with punctuation.
        """
        words = retrieve_words(string)
        assert len(words) == expected, words
    
    @pytest.mark.parametrize("string,expected",
                             [("this is a sentence", 1),
                              ("this string contains a few stopwords", 3),
                              ("to be or not to be", 0)])
    def test_stopwords(self, string, expected):
        """Perform correct stopword removal."""
        stopwords = ["this", "is", "a", "few", "to", "be", "or", "not"]

        words = retrieve_words(string)
        assert [word not in words for word in stopwords]
        assert len(words) == expected, words

    @pytest.mark.parametrize("string,count",
                             [("write wrote written writes", 4),
                              ("book books", 2),
                              ("stare stared staring stares", 4),])
    def test_stemming(self, string, count):
        """Perform reasonable stemming."""
        words = retrieve_words(string)
        assert len(words) < count, words

    def test_unicode(self):
        """Unicode text"""
        
        assert False

        # Add tests for: capitalization, hyphenation, apostrophes, numbers (decimals, commas/period delimiters), titles (mrs. ph.d)
