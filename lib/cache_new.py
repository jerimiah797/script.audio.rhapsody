import pickle
import time
import os
from rhapapi import Api

## sould be a cached wrapper for rhapapi

class newCache():
    def __init__(self, api):
        self.api=api
        self.album_review=dict()
        self.album_details=dict()
        self.album_images=dict()
        self.artist_images=dict()
        self.artist_genre=dict()
        self.new_releases=None
        self.top_albums=None
        self.top_artists=None
        self.artist_top_albums=dict()
        self.artist_top_tracks=dict()
        self.top_tracks=None
        self.genres=None
        self.genre_detail=dict()
        self.bio=dict()
        pass


    def get_album_review(self, album_id):
        if album_id in self.album_review:
            return self.album_review[album_id]
        else:
            data=self.api.get_album_review(album_id)
            if data:
                self.album_review[album_id] = data
            return data


    def get_album_details(self, album_id):
        if album_id in self.album_details:
            return self.album_details[album_id]
        else:
            data=self.api.get_album_details(album_id)
            if data:
                self.album_details[album_id] = data
            return data


    def get_album_images(self, album_id):
        if album_id in self.album_images:
            return self.album_images[album_id]
        else:
            data=self.api.get_album_images(album_id)
            if data:
                self.album_images[album_id] = data
            return data

    def get_artist_images(self, artist_id):
        if artist_id in self.artist_images:
            return self.artist_images[artist_id]
        else:
            data=self.api.get_artist_images(artist_id)
            if data:
                self.artist_images[artist_id] = data
            return data


    def get_artist_genre(self, artist_id):
        if artist_id in self.artist_genre:
            return self.artist_genre[artist_id]
        else:
            data=self.api.get_artist_genre(artist_id)
            if data:
                self.artist_genre[artist_id] = data
            return data


    def get_new_releases(self):
        if self.new_releases is not None:
            return self.new_releases
        else:
            data=self.api.get_new_releases()
            if data:
                self.new_releases=data
            return data


    def get_top_albums(self):
        if self.top_albums is not None:
            return self.top_albums
        else:
            data=self.api.get_top_albums()
            if data:
                self.top_albums=data
            return data


    def get_top_artists(self):
        if self.top_artists is not None:
            return self.top_artists
        else:
            data=self.api.get_top_artists()
            if data:
                self.top_artists=data
            return data

    def get_artist_top_albums(self, artist_id):
        if artist_id in self.artist_top_albums:
            return self.artist_top_albums[artist_id]
        else:
            data=self.api.get_artist_top_albums(artist_id)
            if data:
                self.artist_top_albums[artist_id] = data
            return data


    def get_artist_top_tracks(self, artist_id):
        if artist_id in self.artist_top_tracks:
            return self.artist_top_tracks[artist_id]
        else:
            data=self.api.get_artist_top_tracks(artist_id)
            if data:
                self.artist_top_tracks[artist_id] = data
            return data


    def get_top_tracks(self):
        if self.top_tracks is not None:
            return self.top_tracks
        else:
            data=self.api.get_top_tracks()
            if data:
                self.top_tracks=data
            return data


    def get_genres(self):
        if self.top_tracks is not None:
            return self.genres
        else:
            data=self.api.get_genres()
            if data:
                self.genres=data
            return data

    def get_genre_detail(self, g_id):
        if g_id in self.genre_detail:
            return self.genre_detail[g_id]
        else:
            data=self.api.get_genre_detail(g_id)
            if data:
                self.genre_detail[g_id] = data
            return data


    def get_bio(self, art_id):
        if art_id in self.bio:
            return self.bio[art_id]
        else:
            data=self.api.get_bio(art_id)
            if data:
                self.bio[art_id] = data
            return data


    def get_search_results(self, text, stype):
        return self.api.get_search_results(text,stype)
