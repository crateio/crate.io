import collections
import json
import time

import isoweek

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from packages.models import Package, Release, DownloadDelta

def stats_delta(request, slug):
    package = get_object_or_404(Package, name=slug)
    releases = list(Release.objects.filter(package=package).order_by("order"))
    deltas = list(DownloadDelta.objects.filter(file__release__in=releases).order_by("date"))

    # @@@ Sanity Checks

    data = [{"name": release.version, "data": []} for release in releases]

    # Get First Week
    start_week = isoweek.Week.withdate(deltas[0].date)
    end_week =  isoweek.Week.thisweek()

    current = isoweek.Week(start_week.year, start_week.week)

    while current.year <= end_week.year and current.week <= end_week.week:
        for x in data:
            x["data"].append({"x": int(time.mktime(current.day(0).timetuple()))})
        current = isoweek.Week(current.year, current.week + 1)

    _data = collections.defaultdict(dict)

    for d in deltas:
        target = int(time.mktime(isoweek.Week.withdate(d.date).day(0).timetuple()))
        _data[d.file.release.version][target] = d.delta

    for i in xrange(0, len(data)):
        for j in xrange(0, len(data[i]["data"])):
            data[i]["data"][j]["y"] = _data[data[i]["name"]].get(data[i]["data"][j]["x"], 0)


    return HttpResponse(json.dumps(data), mimetype="application/json")
