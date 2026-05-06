"""Tests for src/crawler.py"""

import pytest
from src.crawler import *


@pytest.fixture(scope='function')
def html_page(request):
    """Modifiable fixture for an HTML page."""
    page = """<html lang="en">
              <head><meta charset="UTF-8"><title>Mock HTML Page</title>
              <link rel="stylesheet" href="/static/bootstrap.min.css"></head>
              <body><div class="container">"""

    # Adds links to the body of the HTML page
    for link in request.param:
        page += f"<a href={link}>link</a></span>"
    
    page += "</div></body></html>"
    return page


class TestRetrieveLinks:
    """Tests for retreive_links()"""
    
    @pytest.mark.parametrize(
        "html_page",
        [{"www.google.com", "https://minerva.leeds.ac.uk"}],
        indirect=True
    )
    def test_absolute_urls(self, html_page):
        """Finds absolute urls."""
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {"www.google.com", "https://minerva.leeds.ac.uk"}

    @pytest.mark.parametrize(
        "html_page",
        [["/about", "/users/123"]],
        indirect=True
    )
    def test_relative_urls(self, html_page):
        """Finds relative urls."""
        base_url = "https://quotes.toscrape.com"
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {base_url+"/about", base_url+"/users/123"}

    @pytest.mark.parametrize(
        "html_page",
        [{"www.google.com", "/about", "https://site.org", "/users/123"}],
        indirect=True
    )
    def test_absolute_and_relative_urls(self, html_page):
        """Finds multiple mixed urls."""
        base_url = "https://quotes.toscrape.com"
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {
            "www.google.com", "https://site.org",
            base_url+"/about", base_url+"/users/123"
        }

    @pytest.mark.parametrize("html_page", [{}], indirect=True)
    def test_no_urls(self, html_page):
        """Handles pages with no links."""
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == set()

    @pytest.mark.parametrize(
        "html_page",
        [["/users/1", "www.google.com", "/users/1"]],
        indirect=True
    )
    def test_duplicate_urls(self, html_page):
        """Parses duplicate urls correctly."""
        base_url = "https://quotes.toscrape.com"
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {"www.google.com", base_url+"/users/1"}

    def test_disallowed(self, html_page):
        """Avoids a disallowed link from a robot.txt file."""
        assert False

class TestRetrievePage:
    def test_basic():
        """Fetches and downloads a correct html page using a link."""
        assert False

    def test_error():
        """Handles errors."""
        assert False