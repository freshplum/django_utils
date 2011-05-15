#From Python:
import string
from random import choice

#From Django:
from django.test import TestCase
from django.test.client import Client

#From Project:
from global_utils.misc import *
from global_utils.manage_html import *


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
