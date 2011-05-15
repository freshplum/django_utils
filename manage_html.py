import re

from django.utils.safestring import mark_safe

try:
    from BeautifulSoup import BeautifulSoup, Comment
except:
    pass
    
def strip(s, all_tags=None):
	valid_tags = ('strong b a i'.split() if not all_tags else '')
	valid_attrs = ('href src'.split() if not all_tags else '')
	soup = BeautifulSoup(s)
	for Comment in soup.findAll(
		text=lambda text: isinstance(text, Comment)):
		comment.extract()
	for tag in soup.findAll(True):
		if tag.name not in valid_tags:
			tag.hidden = True
		tag.attrs = [(attr, val) for attr, val in tag.attrs
					if attr in valid_attrs]
	return soup.renderContents().decode('utf8').replace('javascript:', '')

def convert_links(s):
	#NOTE: TEXT MUST ALREDY BE ESCAPED...
	##Find links that aren't already active (hyperlinked) and turn into hyperlink
	URL_regex = re.compile(r'(|^)http([\w\d\.\:\/]+?)(\s|$|\:|,)', re.IGNORECASE)
	s = URL_regex.sub(r'\1<a href="http\2">http\2</a>\3', s)
	
	URL_regex = re.compile(r'(\s|^)@([\w\d_]+)', re.IGNORECASE)
	s = URL_regex.sub(r'\1<a href="http://twitter.com/\2/">@\2</a>', s)
	return mark_safe(s)