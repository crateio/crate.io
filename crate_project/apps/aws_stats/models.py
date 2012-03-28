from django.db import models


class Log(models.Model):

    when = models.DateTimeField()
    edge_location = models.CharField(max_length=25)

    method = models.CharField(max_length=25)
    status = models.CharField(max_length=3)
    bytes = models.PositiveIntegerField()

    host = models.TextField()
    uri_stem = models.TextField()
    uri_query = models.TextField(blank=True)

    ip = models.GenericIPAddressField(unpack_ipv4=True)
    referer = models.TextField(blank=True)
    user_agent = models.TextField(blank=True)

    def __unicode__(self):
        return "%(method)s %(uri_stem)s" % self.__dict__


class LogProcessed(models.Model):

    name = models.TextField(unique=True)
