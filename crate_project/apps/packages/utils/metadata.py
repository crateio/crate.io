import collections
import email

from django.utils.encoding import force_unicode


def fix_encoding(s):
    return force_unicode(s, errors="ignore").encode("utf-8")


class ValidationError(Exception):
    """
        Raised When Meta Data doesn't validate
    """


class MetaData(object):
    """
        Takes a string representing a PKG-INFO file and validates it. The meta
        data is then available via the dict self.cleaned_data.
    """

    multiple_fields = set([
        "platform",
        "supported-platform",
        "classifier",
        "requires",
        "provides",
        "obsoletes",
        "requires-dist",
        "provides-dist",
        "obsoletes-dist",
        "requires-external",
        "project-url",
    ])

    def __init__(self, data):
        self.data = email.message_from_string(data.strip())
        self.errors = collections.defaultdict(set)

    def is_valid(self):
        if not hasattr(self, "_is_valid"):
            self.cleaned_data = {}

            for key in self.data.keys():
                try:
                    d = [getattr(self, "clean_%s" % key.lower(), lambda i: i)(x) for x in self.data.get_all(key)]
                    if len(d) > 1 and key.lower() not in self.multiple_fields:
                        raise ValidationError("%s has multiple values but that is not supported for this type." % key)

                    if key.lower() not in self.multiple_fields:
                        d = fix_encoding(d[0]) if len(d) else None
                    else:
                        d = [fix_encoding(x) for x in d]

                    self.cleaned_data[key.lower()] = d
                except ValidationError as e:
                    self.errors[key].add(e.message)

            if self.errors:
                self._is_valid = False
            else:
                self._is_valid = True

        return self._is_valid
