import datetime
import hashlib
import logging
import posixpath
import re
import socket
import sys
import time
import traceback
import xmlrpclib

import requests

from celery.exceptions import SoftTimeLimitExceeded
from celery.task import task

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.timezone import utc

from packages.models import Package, Release, TroveClassifier
from packages.models import ReleaseFile, ReleaseRequire, ReleaseProvide, ReleaseObsolete, ReleaseURI
from pypi.models import ChangeLog, Log, PackageModified, TaskLog, DownloadChange


logger = logging.getLogger(__name__)

# @@@ Do We need to mirror The Server Sig's as well? (Our Simple Pages have different markup)
# @@@ We want to log why a particular package is failing,
#       Should We Present this Information to the Average User? The Package Owner?
# @@@ Can we use the has_sig or the server sig (are they the same?) to verify a file download
#       on top of the md5 hash?

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


def task_log(task_id, status, name, args, kwargs, exception=None):
    defaults = {
        "status": status,
        "name": name,
        "args": str(args),
        "kwargs": str(kwargs),
    }

    if exception is not None:
        exc = "".join(traceback.format_exception(*exception))
        defaults.update({"exception": exc})
    else:
        exc = None

    tlog, c = TaskLog.objects.get_or_create(task_id=task_id.replace("-", ""), defaults=defaults)

    if not c:
        tlog.status = TaskLog.STATUS.retry
        if exc is not None:
            tlog.exception = exc
        tlog.save()

    return tlog


@task(time_limit=120, soft_time_limit=60)
def synchronize_mirror(index=None, since=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    try:
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

                    handled = False

                    if action.startswith("new") or action.startswith("add") or action.startswith("create"):
                        names.add(name)
                        handled = True
                    elif action.startswith("update"):
                        # This techincally doesn't need to trigger a download, but it's the best way currently to
                        #   get the updated meta data.
                        names.add(name)
                        handled = True
                    elif action == "remove":
                        if version is None:
                            Package.objects.filter(name=name).delete()
                        else:
                            Release.objects.filter(package__name=name, version=version).delete()
                        handled = True
                    elif action.startswith("remove file"):
                        filename = action[12:]
                        ReleaseFile.objects.filter(release__package__name=name, release__version=version, filename=filename).delete()
                        handled = True
                    elif action == "docupdate":
                        handled = True
                    elif action.startswith("remove Owner"):
                        handled = True
                    else:
                        names.add(name)

                    # @@@ Eventually We Probably Want To Get Rid of This?
                    dt = datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=utc)
                    ChangeLog.objects.create(package=name, version=version, timestamp=dt, action=action, handled=handled)

            for name in names:
                process_package.delay(name, index=index)
    except Exception:
        task_log(synchronize_mirror.request.id, TaskLog.STATUS.failed, synchronize_mirror.name, [], {"index": index}, exception=sys.exc_info())
        raise


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
        task_log(process_package.request.id, TaskLog.STATUS.retry, process_package.name, [name], {"index": index}, exception=sys.exc_info())
        process_package.retry(exc=e)
    except Exception:
        task_log(process_package.request.id, TaskLog.STATUS.failed, process_package.name, [name], {"index": index}, exception=sys.exc_info())
    else:
        task_log(process_package.request.id, TaskLog.STATUS.success, process_package.name, [name], {"index": index})


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
                    current_uris = set([x.label for x in release.uris.all()])
                else:
                    current_classifiers = set()
                    current_requires = set()
                    current_provides = set()
                    current_obsoletes = set()
                    current_uris = set()

                release.summary = get_release_data(data, "summary")
                release.description = get_release_data(data, "description")

                release.author = get_release_data(data, "author")
                release.author_email = get_release_data(data, "author_email")

                release.maintainer = get_release_data(data, "maintainer")
                release.maintainer_email = get_release_data(data, "maintainer_email")

                if get_release_data(data, "home_page"):
                    ru, c = ReleaseURI.objects.get_or_create(release=release, label="Home Page", defaults={"uri": get_release_data(data, "home_page")})
                    if not c and ru.uri != get_release_data(data, "home_page"):
                        ru.uri = get_release_data(data, "home_page")
                        ru.save()
                elif "Home Page" in current_uris:
                    ReleaseURI.objects.filter(release=release, label="Home Page").delete()

                if get_release_data(data, "bugtrack_url"):
                    ru, c = ReleaseURI.objects.get_or_create(release=release, label="Bug Tracker", defaults={"uri": get_release_data(data, "bugtrack_url")})
                    if not c and ru.uri != get_release_data(data, "bugtrack_url"):
                        ru.uri = get_release_data(data, "bugtrack_url")
                        ru.save()
                elif "Bug Tracker" in current_uris:
                    ReleaseURI.objects.filter(release=release, label="Bug Tracker").delete()

                release.license = get_release_data(data, "license")

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
                    ru, c = ReleaseURI.objects.get_or_create(release=release, label=key, defaults={"uri": url})

                    if key in current_uris:
                        current_uris.remove(url)

                if current_uris:
                    ReleaseURI.objects.filter(release=release, uri__in=current_uris).delete()

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
        task_log(process_release_data.request.id, TaskLog.STATUS.retry, process_release_data.name, [package_name, version], {"index": index}, exception=sys.exc_info())
        process_release_data.retry(exc=e)
    except Exception as e:
        task_log(process_release_data.request.id, TaskLog.STATUS.failed, process_release_data.name, [package_name, version], {"index": index}, exception=sys.exc_info())
        raise
    else:
        task_log(process_release_data.request.id, TaskLog.STATUS.success, process_release_data.name, [package_name, version], {"index": index})


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
        task_log(process_release_urls.request.id, TaskLog.STATUS.retry, process_release_urls.name, [package_name, version], {"index": index}, exception=sys.exc_info())
        process_release_urls.retry(exc=e)
    except Exception as e:
        task_log(process_release_urls.request.id, TaskLog.STATUS.failed, process_release_urls.name, [package_name, version], {"index": index}, exception=sys.exc_info())
        raise
    else:
        task_log(process_release_urls.request.id, TaskLog.STATUS.success, process_release_urls.name, [package_name, version], {"index": index})


@task(time_limit=650, soft_time_limit=600)
def download_release(package_name, version, data):
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

            release_file.file.save(data["filename"], ContentFile(resp.content), save=True)

            package_modified.md5 = data["md5_digest"].lower()
            package_modified.last_modified = resp.headers.get("Last-Modified")
            package_modified.release_file = release_file

            if resp.headers.get("Last-Modified"):
                package_modified.save()
            else:
                # The Server Didn't give us Last Modified Information so we shouldn't
                # store it anymore.
                package_modified.delete()

            # Update the Creation Dates of Release
            if release.created > release_file.created:
                release.created = release_file.created
                release.save()

            # Update the Creation Dates of Package
            if package.created > release_file.created:
                package.created = release_file.created
                package.save()
    except (SoftTimeLimitExceeded, OSError, socket.error) as e:
        task_log(download_release.request.id, TaskLog.STATUS.retry, download_release.name, [package_name, version, data], {}, exception=sys.exc_info())
        download_release.retry(exc=e)
    except Exception as e:
        task_log(download_release.request.id, TaskLog.STATUS.failed, download_release.name, [package_name, version, data], {}, exception=sys.exc_info())
        raise
    else:
        task_log(download_release.request.id, TaskLog.STATUS.success, download_release.name, [package_name, version, data], {})


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
        task_log(synchronize_troves.request.id, TaskLog.STATUS.failed, synchronize_troves.name, [], {"index": index}, exception=sys.exc_info())
        raise
    else:
        task_log(synchronize_troves.request.id, TaskLog.STATUS.success, synchronize_troves.name, [], {"index": index})


@task(time_limit=650, soft_time_limit=600)
def synchronize_downloads(index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"

    try:
        for package in Package.objects.all().order_by("downloads_synced_on").prefetch_related("releases", "releases__files")[:150]:
            package.save()

            for release in package.releases.all():
                update_download_counts.delay(package.name, release.version, dict([(x.filename, x.pk) for x in release.files.all()]), index=index)
    except Exception:
        task_log(synchronize_downloads.request.id, TaskLog.STATUS.failed, synchronize_downloads.name, [], {"index": index}, exception=sys.exc_info())
        raise
    else:
        task_log(synchronize_downloads.request.id, TaskLog.STATUS.success, synchronize_downloads.name, [], {"index": index})


@task
def update_download_counts(package_name, version, files, index=None):
    if index is None:
        # Default to PyPI
        index = "http://pypi.python.org/"
    index_url = posixpath.join(index, "pypi")

    try:
        client = xmlrpclib.ServerProxy(index_url)

        downloads = client.release_downloads(package_name, version)

        changed = 0

        for filename, download_count in downloads:
            if filename in files:
                try:
                    current_count = ReleaseFile.objects.get(pk=files[filename]).downloads
                    changed += (download_count - current_count)
                except ReleaseFile.DoesNotExist:
                    pass
                ReleaseFile.objects.filter(pk=files[filename]).update(downloads=download_count)

        try:
            DownloadChange.objects.create(release=Release.objects.get(package__name=package_name, version=version), change=changed)
        except Release.DoesNotExist:
            pass
    except Exception:
        task_log(update_download_counts.request.id, TaskLog.STATUS.failed, update_download_counts.name, [package_name, version, files], {"index": index}, exception=sys.exc_info())
        raise
    else:
        task_log(update_download_counts.request.id, TaskLog.STATUS.success, update_download_counts.name, [package_name, version, files], {"index": index})


@task(time_limit=650, soft_time_limit=600)
def migrate_all_releases():
    for release in Release.objects.all():
        migrate_release.delay(release.pk)


@task(time_limit=650, soft_time_limit=600)
def migrate_release(release_pk):
    Release.objects.get(pk=release_pk).save()
