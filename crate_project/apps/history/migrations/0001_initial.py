# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table('history_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('package', self.gf('django.db.models.fields.SlugField')(max_length=150)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('data', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal('history', ['Event'])

    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table('history_event')

    models = {
        'history.event': {
            'Meta': {'object_name': 'Event'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'data': ('jsonfield.fields.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'package': ('django.db.models.fields.SlugField', [], {'max_length': '150'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['history']