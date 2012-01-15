from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import simplejson as json

from south.modelsinspector import add_introspection_rules


class JSONWidget(forms.Textarea):

    def render(self, name, value, attrs=None):
        if not isinstance(value, basestring):
            value = json.dumps(value, indent=4)
        return super(JSONWidget, self).render(name, value, attrs)


class JSONFormField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs["widget"] = JSONWidget
        super(JSONFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value:
            return
        try:
            return json.loads(value)
        except ValueError, e:
            raise forms.ValidationError(u"JSON decode error: %s" % unicode(e))


class JSONField(models.TextField):

    __metaclass__ = models.SubfieldBase

    def _loads(self, value):
        return json.loads(value)

    def _dumps(self, value):
        return json.dumps(value, cls=DjangoJSONEncoder)

    def to_python(self, value):
        # if value is basestring this likely means this method is being called
        # while a QuerySet is being iterated or otherwise is coming in raw
        # and this is the only case when we should deserialize.
        if isinstance(value, basestring):
            return self._loads(value)

        return value

    def get_db_prep_save(self, value, **kwargs):
        return self._dumps(value)

    def formfield(self, **kwargs):
        return super(JSONField, self).formfield(form_class=JSONFormField, **kwargs)


add_introspection_rules([], ["^crate\.fields\.json\.JSONField"])
