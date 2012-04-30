# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Favorite', fields ['user', 'package']
        db.delete_unique('favorites_favorite', ['user_id', 'package_id'])

        # Deleting model 'Favorite'
        db.delete_table('favorites_favorite')

    def backwards(self, orm):
        # Adding model 'Favorite'
        db.create_table('favorites_favorite', (
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['packages.Package'])),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('favorites', ['Favorite'])

        # Adding unique constraint on 'Favorite', fields ['user', 'package']
        db.create_unique('favorites_favorite', ['user_id', 'package_id'])

    models = {
        
    }

    complete_apps = ['favorites']