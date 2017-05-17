from distutils.core import setup

version = '0.4'

setup(
  name = 'searchbetter',
  packages = ['searchbetter'], # this must be the same as the name above
  version = version,
  description = 'Query rewriting for search engines on small corpuses',
  author = 'Neel Mehta',
  author_email = 'neelmehta96@gmail.com',
  url = 'https://github.com/hathix/searchbetter', # use the URL to the github repo
  download_url = 'https://github.com/hathix/searchbetter/archive/{}.tar.gz'.format(version),
  keywords = ['search engine', 'query rewriting', 'search', 'word2vec', 'nlp'], # arbitrary keywords
  classifiers = [],
)
