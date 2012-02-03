from django import template

from evaluator import suite

register = template.Library()


@register.inclusion_tag("evaluator/report.html")
def evaluate(obj):
    return {"results": [result for result in suite.evaluate(obj)]}
