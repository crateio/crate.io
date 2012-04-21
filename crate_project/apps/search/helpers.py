from jingo import register


@register.function
def facet2short(facet):
    FACETS = {
        "python_versions": "python",
        "operating_systems": "os",
        "licenses": "license",
        "implementations": "implementation",
    }
    return FACETS.get(facet)
