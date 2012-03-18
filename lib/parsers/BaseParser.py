from HTMLParser import HTMLParser
import urllib2
import logging

logger = logging.getLogger(__name__)


class BaseParser(HTMLParser):
    """
    All online manga readers should inherit this class,
    this is used as an interface with all the methods that should
    be implemented
    url is the url to the manga desired to download
    """
    THREADS = 5

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.imagesUrl = list()
        self.title = None
        self.url = url
        self._html = urllib2.urlopen(url)

    def parse(self):
        logger.debug('Started Parsing of %s', self.url)
        self.feed(self._html.read())
        logger.debug('Finished Parsing of %s', self.url)
        return self
