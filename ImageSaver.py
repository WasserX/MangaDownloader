import urllib2
import logging
import os
from threading import Thread

logger = logging.getLogger(__name__)


class ImageSaver(Thread):
    """
    Recovers an image from an url and saves it to the given path
    This process is done in asynchronously using another thread
    """
    def __init__(self, path, url):
        self.url = url
        self.path = path
        Thread.__init__(self)

    def run(self):
        logger.debug('Loading Image %s', self.url)
        img = urllib2.urlopen(self.url).read()
        logger.debug('Loaded Image %s', self.url)
        image = open(self.path, 'w')
        image.write(img)
