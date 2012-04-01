#!/usr/bin/env python

"""Download mangas from online readers. Supports for compression of the
mangas in separate chapters.

A parameter can be passed to establish how many concurrent connections can
be made to the same website. The compression process will always use 4 threads.
"""

import sys
import argparse
import os
import re
import logging

from lib import utils
from lib.parsers.mangareader import MangaReader
from lib.parsers.mangahere import MangaHere
from lib.ImageSaver import ImageSaver


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
    parser.parse()

    #Recovers the images parsed and saves them to <manga>/<chapter>/<image>
    manga_path = os.path.join(args.dest, parser.title)
    ch_digits = len(str(len(parser.imagesUrl)))
    for chapter, pages in parser.imagesUrl:
        #Normalize chapter digits
        chapter = "0" * (ch_digits - len(str(chapter))) + str(chapter)
        chapter_path = os.path.join(manga_path, chapter)
        if not os.path.exists(chapter_path):
            os.makedirs(chapter_path)
        savers = list()
        logging.info('Saving Chapter %s to %s', chapter, chapter_path)

        digits = len(str(len(pages)))
        for page, url in pages:
            #Normalize page digits
            page = "0" * (digits - len(str(page))) + str(page)
            path = os.path.join(chapter_path, str(page) + '.jpg')
            saver = ImageSaver(path, url)
            savers.append(saver)
            saver.start()
        map(lambda thread: thread.join(), savers)

    #If selected, compress chapters as <manga>/<chapter>.cbz
    if args.compress:
        logging.info('Compressing Manga: %s', parser.title)
        compressor = utils.MangaCompressor(parser.title, args.dest, True)
        compressor.compressManga()

    logging.info('Finished Processing Manga: %s', parser.title)

if __name__ == "__main__":
    main()
