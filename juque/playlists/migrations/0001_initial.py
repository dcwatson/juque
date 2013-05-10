# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Playlist'
        db.create_table(u'playlists_playlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='playlists', to=orm['core.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'playlists', ['Playlist'])

        # Adding model 'PlaylistTrack'
        db.create_table(u'playlists_playlisttrack', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('playlist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='playlist_tracks', to=orm['playlists.Playlist'])),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(related_name='playlist_tracks', to=orm['library.Track'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'playlists', ['PlaylistTrack'])

        # Adding unique constraint on 'PlaylistTrack', fields ['playlist', 'track']
        db.create_unique(u'playlists_playlisttrack', ['playlist_id', 'track_id'])

        # Adding unique constraint on 'PlaylistTrack', fields [u'id', 'order']
        db.create_unique(u'playlists_playlisttrack', [u'id', 'order'])

        # Adding model 'LivePlaylist'
        db.create_table(u'playlists_liveplaylist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='liveplaylists', to=orm['core.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('criteria', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ordering', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('limit', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'playlists', ['LivePlaylist'])


    def backwards(self, orm):
        # Removing unique constraint on 'PlaylistTrack', fields [u'id', 'order']
        db.delete_unique(u'playlists_playlisttrack', [u'id', 'order'])

        # Removing unique constraint on 'PlaylistTrack', fields ['playlist', 'track']
        db.delete_unique(u'playlists_playlisttrack', ['playlist_id', 'track_id'])

        # Deleting model 'Playlist'
        db.delete_table(u'playlists_playlist')

        # Deleting model 'PlaylistTrack'
        db.delete_table(u'playlists_playlisttrack')

        # Deleting model 'LivePlaylist'
        db.delete_table(u'playlists_liveplaylist')


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
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'albums'", 'null': 'True', 'to': u"orm['library.Artist']"}),
            'artwork_path': ('django.db.models.fields.TextField', [], {}),
            'artwork_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'release_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
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
        },
        u'playlists.liveplaylist': {
            'Meta': {'object_name': 'LivePlaylist'},
            'criteria': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'liveplaylists'", 'to': u"orm['core.User']"})
        },
        u'playlists.playlist': {
            'Meta': {'object_name': 'Playlist'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'playlists'", 'to': u"orm['core.User']"}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'playlists'", 'symmetrical': 'False', 'through': u"orm['playlists.PlaylistTrack']", 'to': u"orm['library.Track']"})
        },
        u'playlists.playlisttrack': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('playlist', 'track'), ('id', 'order'))", 'object_name': 'PlaylistTrack'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'playlist_tracks'", 'to': u"orm['playlists.Playlist']"}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'playlist_tracks'", 'to': u"orm['library.Track']"})
        }
    }

    complete_apps = ['playlists']