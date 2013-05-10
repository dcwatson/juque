# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Artist'
        db.create_table(u'library_artist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('match_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('musicbrainz_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
        ))
        db.send_create_signal(u'library', ['Artist'])

        # Adding model 'Album'
        db.create_table(u'library_album', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('match_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('musicbrainz_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='albums', to=orm['library.Artist'])),
            ('artwork_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('artwork_path', self.gf('django.db.models.fields.TextField')()),
            ('total_tracks', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('release_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'library', ['Album'])

        # Adding model 'Genre'
        db.create_table(u'library_genre', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('match_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('musicbrainz_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
        ))
        db.send_create_signal(u'library', ['Genre'])

        # Adding model 'Track'
        db.create_table(u'library_track', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('match_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('musicbrainz_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tracks', to=orm['core.User'])),
            ('length', self.gf('django.db.models.fields.FloatField')()),
            ('bitrate', self.gf('django.db.models.fields.IntegerField')()),
            ('sample_rate', self.gf('django.db.models.fields.IntegerField')()),
            ('artist_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('album_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('genre_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('track_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('lyrics', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tracks', null=True, to=orm['library.Artist'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tracks', null=True, to=orm['library.Album'])),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tracks', null=True, to=orm['library.Genre'])),
            ('file_path', self.gf('django.db.models.fields.TextField')()),
            ('file_size', self.gf('django.db.models.fields.IntegerField')()),
            ('file_managed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('file_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('play_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'library', ['Track'])

        # Adding model 'PlayHistory'
        db.create_table(u'library_playhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(related_name='play_history', to=orm['library.Track'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='play_history', to=orm['core.User'])),
            ('date_played', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'library', ['PlayHistory'])


    def backwards(self, orm):
        # Deleting model 'Artist'
        db.delete_table(u'library_artist')

        # Deleting model 'Album'
        db.delete_table(u'library_album')

        # Deleting model 'Genre'
        db.delete_table(u'library_genre')

        # Deleting model 'Track'
        db.delete_table(u'library_track')

        # Deleting model 'PlayHistory'
        db.delete_table(u'library_playhistory')


    models = {
        u'core.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'library.album': {
            'Meta': {'object_name': 'Album'},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'albums'", 'to': u"orm['library.Artist']"}),
            'artwork_path': ('django.db.models.fields.TextField', [], {}),
            'artwork_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'total_tracks': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'library.artist': {
            'Meta': {'object_name': 'Artist'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'library.genre': {
            'Meta': {'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'library.playhistory': {
            'Meta': {'object_name': 'PlayHistory'},
            'date_played': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'play_history'", 'to': u"orm['library.Track']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'play_history'", 'to': u"orm['core.User']"})
        },
        u'library.track': {
            'Meta': {'object_name': 'Track'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tracks'", 'null': 'True', 'to': u"orm['library.Album']"}),
            'album_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tracks'", 'null': 'True', 'to': u"orm['library.Artist']"}),
            'artist_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'file_managed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file_path': ('django.db.models.fields.TextField', [], {}),
            'file_size': ('django.db.models.fields.IntegerField', [], {}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tracks'", 'null': 'True', 'to': u"orm['library.Genre']"}),
            'genre_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'lyrics': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tracks'", 'to': u"orm['core.User']"}),
            'play_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sample_rate': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'track_number': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['library']