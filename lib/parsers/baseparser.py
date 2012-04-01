
"""Module with the base class for online reader parsers.
"""

from HTMLParser import HTMLParser
import urllib2
import logging

logger = logging.getLogger(__name__)


class BaseParser(HTMLParser):
    """Base class for online readers.
    It defines the maximum number of connections allowed to the website,
    and has a parse method that downloads and parses a url using HTMLParser"""
    MAX_CONNECTIONS = 10

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.title = None
        self.url = url
        self._html = urllib2.urlopen(url)

    def parse(self):
        """Download the object's url and start parsing it using HTMLParser."""
        logger.debug('Started Parsing of %s', self.url)
        self.feed(self._html.read())
        logger.debug('Finished Parsing of %s', self.url)
