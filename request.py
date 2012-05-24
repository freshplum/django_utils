import simplejson
import base64
import logging
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
        return request.META['HTTP_X_FORWARDED_FOR']
    else:
        return request.META['REMOTE_ADDR']

def get_GET(request, BASE64='base64'):
    """
    Given a request, this decodes the base64 attributes (if they exist)
    """
    if BASE64 in request.GET:
        try:
            get = simplejson.loads(base64.decodestring(request.GET.get(BASE64, '')))
        except Exception as inst:
            #logger.error('Error in base64 padding\n %s' % str(inst))
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

def get_os(request):
    s = request.META.get('HTTP_USER_AGENT', '')
    if s.find('iPhone') != -1:
        return 'iphone'
    if s.find('iPad') != -1:
        return 'ipad'
    if s.find('Android') != -1:
        return 'android'
    elif s.find('Macintosh') != -1:
        return 'mac'
    elif s.find('Windows') != -1:
        return 'windows'
    elif s.find('Linux') != -1:
        return 'linux'
    else:
        return None

def get_browser(request):
    s = request.META.get('HTTP_USER_AGENT', '')
    if s.find('Chrome') != -1:
        return 'Chrome'
    if s.find('Firefox') != -1:
        return 'Firefox'
    if s.find('MSIE') != -1:
        return 'Internet Explorer'
    if s.find('Safari') != -1:
        return 'Safari'
    else:
        return None