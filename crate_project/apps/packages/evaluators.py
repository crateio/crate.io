from django.utils.safestring import mark_safe

from evaluator import suite

from packages.utils import verlib


class PEP386Compatability(object):
    title = "PEP386 Compatibility"
    message = mark_safe("PEP386 defines a specific allowed syntax for Python package versions."
                "<br /><br />"
                "Previously it was impossible to accurately determine across any Python package what "
                "order the versions should go in, but with PEP386 we can now intelligently sort by version..."
                "<br /><br />"
                "But only if the version numbers are compatible!")

    def evaluate(self, release):
        normalized = verlib.suggest_normalized_version(release.version)

        if release.version == normalized:
            # Release Is Already Normalized
            return {
                "level": "success",
                "message": mark_safe('Compatible with <a href="http://www.python.org/dev/peps/pep-0386/">PEP386</a>.'),
            }
        elif normalized is not None:
            # Release Isn't Normalized, But We Can Figure It Out
            return {
                "level": None,
                "message": mark_safe('Almost Compatible with <a href="http://www.python.org/dev/peps/pep-0386/">PEP386</a>.'),
            }
        else:
            # We Can't Normalize the Release Version
            return {
                "level": "error",
                "message": mark_safe('Incompatible with <a href="http://www.python.org/dev/peps/pep-0386/">PEP386</a>.'),
            }


class PackageHosting(object):
    title = "Package Hosting"
    message = mark_safe("Did you know that packages listed on PyPI aren't required to host there?"
                "<br /><br />"
                "When your package manager tries to install a package from PyPI it looks in number "
                "of locations, one such location is an author specified url of where the package can "
                "be downloaded from."
                "<br /><br />"
                "Packages hosted by the author means that installing this package depends on the "
                "authors server staying up, adding another link in the chain that can cause your "
                "installation to fail")

    def evaluate(self, release):
        if release.files.all().exists():
            return {
                "level": "success",
                "message": "Package is hosted on PyPI",
            }
        elif release.download_uri:
            return {
                "level": "error",
                "message": "Package isn't hosted on PyPI",
            }
        else:
            return {
                "level": "error",
                "message": "No Package Hosting",
            }


suite.register(PEP386Compatability)
suite.register(PackageHosting)
