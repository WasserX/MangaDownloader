#!/usr/bin/env python

"""Download mangas from online readers. Supports for compression of the
mangas in separate chapters.

The compression process will always use MAX_THREADS.
"""

import sys
import argparse
import os
import re
import logging
from threading import Semaphore

from lib import utils
from lib.parsers.baseparser import BaseParser
from lib.parsers.mangareader import MangaReader
from lib.parsers.mangahere import MangaHere

MAX_THREADS = 4


def parse_args():
    """Parse arguments, set the correct logging level and return the args."""
    parser = argparse.ArgumentParser(description='''Download mangas or chapters
                                     from online manga readers.''')
    parser.add_argument('url', type=str, help='Url of the manga to download.')
    parser.add_argument('-c', default=False, action="store_true",
                         dest='compress', help='Compress chapters to cbz?')
    parser.add_argument('-v', default=False, action="store_true",
                        dest='verbose', help='Activate verbose mode')
    parser.add_argument('-d', type=str, default=sys.path[0], dest='dest',
                        help='Destination where manga folder will be created.')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    return args


def recover_images(parser, destination):
    """Parse images and save them to <manga>/<chapter>/<image>."""
    urls = parser.parse()
    manga_path = os.path.join(destination, parser.title)
    ch_digits = len(str(len(urls)))
    for chapter, pages in urls:
        #Normalize chapter digits
        chapter = "0" * (ch_digits - len(str(chapter))) + str(chapter)
        chapter_path = os.path.join(manga_path, chapter)
        if not os.path.exists(chapter_path):
            os.makedirs(chapter_path)
        savers = list()
        logging.info('Saving Chapter %s to %s', chapter, chapter_path)

        pg_digits = len(str(len(pages)))
        sem = Semaphore(BaseParser.MAX_CONNECTIONS)
        for page, url in enumerate(pages, start=1):
            sem.acquire()
            #Normalize page digits
            page = "0" * (pg_digits - len(str(page))) + str(page)
            path = os.path.join(chapter_path, str(page) + '.jpg')
            saver = utils.ImageSaver(path, url, sem)
            savers.append(saver)
            saver.start()
        map(lambda thread: thread.join(), savers)


def main():
    """Download the manga in args and compress it if desired."""
    args = parse_args()

    if re.search('mangareader\.net', args.url):
        parser = MangaReader(args.url)
    elif re.search('mangahere\.com', args.url):
        parser = MangaHere(args.url)
    else:
        raise ValueError('Online Reader not supported')

    logging.info('Fetching and parsing URL: %s', args.url)

    recover_images(parser, args.dest)

    #If selected, compress chapters as <manga>/<chapter>.cbz
    if args.compress:
        logging.info('Compressing Manga: %s', parser.title)
        path = os.path.join(args.dest, parser.title)
        compressor = utils.MangaCompressor(path, parser.title, True)
        compressor.compress_manga(MAX_THREADS)

    logging.info('Finished Processing Manga: %s', parser.title)

if __name__ == "__main__":
    main()
