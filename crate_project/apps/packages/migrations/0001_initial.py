# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TroveClassifier'
        db.create_table('packages_troveclassifier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trove', self.gf('django.db.models.fields.CharField')(unique=True, max_length=350)),
        ))
        db.send_create_signal('packages', ['TroveClassifier'])

        # Adding model 'Package'
        db.create_table('packages_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 28, 13, 38, 31, 227535))),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 28, 13, 38, 31, 227680))),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=150)),
        ))
        db.send_create_signal('packages', ['Package'])

        # Adding model 'PackageURI'
        db.create_table('packages_packageuri', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(related_name='package_links', to=orm['packages.Package'])),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=400)),
        ))
        db.send_create_signal('packages', ['PackageURI'])

        # Adding unique constraint on 'PackageURI', fields ['package', 'uri']
        db.create_unique('packages_packageuri', ['package_id', 'uri'])

        # Adding model 'Release'
        db.create_table('packages_release', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 28, 13, 38, 31, 229663), db_index=True)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 28, 13, 38, 31, 229762))),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(related_name='releases', to=orm['packages.Package'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('platform', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('summary', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('license', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author_email', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('maintainer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('maintainer_email', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('requires_python', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('download_uri', self.gf('django.db.models.fields.URLField')(max_length=1024, blank=True)),
            ('raw_data', self.gf('crate.fields.json.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('packages', ['Release'])

        # Adding unique constraint on 'Release', fields ['package', 'version']
        db.create_unique('packages_release', ['package_id', 'version'])

        # Adding M2M table for field classifiers on 'Release'
        db.create_table('packages_release_classifiers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm['packages.release'], null=False)),
            ('troveclassifier', models.ForeignKey(orm['packages.troveclassifier'], null=False))
        ))
        db.create_unique('packages_release_classifiers', ['release_id', 'troveclassifier_id'])

        # Adding model 'ReleaseFile'
        db.create_table('packages_releasefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime(2012, 1, 28, 13, 38, 31, 228759), db_index=True)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime(2012, 1, 28, 13, 38, 31, 228860))),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='files', to=orm['packages.Release'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=512)),
            ('filename', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True, blank=True)),
            ('digest', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('python_version', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('downloads', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('packages', ['ReleaseFile'])

        # Adding unique constraint on 'ReleaseFile', fields ['release', 'type', 'python_version', 'filename']
        db.create_unique('packages_releasefile', ['release_id', 'type', 'python_version', 'filename'])

        # Adding model 'ReleaseURI'
        db.create_table('packages_releaseuri', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='uris', to=orm['packages.Release'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=500)),
        ))
        db.send_create_signal('packages', ['ReleaseURI'])

        # Adding model 'ReleaseRequire'
        db.create_table('packages_releaserequire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requires', to=orm['packages.Release'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('environment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('packages', ['ReleaseRequire'])

        # Adding model 'ReleaseProvide'
        db.create_table('packages_releaseprovide', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='provides', to=orm['packages.Release'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('environment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('packages', ['ReleaseProvide'])

        # Adding model 'ReleaseObsolete'
        db.create_table('packages_releaseobsolete', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='obsoletes', to=orm['packages.Release'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('environment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('packages', ['ReleaseObsolete'])

    def backwards(self, orm):
        # Removing unique constraint on 'ReleaseFile', fields ['release', 'type', 'python_version', 'filename']
        db.delete_unique('packages_releasefile', ['release_id', 'type', 'python_version', 'filename'])

        # Removing unique constraint on 'Release', fields ['package', 'version']
        db.delete_unique('packages_release', ['package_id', 'version'])

        # Removing unique constraint on 'PackageURI', fields ['package', 'uri']
        db.delete_unique('packages_packageuri', ['package_id', 'uri'])

        # Deleting model 'TroveClassifier'
        db.delete_table('packages_troveclassifier')

        # Deleting model 'Package'
        db.delete_table('packages_package')

        # Deleting model 'PackageURI'
        db.delete_table('packages_packageuri')

        # Deleting model 'Release'
        db.delete_table('packages_release')

        # Removing M2M table for field classifiers on 'Release'
        db.delete_table('packages_release_classifiers')

        # Deleting model 'ReleaseFile'
        db.delete_table('packages_releasefile')

        # Deleting model 'ReleaseURI'
        db.delete_table('packages_releaseuri')

        # Deleting model 'ReleaseRequire'
        db.delete_table('packages_releaserequire')

        # Deleting model 'ReleaseProvide'
        db.delete_table('packages_releaseprovide')

        # Deleting model 'ReleaseObsolete'
        db.delete_table('packages_releaseobsolete')

    models = {
        'packages.package': {
            'Meta': {'object_name': 'Package'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 28, 13, 38, 31, 248043)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 28, 13, 38, 31, 248163)'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'})
        },
        'packages.packageuri': {
            'Meta': {'unique_together': "(['package', 'uri'],)", 'object_name': 'PackageURI'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'package_links'", 'to': "orm['packages.Package']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '400'})
        },
        'packages.release': {
            'Meta': {'unique_together': "(('package', 'version'),)", 'object_name': 'Release'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'author_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'classifiers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'releases'", 'blank': 'True', 'to': "orm['packages.TroveClassifier']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 28, 13, 38, 31, 250204)', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'download_uri': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'maintainer_email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 28, 13, 38, 31, 250319)'}),
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
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime(2012, 1, 28, 13, 38, 31, 249244)', 'db_index': 'True'}),
            'digest': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'downloads': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '512'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime(2012, 1, 28, 13, 38, 31, 249368)'}),
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