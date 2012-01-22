import datetime
import hashlib
import logging
import posixpath
import re
import socket
import time
import xmlrpclib

import requests

from celery.exceptions import SoftTimeLimitExceeded
from celery.task import task

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.timezone import utc

from packages.models import Package, Release, TroveClassifier
from packages.models import ReleaseFile, ReleaseRequire, ReleaseProvide, ReleaseObsolete
from pypi.models import ChangeLog, Log, PackageModified


logger = logging.getLogger(__name__)

# @@@ Mirror Non PyPI Hosted Packages (Requires Link Scraping; Maybe Pip has something we can use.)
# @@@ We Need to be sure to remove Packages/Releases/Files if they've been removed in PyPI Proper
#       There's multiple ways to go about this; We could just do what PyPI does and allow release files to be
#       deleted. Another option is to do something similar to rubygems and translate deleting a file to yanking
#       a file. This way the fact it existed is still recorded?
# @@@ Do We need to mirror The Server Sig's as well? (Our Simple Pages have different markup)
# @@@ We could make mirroring smarter (Don't reprocess on simple things like doc updates, or owner add/remove etc.)
# @@@ We want to log why a particular package is failing,
#       Should We Present this Information to the Average User? The Package Owner?
# @@@ Can we use the has_sig or the server sig (are they the same?) to verify a file download
#       on top of the md5 hash?
# @@@ PyPI Parses links out of the body of long description and includes them on the simple page, we should do the same.
# @@@ Need The Special Pages that PyPI requires (stats, last refreshed ETC)
# @@@ Network Issues can cause missing packages; Somehow we should catch these exceptions and add them for later
#       retry (outside of celery's normal retry methods)
# @@@ If we APIize accessing the Crate site (updating metadata, saving files etc), we can set this up so that
#       these tasks can run anywhere, including S3/Cloud Servers/A Linode Box. Currently they require DB access.
# @@@ Update the Created of Package and Release based on oldest files

_md5_fragment_re = re.compile(r"#md5=([a-zA-Z0-9]{32})")
_disutils2_version_capture = re.compile("^(.*?)(?:\(([^()]+)\))?$")


def split_meta(meta):
    meta_split = meta.split(";", 1)
    meta_name, meta_version = _disutils2_version_capture.search(meta_split[0].strip()).groups()
    meta_env = meta_split[1].strip() if len(meta_split) == 2 else ""

    return {
        "name": meta_name,
        "version": meta_version if meta_version is not None else "",
        "environment": meta_env,
    }


def get_release_data(data, key, default=None):
    if data.get(key) and data[key] != "UNKNOWN":
        return data[key]
    return "" if default is None else default


class PackageHashMismatch(Exception):
    """
    Raised when the hash on the package didn't match what we expected.
    """


@task(time_limit=120, soft_time_limit=60)
def synchronize_mirror(index=None, since=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    if since is None:
        try:
            # Try to Sync from Our Last Time
            dt = Log.objects.filter(type=Log.TYPES.sync, index=index).order_by("-created")[:1][0].created
            since = int(time.mktime(dt.timetuple())) - 1
        except IndexError:
            # Default to the Unix Epoch
            since = 0

    client = xmlrpclib.ServerProxy(index_url)

    with transaction.commit_on_success():
        Log.objects.create(type=Log.TYPES.sync, index=index, message="Synchronizing with %s" % index)

        names = set()

        if since == 0:  # @@@ Should We Do This If since is too far in the past instead of just 0?
            # This is an initial Synchronize and change log will not work
            for name in client.list_packages():
                names.add(name)
        else:
            changelog = client.changelog(since)

            for item in changelog:
                name, version, timestamp, action = item

                # @@@ Eventually We Probably Want To Get Rid of This?
                dt = datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=utc)
                ChangeLog.objects.create(package=name, version=version, timestamp=dt, action=action)

                if action.startswith("new") or action.startswith("add") or action.startswith("create"):
                    names.add(name)
                elif action.startswith("update"):
                    # This techincally doesn't need to trigger a download, but it's the best way currently to
                    #   get the updated meta data.
                    names.add(name)
                elif action == "remove":
                    print " ".join([str(x) for x in ["-", name, version, timestamp, action]])
                    if version is None:
                        Package.objects.filter(name=name).delete()
                    else:
                        Release.objects.filter(package__name=name, version=version).delete()
                elif action.startswith("remove file"):
                    print " ".join([str(x) for x in ["--", name, version, timestamp, action]])
                    filename = action[12:]
                    ReleaseFile.objects.filter(release__package__name=name, release__version=version, filename=filename).delete()
                elif action == "docupdate":
                    continue
                elif action.startswith("remove Owner"):
                    continue
                else:
                    names.add(name)
                    print " ".join([str(x) for x in ["=", name, version, timestamp, action]])

        for name in names:
            process_package.delay(name, index=index)


@task(default_retry_delay=30 * 60)
def process_package(name, index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    if not Package.objects.filter(name=name).exists():
        Package.objects.create(name=name)

    try:
        client = xmlrpclib.ServerProxy(index_url)
        releases = client.package_releases(name, True)

        for release in releases:
            process_release_data.delay(name, release)
    except (SoftTimeLimitExceeded, socket.error, xmlrpclib.ProtocolError) as e:
        process_package.retry(exc=e)
    except Exception:
        raise


@task(default_retry_delay=30 * 60)
def process_release_data(package_name, version, index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    try:
        client = xmlrpclib.ServerProxy(index_url)
        data = client.release_data(package_name, version)

        if data:
            assert data["name"] == package_name
            assert data["version"] == version

            with transaction.commit_on_success():
                package, _ = Package.objects.get_or_create(name=package_name)
                release, c = Release.objects.get_or_create(package=package, version=data["version"])

                if not c:
                    current_classifiers = set(release.classifiers.all())
                    current_requires = set(release.requires.all())
                    current_provides = set(release.provides.all())
                    current_obsoletes = set(release.provides.all())

                    # Cleanup URI's
                    release.uris = {}
                else:
                    current_classifiers = set()
                    current_requires = set()
                    current_provides = set()
                    current_obsoletes = set()

                release.summary = get_release_data(data, "summary")
                release.description = get_release_data(data, "description")

                release.author = get_release_data(data, "author")
                release.author_email = get_release_data(data, "author_email")

                release.maintainer = get_release_data(data, "maintainer")
                release.maintainer_email = get_release_data(data, "maintainer_email")

                if get_release_data(data, "home_page"):
                    release.uris["Home Page"] = get_release_data(data, "home_page")
                elif "Home Page" in release.uris:
                    del release.uris["Home Page"]

                if get_release_data(data, "bugtrack_url"):
                    release.uris["Bug Tracker"] = get_release_data(data, "bugtrack_url")
                elif "Bug Tracker" in release.uris:
                    del release.uris["Bug Tracker"]

                release.license = get_release_data(data, "license")

                # @@@ I'd Love for this to be tags
                release.keywords = get_release_data(data, "keywords")

                release.platform = get_release_data(data, "platform")

                release.download_uri = get_release_data(data, "download_url")

                for classifier in get_release_data(data, "classifiers", []):
                    trove, _ = TroveClassifier.objects.get_or_create(trove=classifier)
                    release.classifiers.add(trove)

                    if trove in current_classifiers:
                        current_classifiers.remove(trove)

                if current_classifiers:
                    release.classifiers.remove(*current_classifiers)

                for key, url in [x.split(",", 1) for x in get_release_data(data, "project_url", [])]:
                    release.uris[key] = url

                release.requires_python = get_release_data(data, "required_python")

                if get_release_data(data, "stable_version"):
                    print ", ".join([package_name, version, "stable_version", get_release_data(data, "stable_version")])

                # Requirements
                for require in get_release_data(data, "requires", []):
                    r, _ = ReleaseRequire.objects.get_or_create(release=release, kind=ReleaseRequire.KIND.requires, **split_meta(require))
                    if r in current_requires:
                        current_requires.remove(r)

                for require in get_release_data(data, "requires_dist", []):
                    r, _ = ReleaseRequire.objects.get_or_create(release=release, kind=ReleaseRequire.KIND.requires_dist, **split_meta(require))
                    if r in current_requires:
                        current_requires.remove(r)

                for require in get_release_data(data, "requires_external", []):
                    r, _ = ReleaseRequire.objects.get_or_create(release=release, kind=ReleaseRequire.KIND.external, **split_meta(require))
                    if r in current_requires:
                        current_requires.remove(r)

                if current_requires:
                    release.requires.filter(pk__in=[x.pk for x in current_requires]).delete()

                # Provides
                for provides in get_release_data(data, "provides", []):
                    p, _ = ReleaseProvide.objects.get_or_create(release=release, kind=ReleaseProvide.KIND.provides, **split_meta(provides))
                    if p in current_provides:
                        current_provides.remove(p)

                for provides in get_release_data(data, "provides_dist", []):
                    p, _ = ReleaseProvide.objects.create(release=release, kind=ReleaseProvide.KIND.provides_dist, **split_meta(provides))
                    if p in current_provides:
                        current_provides.remove(p)

                if current_provides:
                    release.provides.filter(pk__in=[x.pk for x in current_provides]).delete()

                # Obsoletes
                for obsolete in get_release_data(data, "obsoletes", []):
                    o, _ = ReleaseObsolete.objects.get_or_create(release=release, kind=ReleaseObsolete.KIND.obsoletes, **split_meta(obsolete))
                    if o in current_obsoletes:
                        current_obsoletes.remove(o)

                for obsolete in get_release_data(data, "obsoletes_dist", []):
                    o, _ = ReleaseObsolete.objects.get_or_create(release=release, kind=ReleaseObsolete.KIND.obsoletes_dist, **split_meta(obsolete))
                    if o in current_obsoletes:
                        current_obsoletes.remove(o)

                if current_obsoletes:
                    release.obsoletes.filter(pk__in=[x.pk for x in current_obsoletes]).delete()

                release.hidden = get_release_data(data, "_pypi_hidden")

                release.raw_data = data

                release.save()

            process_release_urls.delay(package_name, version)
    except (SoftTimeLimitExceeded, socket.error, xmlrpclib.ProtocolError) as e:
        process_release_data.retry(exc=e)
    except Exception as e:
        raise


@task(default_retry_delay=30 * 60)
def process_release_urls(package_name, version, index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    try:
        client = xmlrpclib.ServerProxy(index_url, use_datetime=True)
        urls = client.release_urls(package_name, version)

        for url_data in urls:
            download_release.delay(package_name, version, url_data)
    except (SoftTimeLimitExceeded, socket.error, xmlrpclib.ProtocolError) as e:
        process_release_urls.retry(exc=e)
    except Exception as e:
        raise


@task(time_limit=650, soft_time_limit=600)
def download_release(package_name, version, data):
    SAVE_FILE = getattr(settings, "PYPI_SAVE_FILE", True)
    try:
        with transaction.commit_on_success():
            package, _ = Package.objects.get_or_create(name=package_name)
            release, _ = Release.objects.get_or_create(package=package, version=version)

            release_file, created = ReleaseFile.objects.get_or_create(
                                        release=release,
                                        type=data["packagetype"],
                                        filename=data["filename"],
                                        python_version=data["python_version"]
                                    )
            package_modified, new_package = PackageModified.objects.get_or_create(
                                                url=data["url"],
                                                defaults={"md5": data["md5_digest"], "release_file": release_file}
                                            )

            if not new_package and package_modified.md5.lower() == data["md5_digest"].lower() and release_file.file:
                # Only ask for If-Modified Since if:
                #   * This is not a New Package in Our System
                #   * The Claimed Hash of the New Package Matches the Stored Hash
                #   * We have an Already Existing File for this Release
                headers = {"If-Modified-Since": package_modified.last_modified}
            else:
                headers = {}

            resp = requests.get(data["url"], headers=headers, prefetch=True)

            if resp.status_code == 304:
                # We've done everything we can to verify this file is the same one we have
                # and it is. Don't bother to Download It.
                print "skipping %s" % resp.url
                return
            print ", ".join(["downloaded %s" % resp.url, str(new_package), package_modified.md5.lower(), data["md5_digest"].lower(), str(release_file.file)])

            resp.raise_for_status()

            # Make sure the MD5 of the file we receive matched what we were told it is
            if hashlib.md5(resp.content).hexdigest().lower() != data["md5_digest"].lower():
                raise PackageHashMismatch("%s does not match %s for %s %s" % (
                                                            hashlib.md5(resp.content).hexdigest().lower(),
                                                            data["md5_digest"].lower(),
                                                            data["packagetype"],
                                                            data["filename"],
                                                        ))

            # @@@ Verify if has_sig = True? How does this work?

            release_file.python_version = data["python_version"]
            release_file.downloads = data["downloads"]
            release_file.comment = data["comment_text"]

            if data.get("upload_time"):
                release_file.created = data["upload_time"].replace(tzinfo=utc)

            release_file.digest = "$".join(["sha256", hashlib.sha256(resp.content).hexdigest().lower()])

            # Do We Have an Existing File for this?
            if release_file.file:
                # @@@ There's No Rollbacks on this. Is there a way we can postpone this?
                release_file.file.delete()

            if SAVE_FILE:
                release_file.file.save(data["filename"], ContentFile(resp.content), save=True)
            else:
                release_file.save()

            package_modified.md5 = data["md5_digest"].lower()
            package_modified.last_modified = resp.headers.get("Last-Modified")
            package_modified.release_file = release_file

            if resp.headers.get("Last-Modified"):
                package_modified.save()
            else:
                # The Server Didn't give us Last Modified Information so we shouldn't
                # store it anymore.
                package_modified.delete()
    except (SoftTimeLimitExceeded, OSError, socket.error) as e:
        download_release.retry(exc=e)
    except Exception as e:
        raise


@task
def synchronize_troves(index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    classifier_url = posixpath.join(index, "pypi?%3Aaction=list_classifiers")

    try:
        resp = requests.get(classifier_url)
        resp.raise_for_status()

        with transaction.commit_on_success():
            for classifier in resp.content.splitlines():
                TroveClassifier.objects.get_or_create(trove=classifier.strip())
    except Exception:
        raise


@task(time_limit=300, soft_time_limit=120)
def synchronize_downloads(index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"

    try:
        for release in Release.objects.exclude(files=None).select_related("package").prefetch_related("files"):
            print release.package.name, release.version
            update_download_counts.delay(release.package.name, release.version, {x.filename: x.pk for x in release.files.all()}, index=index)
    except Exception:
        raise


@task
def update_download_counts(package_name, version, files, index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    try:
        client = xmlrpclib.ServerProxy(index_url)

        downloads = client.release_downloads(package_name, version)

        for filename, download_count in downloads:
            if filename in files:
                ReleaseFile.objects.filter(pk=files[filename]).update(downloads=download_count)
    except Exception:
        raise
