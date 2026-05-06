"""Tests for src/crawler.py"""

import pytest
import requests
from unittest.mock import patch
from src.crawler import *


@pytest.fixture(scope='function')
def html_page(request):
    """Modifiable fixture for an HTML page."""
    page = """<!doctype html><html lang="en">
              <head><meta charset="UTF-8"><title>Mock HTML Page</title>
              <link rel="stylesheet" href="/static/bootstrap.min.css"></head>
              <body><div class="container">"""

    # Adds links to the body of the HTML page
    for link in request.param:
        page += f"<a href={link}>link</a></span>"
    
    page += "</div></body></html>"
    return page


class TestRetrieveLinks:
    """Tests for retrieve_links()"""
    
    @pytest.mark.parametrize(
        "html_page",
        [{"www.google.com", "https://minerva.leeds.ac.uk"}],
        indirect=True
    )
    def test_absolute_urls(self, html_page):
        """Find absolute urls."""
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {"www.google.com", "https://minerva.leeds.ac.uk"}

    @pytest.mark.parametrize(
        "html_page",
        [["/about", "/users/123"]],
        indirect=True
    )
    def test_relative_urls(self, html_page):
        """Find relative urls."""
        base_url = "https://quotes.toscrape.com"
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {base_url+"/about", base_url+"/users/123"}

    @pytest.mark.parametrize(
        "html_page",
        [{"www.google.com", "/about", "https://site.org", "/users/123"}],
        indirect=True
    )
    def test_absolute_and_relative_urls(self, html_page):
        """Find multiple mixed urls."""
        base_url = "https://quotes.toscrape.com"
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {
            "www.google.com", "https://site.org",
            base_url+"/about", base_url+"/users/123"
        }

    @pytest.mark.parametrize("html_page", [{}], indirect=True)
    def test_no_urls(self, html_page):
        """Handle pages with no links."""
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == set()

    @pytest.mark.parametrize(
        "html_page",
        [["/users/1", "www.google.com", "/users/1"]],
        indirect=True
    )
    def test_duplicate_urls(self, html_page):
        """Parse duplicate urls correctly."""
        base_url = "https://quotes.toscrape.com"
        links = retrieve_links(html_page, "https://quotes.toscrape.com")
        assert links == {"www.google.com", base_url+"/users/1"}

    def test_disallowed(self):
        """Avoid a disallowed link from a robot.txt file."""
        assert False

class TestRetrievePage:
    """Tests for retrieve_page()"""

    def test_valid(self):
        """Fetch an HTML page using a valid link."""
        try:
            html = retrieve_page("https://www3.pioneer.com/argentina/PETWS/test"
                                ".html")
        except requests.exceptions.HTTPError as e:
            html = "HTTPError"

        assert html == ("<html>\r\n<head>\r\n"
                        "<title>This is a test static html page</title>\r\n"
                        "</head>\r\n\r\n<body>\r\n"
                        "<p>This is a test static html page for PETWS web "
                        "site</p>\r\n</body>\r\n</html>")
        
    def test_invalid(self):
        """Handle an invalid link."""
        try:
            html = retrieve_page("https://www.google.com/404")
        except requests.exceptions.HTTPError as e:
            assert e.response.status_code == 404, "Wrong status code."
        else:
            assert False, "No HTTPError raised."

@pytest.mark.integrity
def test_retrieve_page_and_retrieve_links():
    """Correct function of retrieve_page into retrieve_links()"""
    url = "https://quotes.toscrape.com"
    try:
        html = retrieve_page(url)
    except requests.exceptions.HTTPError as e:
        assert False, "retrieve_page() failed."
    else:
        links = retrieve_links(html, url)
        assert len(links) == 49, links
