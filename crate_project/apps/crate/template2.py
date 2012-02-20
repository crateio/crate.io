from django.conf import settings

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader(settings.JINJA_TEMPLATE_DIRS), auto_reload=settings.DEBUG)
