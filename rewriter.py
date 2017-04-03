import requests
from lxml import etree
import abc



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
        return [self.clean_category(x.get('title')) for x in tree.findall('.//cl')]




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


    def search(self, term):
        pass
