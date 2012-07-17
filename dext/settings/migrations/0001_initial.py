# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Setting'
        db.create_table('settings_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('settings', ['Setting'])

    def backwards(self, orm):
        # Deleting model 'Setting'
        db.delete_table('settings_setting')

    models = {
        'settings.setting': {
            'Meta': {'object_name': 'Setting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'default': "''"})
        }
    }

    complete_apps = ['settings']