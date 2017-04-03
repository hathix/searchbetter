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
        flattened_results = self.flatten(results)

        return flattened_results
