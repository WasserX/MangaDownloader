import urllib2
import sys
import os
import logging
import string
from BaseParser import BaseParser
from threading import Thread, Semaphore

logger = logging.getLogger(__name__)


class MangaHere(BaseParser):
    BASE_URL = 'http://www.mangahere.com'

    def __init__(self, url):
        BaseParser.__init__(self, url)
        self._parsingChapterConds = 0
        self._parsingName = False
        self._chapters = list()

    def handle_starttag(self, tag, attrs):
        if tag == 'h1' and ('class', 'title') in attrs:
            self._parsingName = True
        if tag == 'div' and ('class', 'detail_list') in attrs:
            self._parsingChapterConds = 1
        elif tag == 'ul' and self._parsingChapterConds == 1:
            self._parsingChapterConds = 2
        elif tag == 'a' and self._parsingChapterConds == 2:
            chapter = [value for attr, value in attrs if attr == 'href'][0]
            logger.debug('Found Chapter URL: %s', chapter)
            self._chapters.append(chapter)

    def handle_data(self, data):
        if self._parsingName:
            self.title = string.capwords(data)
            logger.debug('Found Title: %s', self.title)
            self._parsingName = False

    def handle_endtag(self, tag):
        if tag == 'ul' and self._parsingChapterConds == 2:
            logger.debug('Finished Parsing Chapter\'s URL')
            for chapter in self._chapters:
                self.handle_chapter(chapter)
            self._parsingChapterConds = 0

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
        self._firstTime = True
        self._parsingInfo = False

    def handle_starttag(self, tag, attrs):
        if tag == 'select' and self._firstTime and ('class', 'wid60') in attrs:
            self._parsingPages = True
        elif tag == 'h1':
            self._parsingInfo = True
        elif tag == 'option' and self._parsingPages:
            self.pages.append([value for attr, value in attrs if attr == 'value'][0])

    def handle_data(self, data):
        if self._parsingInfo:
            self.title = data.rstrip('1234567890').strip()
            self.chapter = data.split().pop()
            logger.debug('Found Title: %s', self.title)
            logger.debug('Found Chapter Number: %s', self.chapter)
            self._parsingInfo = False

    def handle_endtag(self, tag):
        if tag == 'select' and self._parsingPages:
            semPages = Semaphore(BaseParser.THREADS)
            threads = list()
            for pageNumber, page in enumerate(self.pages, start=1):
                parser = PageParser(page, self.imagesUrl, pageNumber)
                threads.append(parser)
                semPages.acquire()
                parser.start()
                semPages.release()
            map(lambda thread: thread.join(), threads)
            self.imagesUrl.sort()
            self._parsingPages = False
            self._firstTime = False


class PageParser(BaseParser, Thread):
    def __init__(self, url, imageList=None, pageNumber=None):
        BaseParser.__init__(self, url)
        Thread.__init__(self)
        self._imageList = imageList
        self._pageNumber = pageNumber
        self._imageUrl = None
        self._parsingImage = False

    def run(self):
        self.parse()
        self._imageList.append((self._pageNumber, self._imageUrl))

    def handle_starttag(self, tag, attrs):
        if tag == 'section' and ('id', 'viewer') in attrs:
            self._parsingImage = True
        elif tag == 'img' and self._parsingImage:
            self._imageUrl = [value for attr, value in attrs if attr == 'src'][0]
            logger.debug('Found Image URL: %s', self._imageUrl)
            self._parsingImage = False
