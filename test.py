import logging
logger = logging.getLogger(__name__)

#From Python:
try:
    from BeautifulSoup import BeautifulSoup, Comment
except ImportError:
    BeautifulSoup = None

import string
from random import choice
from datetime import datetime, date, timedelta

import django.test
from django.test.client import Client
from django.core.exceptions import MiddlewareNotUsed
from django.db import connection

from misc import *
from manage_html import *

from django.conf import settings
try:
    SHOW_QUERIES = settings.SHOW_QUERIES
except AttributeError:
    SHOW_QUERIES = False

class TestMiddleware(object):
    """
    Test middleware to print out contents of GET and POST requests
    """
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed

    def process_request(self, request):
        for post_var in request.POST:
            logger.info('%s: %s' % (post_var, request.POST[post_var]))
        return None

    @staticmethod
    def show_sql(connection, show_all = False):
        time = 0
        count = 0
        for query in connection.queries:
            if show_all:
                logger.info('%s\n' % q)
            count += 1
            time += float(query.get('duration', 0))
        if count > 0:
            logger.info('Total Queries: %s' % str(count))
            logger.info('Total Time: %s' % str(time))

    def process_response(self, request, response):
        TestMiddleware.show_sql(connection, show_all = SHOW_QUERIES)
        return response


class TestCase(django.test.TestCase):
    """
    Common base class for all Freshplum unit tests to inherit from.
    """

    multi_db = True
    """Flag to make sure that Django properly loads fixtures for every database"""