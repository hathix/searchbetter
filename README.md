# Query Rewriter

## Where to find data

Name           | URL                                             | Where to put file
-------------- | ----------------------------------------------- | -------------------------------------------------------
Udacity API    | <https://www.udacity.com/public-api/v0/courses> | `datasets/udacity-api.json`
Wikipedia dump | See below                                       | `datasets/wikiclean9`
edX courses    | Proprietary                                     | `datasets/Master CourseListings - edX.csv`
DART data      | Proprietary                                     | `corpus_HarvardX_LatestCourses_based_on_2016-10-18.csv`

### How to prepare Wikipedia data

Download and unzip the `enwik9` dataset from <http://www.mattmahoney.net/dc/enwik9.zip>. Then run:

```
perl processing-scripts/wiki-clean.pl enwik9 > wikclean9
```

This might take a minute or two to run.

And ensure that the new `wikiclean9` file goes to a `datasets` folder.
