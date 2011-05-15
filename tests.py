#From Python:
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

class TestMiddleware(object):
	"""
	Test middleware to print out contents of GET and POST requests
	"""
	def __init__(self):
		if not settings.DEBUG:
			raise MiddlewareNotUsed

	def process_request(self, request):
		for post_var in request.POST:
			print post_var + ": " + request.POST[post_var]
		return None

	@staticmethod
	def show_sql(connection, show_all = False):
		time = 0
		count = 0
		for q in connection.queries:
			if show_all:
				print q
				print ""
			count += 1
			time += float(q['time'])
		if count > 0:
			print "Total Queries: " + str(count)
			print "Total Time: " + str(time)

	def process_response(self, request, response):
		TestMiddleware.show_sql(connection, show_all = False)
		return response

	def process_exception(self, request, exception):
		import traceback
		import sys
		exc_info = sys.exc_info()
		print "######################## Exception #############################"
		print '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))
		print "################################################################"
		#print repr(request)
		#print "################################################################"


###################
# utils.py tests #
##################
class UtilsTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.login = "test_login"
		self.password = 'test_pass1234'

		self.text = '<a href="http://test.com">test.com</a><div><strong>this <i>is</i> a div</strong> http://google.com: http://msn.com, http://yahoo.com http://example.com \'http://tehcrowd.com\'</div> @omarish @tehcrowd_test'
		self.stripped_text = '<a href="http://test.com">test.com</a><strong>this <i>is</i> a div</strong> http://google.com: http://msn.com, http://yahoo.com http://example.com \'http://tehcrowd.com\' @omarish @tehcrowd_test'
		self.convert_links_text = '<a href="http://test.com">test.com</a><div><strong>this <i>is</i> a div</strong> <a href="http://google.com">http://google.com</a>: <a href="http://msn.com">http://msn.com</a>, <a href="http://yahoo.com">http://yahoo.com</a> <a href="http://example.com">http://example.com</a> \'http://tehcrowd.com\'</div> <a href="http://twitter.com/omarish/">@omarish</a> <a href="http://twitter.com/tehcrowd_test/">@tehcrowd_test</a>'

	def testShortenStrong(self):
		print '\nutils > misc.py > test shorten_string'
		n = 1
		chars = string.letters + string.digits + '!@#$%^&*() _-"][{.`~}'
		while n < 33:
			s = ''
			for i in range(32):
				s = s + choice(chars)
			self.assertEqual(len(shorten_string(s, n)), n)
			n += 1

	def testConvertLinks(self):
		print '\nutils > manage_html.py > test convert_links()'
		self.assertEqual(convert_links(self.text), self.convert_links_text)

	def testStripHtml(self):
		print '\nutils > manage_html.py > test strip()'
		self.assertEqual(strip(self.text), self.stripped_text)

	def testSerializeObject(self):
		print '\nnutils > misc.py >  test serialize_object'
		#Haven't yet bothered to teset this...
