"""Functions for a web crawler."""
import re
import requests
from bs4 import BeautifulSoup


def retrieve_links(html, base_url):
    """Retrieves the unique url links in an HTML page."""

    soup = BeautifulSoup(html, "html.parser")
    links = set()

    # Loops through every <a href> tag
    for tag in soup.find_all("a", href=True):
        
        # Adds links, differentiating between absolute and relative urls.
        absolute = re.compile(r"^(https:\/\/|www\.)[^ :]+$")
        if absolute.match(tag["href"]): links.add(tag["href"])
        else: links.add(base_url + tag["href"])

    return links


def retrieve_page(url):
    """Retrieves an HTML page via a GET request to a supplied url."""

    response = requests.get(url)
    response.raise_for_status()
    return response.text


def crawl():
    """For now it retrieves a list of links accessible from the root url."""
    return

