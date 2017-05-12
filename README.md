# SearchBetter: query rewriting for search engines on small corpuses

> by Neel Mehta, Harvard University

SearchBetter lets you make powerful, fast, and drop-in search engines for any dataset, no matter how small or how large. It also offers built-in query rewriting, which uses NLP to help your search engines find semantically-related content to the user's search term.

For instance, a search for `machine learning` might only return results for items that contain the words "machine learning". But with query rewriting, you would get results not only for `machine learning` but also, say, `artificial intelligence` and `neural networks`.

SearchBetter lets you power up your search engines with minimal effort. It's especially useful if you have a small dataset to search on, or if you don't have the time or data to make fancy bespoke query rewriting algorithms.

## Getting started

To drop this module into your app:

```
pip install searchbetter
```

For more advanced analysis and research purposes, use the [interactive demo]((https://github.com/hathix/searchbetter/blob/master/notebooks/searchbetter-demo.ipynb)) to get yourself set up!

## Usage

[Try out the interactive demo](https://github.com/hathix/searchbetter/blob/master/notebooks/searchbetter-demo.ipynb)!

For a truly quick-and-dirty dive into SearchBetter (no setup required), use:

```py
from searchbetter import rewriter

query_rewriter = rewriter.WikipediaRewriter()
query_rewriter.rewrite('biochemistry')
```



## Documentation

Documentation is available online at <http://searchbetter.readthedocs.io/>.

To build the docs yourself using Sphinx:

```
cd docs
make html
open _build/html/index.html
```



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



## Context

SearchBetter was designed as part of a research project by [Neel Mehta](https://github.com/hathix), [Daniel Seaton](https://github.com/dseaton), and [Dustin Tingley](http://scholar.harvard.edu/dtingley/home) for Harvard's CS 91r, a research for credit course.

It was originally designed for [Harvard DART](https://dart.harvard.edu/), a tool that helps educators reuse HarvardX assets such as videos and exercises in their online or offline courses. SearchBetter is especially useful for MOOCs, which often have small corpuses and have to deal with many uncommon queries (students will search for the most unfamiliar terms, after all.) Still, SearchBetter has been made general-purpose enough that it can be used with any corpus or any search engine.
