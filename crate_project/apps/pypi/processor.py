import hashlib
import logging
import re
import urlparse
import xmlrpclib

import redis
import requests
import lxml.html

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from packages.models import Package, Release, TroveClassifier
from packages.models import ReleaseRequire, ReleaseProvide, ReleaseObsolete, ReleaseURI, ReleaseFile
from pypi.exceptions import PackageHashMismatch
from pypi.utils.serversigs import load_key, verify

logger = logging.getLogger(__name__)

INDEX_URL = "http://pypi.python.org/pypi"
SIMPLE_URL = "http://pypi.python.org/simple/"
SERVERSIG_URL = "http://pypi.python.org/serversig/"
SERVERKEY_URL = "http://pypi.python.org/serverkey"

SERVERKEY_KEY = "crate:pypi:serverkey"

_disutils2_version_capture = re.compile("^(.*?)(?:\(([^()]+)\))?$")
_md5_re = re.compile(r"(https?://pypi\.python\.org/packages/.+)#md5=([a-f0-9]+)")


def get_helper(data, key, default=None):
    if data.get(key) and data[key] != "UNKNOWN":
        return data[key]
    return "" if default is None else default


def split_meta(meta):
    meta_split = meta.split(";", 1)
    meta_name, meta_version = _disutils2_version_capture.search(meta_split[0].strip()).groups()
    meta_env = meta_split[1].strip() if len(meta_split) == 2 else ""

    return {
        "name": meta_name,
        "version": meta_version if meta_version is not None else "",
        "environment": meta_env,
    }


class PyPIPackage(object):

    def __init__(self, name, version=None):
        self.name = name
        self.version = version

        self.stored = False

        self.pypi = xmlrpclib.ServerProxy(INDEX_URL, use_datetime=True)
        self.datastore = redis.StrictRedis(**getattr(settings, "PYPI_DATASTORE_CONFIG", {}))

    def fetch(self):
        logger.debug("[FETCH] %s%s" % (self.name, " %s" % self.version if self.version else ""))

        # Fetch meta data for this release
        self.releases = self.get_releases()
        self.release_data = self.get_release_data()
        self.release_url_data = self.get_release_urls()

    def build(self):
        logger.debug("[BUILD] %s%s" % (self.name, " %s" % self.version if self.version else ""))

        # Check to Make sure fetch has been ran
        if not hasattr(self, "releases") or not hasattr(self, "release_data") or not hasattr(self, "release_url_data"):
            raise Exception("fetch must be called prior to running build")  # @@@ Make a Custom Exception

        # Construct our representation of the releases
        self.data = {}
        for release in self.releases:
            data = {}

            data["package"] = self.name
            data["version"] = release

            data["author"] = get_helper(self.release_data[release], "author")
            data["author_email"] = get_helper(self.release_data[release], "author_email")

            data["maintainer"] = get_helper(self.release_data[release], "maintainer")
            data["maintainer_email"] = get_helper(self.release_data[release], "maintainer_email")

            data["summary"] = get_helper(self.release_data[release], "summary")
            data["description"] = get_helper(self.release_data[release], "description")

            data["license"] = get_helper(self.release_data[release], "license")
            data["keywords"] = get_helper(self.release_data[release], "keywords")  # @@@ Switch This to a List
            data["platform"] = get_helper(self.release_data[release], "platform")
            data["download_uri"] = get_helper(self.release_data[release], "download_url")  # @@@ Should This Go Under URI?
            data["requires_python"] = get_helper(self.release_data[release], "required_python")

            data["stable_version"] = get_helper(self.release_data[release], "stable_version")  # @@@ What Is This?

            data["classifiers"] = get_helper(self.release_data[release], "classifiers", [])

            data["hidden"] = get_helper(self.release_data[release], "_pypi_hidden")  # @ Do We Need This?

            # Construct the URIs
            data["uris"] = {}

            if get_helper(self.release_data[release], "home_page"):
                data["uris"]["Home Page"] = get_helper(self.release_data[release], "home_page")

            if get_helper(self.release_data[release], "bugtrack_url"):
                data["uris"]["Bug Tracker"] = get_helper(self.release_data[release], "bugtrack_url")

            for label, url in [x.split(",", 1) for x in get_helper(self.release_data[release], "project_url", [])]:
                data["uris"][label] = url

            # Construct Requires
            data["requires"] = []

            for kind in ["requires", "requires_dist", "requires_external"]:
                for require in get_helper(self.release_data[release], kind, []):
                    req = {"kind": kind if kind is not "requires_external" else "external"}
                    req.update(split_meta(require))
                    data["requires"].append(req)

            # Construct Provides
            data["provides"] = []

            for kind in ["provides", "provides_dist"]:
                for provides in get_helper(self.release_data[release], kind, []):
                    req = {"kind": kind}
                    req.update(split_meta(provides))
                    data["provides"].append(req)

            # Construct Obsoletes
            data["obsoletes"] = []

            for kind in ["obsoletes", "obsoletes_dist"]:
                for provides in get_helper(self.release_data[release], kind, []):
                    req = {"kind": kind}
                    req.update(split_meta(provides))
                    data["obsoletes"].append(req)

            # Construct Files
            data["files"] = []

            for url_data in self.release_url_data[release]:
                data["files"].append({
                    "comment": get_helper(url_data, "comment_text"),
                    "downloads": get_helper(url_data, "downloads"),
                    "file": get_helper(url_data, "url"),
                    "filename": get_helper(url_data, "filename"),
                    "python_version": get_helper(url_data, "python_version"),
                    "type": get_helper(url_data, "packagetype"),
                    "digests": {
                        "md5": url_data["md5_digest"].lower(),
                    }
                })
                if url_data.get("upload_time"):
                    data["files"][-1]["created"] = url_data["upload_time"]

            for file_data in data["files"]:
                if file_data.get("created"):
                    if data.get("created"):
                        if file_data["created"] < data["created"]:
                            data["created"] = file_data["created"]
                    else:
                        data["created"] = file_data["created"]

            self.data[release] = data

            logger.debug("[RELEASE BUILD DATA] %s %s %s" % (self.name, release, data))

    def store(self):
        for data in self.data.values():
            with transaction.commit_on_success():
                package, _ = Package.objects.get_or_create(name=data["package"])
                release, _ = Release.objects.get_or_create(package=package, version=data["version"])

                # This is an extra database call nut it should prevent ShareLocks
                Release.objects.filter(pk=release.pk).select_for_update()

                for key, value in data.iteritems():
                    if key in ["package", "version"]:
                        # Short circuit package and version
                        continue

                    if key == "uris":
                        ReleaseURI.objects.filter(release=release).delete()
                        for label, uri in value.iteritems():
                            ReleaseURI.objects.get_or_create(release=release, label=label, uri=uri)
                    elif key == "classifiers":
                        release.classifiers.clear()
                        for classifier in value:
                            trove, _ = TroveClassifier.objects.get_or_create(trove=classifier)
                            release.classifiers.add(trove)
                    elif key in ["requires", "provides", "obsoletes"]:
                        model = {"requires": ReleaseRequire, "provides": ReleaseProvide, "obsoletes": ReleaseObsolete}.get(key)
                        model.objects.filter(release=release).delete()
                        for item in value:
                            model.objects.get_or_create(release=release, **item)
                    elif key == "files":
                        files = ReleaseFile.objects.filter(release=release)
                        filenames = dict([(x.filename, x) for x in files])

                        for f in value:
                            rf, c = ReleaseFile.objects.get_or_create(
                                release=release,
                                type=f["type"],
                                filename=f["filename"],
                                python_version=f["python_version"],
                                defaults=dict([(k, v) for k, v in f.iteritems() if k not in ["digests", "file", "filename", "type", "python_version"]])
                            )

                            if f["filename"] in filenames.keys():
                                del filenames[f["filename"]]

                            if not c:
                                for k, v in f.iteritems():
                                    if k in ["digests", "file", "filename", "type", "python_version"]:
                                        continue

                                    setattr(rf, k, v)

                                rf.save()

                        if filenames:
                            ReleaseFile.objects.filter(pk__in=[f.pk for f in filenames.values()]).delete()
                    else:
                        setattr(release, key, value)

                release.save()

        self.stored = True

    def download(self):
        # Check to Make sure fetch has been ran
        if not hasattr(self, "releases") or not hasattr(self, "release_data") or not hasattr(self, "release_url_data"):
            raise Exception("fetch and build must be called prior to running download")  # @@@ Make a Custom Exception

        # Check to Make sure build has been ran
        if not hasattr(self, "data"):
            raise Exception("build must be called prior to running download")  # @@@ Make a Custom Exception

        if not self.stored:
            raise Exception("package must be stored prior to downloading")  # @@@ Make a Custom Exception

        for data in self.data.values():
            with transaction.commit_on_success():
                package = Package.objects.get(name=data["package"])
                release = Release.objects.filter(package=package, version=data["version"]).select_for_update()

                for release_file in ReleaseFile.objects.filter(release=release).select_for_update():
                    file_data = [x for x in data["files"] if x["filename"] == release_file.filename][0]

                    datastore_key = "crate:pypi:download:%(package)s:%(version)s:%(url)s" % {
                                        "package": data["package"],
                                        "version": data["version"],
                                        "url": file_data["file"],
                                    }
                    stored_file_data = self.datastore.hgetall(datastore_key)

                    headers = None

                    if stored_file_data:
                        # Stored data exists for this file
                        if release_file.file:
                            try:
                                release_file.file.read()
                            except IOError:
                                pass
                            else:
                                if release_file.file and release_file.file.read():
                                    # We already have a file
                                    if stored_file_data["md5"].lower() == file_data["digests"]["md5"].lower():
                                        # The supposed MD5 from PyPI matches our local
                                        headers = {
                                            "If-Modified-Since": stored_file_data["modified"],
                                        }

                    resp = requests.get(file_data["file"], headers=headers, prefetch=True)

                    if resp.status_code == 304:
                        logger.info("[DOWNLOAD] skipping %(filename)s because it has not been modified" % {"filename": release_file.filename})
                        return
                    logger.info("[DOWNLOAD] downloading %(filename)s" % {"filename": release_file.filename})

                    resp.raise_for_status()

                    # Get the Server Key for PyPI
                    if self.datastore.get(SERVERKEY_KEY):
                        key = load_key(self.datastore.get(SERVERKEY_KEY))
                    else:
                        serverkey = requests.get(SERVERKEY_URL, prefetch=True)
                        key = load_key(serverkey.content)
                        self.datastore.set(SERVERKEY_KEY, serverkey.content)

                    # Download the "simple" page from PyPI for this package
                    simple = requests.get(urlparse.urljoin(SIMPLE_URL, data["package"]), prefetch=True)
                    simple.raise_for_status()

                    # Download the "serversig" page from PyPI for this package
                    serversig = requests.get(urlparse.urljoin(SERVERSIG_URL, data["package"]), prefetch=True)
                    serversig.raise_for_status()

                    if not verify(key, simple.content, serversig.content):
                        raise Exception("Simple API page does not match serversig")  # @@@ This Should be Custom Exception

                    # Make sure the MD5 of the file we receive matched what we were told it is
                    if hashlib.md5(resp.content).hexdigest().lower() != file_data["digests"]["md5"].lower():
                        raise PackageHashMismatch("%s does not match %s for %s %s" % (
                                                            hashlib.md5(resp.content).hexdigest().lower(),
                                                            file_data["digests"]["md5"].lower(),
                                                            file_data["type"],
                                                            file_data["filename"],
                                                        ))

                    simple_html = lxml.html.fromstring(simple.content)
                    simple_html.make_links_absolute(urlparse.urljoin(SIMPLE_URL, data["package"]) + "/")

                    for link in simple_html.iterlinks():
                        m = _md5_re.search(link[2])
                        if m:
                            url, md5_hash = m.groups()
                            if url == file_data["file"]:
                                if md5_hash.lower() != file_data["digests"]["md5"].lower():
                                    raise Exception("MD5 does not match simple API md5 [Verified by ServerSig]")  # @@@ Custom Exception

                    release_file.digest = "$".join(["sha256", hashlib.sha256(resp.content).hexdigest().lower()])

                    release_file.file.save(file_data["filename"], ContentFile(resp.content), save=True)

                    # Store data relating to this file (if modified etc)
                    stored_file_data = {
                        "md5": file_data["digests"]["md5"].lower(),
                        "modified": resp.headers.get("Last-Modified"),
                    }

                    if resp.headers.get("Last-Modified"):
                        self.datastore.hmset(datastore_key, {
                            "md5": file_data["digests"]["md5"].lower(),
                            "modified": resp.headers["Last-Modified"],
                        })
                        # Set a year expire on the key so that stale entries disappear
                        self.datastore.expire(datastore_key, 31556926)
                    else:
                        self.datastore.delete(datastore_key)

    def get_releases(self):
        if self.version is None:
            releases = self.pypi.package_releases(self.name, True)
        else:
            releases = [self.version]

        logger.debug("[RELEASES] %s%s [%s]" % (self.name, " %s" % self.version if self.version else "", ", ".join(releases)))

        return releases

    def get_release_data(self):
        release_data = []
        for release in self.releases:
            data = self.pypi.release_data(self.name, release)
            logger.debug("[RELEASE DATA] %s %s" % (self.name, release))
            release_data.append([release, data])
        return dict(release_data)

    def get_release_urls(self):
        release_url_data = []
        for release in self.releases:
            data = self.pypi.release_urls(self.name, release)
            logger.info("[RELEASE URL] %s %s" % (self.name, release))
            logger.debug("[RELEASE URL DATA] %s %s %s" % (self.name, release, data))
            release_url_data.append([release, data])
        return dict(release_url_data)
