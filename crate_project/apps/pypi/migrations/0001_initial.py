# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("packages", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'Log'
        db.create_table('pypi_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 8, 3, 18, 57, 369909))),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 8, 3, 18, 57, 370030))),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('index', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('pypi', ['Log'])

        # Adding model 'ChangeLog'
        db.create_table('pypi_changelog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 8, 3, 18, 57, 370841))),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 8, 3, 18, 57, 370939))),
            ('package', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('action', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('pypi', ['ChangeLog'])

        # Adding model 'PackageModified'
        db.create_table('pypi_packagemodified', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 8, 3, 18, 57, 374148))),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 8, 3, 18, 57, 374251))),
            ('release_file', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['packages.ReleaseFile'])),
            ('url', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('last_modified', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('md5', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('pypi', ['PackageModified'])

    def backwards(self, orm):
        # Deleting model 'Log'
        db.delete_table('pypi_log')

        # Deleting model 'ChangeLog'
        db.delete_table('pypi_changelog')

        # Deleting model 'PackageModified'
        db.delete_table('pypi_packagemodified')

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 379936)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 380034)'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'packages.release': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'author_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'releases'", 'blank': 'True', 'to': "orm['packages.TroveClassifier']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 380932)'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'download_uri': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 381027)'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['packages.Package']"}),
            'platform': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'raw_data': ('crate.fields.json.JSONField', [], {'null': 'True'}),
            'requires_python': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'packages.releasefile': {
            'Meta': {'unique_together': "(('release', 'type', 'python_version', 'filename'),)", 'object_name': 'ReleaseFile'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 382424)'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '512'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 382545)'}),
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
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 380316)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 380415)'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        'pypi.log': {
            'Meta': {'object_name': 'Log'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 379410)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 379522)'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pypi.packagemodified': {
            'Meta': {'object_name': 'PackageModified'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 383311)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 8, 3, 18, 57, 383409)'}),
            'release_file': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['packages.ReleaseFile']"}),
            'url': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['pypi']
