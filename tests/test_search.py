"""Tests for src/search.py"""

import pytest
import string
from search import *


class TestQueryTokens:
    """"Tests for query_tokens()."""
    
    @pytest.mark.parametrize("query,expected",[
        ("albert einstein", ["albert", "einstein"]),
        ("love quotes", ["love", "quot"]),
        ("horror movies 2026 upcoming", ["horror", "movi", "2026", "upcom"])])
    @pytest.mark.benchmark(group="query_tokens()")
    def test_basic(self, benchmark, query, expected):
        """Reduce query to appropriate tokens."""
        tokens = benchmark(query_tokens, query)

        assert tokens == expected
        
    @pytest.mark.parametrize("query",[
        "is albert einstein alive",
        "are hobbies a waste of time",
        "country with the highest population",
        "my stomach is cramping and nauseous"])
    @pytest.mark.benchmark(group="query_tokens()")
    def test_stopwords(self, benchmark, query):
        """Remove stopwords correctly."""
        stopwords = ["is", "are", "a", "of", "the", "with", "the", "my", "and"]
        tokens = benchmark(query_tokens, query)

        assert [word not in tokens for word in stopwords]
        assert len(tokens) == 3, tokens
        
    @pytest.mark.parametrize("query",[
        "albert einstein alive today?",
        "hobbies waste alot time!",
        "hand-drawn graph theory"])
    @pytest.mark.benchmark(group="query_tokens()")
    def test_punctuation(self, benchmark, query):
        """Handle punctuation."""
        tokens = benchmark(query_tokens, query)

        assert [c not in " ".join(tokens) for c in string.punctuation]
        assert len(tokens) == 4, tokens
    
    
def test_tfidf():
    assert False