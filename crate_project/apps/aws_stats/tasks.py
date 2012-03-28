import datetime
import gzip
import itertools
import logging
import re
import StringIO
import urllib

from django.conf import settings
from django.db import transaction

from boto.s3.connection import S3Connection
from celery.task import task
from pytz import utc

from aws_stats.models import Log, LogProcessed

logger = logging.getLogger(__name__)


_log_filename = re.compile(settings.AWS_STATS_LOG_REGEX)


@task
def process_aws_log(key):
    if LogProcessed.objects.filter(name=key).exists():
        return

    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.lookup(settings.AWS_STATS_BUCKET_NAME)

    k = bucket.get_key(key)

    logs = []

    with gzip.GzipFile(fileobj=StringIO.StringIO(k.get_contents_as_string())) as f:
        fields = None
        for line in f:
            if line.startswith("#"):
                directive, value = line[1:].split(":", 1)

                directive = directive.strip()
                value = value.strip()

                if directive == "Version":
                    assert value == "1.0"

                if directive == "Fields":
                    fields = value.split()
            else:
                assert fields is not None

                logs.append(dict(itertools.izip(fields, [urllib.unquote(x) if x is not "-" else "" for x in line.split()])))

    with transaction.commit_on_success():
        for l in logs:
            when = datetime.datetime.strptime("T".join([l["date"], l["time"]]), "%Y-%m-%dT%H:%M:%S")
            when = when.replace(tzinfo=utc)

            Log.objects.create(
                    when=when,
                    edge_location=l["x-edge-location"],
                    method=l["cs-method"],
                    status=l["sc-status"],
                    bytes=int(l["sc-bytes"]),
                    host=l["cs(Host)"],
                    uri_stem=l["cs-uri-stem"],
                    uri_query=l["cs-uri-query"],
                    ip=l["c-ip"],
                    referer=l["cs(Referer)"],
                    user_agent=l["cs(User-Agent)"]
                )

        LogProcessed.objects.get_or_create(name=key)

    k.delete()


@task
def process_aws_logs():
    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.lookup(settings.AWS_STATS_BUCKET_NAME)

    for k in bucket:
        if _log_filename.search(k.name) is not None:
            process_aws_log.delay(k.name)
        else:
            logger.warning("%s doesn't match the aws log regex" % k.name)
