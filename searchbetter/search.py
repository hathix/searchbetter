from whoosh.fields import *
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import *
import abc
import copy
import csv
import json
import os.path
import sys

# TODO clean up formattin


class SearchEngine(object):
  """
  An abstract class for search engines.
  A batteries-included search engine that can operate on any
  given dataset. Uses the Whoosh library to index and run searches
  on the dataset. Has built-in support for query rewriting.
  """

  # make it an abstract class
  __metaclass__ = abc.ABCMeta

  # TODO consider making more hierarchy. This is the WhooshSearchEngine,
  # which has the cool indexing capabilities. But more generally, you
  # could have a search engine that only has to support search().
  # but at that point it's just a useless interface, mostly.
  # anyway, such a search engine would let the query rewriting search engine
  # inherit from search engine too.

  def __init__(self, create, search_fields, index_path):
    """
    Creates a new search engine.

    :param create {bool}: If True, recreates an index from scratch.
        If False, loads the existing index
    :param search_fields {str[]}: An array names of fields in the index that our
        search engine will search against.
    :param index_path {str}: A relative path to a folder where the whoosh
        index should be stored.
    """
    # TODO have an auto-detect feature that will determine if the
    # index exists, and depending on that creates or loads the index
    # TODO have the `create` option become `force_create`; normally
    #   it'll intelligently auto-generate, but if you force it it'll
    #   do what you say

    self.index_path = index_path

    # both these functions return an index
    if create:
      self.index = self.create_index()
    else:
      self.index = self.load_index()

    # set up searching
    # first, query parser
    self.parser = MultifieldParser(search_fields, self.index.schema)

    # no rewriter yet
    # TODO let someone pass this in the constructor
    self.rewriter = None

  def load_index(self):
    """
    Used when the index is already created. This just loads it and
    returns it for you.
    """
    index = open_dir(self.index_path)
    return index

  def create_index(self):
    """
    Creates and returns a brand-new index. This will call
    get_empty_index() behind the scenes.
    Subclasses must implement!
    """
    raise NotImplementedError("Subclasses must implement!")

  def get_empty_index(self, path, schema):
    """
    Makes an empty index file, making the directory where it needs
    to be stored if necessary. Returns the index.

    This is called within create_index().
    TODO this breakdown is still confusing
    """
    if not os.path.exists(path):
      os.mkdir(path)
    index = create_in(path, schema)
    return index

  def flatten(self, l):
    """
    Flattens a list.
    """
    return [item for sublist in l for item in sublist]

  def set_rewriter(self, rewriter):
    """
    Sets a new query rewriter (from this_package.rewriter) as the default
    rewriter for this search engine.
    """
    self.rewriter = rewriter

  def search(self, term):
    """
    Runs a plain-English search and returns results.
    :param term {String}: a query like you'd type into Google.
    :return: a list of dicts, each of which encodes a search result.
    """
    if self.rewriter is None:
      # if there's no query rewriter in place, just search for the
      # original term
      return self._single_search(term)
    else:
      # there's a rewriter! use it
      rewritten_queries = self.rewriter.rewrite(term)
      results = [self._single_search(q) for q in rewritten_queries]

      # results are multi-level... flatten it
      flattened_results = self.flatten(results)

      # only give the unique ones
      # this works now that we use a Result object, which is hashable!
      unique_results = list(set(flattened_results))

      return unique_results

  def _single_search(self, term):
    """
    Helper function for search() that just returns search results for a
    single, non-rewritten search term.
    Returns a list of results, each of which is a Result object.
    The makeup of the results objects varies
    from search engine to search engine.
    """
    outer_results = []

    with self.index.searcher() as searcher:
      query_obj = self.parser.parse(term)
      # this variable is closed when the searcher is closed, so save this data
      # in a variable outside the with-block
      results = searcher.search(query_obj, limit=None)
      # this is still a list of Hits; convert to just a list of dicts
      result_dicts = [hit.fields() for hit in list(results)]
      # make sure we store it outside the with-block b/c scope
      outer_results = result_dicts

    # those are raw results, we need to map to a Result object
    cleaned_results = [Result(d) for d in outer_results]

    return cleaned_results


class UdacitySearchEngine(SearchEngine):
  # DATASET_PATH = secure.DATASET_PATH_BASE+'udacity-api.json'
  # INDEX_PATH = secure.INDEX_PATH_BASE+'udacity'
  SEARCH_FIELDS = ["title", "subtitle", "expected_learning",
                   "syllabus", "summary", "short_summary"]

  def __init__(self, dataset_path, index_path, create=False):
    """
    Creates a new Udacity search engine.

    :param dataset_path {string}: the path to the Udacity API JSON file.
    :param index_path {string}: the path to a folder where you'd like to
        store the search engine index. The given folder doesn't have to exist,
        but its *parent* folder does.
    :param create {bool}: If True, recreates an index from scratch.
        If False, loads the existing index
    """
    self.dataset_path = dataset_path
    super(UdacitySearchEngine, self).__init__(
        create, self.SEARCH_FIELDS, index_path)



  def create_index(self):
    """
    Creates a new index to search the Udacity dataset. You only need to
    call this once; once the index is created, you can just load it again
    instead of creating it afresh all the time.
    """

    # load data
    udacity_data = None
    with open(self.dataset_path, 'r') as file:
      udacity_data = json.load(file)

    # set up whoosh
    # schema

    # TODO: use StemmingAnalyzer here so we get the built-in benefits
    # of stemming in our search engine
    # http://whoosh.readthedocs.io/en/latest/stemming.html

    schema = Schema(
        slug=ID(stored=True),
        title=TEXT(stored=True),
        subtitle=TEXT,
        expected_learning=TEXT,
        syllabus=TEXT,
        summary=TEXT,
        short_summary=TEXT
    )

    # make an index to store this stuff in
    index = self.get_empty_index(self.index_path, schema)

    # start adding documents (i.e. the courses) to the index
    try:
      writer = index.writer()
      for course in udacity_data['courses']:
        writer.add_document(
            slug=course['slug'],
            title=course['title'],
            subtitle=course['subtitle'],
            expected_learning=course['expected_learning'],
            syllabus=course['syllabus'],
            summary=course['summary'],
            short_summary=course['short_summary'])
      writer.commit()
    except Exception as e:
      print e

    # all done for now
    return index


class HarvardXSearchEngine(SearchEngine):
  # INDEX_PATH = secure.INDEX_PATH_BASE+'harvardx'
  SEARCH_FIELDS = ["display_name", "contents"]

  def __init__(self, dataset_path, index_path, create=False):
    """
    Creates a new HarvardX search engine. Searches over the HarvardX/DART
    database of all courses and course materials used in HarvardX. This includes
    videos, quizzes, etc.

    TODO: consider renaming to DART, probz

    :param dataset_path {string}: the path to the HarvardX course catalog CSV file.
    :param index_path {string}: the path to a folder where you'd like to
        store the search engine index. The given folder doesn't have to exist,
        but its *parent* folder does.
    :param create {bool}: If True, recreates an index from scratch.
        If False, loads the existing index
    """
    super(HarvardXSearchEngine, self).__init__(
        create, self.SEARCH_FIELDS, index_path)

    self.dataset_path = dataset_path

  def create_index(self):
    """
    Creates a new index to search the dataset. You only need to
    call this once; once the index is created, you can just load it again
    instead of creating it afresh all the time.

    Returns the index object.
    """

    # load data
    # real data
    # csvfile_path = secure.DATASET_PATH_BASE+'corpus_HarvardX_LatestCourses_based_on_2016-10-18.csv'
    # test data
    # csvfile_path = 'datasets/test.csv'

    # only consider resources with this category (type of content)
    # unsure about courses (b/c they have no content) and html (b/c they often include messy CSS/JS in there)
    # TODO: add "html" support. requires stripping comments
    #       http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    #
    supported_categories = ('problem', 'video', 'course')

    # set up whoosh schema
    schema = Schema(
        course_id=ID(stored=True),
        display_name=TEXT(stored=True),
        contents=TEXT
    )

    # TODO: use StemmingAnalyzer here so we get the built-in benefits
    # of stemming in our search engine
    # http://whoosh.readthedocs.io/en/latest/stemming.html

    # make an index to store this stuff in
    index = self.get_empty_index(self.index_path, schema)

    # start adding documents (i.e. the courses) to the index

    # first, some of the fields are HUGE so we need to let the csv
    # reader handle them
    csv.field_size_limit(sys.maxsize)

    with open(self.dataset_path, 'r') as csvfile:
      reader = csv.DictReader(csvfile)

      writer = index.writer()

      try:
        for row in reader:
          # ensure the content is actually a valid type
          if row['category'] not in supported_categories:
            pass

          # write
          writer.add_document(
              course_id=row['course_id'].decode('utf8'),
              display_name=row['display_name'].decode('utf8'),
              contents=row['contents'].decode('utf8'))

        writer.commit()
      except Exception as e:
        print e
        writer.cancel()

    # all done for now
    return index


class EdXSearchEngine(SearchEngine):
  # INDEX_PATH = secure.INDEX_PATH_BASE+'edx'
  SEARCH_FIELDS = ["name"]

  def __init__(self, dataset_path, index_path, create=False):
    """
    Creates a new search engine that searches over edX courses.

    :param dataset_path {string}: the path to the edX course listings file.
    :param index_path {string}: the path to a folder where you'd like to
        store the search engine index. The given folder doesn't have to exist,
        but its *parent* folder does.
    :param create {bool}: If True, recreates an index from scratch.
        If False, loads the existing index
    """
    super(EdXSearchEngine, self).__init__(
        create, self.SEARCH_FIELDS, index_path)

    self.dataset_path = dataset_path

  def create_index(self):
    """
    Creates a new index to search the dataset. You only need to
    call this once; once the index is created, you can just load it again
    instead of creating it afresh all the time.

    Returns the index object.
    """

    # load data
    # csvfile_path = secure.DATASET_PATH_BASE+'Master CourseListings - edX.csv'

    # set up whoosh schema
    schema = Schema(
        course_id=ID(stored=True),
        name=TEXT(stored=True)
    )

    # TODO: use StemmingAnalyzer here so we get the built-in benefits
    # of stemming in our search engine
    # http://whoosh.readthedocs.io/en/latest/stemming.html

    # make an index to store this stuff in
    index = self.get_empty_index(self.index_path, schema)

    # start adding documents (i.e. the courses) to the index

    with open(self.dataset_path, 'r') as csvfile:
      reader = csv.DictReader(csvfile)

      writer = index.writer()

      try:
        for row in reader:
          # write
          writer.add_document(
              course_id=row['course_id'].decode('utf8'),
              name=row['name'].decode('utf8'))

        writer.commit()
      except Exception as e:
        print e
        writer.cancel()

    # all done for now
    return index


class PrebuiltSearchEngine(SearchEngine):
    """
    A search engine designed for when you're just given a model file and can
    use that directly without having to build anything.
    """

    def __init__(self, search_fields, index_path):
        super(PrebuiltSearchEngine, self).__init__(
            create=False, search_fields=search_fields, index_path=index_path)


    def create_index(self):
        # no need to create!!
        # TODO raise an error
        raise NotImplementedError("This search engine doesn't need to create an index! Use create = False.")
        pass


class Result(object):
    """
    Encodes a search result. Basically a wrapper around a result dict.
    """

    def __init__(self, dict_data):
        self.dict_data = dict_data


    def get_dict(self):
        """
        Get the underlying dict data
        """
        return self.dict_data


    def __repr__(self):
        """
        Stringified version of the dict.
        """
        return str(self.dict_data)

    # to enable hashing
    def __hash__(self):
        return hash(frozenset(self.dict_data.items()))


    def __eq__(self, other):
        return frozenset(self.dict_data.items()) == frozenset(other.dict_data.items())
