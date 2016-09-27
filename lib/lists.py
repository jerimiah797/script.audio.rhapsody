import time
import pickle

import xbmcgui


class ContentList(object):
    # handle new releases, top albums, artist discography, library album list, etc.
    def __init__(self, type, name, filename, app):

        self.data = []
        self.liz = []
        self.built = False
        self.fresh = False
        self.pos = 0
        self.timestamp = time.time()
        self.type = type
        self.name = name
        self.filename = filename
        self.app = app
        self.win = self.app.win
        self.cache = self.app.cache
        self.img = self.app.img
        self.api = self.app.api
        self.raw = None
        print 'Instantiating ' + self.name
        if (self.name == "srch_albums") or (self.name == "srch_artists") or (self.name == "srch_tracks") or (
                    self.name == "srch_brdcst"):
            self.built = True
            self.fresh = True

    # def fresh(self):
    #	return True

    def make_active(self, results=None):
        if (self.app.get_var('last_rendered_list') == self.name) and self.win.getListSize() > 2:
            #print "Window already has that list in memory. Skipping list building"
            return
        #print "ContentList: make active " +self.name
        #print "current frame: "+self.win.getProperty('frame')
        #print "current view: "+self.win.getProperty('browseview')
        #print "Built: "+str(self.built)
        #print "Fresh: "+str(self.fresh)
        if (self.name == "hist_tracks"):
            self.build()
        elif self.built and self.fresh:
            #print "doing simple list building for mainwin"
            self.build_winlist()
        else:
            #print "Doing full data fetch and list building for mainwin"
            self.build(results=results)
        self.app.set_var('last_rendered_list', self.name)
        self.app.set_var('list', self.data)


    def build(self, results=None):
        #print "ContentList: build (full)"
        if results is None:
            results = self.download_list()
        if results:
            self.ingest_list(results)
            self.fresh = True
        #self.win.search_submitted = False
        else:
            #print "Couldn't get info from servers about "+self.name
            pass

    def save_raw_data(self, data):
        jar = open(self.filename, 'wb')
        pickle.dump(data, jar)
        jar.close()
        print self.name + " info cache saved to disk."

    def download_list(self):
        #print "Download_list. self.filename: "+self.filename
        try:
            pkl_file = open(self.filename, 'rb')
            self.raw = pickle.load(pkl_file)
            pkl_file.close()
            print "Loaded cache file from disk"
            r = self.raw
        except:
            print "No list cache file found on disk. Let's download it"
            d = {'newreleases': self.api.get_new_releases,
                 'topalbums': self.api.get_top_albums,
                 'topartists': self.api.get_top_artists,
                 'toptracks': self.api.get_top_tracks,
                 'lib_albums': self.api.get_library_albums,
                 'lib_artists': self.api.get_library_artists,
                 'hist_tracks': self.api.get_listening_history,
                 'lib_playlists': self.api.get_library_playlists,
                 'lib_playlists': self.api.get_library_playlists,
                 #'lib_tracks':    api.get_library_artist_tracks,
                 #'lib_stations':  api.get_library_stations,
                 #'lib_favorites': api.get_library_favorites,  #'lib_favorites': api.get_library_favorites,
            }
            r = d[self.name]()
        #self.save_raw_data(r)
        #utils.prettyprint(r)
        return r

    def ingest_list(self, results):

        print "Processing %s list containing %s items." % (self.type, str(len(results)))
        self.win.clist.reset()
        self.liz = []
        self.data = []

        __ = {}

        d = {'album': self.cache.album,
             'artist': self.cache.artist,
             'playlist': self.cache.playlist,
             'track': __,
             'station': __}

        store = d[self.type]
        recycle = {}

        for i, item in enumerate(results):
            id = item['id']
            if self.type == 'album':
                infos = self.process_album(i, item, recycle)
                if infos:
                    self.data.append(infos[self.type]['album_id'])
            elif self.type == 'artist':
                infos = self.process_artist(i, item, recycle)
                self.data.append(infos[self.type]['artist_id'])
            elif self.type == 'track':
                infos = self.process_track(i, item, recycle)
                self.data.append(infos[self.type])
            elif self.type == 'playlist':
                infos = self.process_playlist(i, item, recycle)
                self.data.append(infos[self.type])
            if infos:
                self.liz.append(infos['listitem'])
                self.add_lizitem_to_winlist(infos['listitem'])
                if not id in store:
                    store[id] = infos[self.type]
            del infos

        self.built = True

    #utils.prettyprint(self.data)



    def process_album(self, count, item, data):
        #data = {}
        #thumb = self.img.handler(item["images"][0]["url"], 'small', 'album')
        thumb = self.img.default_album_img
        data = {}
        try:
            data['album'] = {'album_id': item["id"],
                             'album': item["name"],
                             'thumb': thumb,
                             'thumb_url': item["images"][0]["url"],
                             'album_date': time.strftime('%B %Y', time.localtime(int(item["released"]) / 1000)),
                             'orig_date': "",
                             'label': "",
                             'type': item['type']['name'],
                             'explicit': self.determine_explicit(item),
                             'tags': self.concat_tags(item),
                             'review': "",
                             'bigthumb': "",
                             'tracks': "",
                             'style': "",
                             'genre_id': "",
                             'artist': item["artist"]["name"],
                             'list_id': count,
                             'artist_id': item["artist"]["id"]}
            #print data["album"]["thumb_url"]
            data['listitem'] = xbmcgui.ListItem(item["name"], item["artist"]["name"], '', thumb)
            data['listitem'].setProperty('thumb_url', data["album"]["thumb_url"])
            if data['album']['explicit']:
                data['listitem'].setProperty('explicit', "True")
            else:
                data['listitem'].setProperty('explicit', "False")
            return data
        except:
            print "Problem processing %s, %s" % (item['id'], item['name'])
            return False

    def determine_explicit(self, item):
        if 'Explicit' in item['tags']:
            #print "item has Explicit tag!"
            return True
        else:
            return False

    def concat_tags(self, item):
        s = ""
        for tag in item['tags']:
            #print "item has Explicit tag!"
            s += tag
            s += ", "
        return s


    def process_artist(self, count, item, data):

        bigthumb = self.img.default_artist_img

        data['artist'] = {'artist_id': item["id"],
                          'name': item["name"],
                          'thumb': "",
                          'thumb_url': "",
                          'bio': "",
                          'bigthumb': "",
                          'toptracks': "",
                          'style': "",
                          'list_id': count}
        data['listitem'] = xbmcgui.ListItem(item["name"], data["artist"]["style"], '', bigthumb)
        data['listitem'].setProperty('artist_id', data["artist"]["artist_id"])
        return data

    def process_track(self, count, item, data):
        #data = {}
        #thumb = img.handler(item["images"][0]["url"], 'small', 'album')
        thumb = 'none.png'
        data['track'] = {'id': item["id"],
                         'name': item["name"],
                         'thumb': thumb,
                         'genre_id': item['genre']['id'],
                         'duration': item['duration'],
                         'playbackSeconds': item['duration'],
                         'style': '',
                         'previewURL': item['sample'],
                         'list_id': count,
                         'trackIndex': count + 1}
        data['track']['album'] = {'id': item['album']['id'],
                                  'name': item['album']['name'],
                                  'displayAlbumName': item['album']['name']
        }
        data['track']['artist'] = {'id': item['artist']['id'],
                                   'name': item['artist']['name'],
                                   'displayArtistName': item['artist']['name']
        }
        data['listitem'] = xbmcgui.ListItem(item["name"], item["artist"]["name"])
        info = {
            "title": item["name"],
            "album": item['album']['name'],
            "artist": item["artist"]["name"],
            "duration": item['duration'],
            "tracknumber": count + 1,
        }
        data['listitem'].setInfo("music", info)
        return data


    def process_playlist(self, count, item, data):
        #data = {}
        #thumb = self.img.handler('none.jpg', 'small', 'album')
        data['playlist'] = {'playlist_id': item["id"],
                            'name': item["name"],
                            'date_created': time.strftime('%B %Y', time.localtime(int(item["created"]) / 1000)),
                            'author': item['author'],
                            'tracks': {},
                            'track_count': 0,
                            'total_time': 0
        }
        data['listitem'] = xbmcgui.ListItem(item["name"], data['playlist']['date_created'], "", "none.png")
        return data

    def add_lizitem_to_winlist(self, li):
        self.win.clist.addItem(li)

    def build_winlist(self):
        print "ContentList: build_winlist"
        self.win.clist.reset()
        for i, item in enumerate(self.liz):
            self.win.clist.addItem(self.liz[i])


    def save_data(self):
        self.cache.save_album_data()
        self.cache.save_artist_data()


class WindowTrackList(object):
    def __init__(self):
        pass

    # handle albums, playlists

    def get_litems(self, tracklist):
        print "Tracklist: adding tracks for gui list"
        mylist = []
        i = None
        for i, item in enumerate(tracklist):
            newlistitem = xbmcgui.ListItem(path="http://dummyurl.org")
            newlistitem.setInfo('music', {'tracknumber': int(i) + 1,
                                          'title': item["name"],
                                          'duration': item["duration"]
            })
            mylist.append(newlistitem)
        if i:
            # print "Showing "+str(i+1)+" tracks"
            pass
        return mylist

