import re

def flatten(l):
    """
    Flattens a list.
    """
    return [item for sublist in l for item in sublist]


def unique_words_in_string(string):
    """
    Counts the number of unique words in a string.
    """

    # find all words... lowercase the string first
    words = re.findall(r"\b[a-zA-Z_']+\b", string.lower())

    # unique words
    unique_words = set(words)

    return len(unique_words)


def unique_words_of_field(engine, field_name):
    """
    Approximates the set of unique words stored in a single field (column)
    of a SearchEngine.
    """
    # get all unique elements in text from the search engine
    entries = engine.index.searcher().lexicon(field_name)

    # only include words
    texts = [w for w in entries if re.match(r"\b[a-zA-Z_']+\b", w) is not None]

    # lowercase and unique it all
    lowers = [w.lower() for w in texts]

    return set(lowers)
