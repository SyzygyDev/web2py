from gluon import *
import requests
from requests_oauthlib import OAuth1

# determine max int value
try: from sys import maxint # python2
except ImportError: from sys import maxsize as maxint # python3

try: from urllib.parse import parse_qs, quote_plus, unquote # python3
except ImportError: from urlparse import parse_qs; from urllib import quote_plus, unquote #python2

class TwitterSearch(object):
	"""
	This class actually performs the calls to the Twitter Search API (v1.1 only).

	It is configured using an instance of TwitterSearchOrder and valid Twitter credentials.
	"""

	_base_url = 'https://api.twitter.com/1.1/'
	_verify_url = 'account/verify_credentials.json'
	_search_url = 'search/tweets.json'
	_lang_url = 'help/languages.json'

	# see https://dev.twitter.com/docs/error-codes-responses
	exceptions = {
					 400 : 'Bad Request: The request was invalid',
					 401 : 'Unauthorized: Authentication credentials were missing or incorrect',
					 403 : 'Forbidden: The request is understood, but it has been refused or access is not allowed',
					 404 : 'Not Found: The URI requested is invalid or the resource requested does not exists',
					 406 : 'Not Acceptable: Invalid format is specified in the request',
					 410 : 'Gone: This resource is gone',
					 420 : 'Enhance Your Calm:  You are being rate limited',
					 422 : 'Unprocessable Entity: Image unable to be processed',
					 429 : 'Too Many Requests: Request cannot be served due to the application\'s rate limit having been exhausted for the resource',
					 500 : 'Internal Server Error: Something is broken',
					 502 : 'Bad Gateway: Twitter is down or being upgraded',
					 503 : 'Service Unavailable: The Twitter servers are up, but overloaded with requests',
					 504 : 'Gateway timeout: The request couldn\'t be serviced due to some failure within our stack',
				 }

	def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, verify=True):

		# app
		self.__consumer_key = consumer_key
		self.__consumer_secret = consumer_secret

		# user
		self.__access_token = access_token
		self.__access_token_secret = access_token_secret

		# init internal variables
		self.__response = {}
		self.__nextMaxID = maxint
		self.__proxy = {}

		# statistics
		self.__statistics = { 'queries' : 0, 'tweets' : 0 }

		# verify
		self.authenticate(verify)

	def __repr__(self):
		return '<TwitterSearch %s>' % self.__access_token

	def setProxy(self, proxy):
		""" Sets a given dict as proxy handler """
		if isinstance(proxy, dict) and 'https' in proxy:
			self.__proxy = proxy
		else:
			raise TwitterSearchException(1016)

	def authenticate(self, verify=True):
		""" Creates internal oauth handler needed for queries to Twitter and verifies credentials if needed """
		self.__oauth = OAuth1(self.__consumer_key,
			client_secret = self.__consumer_secret,
			resource_owner_key = self.__access_token,
			resource_owner_secret = self.__access_token_secret )

		if verify:
			r = requests.get(self._base_url + self._verify_url, auth=self.__oauth, proxies=self.__proxy)
			self.checkHTTPStatus(r.status_code)

	def checkHTTPStatus(self, http_status):
		""" Checks a given http_status and returns an exception in case wrong status """
		if http_status in self.exceptions:
			raise TwitterSearchException(http_status, self.exceptions[http_status])

	def searchTweetsIterable(self, order):
		""" Returns itself. Is called when using an instance of this class as iterable """
		self.searchTweets(order)
		return self

	def sentSearch(self, url):
		""" Sents a given query string to the Twitter Search API, stores results interally and validates returned HTTP status code """
		if not isinstance(url, basestring):
			raise TwitterSearchException(1009)

		r = requests.get(self._base_url + self._search_url + url, auth=self.__oauth, proxies=self.__proxy)
		self.__response['meta'] = r.headers

		self.checkHTTPStatus(r.status_code)

		# using IDs to request more results - former versions used page parameter
		# see https://dev.twitter.com/docs/working-with-timelines
		given_count = int(parse_qs(url)['count'][0])
		self.__response['content'] = r.json()

		self.__statistics['queries'] += 1
		self.__statistics['tweets'] += len(self.__response['content']['statuses'])

		# if we've seen the correct amount of tweets there may be some more
		if len(self.__response['content']['statuses']) > 0 and int(self.__response['content']['search_metadata']['count']) == given_count:
			self.__nextMaxID = min(self.__response['content']['statuses'], key=lambda i: i['id'])['id'] - 1

		else: # we got less tweets than requested -> no more results in API
			self.__nextMaxID = None

		return self.__response['meta'], self.__response['content']

	def searchTweets(self, order):
		""" Creates an query string through a given TwitterSearchOrder instance and takes care that it is sent to the Twitter API. Returns unmodified response """
		if not isinstance(order, TwitterSearchOrder):
			raise TwitterSearchException(1010)

		self._startURL = order.createSearchURL()
		self.sentSearch(self._startURL)
		return self.__response

	def searchNextResults(self):
		""" Returns True if there are more results available within the Twitter Search API """
		if not self.__nextMaxID:
			raise TwitterSearchException(1011)

		self.sentSearch("%s&max_id=%i" % (self._startURL, self.__nextMaxID))
		return self.__response

	def getMetadata(self):
		""" Returns all available meta data collected during last query """
		if not self.__response:
			raise TwitterSearchException(1012)
		return self.__response['meta']

	def getTweets(self):
		""" Returns all available data from last query """
		if not self.__response:
		   raise TwitterSearchException(1013)
		return self.__response['content']

	def getStatistics(self):
		""" Returns dict with statistical information about amount of queries and received tweets """
		return self.__statistics

	def setSupportedLanguages(self, order):
		""" Loads currently supported languages from Twitter API and sets them in a given TwitterSearchOrder instance """
		if not isinstance(order, TwitterSearchOrder):
			raise TwitterSearchException(1010)

		r = requests.get(self._base_url + self._lang_url, auth=self.__oauth, proxies=self.__proxy)
		self.__response['meta'] = r.headers
		self.checkHTTPStatus(r.status_code)
		self.__response['content'] = r.json()

		order.iso_6391 =  []
		for lang in self.__response['content']:
			order.iso_6391.append(lang['code'])

	# Iteration
	def __iter__(self):
		if not self.__response:
			raise TwitterSearchException(1014)
		self._nextTweet = 0
		return self

	def next(self):
		""" Python2 method, simply returns .__next__() """
		return self.__next__()

	def __next__(self):
		if self._nextTweet < len(self.__response['content']['statuses']):
			self._nextTweet += 1
			return self.__response['content']['statuses'][self._nextTweet-1]

		try:
			self.searchNextResults()
		except TwitterSearchException:
			raise StopIteration

		if len(self.__response['content']['statuses']) != 0:
			self._nextTweet = 1
			return self.__response['content']['statuses'][self._nextTweet-1]
		raise StopIteration

class TwitterSearchException(Exception):
	"""
	This class handles all exceptions directly based on TwitterSearch.
	"""

   # HTTP status codes are stored in TwitterSearch.exceptions due to possible on-the-fly modifications
	_error_codes = {
		1000 : 'Neither a list nor a string',
		1001 : 'Not a list object',
		1002 : 'No ISO 6391-1 language code',
		1003 : 'No valid result type',
		1004 : 'Invalid number',
		1005 : 'Invalid unit',
		1006 : 'Invalid callback string',
		1007 : 'Not a date object',
		1008 : 'Invalid boolean',
		1009 : 'Invalid string',
		1010 : 'Not a valid TwitterSearchOrder object',
		1011 : 'No more results available',
		1012 : 'No meta data available',
		1013 : 'No tweets available',
		1014 : 'No results available',
		1015 : 'No keywords given',
		1016 : 'Invalid dict',
	}

	def __init__(self, code, msg = None):
		self.code = code
		if msg:
			self.message = msg
		else:
			self.message = self._error_codes.get(code)

	def __str__(self):
		return "Error %i: %s" % (self.code, self.message)

class TwitterSearchOrder(object):
	from Twitter import TwitterSearchException
	"""
	This class is for configurating all available arguments of the Twitter Search API (v1.1).

	It also creates valid query strings which can be used in other environments identical to the syntax of the Twitter Search API.
	"""

	# default value for count should be the maximum value to minimize traffic
	# see https://dev.twitter.com/docs/api/1.1/get/search/tweets
	_max_count = 100

	# taken from http://www.loc.gov/standards/iso639-2/php/English_list.php
	iso_6391 = ['aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az', 'ba', 'be', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'br', 'bs', 'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy', 'da', 'de', 'dv', 'dz', 'ee', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gu', 'gv', 'ha', 'he', 'hi', 'ho', 'hr', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'ka', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'kv', 'kw', 'ky', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'na', 'nb', 'nd', 'ne', 'ng', 'nl', 'nn', 'no', 'nr', 'nv', 'ny', 'oc', 'oj', 'om', 'or', 'os', 'pa', 'pi', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'rw', 'sa', 'sc', 'sd', 'se', 'sg', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'wo', 'xh', 'yi', 'yo', 'za', 'zh', 'zu']

	def __init__(self):
		self.arguments = { 'count' : '%s' % self._max_count }
		self.searchterms = []
		self.url = ''

	def addKeyword(self, word):
		""" Adds a given string or list to the current keyword list """
		if isinstance(word, basestring) and len(word) >= 2:
		  self.searchterms.append(word)
		elif isinstance(word, list):
			self.searchterms += word
		else:
			raise TwitterSearchException(1000)

	def setKeywords(self, word):
		""" Sets a given list as the new keyword list """
		if not isinstance(word, list):
			raise TwitterSearchException(1001)
		self.searchterms = word

	def setSearchURL(self, url):
		""" Reads given query string and stores key-value tuples """
		if url[0] == '?':
			url = url[1:]

		args = parse_qs(url)
		self.searchterms = args['q']
		del args['q']

		# urldecode keywords
		for item in self.searchterms:
			item = unquote(item)

		self.arguments = {}
		for key, value in args.items():
			self.arguments.update({key : unquote(value[0])})

	def createSearchURL(self):
		""" Generates (urlencoded) query string from stored key-values tuples """
		if len(self.searchterms) == 0:
			raise TwitterSearchException(1015)

		url = '?q='
		url += '+'.join([ quote_plus(i) for i in self.searchterms])

		for key, value in self.arguments.items():
			url += '&%s=%s' % (quote_plus(key), (quote_plus(value) if key != 'geocode' else value) )

		self.url = url
		return self.url

	def setLanguage(self, lang):
		""" Sets 'lang' paramater """
		if lang in self.iso_6391:
			self.arguments.update( { 'lang' : '%s' % lang } )
		else:
			raise TwitterSearchException(1002)

	def setLocale(self, lang):
		""" Sets 'locale' paramater """
		if lang in self.iso_6391:
			self.arguments.update( { 'locale' : '%s' % lang } )
		else:
			raise TwitterSearchException(1002)

	def setResultType(self, tor):
		""" Sets 'result_type' paramater """
		if tor == 'mixed' or tor == 'recent' or tor == 'popular':
			self.arguments.update( { 'result_type' : '%s' % tor } )
		else:
			raise TwitterSearchException(1003)

	def setSinceID(self, twid):
		""" Sets 'since_id' parameter """
		if not isinstance(twid, (int, long)):
				raise TwitterSearchException(1004)

		if twid > 0:
			self.arguments.update( { 'since_id' : '%s' % twid } )
		else:
			raise TwitterSearchException(1004)

	def setMaxID(self, twid):
		""" Sets 'max_id' parameter """
		if not isinstance(twid, (int, long)):
				raise TwitterSearchException(1004)

		if twid > 0:
			self.arguments.update( { 'max_id' : '%s' % twid } )
		else:
			raise TwitterSearchException(1004)

	def setCount(self, cnt):
		""" Sets 'count' paramater """
		if isinstance(cnt, int) and cnt > 0 and cnt <= 100:
			self.arguments.update( { 'count' : '%s' % cnt } )
		else:
			raise TwitterSearchException(1004)

	def setGeocode(self, latitude, longitude, radius, km=True):
		""" Sets geolocation paramaters """
		if not isinstance(radius, (int, long) ) or radius <= 0:
		   raise TwitterSearchException(1004)

		if isinstance(latitude, float) and isinstance(longitude, float):
			if isinstance(km, bool):
				self.arguments.update( { 'geocode' : '%s,%s,%s%s' % (latitude, longitude, radius, 'km' if km else 'mi') } )
			else:
				raise TwitterSearchException(1005)
		else:
			raise TwitterSearchException(1004)

	def setCallback(self, func):
		""" Sets 'callback' paramater """
		if isinstance(func, basestring) and func:
			self.arguments.update( { 'callback' : '%s' % func } )
		else:
			raise TwitterSearchException(1006)

	def setUntil(self, date):
		""" Sets 'until' parameter """
		if isinstance(date, datetime.date) and date <= datetime.date.today():
			self.arguments.update( { 'until' : '%s' % date.strftime('%Y-%m-%d') } )
		else:
			raise TwitterSearchException(1007)

	def setIncludeEntities(self, include):
		""" Sets 'include entities' paramater """
		if not isinstance(include, bool):
			raise TwitterSearchException(1008)

		if include:
			self.arguments.update( { 'include_entities' : 'True' } )
		else:
			self.arguments.update( { 'include_entities' : 'False' } )