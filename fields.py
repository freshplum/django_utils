import inspect
import re
import simplejson
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

class GenChoice:
    hidden_pat = re.compile(r'__\w+__')

    @classmethod
    def choices(cls):
        fn = lambda x: (isinstance(x[1], str) or\
                        isinstance(x[1], int) or\
                        isinstance(x[1], float))\
                   and (not GenChoice.hidden_pat.match(x[0]))
        return filter(fn, inspect.getmembers(cls))


class ManyToManyJSONField(models.Field):

    __metaclass__ = models.SubfieldBase

    def __init__(self, model, *args, **kwargs):
        self.Model = model
        super(ManyToManyJSONField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'longtext'

    def get_prep_value(self, value):
        ids = []
        for v in value:
            ids.append(v.id)
        return simplejson.dumps(ids) if ids else None

    def to_python(self, value='[]'):
        if not value:
            value = '[]'
        ids = simplejson.loads(str(value))
        return [self.Model.objects.get(id=id) for id in ids]


class JSONField(models.TextField):
    """
    Serializes/deserializes JSON object into a text field in a SQLite database
    """

    description = "A JSON object"

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return {}

        try:
            if isinstance(value, basestring):
                return simplejson.loads(value)
        except ValueError:
            pass

        return value


    def get_db_prep_save(self, value, connection):
        """Convert our JSON object to a string before we save"""
        if value == "":
            return None

        if isinstance(value, dict):
            value = simplejson.dumps(value)

        # TODO: If the value is a string, make sure it is valid JSON before saving it
        return super(JSONField, self).get_db_prep_save(value, connection)
