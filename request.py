import simplejson
import base64
import logging
import re

import httpagentparser

from django.core.mail import mail_managers
logger = logging.getLogger(__name__)

def get_ip(request):
    """
    Get the appropriate IP address of a request object.

    This was written because a load balancer rewrites the
    request header with the IP address of the original request
    as a different property
    """
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return (ip + ',').split(',')[0]

def get_GET(request, BASE64='base64'):
    """
    Given a request, this decodes the base64 attributes (if they exist)
    """
    if BASE64 in request.GET:
        try:
            encoded = request.GET.get(BASE64, '')

            # convert to ascii
            encoded.encode('ascii', 'ignore')

            # decode from base64
            decoded = base64.decodestring(encoded)

            # replace invalid json
            decoded.replace('undefined', 'null')

            # decode json
            get = simplejson.loads(decoded)
        except Exception as inst:
            print inst
            logger.error('Error in base64 padding\n%s\n%s\n%s' % (inst, request.GET.get(BASE64), request))
            raise ValueError
        for key, value in request.GET.items():
            if key != BASE64:
                get[key] = value
        return get
    else:
        raw = request.GET.copy()
        d = {}
        for k,v in raw.items():
            try:
                d[k] = simplejson.loads(v)
            except simplejson.JSONDecodeError:
                d[k] = str(v)
        return d

def get_os_browser(request):
    ua = request.META.get('HTTP_USER_AGENT', '')

    os = get_os(ua)
    browser = get_browser(ua)

    ua_info = httpagentparser.detect(ua)
    return {
        'os': {
            'type': get_os(ua),
            'vsn': major_minor(ua_info.get('os', {}).get('version', ''))
        },
        'browser': {
            'type': get_browser(ua),
            'vsn': major_minor(ua_info.get('browser', {}).get('version', ''))
        },
        'is_mobile': is_mobile(ua),
    }


MAJOR_MINOR_RE = re.compile(r'(?:^| )(\d+)\.?(\d+)?')
def major_minor(vsn):
    m = MAJOR_MINOR_RE.match(vsn)
    if m:
        return m.groups()
    else:
        vsn

def get_os(ua):
    if ua.find('iPhone') != -1:
        return 'iphone'
    if ua.find('iPad') != -1:
        return 'ipad'
    if ua.find('Android') != -1:
        return 'android'
    elif ua.find('Macintosh') != -1:
        return 'mac'
    elif ua.find('Windows') != -1:
        return 'windows'
    elif ua.find('Linux') != -1:
        return 'linux'
    else:
        return None

def get_browser(ua):
    if ua.find('Chrome') != -1:
        return 'Chrome'
    if ua.find('Firefox') != -1:
        return 'Firefox'
    if ua.find('MSIE') != -1:
        return 'Internet Explorer'
    if ua.find('Safari') != -1:
        return 'Safari'
    else:
        return None

def is_mobile(ua):
    return (get_os(ua) or '').lower() in ['iphone', 'android',]
