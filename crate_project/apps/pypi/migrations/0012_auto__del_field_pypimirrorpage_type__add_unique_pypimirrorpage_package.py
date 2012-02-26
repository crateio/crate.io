# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'PyPIMirrorPage', fields ['type', 'package']
        db.delete_unique('pypi_pypimirrorpage', ['type', 'package_id'])

        # Deleting field 'PyPIMirrorPage.type'
        db.delete_column('pypi_pypimirrorpage', 'type')

        # Adding unique constraint on 'PyPIMirrorPage', fields ['package']
        db.create_unique('pypi_pypimirrorpage', ['package_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'PyPIMirrorPage', fields ['package']
        db.delete_unique('pypi_pypimirrorpage', ['package_id'])


        # User chose to not deal with backwards NULL issues for 'PyPIMirrorPage.type'
        raise RuntimeError("Cannot reverse this migration. 'PyPIMirrorPage.type' and its values cannot be restored.")
        # Adding unique constraint on 'PyPIMirrorPage', fields ['type', 'package']
        db.create_unique('pypi_pypimirrorpage', ['type', 'package_id'])

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'downloads_synced_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'pypi.changelog': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'ChangeLog'},
            'action': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'handled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        'pypi.log': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Log'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pypi.pypimirrorpage': {
            'Meta': {'object_name': 'PyPIMirrorPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.Package']", 'unique': 'True'})
        },
        'pypi.pypiserversigpage': {
            'Meta': {'object_name': 'PyPIServerSigPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['packages.Package']"})
        }
    }

    complete_apps = ['pypi']