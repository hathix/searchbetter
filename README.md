# SearchBetter: query rewriting for search engines on small corpuses

> by Neel Mehta, Harvard University

SearchBetter lets you make powerful, fast, and drop-in search engines for any dataset, no matter how small or how large. It also offers built-in query rewriting, which uses NLP to help your search engines find semantically-related content to the user's search term.

For instance, a search for `machine learning` might only return results for items that contain the words "machine learning". But with query rewriting, you would get results not only for `machine learning` but also, say, `artificial intelligence` and `neural networks`.

SearchBetter lets you power up your search engines with minimal effort. It's especially useful if you have a small dataset to search on, or if you don't have the time or data to make fancy bespoke query rewriting algorithms.

## Usage

[Try out the interactive demo](https://github.com/hathix/searchbetter/blob/master/notebooks/searchbetter-demo.ipynb)!

For a truly quick-and-dirty dive into SearchBetter (no setup required), use:

```py
from searchbetter import rewriter

query_rewriter = rewriter.WikipediaRewriter()
query_rewriter.rewrite('biochemistry')
```

## Getting started

To drop this module into your app:

```
pip install searchbetter
```

For more advanced analysis and research purposes, use the demo to get yourself set up!

## Where to find data

Some of this data is proprietary to Harvard and HarvardX. Other info, like the Udacity API and Wikipedia dump, is open to the public.

Name           | URL                                             | What to name file
-------------- | ----------------------------------------------- | -------------------------------------------------------
Udacity API    | <https://www.udacity.com/public-api/v0/courses> | `udacity-api.json`
Wikipedia dump | See below                                       | `wikiclean8`
edX courses    | Proprietary                                     | `Master CourseListings - edX.csv`
DART data      | Proprietary                                     | `corpus_HarvardX_LatestCourses_based_on_2016-10-18.csv`

### How to prepare Wikipedia data

Download and unzip the `enwik8` dataset from <http://www.mattmahoney.net/dc/enwik8.zip>. Then run:

```
perl processing-scripts/wiki-clean.pl enwik8 > wikiclean8
```

This might take a minute or two to run.
