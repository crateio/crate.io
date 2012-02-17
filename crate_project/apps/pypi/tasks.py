import collections
import hashlib
import logging
import re
import xmlrpclib

from pypi.processor import PyPIPackage

logger = logging.getLogger(__name__)

INDEX_URL = "http://pypi.python.org/pypi"


def process(name, version, timestamp, action):
    package = PyPIPackage(name)
    package.fetch()
    package.build()
    package.store()
    # package.download()

    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(package.data)


def synchronize(since=None):
    # @@@ Since Needs Stored Somewhere
    if since is None:
        since = 1320000896

    pypi = xmlrpclib.ServerProxy(INDEX_URL)

    # Debug Shortcut
    process("pyverify", "0.8.1", None, None)
    return

    if since is None:
        pass
    else:
        logger.info("[SYNCING] Changes since %s" % since)
        changes = pypi.changelog(since)

        for name, version, timestamp, action in changes:
            line_hash = hashlib.sha256(":".join([str(x) for x in (name, version, timestamp, action)])).hexdigest()
            logdata = {"action": action, "name": name, "version": version, "timestamp": timestamp, "hash": line_hash}

            if True:  # @@@ Switch To Checking a Hash of the Data
                logger.debug("[PROCESS] %(name)s %(version)s %(timestamp)s %(action)s" % logdata)
                logger.debug("[HASH] %(name)s %(version)s %(hash)s" % logdata)

                dispatch = collections.OrderedDict([
                    (re.compile("^create$"), process),
                    (re.compile("^new release$"), process),
                    (re.compile("^add [\w\d\.]+ file .+$"), process),
                    #(re.compile("^remove$"), remove),  # @@@ Do Something
                    #(re.compile("^remove file .+$"), remove_file),  # @@@ Do Something
                    (re.compile("^update [\w]+(, [\w]+)*$"), process),
                    #(re.compile("^docupdate$"), docupdate),  # @@@ Do Something
                    #(re.compile("^add (Owner|Maintainer) .+$"), add_user_role),  # @@@ Do Something
                    #(re.compile("^remove (Owner|Maintainer) .+$"), remove_user_role),  # @@@ Do Something
                ])

                # Dispatch Based on the action
                for pattern, func in dispatch.iteritems():
                    if pattern.search(action) is not None:
                        func(name, version, timestamp, action)
                        break
                else:
                    logger.warn("[UNHANDLED] %(name)s %(version)s %(timestamp)s %(action)s" % logdata)
            else:
                logger.debug("[SKIP] %(name)s %(version)s %(timestamp)s %(action)s" % logdata)
                logger.debug("[HASH] %(name)s %(version)s %(hash)s" % logdata)
