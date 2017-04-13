import gensim.models as models
import gensim.models.word2vec as word2vec

"""
Utilities for generating a corpus.
"""

def generate_bigram_corpus(raw_corpus):
    """
    Given a raw corpus (like the Wikipedia corpus or a custom corpus made of
    words on each line), returns a new corpus that recognizes bigrams. You can
    drop this into word2vec instead of the raw corpus.
    """
