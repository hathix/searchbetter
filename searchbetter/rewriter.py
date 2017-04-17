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
        return x.replace('Category:','')

    def rewrite(self, term):
        """
        Given a base term, returns a list of related terms based on the Wikipedia
        category API.
        """
        api = self.WIKI_BASE + term
        r = requests.get(api)
        tree = etree.fromstring(r.text)

        # TODO join this an dthe below
        wikipedia_results = [self.clean_category(x.get('title')) for x in tree.findall('.//cl')]

        # Words that identify a need to drop the category
        dropwords = ['articles','wikipedia','accuracy','articles','statements','magic','pages','authors','editors','appearances','redirects','cs1']
        dropwords.append(term)
        wikipedia_results = [w.split('Category:')[-1].lower() for w in wikipedia_results if not any(d in w.lower() for d in dropwords)]

        # append the original term just for completeness
        print wikipedia_results
        print ' '.join(wikipedia_results + [term])
        return wikipedia_results + [term]


class Word2VecRewriter(Rewriter):
    """
    A class to rewrite queries using Word2Vec trained on a user-provided
    corpus.
    """

    # where the model will be stored
    # MODEL_PATH = secure.MODEL_PATH_BASE+'word2vec/word2vec'

    def __init__(self, model_path, corpus=None, create=False):
        """
        Initializes the rewriter, given a particular word2vec corpus.
        A good example corpus is the Text8Corpus or the Brown corpus.
        You only need the corpus if you aren't recreating this from scratch.

        If create is True, this generates a new Word2Vec
        model (which takes a really long time to build.) If False, this loads
        an existing model we already saved.

        :param model_path {string}: where to store the model files. This file
            needn't exist, but its parent folder should.
        """

        self.model_path = model_path

        # TODO: add logic around defaulting to creating or not

        if create:
            # generate a new Word2Vec model... takes a while!
            # TODO optimize parameters
            self.model = word2vec.Word2Vec(corpus, workers=8)
            self.model.save(self.model_path)
        else:
            self.model = word2vec.Word2Vec.load(self.model_path)

    def rewrite(self, term):
        # try using the model to rewrite the term
        cleaned_results = []
        try:
            # most_similar returns an array of tuples
            raw_results = self.model.similar_by_word(term, topn=10)
            # extract just the name, which is index 0
            cleaned_results = [r[0] for r in raw_results]
        except KeyError as k:
            # the word wasn't found in the model... must be too niche.
            # just return nothing then.
            pass

        # finally, tack on the original term to the results for completeness
        return cleaned_results + [term.decode("utf8")]
