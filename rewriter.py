from lxml import etree
import abc
import re
import requests

import gensim.models as models
import gensim.models.word2vec as word2vec



# Abstract Rewriter class
# TODO: abstract out more functionality here
class Rewriter(object):
    # make it an abstract class
    __metaclass__ = abc.ABCMeta

    def rewrite(self, term):
        """
        Subclasses must implement!
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
        return x.replace('Category:','')

    def rewrite(self, term):
        """
        Given a base term, returns a list of related terms based on the Wikipedia
        category API.
        """
        api = self.WIKI_BASE + term
        r = requests.get(api)
        tree = etree.fromstring(r.text)
        # TODO: ignore wikipedia internal categories
        # https://en.wikipedia.org/wiki/Category:Tracking_categories
        wikipedia_results = [self.clean_category(x.get('title')) for x in tree.findall('.//cl')]

        # append the original term just for completeness
        return wikipedia_results + [term]


class Word2VecRewriter(Rewriter):
    """
    A class to rewrite queries using Word2Vec trained on a corpus gathered
    from Wikipedia.
    """

    # where the model will be stored
    MODEL_PATH = 'models/word2vec/word2vec'

    def __init__(self, create=False):
        """
        Initializes the rewriter. If create is True, this generates a new Word2Vec
        model (which takes a really long time to build.) If false, this loads
        an existing model we already saved.
        """

        if create:
            # generate a new Word2Vec model... takes a while!
            corpus = word2vec.Text8Corpus('datasets/enwik8')
            self.model = word2vec.Word2Vec(corpus, workers=8)
            self.model.save(self.MODEL_PATH)
        else:
            self.model = word2vec.Word2Vec.load(self.MODEL_PATH)


    def clean(self, string):
        """
        Cleans up a string of text you get from wikipedia, which is often formatted like
        `*[[Games`.
        """
        # remove [[, ]], *
        # TODO: also remove commas and punctuation
        # (though apostrophes and dashes can stay, i guess)
        return re.sub(r"(\[\[|\]\]|\*)", "", string)


    def rewrite(self, term):
        # try using the model to rewrite the term
        cleaned_results = []
        try:
            # most_similar returns an array of tuples... extract just the name, which is index 0
            # we also have to clean the text
            raw_results = self.model.most_similar(positive=[term], topn=10)
            cleaned_results = [self.clean(r[0]) for r in raw_results]
        except KeyError as k:
            # the word wasn't found in the model... must be too niche.
            # just return nothing then.
            pass

        # finally, tack on the original term to the results for completeness
        return cleaned_results + [term.decode("utf8")]


class RewritingSearchEngine(object):
    """
    A query rewriting-enabled search engine. Wraps a search engine and a rewriter
    so you can, hopefully, get better results. Note that this doesn't inherit
    the "SearchEngine" class because it works so differently.
    """
    # TODO: rethink inheritence structures

    def __init__(self, rewriter, search_engine):
        self.rewriter = rewriter
        self.search_engine = search_engine


    def flatten(self, l):
        """
        Flattens a list.
        """
        return [item for sublist in l for item in sublist]


    def search(self, term):
        """
        Using the given search term (or query), rewrites it according to the
        rewriter and then passes that through the search engine.
        """
        rewritten_queries = self.rewriter.rewrite(term)

        results = [self.search_engine.search(q) for q in rewritten_queries]

        # results are multi-level... flatten it
        # TODO: use set() to remove duplicates
        flattened_results = self.flatten(results)

        return flattened_results
