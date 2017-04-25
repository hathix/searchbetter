# SearchBetter: query rewriting for search engines on small corpuses

## Demo

[Try out the interactive demo](https://github.com/hathix/searchbetter/blob/master/notebooks/searchbetter-demo.ipynb)!

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
