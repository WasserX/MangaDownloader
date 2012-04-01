
"""Parser for the website mangareader.net.

It can parse whole mangas or a chapter. To parse a chapter the url passed
must be that of a chapter's page.
"""

import logging
from baseparser import BaseParser
from threading import Thread, Semaphore

logger = logging.getLogger(__name__)


class MangaReader(BaseParser):
    """Complete parser of MangaReader, can parse chapter or whole mangas."""
    BASE_URL = 'http://www.mangareader.net'

    def __init__(self, url):
        BaseParser.__init__(self, url)
        self.parsed_manga = list()
        self._parsing_chapters = False
        self._parsing_metadata = False
        self._chapters = list()

    def parse(self):
        BaseParser.parse(self)
        return self.parsed_manga

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
            if not self.parsed_manga:
                logger.debug('URL was not that of a manga, trying as a Chapter')
                self.title = self.handle_chapter(self.url).title

    def handle_chapter(self, chapter):
        """Parse a chapter using ChapterParser."""
        logger.info('Parsing Chapter: %s', chapter)
        parser = ChapterParser(chapter)
        self.parsed_manga.append(parser.parse())
        #If url wasn't that of a manga, return the parser to retrieve the title
        return parser


class ChapterParser(BaseParser):
    """Parses a chapter of mangareader."""
    def __init__(self, url):
        BaseParser.__init__(self, url)
        self.pages = list()
        self.chapter = None
        self.parsed_chapter = list()
        self._parsing_pages = False
        self._parsing_metadata = False

    def parse(self):
        BaseParser.parse(self)
        return (self.chapter, self.parsed_chapter)

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
            sem = Semaphore(BaseParser.MAX_CONNECTIONS)
            for url in self.pages:
                sem.acquire()
                parser = PageParser(MangaReader.BASE_URL + url, sem)
                threads.append(parser)
                parser.start()
            map(lambda thread: thread.join(), threads)
            self.parsed_chapter = [thread.image_url for thread in threads]
            self._parsing_pages = False


class PageParser(BaseParser, Thread):
    """Extracts the image url. A semaphore can limit operations"""
    def __init__(self, url, semaphore=None):
        BaseParser.__init__(self, url)
        Thread.__init__(self)
        self.image_url = None
        self._semaphore = semaphore

    def run(self):
        self.parse()
        if self._semaphore:
            self._semaphore.release()

    def handle_starttag(self, tag, attrs):
        if tag == 'img' and ('id', 'img') in attrs:
            self.image_url = [v for k, v in attrs if k == 'src'][0]
            logger.debug('Found Image URL: %s', self.image_url)
