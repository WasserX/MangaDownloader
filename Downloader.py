#!/usr/bin/env python

import sys
sys.path.append('lib')
sys.path.append('lib/parsers')

import argparse
import os
import re
import logging

import utils
import MangaReader
import MangaHere
from ImageSaver import ImageSaver


def main():
    parser = argparse.ArgumentParser(description='Download images from an online manga reader')
    parser.add_argument('url', metavar='manga_url', type=str,
                        help='Website of the manga to download from one of the available sites')
    parser.add_argument('-c', default=False, action="store_true", dest='compress',
                        help='Should we compress each chapter using zip?')
    parser.add_argument('-v', default=False, action="store_true", dest='verbose',
                        help='Should we activate verbose mode')
    parser.add_argument('-d', metavar='destination', type=str, default=sys.path[0], dest='dest',
                        help='Where to create the folder with the manga')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if re.search('mangareader\.net', args.url):
        parser = MangaReader.MangaReader(args.url)
    elif re.search('mangahere\.com', args.url):
        parser = MangaHere.MangaHere(args.url)
    else:
        raise ValueError('Online Reader not supported')

    """
    All Parsers follow the same interface.
    'parse' creates a list of chapters, each containing a list of (page,url)
    In case the website given is that of a chapter, the list will contain
    one list corresponding to that chapter.
    This is done using as many threads as the website supports.
    """
    logging.info('Fetching and parsing URL: %s', args.url)
    parser.parse()

    basePath = os.path.join(args.dest, parser.title)
    if not os.path.exists(basePath):
        os.makedirs(basePath)

    """
    Recovers the images parsed and saves them to <manga>/<chapter>/<image>
    """
    chDigits = len(str(len(parser.imagesUrl)))
    for chapter, pages in parser.imagesUrl:
        #Normalize chapter digits
        chapter = "0" * (chDigits - len(str(chapter))) + str(chapter)
        chapterPath = os.path.join(basePath, chapter)
        if not os.path.exists(chapterPath):
            os.makedirs(chapterPath)
        savers = list()
        logging.info('Saving Chapter %s to %s', chapter, chapterPath)

        pgDigits = len(str(len(pages)))
        for page, url in pages:
            #Normalize page digits
            page = "0" * (pgDigits - len(str(page))) + str(page)
            imgSaver = ImageSaver(os.path.join(chapterPath, str(page) + '.jpg'), url)
            savers.append(imgSaver)
            imgSaver.start()
        map(lambda thread: thread.join(), savers)

    """
    If the user wants to compress each chapter inside of <manga>/
    a file named <chapter>.cbz will be created containing the images for
    that chapter
    """
    if args.compress:
        logging.info('Compressing Manga: %s', parser.title)
        compressor = utils.MangaCompressor(parser.title, args.dest, True)
        compressor.compressManga()

    logging.info('Finished Processing Manga: %s', parser.title)

if __name__ == "__main__":
    main()
