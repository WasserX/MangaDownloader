
"""Module with several utils to download, parse and compress
the mangas.
"""

import zipfile
import urllib2
import os
import shutil
import glob
import logging
from threading import Thread, Semaphore

logger = logging.getLogger(__name__)


class ImageSaver(Thread):
    """Object to save an image url to a destination.
    A semaphore can be released when finished"""
    def __init__(self, path, url, semaphore=None):
        Thread.__init__(self)
        self.url = url
        self.path = path
        self._semaphore = semaphore

    def run(self):
        logger.debug('Loading Image %s', self.url)
        img = urllib2.urlopen(self.url).read()
        logger.debug('Loaded Image %s', self.url)
        image = open(self.path, 'w')
        image.write(img)
        if self._semaphore:
            self._semaphore.release()


class MangaCompressor(Thread):
    """Compressor of Manga folders. Can use several threads to compress.
    Path is the path to the manga and erase_dirs defines if after compressing
    the folders should be deleted.

    The method compress_manga receives the maximum number of threads to use
    and will compress the manga whose path was given when the object was
    created.
    """
    def __init__(self, path, title, erase_dirs=False):
        Thread.__init__(self)
        self.title = title
        self.erase = erase_dirs
        self.path = path
        self._semaphore = None

    def _compress_chapter(self):
        """Compress a directory creating a '<manga title> <subdir name>.cbz'
        it also deletes the files inside the directory if it was specified."""
        path = os.path.split(self.path)[0]
        name = self.title + ' ' + os.path.basename(self.path) + '.cbz'
        path = os.path.join(path, name)
        ch_file = zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED)

        for img in glob.glob(os.path.join(self.path, '*')):
            ch_file.write(img)
        ch_file.close()

        if self.erase:
            shutil.rmtree(self.path)

        if self._semaphore:
            self._semaphore.release()

    def compress_manga(self, max_threads=1):
        """Compress a whole directory creating files in the format
        '<manga title> <subdir name>.cbz'"""
        threads = list()
        sem = Semaphore(max_threads)

        for chapter in os.listdir(self.path):
            ch_path = os.path.join(self.path, chapter)
            if os.path.isdir(ch_path):
                sem.acquire()
                logger.info('Compressing Chapter: %s', chapter)
                compressor = MangaCompressor(ch_path, self.title, self.erase)
                compressor._semaphore = sem
                threads.append(compressor)
                compressor.start()
        map(lambda thread: thread.join(), threads)

    def run(self):
        self._compress_chapter()
