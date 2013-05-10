# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Album.scrobbled_name'
        db.add_column(u'library_album', 'scrobbled_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Genre.scrobbled_name'
        db.add_column(u'library_genre', 'scrobbled_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Artist.scrobbled_name'
        db.add_column(u'library_artist', 'scrobbled_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Track.scrobbled_name'
        db.add_column(u'library_track', 'scrobbled_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Album.scrobbled_name'
        db.delete_column(u'library_album', 'scrobbled_name')

        # Deleting field 'Genre.scrobbled_name'
        db.delete_column(u'library_genre', 'scrobbled_name')

        # Deleting field 'Artist.scrobbled_name'
        db.delete_column(u'library_artist', 'scrobbled_name')

        # Deleting field 'Track.scrobbled_name'
        db.delete_column(u'library_track', 'scrobbled_name')


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
            'scrobbled_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'total_tracks': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'library.artist': {
            'Meta': {'object_name': 'Artist'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'scrobbled_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'library.genre': {
            'Meta': {'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'scrobbled_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
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
            'scrobbled_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'track_number': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['library']