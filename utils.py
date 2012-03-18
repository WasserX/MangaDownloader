import zipfile
import os
import shutil
import glob
import sys
import logging
from threading import Thread, Semaphore

logger = logging.getLogger(__name__)


class MangaCompressor(Thread):
    """
    Compresses content stored in the subdirectory <mangaTitle>
    All the directories inside will be compress generating files
    in the form <mangaTitle> <directory_name>.cbz

    The subdirectories will be erased if specified
    """
    THREADS = 4

    def __init__(self, title, path, eraseDirectories=False):
        Thread.__init__(self)
        self.title = title
        self.mangaRoot = os.path.join(path, title)
        self.root = path
        self.eraseDirectories = eraseDirectories

    """
    Compress a single subdirectory of the root directory, if the hierarchy
    is well formatted, a <subdirectory> corresponds to a chapter number
    """
    def compressChapter(self, chapter=None):
        self._chapter = chapter if chapter else self._chapter
        logger.info('Compressing Chapter: %s', self._chapter)
        chapterFile = zipfile.ZipFile(os.path.join(self.mangaRoot, self.title + ' ' + self._chapter + '.cbz'), mode='w',
                                  compression=zipfile.ZIP_DEFLATED)
        for img in glob.glob(os.path.join(self.mangaRoot, self._chapter, '*')):
            chapterFile.write(img)
        chapterFile.close()

        if self.eraseDirectories:
            shutil.rmtree(os.path.join(self.mangaRoot, self._chapter))

    """
    Compress a whole directory creating <N> compressed files, being <N> the
    number of subdirectories. In general, the directory's name is the same
    as the manga title.
    """
    def compressManga(self):
        threads = list()
        semChapters = Semaphore(MangaCompressor.THREADS)

        def runSingleCompressor(name):
            semChapters.acquire()
            singleCompressor = MangaCompressor(self.title, self.root, self.eraseDirectories)
            singleCompressor._chapter = name
            threads.append(singleCompressor)
            singleCompressor.start()
            semChapters.release()

        map(runSingleCompressor, [name for name in os.listdir(self.mangaRoot)
                                   if os.path.isdir(os.path.join(self.mangaRoot, name))])
        map(lambda thread: thread.join(), threads)

    def run(self):
        self.compressChapter()
