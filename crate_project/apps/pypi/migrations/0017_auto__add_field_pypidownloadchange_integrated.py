# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PyPIDownloadChange.integrated'
        db.add_column('pypi_pypidownloadchange', 'integrated',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'PyPIDownloadChange.integrated'
        db.delete_column('pypi_pypidownloadchange', 'integrated')

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'downloads_synced_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'normalized_name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'packages.release': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'author_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'releases'", 'blank': 'True', 'to': "orm['packages.TroveClassifier']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'download_uri': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['packages.Package']"}),
            'platform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'raw_data': ('crate.fields.json.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'requires_python': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'show_install_command': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'packages.releasefile': {
            'Meta': {'unique_together': "(('release', 'type', 'python_version', 'filename'),)", 'object_name': 'ReleaseFile'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'python_version': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['packages.Release']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'packages.troveclassifier': {
            'Meta': {'object_name': 'TroveClassifier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'trove': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '350'})
        },
        'pypi.pypidownloadchange': {
            'Meta': {'object_name': 'PyPIDownloadChange'},
            'change': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.ReleaseFile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integrated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        'pypi.pypiindexpage': {
            'Meta': {'object_name': 'PyPIIndexPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        'pypi.pypimirrorpage': {
            'Meta': {'object_name': 'PyPIMirrorPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.Package']", 'unique': 'True'})
        },
        'pypi.pypiserversigpage': {
            'Meta': {'object_name': 'PyPIServerSigPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.Package']"})
        }
    }

    complete_apps = ['pypi']