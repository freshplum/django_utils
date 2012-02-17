import logging
import time
import hashlib
from math import sqrt
import urllib

from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.encoding import DjangoUnicodeDecodeError
from django.db.models.query import ValuesListQuerySet
from django.template.defaultfilters import slugify, truncatewords
from django.utils.encoding import smart_str

from django.conf import settings

class CustomError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

def custom_slugify(slug=None, name=None, length=16, num_words=2):
    if slug and len(slug):
        return slugify(slug).replace('-', '_')[0:length]
    elif name and len(name):
        return slugify(truncatewords(name, num_words)).replace('-', '_')[0:length]
    return ''


#TODO - implement these functions to remove user_ids (and photo slugs) from the URL.
def encrypt_id(n):
    from Crypto.Cipher import AES
    text = unicode(n) + '_' + settings.SECRET_SALT
    while (len(text)%16):
        text += '_'
    obj = AES.new(settings.SECRET_KEY[0:32], AES.MODE_ECB)
    return obj.encrypt(text)


#TODO - implement these functions to remove user_ids (and photo slugs) from the URL.
def decrypt_id(ciph):
    from Crypto.Cipher import AES
    obj = AES.new(settings.SECRET_KEY[0:32], AES.MODE_ECB)
    text = obj.decrypt(ciph)
    return int(text.split('_')[0])


def cache_layer(key, query, expiration=None, limit=None):
    try:
        query_cache = cache.get(key, None)
    except DjangoUnicodeDecodeError:
        query_cache = None
        logging.basicConfig(filename='./hackerhouses.log', level=logging.DEBUG,)
        logger = logging.getLogger('hackerhouses')
        logger.error('Can\'t decode unicode for cache.get.  Key: ' + key + ', Query: ' + query)
    if query_cache == None:
        query_cache = list(query[0:limit])
        if expiration:
            cache.set(key, query_cache, expiration)
        else:
            cache.set(key, query_cache)
    return query_cache

def do_pagination(paginate_by, GET, object_list):
    if not 'page' in GET:
        page = 1
    else:
        try:
            page = int(GET['page'])
        except ValueError:
            page = 1
    paginator = Paginator(object_list, paginate_by, orphans=3)
    try:
        page_obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_obj = paginator.page(paginator.num_pages)

    if len(paginator.page_range) > 9:
        paginator.trunc_page_range = paginator.page_range
        first_in_set = page - 3
        last_in_set = page + 3
        paginator.trunc_low = False
        paginator.trunc_high = False
        for p in paginator.page_range:
            if p < first_in_set:
                paginator.trunc_low = True
                paginator.trunc_page_range.remove(p)
            if p > last_in_set:
                paginator.trunc_high = True
                paginator.trunc_page_range.remove(p)
    return page_obj, paginator


def print_timing(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        t2 = time.time()
        timediff = (t2-t1)*1000.0
        s = '%s took %0.3f ms (%s)' % (func.__name__, timediff, func.func_code if hasattr(func, 'func_code') else '')
        if timediff > 40:
            logging.basicConfig(filename='./hackerhouses.log', level=logging.DEBUG,)
            logger = logging.getLogger('hackerhouses')
            if timediff > 3000:
                logger.critical(s)
            elif timediff > 750:
                logger.error(s)
            elif timediff > 350:
                logger.warning(s)
            elif timediff > 100:
                logger.info(s)
            else:
                logger.debug(s)
        return res
    return wrapper


def shorten_string(s, l):
    l = int(l)
    if len(s) > l:
        if l < 6:
            s = s[:l]
        else:
            s = s[:(l - 3)] + '...'
    return s


def clean_filename(f):
    """
    AWS fails on unicode image failnames.  This method removes any special characters.
    """
    if f and f.name and len(f.name):
        try: extension = f.name.rsplit('.', 1)[1]
        except IndexError: extension = 'png'
        f.name = custom_slugify(f.name.rsplit('.', 1)[0]) + '.' + extension
    return f


def get_lat_long(location):
    key = settings.GOOGLE_API_KEY
    output = "csv"
    location = smart_str(urllib.quote_plus(location))
    request = "http://maps.google.com/maps/geo?q=%s&output=%s&key=%s" % (location, output, key)
    try:
        data = urllib.urlopen(request).read()
        dlist = data.split(',')
    except IOError:
        dlist = None

    if dlist and dlist[0] == '200':
        return {'lat':float(dlist[2]), 'lon':float(dlist[3])}
    else:
        return None

def domain_is_blocked(d):
    blocked_domains = (
        '@asdf',
        '@test',
        '@spam.la',
        '@spammotel.com',
        '@kasmail.com',
        '@spamfree24.org',
        '@tempemail.net',
        '@10minutemail.com',
        '@guerrillamail.org',
        '@jetable.org',
        '@maileater.com',
        '@temporaryinbox.com',
        '@mailexpire.com',
        '@mytrashmail.com',
        '@mt2009.com',
        '@mt2010.com',
        '@mailinator',
        '@sogetthis',
        '@thisisnotmyrealemail',
        '@spamherelots',
        '@mailin8r',
        '@bouncr.com',
        '@email-masking',
        '@spaml',
        '@guerrillamail.com',
        '@mailmoat',
        '@sneakemail',
        '@spamgourmet',
        '@spamex',
        '@emailias.com',
        '@freshplum.com',
    )
    flagged = False

    for b in blocked_domains:
        if b in d:
            flagged = True
    return flagged