import urllib2
import sys
import os
import logging
from BaseParser import BaseParser
from threading import Thread

logger = logging.getLogger(__name__)


class MangaReader(BaseParser):
    BASE_URL = 'http://www.mangareader.net'

    def __init__(self, url):
        BaseParser.__init__(self, url)
        self._parsingChapters = False
        self._parsingName = False
        self._chapters = list()

    def handle_starttag(self, tag, attrs):
        if tag == 'table' and ('id', 'listing') in attrs:
            self._parsingChapters = True
        elif tag == 'h2' and ('class', 'aname') in attrs:
            self._parsingName = True
        elif tag == 'a' and self._parsingChapters:
            chapter = MangaReader.BASE_URL + [value for attr, value in attrs if attr == 'href'][0]
            logger.debug('Found Chapter URL: %s', chapter)
            self._chapters.append(chapter)

    def handle_data(self, data):
        if self._parsingName:
            self.title = data
            logger.debug('Found Title: %s', self.title)
            self._parsingName = False

    def handle_endtag(self, tag):
        if tag == 'table' and self._parsingChapters:
            logger.debug('Finished Parsing Chapter\'s URL')
            for chapter in self._chapters:
                self.handle_chapter(chapter)
            self._parsingChapters = False

        elif tag == 'html':
            if not self.imagesUrl:
                logger.debug('The given URL was not a Manga url, trying as a Chapter URL')
                self.title = self.handle_chapter(self.url).title

    def handle_chapter(self, chapter):
        logger.info('Parsing Chapter: %s', chapter)
        parser = ChapterParser(chapter).parse()
        self.imagesUrl.append((parser.chapter, parser.imagesUrl))
        return parser


class ChapterParser(BaseParser):
    def __init__(self, url):
        BaseParser.__init__(self, url)
        self.pages = list()
        self.chapter = None
        self._parsingPages = False
        self._parsingInfo = False

    def handle_starttag(self, tag, attrs):
        if tag == 'select' and ('id', 'pageMenu') in attrs:
            self._parsingPages = True
        elif tag == 'h1':
            self._parsingInfo = True
        elif tag == 'option' and self._parsingPages:
            self.pages.append([value for attr, value in attrs if attr == 'value'][0])

    def handle_data(self, data):
        if self._parsingInfo:
            self.title = data.rstrip('1234567890').rstrip()
            self.chapter = data.split().pop()
            logger.debug('Found Title: %s', self.title)
            logger.debug('Found Chapter Number: %s', self.chapter)
            self._parsingInfo = False

    def handle_endtag(self, tag):
        if tag == 'div' and self._parsingPages:
            threads = list()
            for pageNumber, page in enumerate(self.pages, start=1):
                parser = PageParser(MangaReader.BASE_URL + page, self.imagesUrl, pageNumber)
                threads.append(parser)
                parser.start()
            map(lambda thread: thread.join(), threads)
            self.imagesUrl.sort()
            self._parsingPages = False


class PageParser(BaseParser, Thread):
    def __init__(self, url, imageList=None, pageNumber=None):
        BaseParser.__init__(self, url)
        Thread.__init__(self)
        self._imageList = imageList
        self._pageNumber = pageNumber
        self._imageUrl = None

    def run(self):
        self.parse()
        self._imageList.append((self._pageNumber, self._imageUrl))

    def handle_starttag(self, tag, attrs):
        if tag == 'img' and ('id', 'img') in attrs:
            self._imageUrl = [value for attr, value in attrs if attr == 'src'][0]
            logger.debug('Found Image URL: %s', self._imageUrl)
