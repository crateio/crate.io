# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaskLog'
        db.create_table('pypi_tasklog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 23, 5, 18, 13, 579234))),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 23, 5, 18, 13, 579336))),
            ('task_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32)),
            ('status', self.gf('model_utils.fields.StatusField')(default='success', max_length=100, no_check_for_status=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('args', self.gf('django.db.models.fields.TextField')()),
            ('kwargs', self.gf('django.db.models.fields.TextField')()),
            ('worker', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('pypi', ['TaskLog'])

    def backwards(self, orm):
        # Deleting model 'TaskLog'
        db.delete_table('pypi_tasklog')

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 604913)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 605012)'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'packages.release': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'author_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'releases'", 'blank': 'True', 'to': "orm['packages.TroveClassifier']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 599975)'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'download_uri': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 600073)'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 603444)'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '512'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 603552)'}),
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
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 605301)'}),
            'handled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 605399)'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        'pypi.log': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Log'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 604367)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 604470)'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pypi.packagemodified': {
            'Meta': {'object_name': 'PackageModified'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 599386)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'md5': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 599489)'}),
            'release_file': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['packages.ReleaseFile']"}),
            'url': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'pypi.tasklog': {
            'Meta': {'object_name': 'TaskLog'},
            'args': ('django.db.models.fields.TextField', [], {}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 602660)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 23, 5, 18, 13, 602775)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'success'", 'max_length': '100', 'no_check_for_status': 'True'}),
            'task_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32'}),
            'worker': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['pypi']
