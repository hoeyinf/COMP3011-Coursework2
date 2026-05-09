
# COMP3011 Coursework 2: Search Engine Tool

This project is a  search engine tool that crawls a website to build an inverted index. Search queries can be run on the inverted index to provide the most relevant pages from the website.


## Running the Program
Main program files are located in `src/`.
Instructions below are given in reference to the command line.

Clone or download the project:
```bash
git clone https://github.com/hoeyinf/COMP3011-Coursework2
```

Go to the main project directory and start a python virtual environment:
```bash
python -m venv
```
Activate the virtual environment.\
macOS/Linux: `source myfirstproject/bin/activate`\
Windows: `myfirstproject\Scripts\activate`

Install dependencies using requirements.txt:
```bash
pip install -r requirements.txt
```
Run the program:
```bash
python src/main.py
```
or:
```bash
python3 src/main.py
```
depending on the version of python installed.


## Usage and Examples
The program will display a list of command options via the terminal.
```bash
-----------------------OPTIONS-----------------------
build - crawls a website to build an inverted index
load  - loads a built inverted index
print - prints the inverted index for a given word
find  - find all relevant pages for a search query
quit  - exit the program
-----------------------------------------------------
```
Any invalid command will be handled and ignored.
```
Enter an option: search University of Leeds
Invalid option entered
```
After an option has finished running, the program will return to the options menu.

### `build`

`build` will prompt the user to enter a website to crawl. 
```
Enter an option: build
Enter website (default=https://quotes.toscrape.com): 
```
If no URL is given,  `https://quotes.toscrape.com` is used. Once selected, the program will start crawling and building an index from a given website. It will print which URLs it is visiting as it runs.
```
Visiting https://quotes.toscrape.com
Visiting https://quotes.toscrape.com/tag/simile
Visiting https://quotes.toscrape.com/tag/be-yourself
Visiting https://quotes.toscrape.com/tag/choices
```
Connection errors will be displayed as below.
```
Connection error: https://quotes.toscrape.com. Retrying...
```
If the crawler is unable to access a link after 3 tries, it is skipped. If it can't access any link after 5 consecutive attempts, crawling is aborted.
```
Too many connection errors. Check your internet access.
```
Once it is done crawling, the completed inverted index will be stored in `data/inverted_index.p`. This is a binary file, so it can not be read plainly. The following message is displayed.
```
Finished crawling website. 203 pages found with 3839 terms indexed.
Inverted index saved successfully in data/inverted_index.p
```
### `load`
`load` will read in a saved inverted index from `data/inverted_index.p`
```
Enter an option: load
Inverted index loaded successfully: 203 total pages with 3839 terms indexed.
```
It will give the following message if there is no inverted index.
```
Can not find the inverted index. Use build before load
```
### `print <word>`
`print <word>` will print the index entry for the given word. Each index is in the form of `{document number 1: [position 1, position 2, ..., position n], document number 2: []...}`.
The position numbers give the location(s) of the word in the document.
```
Enter an option: print success
Inverted index for success
{0: [83, 92], 5: [115], 15: [79], 22: [7, 11, 20], 25: [11, 20],
28: [11, 20], 39: [38], 42: [156], 48: [108], 55: [119, 213],
70: [82, 106], 123: [152], 125: [97], 127: [161], 139: [32],
151: [95], 166: [36], 171: [147, 178], 177: [117], 191: [120]}
```
For example, `0: [83, 92]` means that "success" appears in document 0 in positions 83 and 92.

The inverted index is followed by a document reference to show which document number corresponds to which URL.
```
Document number reference:
0: https://quotes.toscrape.com
5: https://quotes.toscrape.com/author/Jane-Austen
15: https://quotes.toscrape.com/author/Steve-Martin
22: https://quotes.toscrape.com/tag/success
25: https://quotes.toscrape.com/tag/adulthood
...
```
If the entry does not exist, the following message is given.
```
Enter an option: print Leeds
No index found for Leeds
```
Multiple words can not be entered.
```
Enter an option: print University of Leeds
Incorrect usage. Must be: print <single-word>
```

### `find <search query>`
`find <search query>` will find the pages that contain the terms in the search query, sorted by relevance.
```
Results (3 found):
Enter an option: find love and war
https://quotes.toscrape.com/author/E-E-Cummings
https://quotes.toscrape.com/tag/love
https://quotes.toscrape.com/page/5
```
If no results were found, the following message is given.
```
Enter an option: find University of Leeds
Results (0 found):
No matching pages found.
```
### `quit`
Quits the program immediately.
## Implementation Overview and Design Choices
The given structure of for the repository (as outlined in the brief) provided a clear path for the project.

All code has been modularized reasonably into separate functions in each file. PEP 8 and PEP 257 style conventions were followed for readibility and comprehension, with descriptive docstring and inline comments throughout the code.

### `crawler.py`
HTML pages are retrieved with GET requests via the standard python package `requests`. Requests were sent with an appropriate User-Agent header. The `beautifulsoup4` package was used to scrape the HTML to find all relevant links to continue crawling.

Links are normalized according to a few rules:
- SSL is enforced and all URLs start with `https://`
- Any `www.` is removed.
- Port numbers, query parameters (except pages), and fragments are all removed.
- Trailing forward slashes are removed.

Additionally, a design choice was made to consider first pages redundant, since `https://example.com/page/1` will lead to the same page as `https://example.com` in a lot of cases. This filter considers pagination via both `page/1` and `?page=1`, and is careful to only filter out first pages (and not e.g. `page/10`).

Only links that lead to a page on the same website were added to the queue. This is because the scope for this project is to create a search engine tool for one website.
Only links in `<a href=>` tags were considered, and links in the `<footer>` were also ignored.

The crawler will attempt to find and read a `robots.txt`, and will obey any disallowed URLs listed on it. By default, the crawler adheres to a politness window of at least 6 seconds. It has a randomised wait time of 6-9 seconds between requests.
### `indexer.py`
HTML pages were converted to text using `beautifulsoup4`. The text was then parse as follows:
- Unicode was normalized into NFKD form. Multiple encoding of the same symbol, or the same symbol with an accent, are converted to be the same symbol e.g. a á ä = a.
- The text was converted to lowercase.
- Apostrophes were removed and contracted e.g. people's = peoples and don't = dont.
- Hyphens and doublequotes were replace with whitespace.
- Any leftover single punctuation marks, like ! and ?, are removed
- Stopwords are removed. This was done using the `nltk` package's English stopwords corpus.
- The final list of tokens is stemmed using the `SnowballStemmer` from `nltk`. It is an extension of the Porter Stemmer.

The final result is a dictionary of tokens and their position(s) in the document. These were then collated over time into a nested dictionary that forms the inverted index for the website.
The inverted index and document index are stored as a binary file using the `pickle` package. It provides faster serialization than json, and it is easier to store nested dictionaries with it. The size of the resulting file is also much smaller. However, the index is not human-readable. However, since the search engine is used though the command-line (the index is not seen  by the user), this should be fine.

### `search.py`
Search queries were normalized as outline in `indexer.py`. This was done to ensure that the same words that were found in the documents match with the terms in the search query.

Only documents that contained all identified tokens in the search query were considered. While restrictive, it prevents the problem where too many irrelevant pages were being shown in the results. It's also the intended function of the `find` command, as outlined in the brief.

Documents were ranked using TD-IDF. Most of the data needed to calculate it was already extractable from the inverted index; however, the number of tokens identified in each document was added to the document index to make calculation more efficient for relatively little storage (one extra number per document).

### `main.py`
This file cotains the main program, including the command-line interface display and user input processing.
The main overview is in the previous Usage/Examples section.
## Testing
Tests are located in `tests/`. They were written using python packages `pytest` and `pytest-benchmark`.

To run tests, run the following command

```bash
pytest
```
Example of tests being run (dots are passed tests, Fs are failed tests):
```
configfile: pytest.ini
plugins: benchmark-5.2.3
collected 61 items

tests\test_crawler.py ......FF.....F.........   [ 37%]
tests\test_indexer.py ......F......             [ 77%]
```
The results of the tests are shown in the terminal.
```
FAILED tests/test_crawler.py::TestNormalizeLink::test_links[https://www.example.com] - AssertionError: https://example.com
FAILED tests/test_crawler.py::TestNormalizeLink::test_links[http://example.com] - AssertionError: https://example.com
FAILED tests/test_crawler.py::TestNormalizeLink::test_links[https://example.com/page/1] - AssertionError: https://example.com
============================================ 3 failed, 58 passed, 1 warning in 50.78s ======================================
```
Performace testing was done for certain vital functions (that are called at a high frequency). The results are displayed just above the test summary. An example for TF-IDF calculation is shown below.
```
----------------------------------------------------------------------------------------- benchmark 'tfidf()': 3 tests ----------------------------------------------------------------------------------------
Name (time in ns)                   Min                     Max                Mean              StdDev              Median                 IQR            Outliers  OPS (Mops/s)            Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_tfidf[brown-0-0.3996]     209.0899 (1.0)       61,527.2729 (1.0)      234.4912 (1.0)      350.2601 (1.0)      218.1835 (1.0)        4.5481 (1.0)    2007;15183        4.2646 (1.0)      196077          22
test_tfidf[milk-5-0.6496]      209.0899 (1.0)       62,395.4561 (1.01)     244.9278 (1.04)     397.4820 (1.13)     227.2745 (1.04)       9.0910 (2.00)   1791;10072        4.0828 (0.96)     188680          22
test_tfidf[cat-6-0.3154]       299.9441 (1.43)     180,099.9744 (2.93)     358.5072 (1.53)     919.3663 (2.62)     300.0023 (1.38)     100.0008 (21.99)    379;2412        2.7893 (0.65)     185184           1
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```
## Acknowledgements

 - [Python3 Style Checker](https://www.codewof.co.nz/style/python3/)
 - [Unicode Normalization Forms](https://www.unicode.org/reports/tr15/)
 - [SnowballStemmer](https://www.nltk.org/api/nltk.stem.SnowballStemmer.html)
 - Microsoft 365 Copilot
