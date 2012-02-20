# -*- coding: utf-8 -*-
import redis

from django.conf import settings

from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        datastore = redis.StrictRedis(**getattr(settings, "PYPI_DATASTORE_CONFIG", {}))

        for package_modified in orm["pypi.PackageModified"].objects.all():
            datastore_key = "crate:pypi:download:%(url)s" % {"url": package_modified.url}

            datastore.hmset(datastore_key, {
                "md5": package_modified.md5,
                "modified": package_modified.last_modified,
            })

            datastore.expire(datastore_key, 31556926)

    def backwards(self, orm):
        datastore = redis.StrictRedis(**getattr(settings, "PYPI_DATASTORE_CONFIG", {}))

        for key in datastore.keys("crate:pypi:download:*"):
            url = key.rsplit(":", 1)[1]
            data = datastore.hgetall("crate_pypi:download:%s" % url)

            defaults = {
                "md5": data["md5"],
                "last_modified": data["modified"],
            }

            pm, c = orm["pypi.PackageModified"].objects.get_or_create(url=url, defaults=defaults)

            if not c:
                pm.md5 = defaults["md5"]
                pm.last_modified = defaults["last_modified"]
                pm.save()

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 516258)'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'downloads_synced_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 516622)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 516386)'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'packages.release': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'author_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'releases'", 'blank': 'True', 'to': "orm['packages.TroveClassifier']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 518316)', 'db_index': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'download_uri': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 518416)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['packages.Package']"}),
            'platform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'raw_data': ('crate.fields.json.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'requires_python': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'packages.releasefile': {
            'Meta': {'unique_together': "(('release', 'type', 'python_version', 'filename'),)", 'object_name': 'ReleaseFile'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 516856)', 'db_index': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '512'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 516957)'}),
            'python_version': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['packages.Release']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'packages.troveclassifier': {
            'Meta': {'object_name': 'TroveClassifier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'trove': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '350'})
        },
        'pypi.changelog': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'ChangeLog'},
            'action': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 520825)'}),
            'handled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 520930)'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        'pypi.downloadchange': {
            'Meta': {'object_name': 'DownloadChange'},
            'change': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 521504)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 521603)'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.Release']"})
        },
        'pypi.log': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Log'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 517789)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 517890)'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pypi.packagemodified': {
            'Meta': {'object_name': 'PackageModified'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 521976)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 522074)'}),
            'release_file': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['packages.ReleaseFile']"}),
            'url': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'pypi.pypimirrorpage': {
            'Meta': {'unique_together': "(('package', 'type'),)", 'object_name': 'PyPIMirrorPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.Package']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'pypi.tasklog': {
            'Meta': {'object_name': 'TaskLog'},
            'args': ('django.db.models.fields.TextField', [], {}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 520036)'}),
            'exception': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 2, 20, 0, 27, 7, 520138)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'pending'", 'max_length': '100', 'no_check_for_status': 'True'}),
            'task_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['pypi']
    symmetrical = True
