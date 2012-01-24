# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Release', fields ['created']
        db.create_index('packages_release', ['created'])

        # Adding index on 'ReleaseFile', fields ['created']
        db.create_index('packages_releasefile', ['created'])

    def backwards(self, orm):
        # Removing index on 'ReleaseFile', fields ['created']
        db.delete_index('packages_releasefile', ['created'])

        # Removing index on 'Release', fields ['created']
        db.delete_index('packages_release', ['created'])

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 24, 3, 48, 3, 61153)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 24, 3, 48, 3, 61276)'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'packages.release': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'author_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'releases'", 'blank': 'True', 'to': "orm['packages.TroveClassifier']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 24, 3, 48, 3, 64645)', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'download_uri': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 24, 3, 48, 3, 64751)'}),
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
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 24, 3, 48, 3, 63237)', 'db_index': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '512'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 24, 3, 48, 3, 63351)'}),
            'python_version': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['packages.Release']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'packages.releaseobsolete': {
            'Meta': {'object_name': 'ReleaseObsolete'},
            'environment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'obsoletes'", 'to': "orm['packages.Release']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'packages.releaseprovide': {
            'Meta': {'object_name': 'ReleaseProvide'},
            'environment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'provides'", 'to': "orm['packages.Release']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'packages.releaserequire': {
            'Meta': {'object_name': 'ReleaseRequire'},
            'environment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requires'", 'to': "orm['packages.Release']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'packages.releaseuri': {
            'Meta': {'object_name': 'ReleaseURI'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uris'", 'to': "orm['packages.Release']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '500'})
        },
        'packages.troveclassifier': {
            'Meta': {'object_name': 'TroveClassifier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'trove': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '350'})
        }
    }

    complete_apps = ['packages']