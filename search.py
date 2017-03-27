import json
import os.path
from whoosh.index import create_in, open_dir
from whoosh.fields import *


class UdacitySearchEngine:
    DATASET_PATH = 'datasets/udacity-api.json'
    INDEX_PATH = 'whoosh_indices/udacity'

    def __init__(self, create=False):
        """
        Creates a new Udacity search engine.

        :param create {bool}: If True, recreates an index from scratch.
            If False, loads the existing index
        """
        # TODO have an auto-detect feature that will determine if the
        # index exists, and depending on that creates or loads the index

        # TODO clean up the object orientation here

        # both these functions return an index
        if create:
            self.index = self.create_index()
        else:
            self.index = self.load_index()


    def create_index(self):
        """
        Creates a new index to search the Udacity dataset. You only need to
        call this once; once the index is created, you can just load it again
        instead of creating it afresh all the time.
        """

        # load data
        udacity_data = None
        with open(self.DATASET_PATH, 'r') as file:
            udacity_data = json.load(file)

        # set up whoosh
        # schema
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
        if not os.path.exists(self.INDEX_PATH):
            os.mkdir(self.INDEX_PATH)
        index = create_in(self.INDEX_PATH, schema)

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


    def load_index(self):
        """
        Used when the index is already created. This just loads it and
        returns it for you.
        """

        index = open_dir(self.INDEX_PATH)
        return index
