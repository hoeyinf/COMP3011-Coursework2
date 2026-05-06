"""Functions for a web crawler."""
import re
import requests
from bs4 import BeautifulSoup


def retrieve_links(html, base_url):
    """Retrieve the unique url links in an HTML page.
    
    Args:
        html (str): the HTML page to be parsed.
        base_url (str): the base URL of the HTML page.
    
    Returns:
        set: Unique links found.
    """

    soup = BeautifulSoup(html, "html.parser")
    links = set()

    # Loops through every <a href> tag
    for tag in soup.find_all("a", href=True):
        
        # Adds links, differentiating between absolute and relative urls.
        absolute = re.compile(r"^(https:\/\/|www\.)[^ :]+$")
        # Matches an absoulte url and is not the base url (self-link)
        if absolute.match(tag["href"]) and tag["href"] != base_url:
            links.add(tag["href"])
        else:
            links.add(base_url + tag["href"])

    return links


def retrieve_page(url):
    """Retrieve an HTML page via a GET request.
    
    Args:
        url (str): the url used for the GET request
    
    Returns:
        str: The HTML of the web page.
    
    Raises:
        HTTPError: An HTTP error.
    """

    response = requests.get(url)
    response.raise_for_status()
    return response.text


def crawl():
    """For now it retrieves a list of links accessible from the root url."""
    return

