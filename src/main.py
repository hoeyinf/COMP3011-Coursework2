"""Main program for the search engine."""

import os.path
import pickle
import nltk
from crawler import crawl
from search import query_tokens, search


def build(args: list[str], fname: str) -> None:
    """Option to crawl website and build the inverted index.

    Args:
        args (list): arguments entered by the user.
        fname (str): filename for the inverted_index.
    """
    if len(args) != 1:
        print("Incorrect usage. Must be: build")
        return

    # User can input a different website if they want to.
    website = input("Enter website (default=https://quotes.toscrape.com): ")
    if website == "":
        website = "https://quotes.toscrape.com"

    docs, index = crawl(website)
    if not all([docs, index]):
        print("Too many connection errors. Check your internet access.")
        return
    elif docs == "Bad" and index == "Url":
        return

    print(f"Finished crawling website. {len(docs)} pages found with "
          f"{len(index)} terms indexed.")

    # Writes the resulting dictionaries as binary using pickle
    with open(fname, "wb") as f:
        pickle.dump(docs, f)
        pickle.dump(index, f)
    print("Inverted index saved successfully in data/inverted_index.p")


def load(args: list[str],
         fname: str,
         inverted_index: list[dict, dict]) -> None:
    """Option to load a build inverted index.

    Args:
        args (list): arguments entered by the user.
        fname (str): filename for the inverted_index.
        inverted_index (list): list of dicts to store the inverted index.
    """
    if len(args) != 1:
        print("Incorrect usage. Must be: load")
    # Checks that inverted index exists
    elif not os.path.exists(fname):
        print("Can not find the inverted index. Use build before load")
    else:
        inverted_index.clear()
        # Loads both dictionaries with pickle
        with open(fname, "rb") as f:
            inverted_index.append(pickle.load(f))
            inverted_index.append(pickle.load(f))
        print(f"Inverted index loaded successfully: {len(inverted_index[0])} "
              f"total pages with {len(inverted_index[1])} terms indexed.")


def print_index(args: str, inverted_index: list[dict, dict]) -> None:
    """Option to print a word's inverted index.

    Args:
        args (list): arguments entered by the user.
        inverted_index (list): a loaded inverted index.
    """
    # Checks if word was entered or index is loaded
    if len(args) != 2:
        print("Incorrect usage. Must be: print <single-word>")
    elif inverted_index == []:
        print("Inverted index not loaded. Use load before print")
    else:
        # Normalizes the entered word
        stem = query_tokens(args[1])[0]
        # Prints index if it exists
        if stem in inverted_index[1]:
            print(f"Inverted index for {args[1]}\n{inverted_index[1][stem]}\n")
            # Prints relevant document names for reference
            print("Document number reference:")
            for doc in inverted_index[1][stem]:
                print(f"{doc}: {inverted_index[0][doc][0]}")
        else:
            print(f"No index found for {args[1]}")


def find(query: str, inverted_index: list[dict, dict]) -> None:
    """Option to find pages containing the search query.

    Args:
        query (list): arguments entered by the user.
        inverted_index (list): a loaded inverted index.
    """
    # Checks if query is empty or index is loaded
    if len(query) == 1:
        print("Empty query. Must be: find <search query>")
    elif inverted_index == []:
        print("Inverted index not loaded. Use load before find")
    else:
        results = search(" ".join(query[1:]),
                         inverted_index[0],
                         inverted_index[1])
        print(f"Results ({len(results)} found):")
        [print(result) for result in results]

        if len(results) == 0:
            print("No matching pages found.")


def main_loop(inverted_index: list[dict, dict]) -> None:
    """Run the command-line interface for the program.

    Args:
        inverted_index (list): structure to store an inverted index.
    """
    fname = os.path.dirname(__file__) + '/../data/inverted_index.p'

    # Displays the options
    print("\n-----------------------OPTIONS-----------------------\n"
          "build -\tcrawls a website to build an inverted index\n"
          "load  -\tloads a built inverted index\n"
          "print -\tprints the inverted index for a given word\n"
          "find  -\tfind all relevant pages for a search query\n"
          "quit  -\texit the program\n"
          "-----------------------------------------------------\n")
    option = input("Enter an option: ")
    options = option.split()

    # Ignores empty user input
    if len(options) == 0:
        print("No option entered. Try again.")
        return

    # Selects the option based on user input
    if options[0] == "build":
        build(options, fname)
    elif options[0] == "load":
        inverted_index = load(options, fname, inverted_index)
    elif options[0] == "print":
        print_index(options, inverted_index)
    elif options[0] == "find":
        find(options, inverted_index)
    elif option == "quit":
        exit(0)
    else:
        print("Invalid option entered")


if __name__ == "__main__":

    # Necessary downloads for parsing tokens
    nltk.download('punkt_tab')
    nltk.download('stopwords')

    print("\nSearch Engine Tool for COMP3011\n")

    inverted_index = []
    while True:
        main_loop(inverted_index)
