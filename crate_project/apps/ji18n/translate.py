from django.utils.translation import ugettext, ungettext
import jingo


class JinjaTranslations:
    def gettext(self, message):
        return ugettext(message)

    def ngettext(self, singular, plural, number):
        return ungettext(singular, plural, number)

def patch():
    jingo.env.install_gettext_translations(JinjaTranslations(), newstyle=True)
