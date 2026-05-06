"""Functions for a web crawler."""
import re
import requests
import time
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
        
        # Defines a regular expression for an absolute URL
        absolute = re.compile(r"^(https:\/\/|www\.)[^ :]+$")
        
        # If it matches an absoulte url and is not the base url (self-link)
        if absolute.match(tag["href"]) and tag["href"] != base_url:
            links.add(tag["href"])
        # Else it is a relative url
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


def crawl(seed):
    """Perform a web crawl using a provided seed URL.
    
    Args:
        seeds (list): seed URL to start a crawl.
    """
    visited = set()
    retrieval_time = time.time() - 6

    # Initializes queue and loops until it is empty.
    queue = [seed]
    while queue:
        url = queue.pop(0)
        if url in visited: continue

        # Obeys politeness window of at least 6 seconds
        i = 0
        while time.time() - retrieval_time < 6:
            time.sleep(1)

        # Downloads page and adds it to the visited list
        html = retrieve_page(url)
        retrieval_time = time.time()
        print(f"{url} visited\n")
        visited.add(url)
        
        # Adds links that have not been visited to the queue
        links = retrieve_links(html, url)
        for link in links:
            if link not in visited:
                queue.append(link)
    return

