"""Functions for a web crawler."""
import re
import requests
import time
from bs4 import BeautifulSoup
from indexer import index
from urllib.parse import urlparse


def normalize_link(link):
    """Normalizes a link."""
    # Remove trailing slash
    if link[-1] == "/":
        link = link[:-1]
    
    return link


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
    
    # Ignores footer content
    for footer in soup.find_all("footer"):
        footer.decompose()

    # Loops through every <a href> tag
    for tag in soup.find_all("a", href=True):
        
        # Defines a regular expression for an absolute URL
        absolute = re.compile(r"^(https:\/\/|www\.)[^ :]+$")
        
        # If it matches an absoulte url and is not the base url (self-link)
        if absolute.match(tag["href"]) and tag["href"] != base_url:
            link = tag["href"]
        # Else it is a relative url
        else:
            link = base_url + tag["href"]
        
        links.add(normalize_link(link))

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
    response = requests.get(url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; "
                                 "Win64; x64) AppleWebKit/537.36 (KHTML, like "
                                 "Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/14"
                                 "3.0.0.0"},
                        timeout=10)
    response.raise_for_status()
        
    return response.text


def crawl(seed):
    """Perform a web crawl using a provided seed URL.
    
    Args:
        seeds (list): seed URL to start a crawl.
    """
    visited = dict()
    inverted_index = dict()
    retrieval_time = time.time() - 6

    # Initializes queue and loops until it is empty.
    queue = [seed]
    doc_number = 0
    while queue:
        url = queue.pop(0)
        if url in visited.values(): continue

        # Obeys politeness window of at least 6 seconds
        while time.time() - retrieval_time < 6:
            time.sleep(1)

        # Tries to download page, handles request errors
        retrieval_time = time.time()
        try:
            html = retrieve_page(url)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {url}")
            print(e)
            # Re-inserts the url back into the queue to retry
            queue.insert(1, url)
            print(queue[0:3])
            continue
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404: print(e)
            continue
        
        # Adds page to visited dictionary
        visited[doc_number] = url
        print(url)
        
        # Indexes the page
        index(html, doc_number, inverted_index)
        doc_number += 1
        
        # Finds the base URL
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Adds links that have not been visited to the queue
        links = retrieve_links(html, base_url)
        for link in links:
            if link not in visited:
                queue.append(link)

    return visited, inverted_index

