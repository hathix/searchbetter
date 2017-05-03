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
