
"""Parser for the website mangareader.net.

It can parse whole mangas or a chapter. To parse a chapter the url passed
must be that of a chapter's page.
"""

import logging
from baseparser import BaseParser
from threading import Thread

logger = logging.getLogger(__name__)


class MangaReader(BaseParser):
    """Complete parser of MangaReader, can parse chapter or whole mangas."""
    BASE_URL = 'http://www.mangareader.net'

    def __init__(self, url):
        BaseParser.__init__(self, url)
        self._parsing_chapters = False
        self._parsing_metadata = False
        self._chapters = list()

    def handle_starttag(self, tag, attrs):
        if tag == 'table' and ('id', 'listing') in attrs:
            self._parsing_chapters = True
        elif tag == 'h2' and ('class', 'aname') in attrs:
            self._parsing_metadata = True
        elif tag == 'a' and self._parsing_chapters:
            chapter = MangaReader.BASE_URL
            chapter += [v for k, v in attrs if k == 'href'][0]
            logger.debug('Found Chapter URL: %s', chapter)
            self._chapters.append(chapter)

    def handle_data(self, data):
        if self._parsing_metadata:
            self.title = data
            logger.debug('Found Title: %s', self.title)
            self._parsing_metadata = False

    def handle_endtag(self, tag):
        if tag == 'table' and self._parsing_chapters:
            logger.debug('Finished Parsing Chapter\'s URL')
            for chapter in self._chapters:
                self.handle_chapter(chapter)
            self._parsing_chapters = False

        elif tag == 'html':
            if not self.imagesUrl:
                logger.debug('URL was not that of a manga, trying as a Chapter')
                self.title = self.handle_chapter(self.url).title

    def handle_chapter(self, chapter):
        """Parse a chapter using ChapterParser."""
        logger.info('Parsing Chapter: %s', chapter)
        parser = ChapterParser(chapter).parse()
        self.imagesUrl.append((parser.chapter, parser.imagesUrl))
        return parser


class ChapterParser(BaseParser):
    """Parses a chapter of mangareader."""
    def __init__(self, url):
        BaseParser.__init__(self, url)
        self.pages = list()
        self.chapter = None
        self._parsing_pages = False
        self._parsing_metadata = False

    def handle_starttag(self, tag, attrs):
        if tag == 'select' and ('id', 'pageMenu') in attrs:
            self._parsing_pages = True
        elif tag == 'h1':
            self._parsing_metadata = True
        elif tag == 'option' and self._parsing_pages:
            self.pages.append([v for k, v in attrs if k == 'value'][0])

    def handle_data(self, data):
        if self._parsing_metadata:
            self.title = data.rstrip('1234567890').rstrip()
            self.chapter = data.split().pop()
            logger.debug('Found Title: %s', self.title)
            logger.debug('Found Chapter Number: %s', self.chapter)
            self._parsing_metadata = False

    def handle_endtag(self, tag):
        if tag == 'div' and self._parsing_pages:
            threads = list()
            for page, url in enumerate(self.pages, start=1):
                url = MangaReader.BASE_URL + url
                parser = PageParser(url, self.imagesUrl, page)
                threads.append(parser)
                parser.start()
            map(lambda thread: thread.join(), threads)
            self.imagesUrl.sort()
            self._parsing_pages = False


class PageParser(BaseParser, Thread):
    """Extracts the image url from a chapters page."""
    def __init__(self, url, image_list=None, page=None):
        BaseParser.__init__(self, url)
        Thread.__init__(self)
        self._image_list = image_list
        self._page = page
        self._image_url = None

    def run(self):
        self.parse()
        self._image_list.append((self._page, self._image_url))

    def handle_starttag(self, tag, attrs):
        if tag == 'img' and ('id', 'img') in attrs:
            self._image_url = [v for k, v in attrs if k == 'src'][0]
            logger.debug('Found Image URL: %s', self._image_url)
