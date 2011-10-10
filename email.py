from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
try:
    from django.conf import EMAIL_TEMPLATE_ROOT
except ImportError:
    EMAIL_TEMPLATE_ROOT = 'www/emails'

class Email(object):
    """
    Class for handling emailing in Django with built in templates.
    
    A template's first line is used for the subject of the email. 
    Everything else makes up the body.
    """
    def __init__(self, template, to=None, data=None, from_name='Freshplum Mail'):
        self.to = to
        self.template = template
        self.data = data or {}
        self.from_name = from_name

    def render(self):
        data = self.data.update(self._return_context_vars())
        as_string = render_to_string('%s/%s.txt' % (EMAIL_TEMPLATE_ROOT, self.template), self.data)
        lines = as_string.splitlines()
        self.subject = lines[0]
        self.body = "\n".join(lines[1:])
        return self.subject, self.body

    def _return_context_vars(self):
        d = {'WEB_ROOT': 'https://freshplum.com'}
        if hasattr(self.to, 'first_name'):
            d['first_name'] = self.to.first_name
        return d
        
    def get_from_address(self):
        return '%s <%s>' % (self.from_name, settings.EMAIL_HOST_USER)

    def send(self):
        if not hasattr(self, 'subject'):
            self.render()
        if type(self.to) == type([]):
            to_field = self.to
        elif type(self.to) == type(''):
            to_field = [to]
        else:
            try:
                to_field = [str(getattr(self.to, 'email'))]
            except KeyError:
                raise KeyError('Email address not found in to object')
        self.email = EmailMessage(self.subject, self.body, from_email=self.get_from_address(), to=to_field)
        return self.email.send()
