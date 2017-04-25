from lxml import etree
import abc
import re
import requests

import gensim.models as models
import gensim.models.phrases as phrases
import gensim.models.word2vec as word2vec


# Abstract Rewriter class
# TODO: abstract out more functionality here
class Rewriter(object):
  # make it an abstract class
  __metaclass__ = abc.ABCMeta

  def rewrite(self, term):
    """
    Rewrites a term to a list of new terms to search with.
    """
    raise NotImplementedError("Subclasses must implement!")


class ControlRewriter(Rewriter):
  """
  A rewriter that's basically a no-op. Just returns the term you give it.
  """

  def rewrite(self, term):
    return [term]


class WikipediaRewriter(Rewriter):
  """
  A class to rewrite queries using Wikipedia's category api.
  """

  WIKI_BASE = 'https://en.wikipedia.org/w/api.php?format=xml&action=query&prop=categories&titles='

  def clean_category(self, x):
    return x.replace('Category:', '')

  def rewrite(self, term):
    """
    Given a base term, returns a list of related terms based on the Wikipedia
    category API.
    """
    api = self.WIKI_BASE + term
    r = requests.get(api)
    tree = etree.fromstring(r.text)

    # TODO join this and the below
    wikipedia_results = [self.clean_category(
        x.get('title')) for x in tree.findall('.//cl')]

    # Words that identify a need to drop the category
    dropwords = ['articles', 'wikipedia', 'accuracy', 'articles', 'statements',
                 'magic', 'pages', 'authors', 'editors', 'appearances', 'redirects', 'cs1']
    dropwords.append(term)
    wikipedia_results = [w.split('Category:')[-1].lower()
                         for w in wikipedia_results if not any(d in w.lower() for d in dropwords)]

    # append the original term just for completeness
    raw_results = wikipedia_results + [term]
    # convert to unicode for consistency w/ other rewriters
    # TODO this doesn't work
    return raw_results
    # return [unicode(rr) for rr in raw_results]


class Word2VecRewriter(Rewriter):
  """
  A class to rewrite queries using Word2Vec trained on a user-provided
  corpus.
  """

  # TODO use kwargs or something to make creating this less insane
  # http://stackoverflow.com/questions/1098549/proper-way-to-use-kwargs-in-python#1098556
  def __init__(self, model_path, create=False, corpus=None, bigrams=True):
    """
    Initializes the rewriter, given a particular word2vec corpus.
    A good example corpus is the Text8Corpus or the Brown corpus.
    You only need the corpus if you are recreating the model from scratch.

    If create is True, this generates a new Word2Vec
    model (which takes a really long time to build.) If False, this loads
    an existing model we already saved.

    :param model_path {string}: where to store the model files. This file
        needn't exist, but its parent folder should.
    :param create {bool}: True to create a new Word2Vec model, False to
        use the one stored at `model_path`.
    :param corpus {Iterable}: only needed if `create=True`. Defines a corpus
        for Word2Vec to learn from.
    :param bigrams {bool}: only needed if `create=True`. If True, takes some
        more time to build a model that supports bigrams (e.g. `new_york`).
        Otherwise, it'll only support one-word searches. `bigram=True` makes
        this slower but more complete.
    """

    self.model_path = model_path

    # TODO: add logic around defaulting to creating or not

    if create:
      # generate a new Word2Vec model... takes a while!
      # TODO optimize parameters

      transformed_corpus = None
      if bigrams:
        # TODO save the phraser somewhere... but that requires
        # even more arguments.
        # the Phrases class lets you generate bigrams, but the
        # Phraser class is a more compact version of the same
        # TODO making the phrases takes forever, making the phraser
        # takes forever, turning it into a list takes forever... this
        # is really annoying. is there any way to speed it up?
        bigram_generator = phrases.Phraser(phrases.Phrases(corpus))
        # weird bug where the bigram generator won't work unless
        # it's turned into a list first. if you try to do it straight,
        # it'll give you total gibberish. FIXME
        bigram_corpus = list(bigram_generator[corpus])
        transformed_corpus = bigram_corpus
      else:
        # no bigrams, same old corpus
        transformed_corpus = corpus

      self.model = word2vec.Word2Vec(transformed_corpus, workers=8)
      self.model.save(self.model_path)
    else:
      self.model = word2vec.Word2Vec.load(self.model_path)

  def rewrite(self, term):
    # try using the model to rewrite the term
    results = []
    try:
      # preprocess the term so it's more palatable to word2vec
      encoded_term = self.encode_term(term)
      # most_similar returns an array of tuples, each representing a term/phrase
      # that is close to the original
      # TODO consider choosing fewer results! or have a higher bar on how
      # related they need to be
      raw_results = self.model.similar_by_word(encoded_term, topn=10)
      # extract just the name, which is index 0
      # and decode all the results we get from word2vec
      results = [self.decode_term(r[0]) for r in raw_results]
    except KeyError as k:
      # the word wasn't found in the model... must be too niche.
      # no results then
      results = []

    # finally, tack on the original term to the results for completeness
    return results + [term.decode("utf8")]

  def encode_term(self, term):
    """
    Converts a search term like `Hadrian's Wall` to `hadrians_wall`, which
    plays better with word2vec.
    """
    # remove anything that isn't alphanumeric or space
    alphanum_pattern = re.compile(r'[^\w\d\s]')
    cleaned = alphanum_pattern.sub('', term)
    # sub out spaces for underscores
    space_pattern = re.compile(' ')
    cleaned = space_pattern.sub('_', cleaned)
    # finally lowercase it all
    # TODO replace numbers with words (mp3 => mp_three)
    return cleaned.lower()

  def decode_term(self, encoded):
    """
    Converts an encoded search term into something more human readable,
    like `hadrians_wall` to `hadrians wall`.
    """
    # not much we can do besides replace underscores with spaces
    underscore_pattern = re.compile('_')
    return underscore_pattern.sub(' ', encoded)
