# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Log'
        db.create_table('aws_stats_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')()),
            ('edge_location', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('bytes', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('host', self.gf('django.db.models.fields.TextField')()),
            ('uri_stem', self.gf('django.db.models.fields.TextField')()),
            ('uri_query', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ip', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39)),
            ('referer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user_agent', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('aws_stats', ['Log'])

    def backwards(self, orm):
        # Deleting model 'Log'
        db.delete_table('aws_stats_log')

    models = {
        'aws_stats.log': {
            'Meta': {'object_name': 'Log'},
            'bytes': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'edge_location': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'host': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'referer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'uri_query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'uri_stem': ('django.db.models.fields.TextField', [], {}),
            'user_agent': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['aws_stats']