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

from django.test import TestCase
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


class UtilsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login = 'test_login'
        self.password = 'test_pass1234'

        self.text = '<a href="http://test.com">test.com</a><div><strong>this <i>is</i> a div</strong> http://google.com: http://msn.com, http://yahoo.com http://example.com \'http://tehcrowd.com\'</div> @omarish @tehcrowd_test'
        self.convert_links_text = '<a href="http://test.com">test.com</a><div><strong>this <i>is</i> a div</strong> <a href="http://google.com">http://google.com</a>: <a href="http://msn.com">http://msn.com</a>, <a href="http://yahoo.com">http://yahoo.com</a> <a href="http://example.com">http://example.com</a> \'http://tehcrowd.com\'</div> <a href="http://twitter.com/omarish/">@omarish</a> <a href="http://twitter.com/tehcrowd_test/">@tehcrowd_test</a>'
        self.stripped_text = '<a href="http://test.com">test.com</a><strong>this <i>is</i> a div</strong> http://google.com: http://msn.com, http://yahoo.com http://example.com \'http://tehcrowd.com\' @omarish @tehcrowd_test'

    def testShortenStrong(self):
        n = 1
        chars = string.letters + string.digits + '!@#$%^&*() _-"][{.`~}'
        while n < 33:
            s = ''
            for i in range(32):
                s = s + choice(chars)
            self.assertEqual(len(shorten_string(s, n)), n)
            n += 1

    def testConvertLinks(self):
        self.assertEqual(convert_links(self.text), self.convert_links_text)

    def testStripHtml(self):
        if BeautifulSoup:
            self.assertEqual(strip(self.text), self.stripped_text)
        else:
            logger.info('\nutils > manage_html.py: BEAUTIFUL SOUP NOT INSTALLED')