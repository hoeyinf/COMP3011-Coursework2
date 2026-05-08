"""Tests for src/search.py."""

import pytest
import string
from search import query_tokens, tfidf, search
from indexer import index


@pytest.fixture()
def documents():
    """Fixture for documents."""
    return {0:  ["the quick brown fox jumped over the lazy dog"],
            1:  ["foxes and cats are mammals with triangular ears"],
            2:  ["dogs and cats are the most common household pets"],
            3:  ["mammals produce milk and have fur or hair"],
            4:  ["cat ears are a common accessory"],
            5:  ["the most common milk to drink is cow milk"],
            6:  ["having a pet cat means having cat hair everywhere"],
            7:  ["my cat is lazy and drinks milk in the common room"],
            8:  ["while a common practice, do not dog-ear your books"],
            9:  ["i was too lazy to book a practice room online"],
            10: ["can commonly get the book online or as a physical book"]}


@pytest.fixture()
def indices(documents):
    """Fixture for a document index and its inverted index."""
    ii = dict()
    for doc in documents:
        terms = index(documents[doc][0], doc, ii)
        documents[doc].append(terms)
    return documents, ii


class TestQueryTokens:
    """Tests for query_tokens()."""

    @pytest.mark.parametrize("query,expected", [
        ("albert einstein", ["albert", "einstein"]),
        ("love quotes", ["love", "quot"]),
        ("horror movies 2026 upcoming", ["horror", "movi", "2026", "upcom"])])
    @pytest.mark.benchmark(group="query_tokens()")
    def test_basic(self, benchmark, query, expected):
        """Reduce query to appropriate tokens."""
        tokens = benchmark(query_tokens, query)

        assert tokens == expected

    @pytest.mark.parametrize("query", [
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

    @pytest.mark.parametrize("query", [
        "albert einstein alive today?",
        "hobbies waste alot time!",
        "hand-drawn graph theory"])
    @pytest.mark.benchmark(group="query_tokens()")
    def test_punctuation(self, benchmark, query):
        """Handle punctuation."""
        tokens = benchmark(query_tokens, query)

        assert [c not in " ".join(tokens) for c in string.punctuation]
        assert len(tokens) == 4, tokens


@pytest.mark.parametrize("term,document,expected", [
    ("cat", 6, 0.3154),
    ("milk", 5, 0.6496),
    ("brown", 0, 0.3996)])
@pytest.mark.benchmark(group="tfidf()")
def test_tfidf(indices, benchmark, term, document, expected):
    """Calculate the correct TF-IDF."""
    dicts = indices
    score = benchmark(tfidf, dicts[1][term], document, dicts[0])

    assert abs(score - expected) < 0.001


@pytest.mark.parametrize("query,expected", [
    ("cat", [
        "having a pet cat means having cat hair everywhere",
        "cat ears are a common accessory",
        "dogs and cats are the most common household pets",
        "foxes and cats are mammals with triangular ears",
        "my cat is lazy and drinks milk in the common room"])
    ])
@pytest.mark.benchmark(group="search()")
def test_search(indices, benchmark, query, expected):
    """Return expected search results."""
    dicts = indices
    docs = benchmark(search, query, dicts[0], dicts[1])

    assert docs == expected
