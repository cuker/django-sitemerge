# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContentMergeBatch'
        db.create_table('sitemerge_contentmergebatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site_merge_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitemerge.SiteMergeProfile'])),
        ))
        db.send_create_signal('sitemerge', ['ContentMergeBatch'])

        # Adding model 'SiteMergeProfile'
        db.create_table('sitemerge_sitemergeprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('merge_action', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=10)),
            ('scheduled_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('completion_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_ids', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('site_field', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('log', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('src_site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sitemergeprofile_sources', to=orm['sites.Site'])),
            ('dst_site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sitemergeprofile_destinations', to=orm['sites.Site'])),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal('sitemerge', ['SiteMergeProfile'])

        # Adding field 'ContentMerge.batch'
        db.add_column('sitemerge_contentmerge', 'batch',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitemerge.ContentMergeBatch'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ContentMergeBatch'
        db.delete_table('sitemerge_contentmergebatch')

        # Deleting model 'SiteMergeProfile'
        db.delete_table('sitemerge_sitemergeprofile')

        # Deleting field 'ContentMerge.batch'
        db.delete_column('sitemerge_contentmerge', 'batch_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sitemerge.contentmerge': {
            'Meta': {'object_name': 'ContentMerge'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitemerge.ContentMergeBatch']", 'null': 'True', 'blank': 'True'}),
            'completion_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'dst_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contentmerge_destinations'", 'to': "orm['sites.Site']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'merge_action': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'object_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'scheduled_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'scheduled_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'site_field': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'src_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contentmerge_sources'", 'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '10'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'sitemerge.contentmergebatch': {
            'Meta': {'object_name': 'ContentMergeBatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_merge_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitemerge.SiteMergeProfile']"})
        },
        'sitemerge.sitemergeprofile': {
            'Meta': {'object_name': 'SiteMergeProfile'},
            'completion_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'dst_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sitemergeprofile_destinations'", 'to': "orm['sites.Site']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'merge_action': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_ids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'scheduled_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'scheduled_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'site_field': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'src_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sitemergeprofile_sources'", 'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '10'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sitemerge']