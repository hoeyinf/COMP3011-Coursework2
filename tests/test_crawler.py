"""Tests for src/crawler.py"""

import pytest
import requests
from unittest.mock import patch
from crawler import *


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


class TestNormalizeLink:
    """Tests for normalize_link()."""

    @pytest.mark.parametrize("url", [
        "https://example.com/",
        "www.example.com",
        "https://www.example.com",
        "http://example.com",
        "https://example.com/page/1",
        "https://example.com?page=1",
        "https://example.com?search=friend",
        "https://example.com?filter=new&search=leeds",
        "https://example.com#bar",
        "https://example.com:443"])
    @pytest.mark.benchmark(group="normalize_link()")
    def test_links(self, benchmark, url):
        """Normalize URLS correctly, with performance testing.
        
        Checks for URLS that have: trailing forward slashes, www.,
        non-https, redundant first pages, query parameters, fragments,
        and port numbers.
        """
        result = benchmark(normalize_link, link=url)
        assert result == "https://example.com"

    @pytest.mark.parametrize("url", [
        "https://example.com?page=10",
        "https://example.com/page/11",
        "https://example.com/page=2"
        "https://example.com?page=3"])
    def test_pages(self, url):
        """Do not remove pages that are not 1."""
        assert normalize_link(url) == url
                            
    def test_complex(self):
        """Complex URL normalization"""
        
        link = normalize_link("www.example.com:443/users?search=jane&page=2")
        assert link == "https://example.com/users?page=2"

class TestRetrieveLinks:
    """Tests for retrieve_links()"""
    base = "https://example.com"
    
    @pytest.mark.parametrize(
        "html_page",
        [{"https://example.com/about", "https://example.com/page/2",
          "https://example.com"}],
        indirect=True
    )
    def test_absolute_urls(self, html_page):
        """Find absolute urls."""
        links = retrieve_links(html_page, self.base)
        assert links == {"https://example.com/about",
                         "https://example.com/page/2",
                         "https://example.com"}

    @pytest.mark.parametrize(
        "html_page", [["/about", "/page/2", "/users/page/3"]], indirect=True
    )
    def test_relative_urls(self, html_page):
        """Find relative urls."""
        links = retrieve_links(html_page, self.base)
        assert links == {self.base+"/about",
                         self.base+"/page/2",
                         self.base+"/users/page/3"}

    @pytest.mark.parametrize("html_page",
        [{"www.google.com", "https://site.org", "/users/123"}],
        indirect=True)
    def test_outside_domain(self, html_page):
        """Ignore links that lead out of domain of the base URL."""
        links = retrieve_links(html_page, self.base)
        assert links == {self.base+"/users/123"}

    @pytest.mark.parametrize("html_page", [{}], indirect=True)
    def test_no_urls(self, html_page):
        """Handle pages with no links."""
        links = retrieve_links(html_page, self.base)
        assert links == set()

    @pytest.mark.parametrize(
        "html_page",
        [["/users/1", "/users/2", "/users/1"]],
        indirect=True
    )
    def test_duplicate_urls(self, html_page):
        """Parse duplicate URLs correctly."""
        links = retrieve_links(html_page, self.base)
        assert links == {self.base+"/users/1", self.base+"/users/2"}

    @pytest.mark.parametrize(
        "html_page",
        [["/users/1", "/users/2", "/users/1/"]],
        indirect=True
    )
    def test_duplicate_urls_distinct(self, html_page):
        """Parse duplicate URLs that are formatted differently."""
        links = retrieve_links(html_page, self.base)
        assert links == {self.base+"/users/1", self.base+"/users/2"}

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
    url = "https://quotes.toscrape.com/tag/abilities"
    try:
        html = retrieve_page(url)
    except requests.exceptions.HTTPError as e:
        assert False, "retrieve_page() failed."
    else:
        links = retrieve_links(html, url)
        assert len(links) == 15
