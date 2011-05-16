######################
# Returns HTTP pages #
######################
#From Python:

#From Django:
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core import urlresolvers
from django.utils.safestring import mark_safe
from django.contrib.auth import logout
from django.template import Template

#From Project:
from settings import LOGIN_URL, LOGOUT_URL

#allways use this when rendering templates (it executes required functions) before rendering the template
#TODO - include these in generic views...
def template(template_name, locals_dict=None, status=200):
    no_redirects = (
        LOGIN_URL,
        LOGOUT_URL,
    )
    
    #these functions should be executed before every page render:
    if 'next' in locals_dict['request'].GET:
        locals_dict['request'].session['prev_page'] = locals_dict['request'].GET['next']
    elif not 'forget_path' in locals_dict:
        locals_dict['request'].session['prev_page'] = locals_dict['request'].path
    
    if 'prev_page' in locals_dict['request'].session and (locals_dict['request'].session['prev_page'] in no_redirects or '/api/' in locals_dict['request'].session['prev_page']):
        locals_dict['request'].session['prev_page'] = '/'

    #TODO - THIS SHOULD ALSO CHECK IF USER IS LOGGED IN:
    if locals_dict['request'].user.is_authenticated():
        locals_dict['user'] = locals_dict['request'].user
    return render_wrapper(template_name, locals_dict, status=status)
    
def previous(request):
    redirect = ('/' + request.session['prev_page'].lstrip('/') if 'prev_page' in request.session else urlresolvers.reverse('index'))
    return HttpResponseRedirect(redirect)

def render_wrapper(template_name, locals_dict, status=200):
    t = template_name if type(template_name) == Template else loader.get_template(template_name)
    c = RequestContext(locals_dict['request'], locals_dict) if 'request' in locals_dict    else Context(locals_dict)
    return HttpResponse(t.render(c), status=status)