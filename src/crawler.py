"""Functions for a web crawler."""

import re
import requests
import time
from bs4 import BeautifulSoup
from indexer import index
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from urllib import robotparser
from random import randint


def normalize_link(link: str) -> str:
    """Normalize a link.

    Args:
        link (str): the link being normalized.

    Returns:
        link (str): the normalized link
    """
    # Removes "www."
    link = link.replace("www.", "")

    # Changes all links to start with https://
    if not link.startswith(("http://", "https://")):
        link = "https://" + link
    link = link.replace("http://", "https://")

    # Removes port numbers, fragments, and all query parameters (except page)
    parts = urlparse(link)
    qs = parse_qs(parts.query)
    new_qs = {}
    if 'page' in qs:
        new_qs['page'] = qs['page'][0]

    link = urlunparse((parts.scheme, parts.netloc.split(":")[0],
                       parts.path, "", urlencode(new_qs), ""))

    # Finds paginated URLs
    page_i = link.find("page")
    if page_i != -1:
        # Regex first page only ("page=1" or "page/1", but not e.g. "page=10")
        page_ex = re.compile(r"^page(?:=|/)1(?!\d).*")
        if page_ex.match(link[page_i:]):
            # Removes any page that is a first page (assumed to be redundant)
            link = link.replace(link[page_i:page_i+6], "")

            # Checks page was a query parameter
            if link[page_i - 1] == "?":
                # Deletes either "?" or "&"
                # depending on if there were other query parameters
                if len(link) > page_i:
                    if link[page_i] == "&":
                        page_i += 1
                link = link.replace(link[page_i - 1], "")

    # Remove trailing slash
    link = link.rstrip("/")
    return link


def retrieve_links(html: str, base: str) -> set[str]:
    """Retrieve the unique relative URLs in an HTML page.

    Args:
        html (str): the HTML page to be parsed.
        base (str): the website domain (base URL).

    Returns:
        links (set): all unique relative links found.
    """
    links = set()
    # Reads HTML, ignoring footer content
    soup = BeautifulSoup(html, "html.parser")
    for footer in soup.find_all("footer"):
        footer.decompose()

    # Loops through every <a href> tag
    for tag in soup.find_all("a", href=True):

        # Defines a regular expression for an absolute URL
        absolute = re.compile(r"^(https?:\/\/|www\.)[^ :]+$")

        # Changes relative links to absolute links
        if tag["href"][0] == "/":
            link = base + tag["href"]
        else:
            link = tag["href"]

        # Normalizes all absolute URLS, skipping skips badly formatted links
        if absolute.match(link):
            link = normalize_link(link)
        else:
            continue

        # Adds the link only if it leads to the same website domain (base URL)
        if link.startswith(base):
            links.add(link)

    return links


def retrieve_page(url: str) -> str:
    """Retrieve an HTML page via a GET request.

    Args:
        url (str): the url used for the GET request

    Returns:
        html (str): The HTML of the web page.

    Raises:
        ConnectionError: A connection error.
        HTTPError: An HTTP error.
    """
    response = requests.get(url,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT "
                                "10.0; Win64; x64) AppleWebKit/537.36 (KHTM"
                                "L, like Gecko) Chrome/143.0.0.0 Safari/537"
                                ".36 Edg/143.0.0.0"},
                            timeout=10)
    response.raise_for_status()

    return response.text


def crawl(seed: str) -> list[dict]:
    """Perform a web crawl using a provided seed URL.

    Args:
        seeds (str): seed URL to start a crawl.

    Returns:
        visited (dict): document index of all URLs visited in the crawl.
        inverted_index (dict): inverted index of all terms in visited URLs.
    """
    visited = dict()
    inverted_index = dict()
    retrieval_time = time.time() - 6

    # Checks the website URL format and finds the base URL
    parsed = urlparse(seed)
    if not all([parsed.scheme, parsed.netloc]):
        print("Provided website is not a proper URL.")
        return ["Bad", "Url"]
    seed = normalize_link(seed)
    parsed = urlparse(seed)
    base = f"https://{parsed.netloc}"

    # Checks for a robot.txt file
    rp = robotparser.RobotFileParser()
    rp.set_url(f"{base}/robots.txt")
    rp.read()

    # Initializes queue and loops until it is empty.
    queue = [seed]
    doc_number = 0
    retry = 0
    connection = 0
    while queue:
        url = queue.pop(0)
        # Avoids visited URLs and disallowed URLs
        if any(url in value for value in visited.values()):
            continue
        if not rp.can_fetch("*", url):
            continue

        # Ensures a politeness window of at least 6 seconds
        while time.time() - retrieval_time < 6:
            time.sleep(1)

        # Tries to download page, handles request errors
        retrieval_time = time.time()
        try:
            print(f"Visiting {url}")
            html = retrieve_page(url)
        except requests.exceptions.ConnectionError:
            # Retries requests up to 3 times when ConnectionError
            connection += 1
            if connection > 5:
                return [False, False]
            if retry > 3:
                print("Cannot access URL. Skipping...")
                retry = 0
                continue
            else:
                print(f"Connection error: {url}. Re-trying...")
                retry += 1
                # Re-inserts the url back into the queue to retry
                queue.insert(0, url)
                continue
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                print(e)
            continue

        retry = 0
        connection = 0

        # Indexes the page
        doc_terms = index(html, doc_number, inverted_index)

        # Adds page and its number of terms to document dictionary
        visited[doc_number] = [url, doc_terms]
        doc_number += 1

        # Adds links that have not been visited to the queue
        links = retrieve_links(html, base)
        for link in links:
            if not any(link in value for value in visited.values()):
                if rp.can_fetch("*", url):
                    queue.append(link)

        # Randomizes wait time
        time.sleep(randint(6, 9))

    return visited, inverted_index
