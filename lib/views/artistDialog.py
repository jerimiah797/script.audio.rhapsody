import xbmcgui
import xbmc
import xbmcvfs

import os
import subprocess
import thread

from base import DialogBase
from lib.cache_new import newCache


class ArtistDialog(DialogBase):

    def __init__(self, *args, **kwargs):
        DialogBase.__init__(self, *args)
        self.current_list = kwargs.get('current_list')
        self.cache = kwargs.get('cache')
        self.id = kwargs.get('artist_id')
        self.pos = kwargs.get('pos')
        self.app = kwargs.get('app')
        self.win = self.app.win
        self.api = self.app.api
        self.img = self.app.img
        self.img_dir = self.app.__addon_path__+'/resources/skins/Default/media/'
        self.listcontrol_id = 3150
        self.list_ready = False
        self.thr1 = {}
        self.thr2 = {}
        self.thr3 = {}
        self.toptracks = None
        self.tracks_ready=False



    def onInit(self):
        self.view = self.win.handle.getProperty('browseview')
        self.list_instance = self.app.get_var('view_matrix')[self.view]
        self.clist = self.getControl(self.listcontrol_id)
        self.app.set_var('alb_dialog_id', self.id)

        self.show_info(self.id, self.cache)


    def show_info(self, artist_id, cache):

        def get_art(self, cache, artist):
            static_id = self.id[:]
            #print "Get art for "+static_id
            self.manage_artwork(cache, artist)
            if static_id == self.id:
                self.getControl(7).setImage(artist["bigthumb"])
            #self.manage_windowtracklist(cache, artist)
            else:
                pass
            #print "********* got image but not showing it right now ******"

        def get_bio(self, cache, artist):
            static_id = self.id[:]
            #print "Get review for "+self.id
            self.manage_review(cache, artist)
            if static_id == self.id:
                #print self.id
                self.getControl(14).setText(artist["bio"])
            else:
                pass
            #print "********* got review but not showing it right now ******"

        def get_details(self, cache, artist):
            static_id = self.id[:]
            #print "Get details for "+self.id
            #self.manage_details(cache, artist)
            if static_id == self.id:
                self.manage_windowtracklist(cache, artist)
                self.tracks_ready=True
                self.getControl(10).setLabel(artist["style"])
                #self.getControl(10).setLabel(artist["label"])
                #self.getControl(6).setLabel(artist["tags"]+album['type'])
            else:
                pass
            #print "********* got details but not showing it right now ******"

        self.list_ready = False
        artist = cache[artist_id]
        self.reset_fields()
        #self.clearList()
        self.clist.reset()
        self.getControl(11).setText(artist["name"])
        self.getControl(13).setLabel(artist["style"])
        #self.getControl(8).setLabel(artist["album_date"])
        thread.start_new_thread(get_art, (self, cache, artist))
        thread.start_new_thread(get_bio, (self, cache, artist))
        thread.start_new_thread(get_details, (self, cache, artist))
        #thread.start_new_thread(self.manage_windowtracklist, (cache, artist))


    def show_next_album(self, offset):
        self.pos = (self.pos+offset) % len(self.current_list)
        self.id = self.current_list[self.pos]#['album_id']
        self.app.set_var('alb_dialog_id', self.id)
        self.show_info(self.id, self.cache)

    def manage_windowtracklist(self, cache, artist):
        print "ArtistDialog: Manage tracklist for gui list"

        self.list_ready = False
        self.toptracks=self.app.newCache.get_artist_top_tracks(artist['artist_id'])
        liz = self.app.windowtracklist.get_artist_litems(self.toptracks)
        for item in liz:
            self.clist.addItem(item)
        self.win.sync_playlist_pos()
        self.list_ready = True
        print "self.clist.size: "+str(self.clist.size())

    def onAction(self, action):
        #print action
        #print str(action.getId())
        if action.getId() == 1:                     # --- left arrow ---
            if self.getFocusId() == 31:
                self.show_next_album(-1)
        elif action.getId() == 2:                   # --- right arrow ---
            if self.getFocusId() == 31:
                self.show_next_album(1)
        elif action.getId() == 7:                   # --- Enter / Select ---
            if self.getFocusId() == 21:             # --- Play Button ---
                self.start_playback(self.getFocusId(), self.cache[self.id])
            elif self.getFocusId() == 27:           # --- Next Button ---
                self.show_next_album(1)
            elif self.getFocusId() == 26:           # --- Prev Button ---
                self.show_next_album(-1)
            elif self.getFocusId() == self.listcontrol_id:           # --- Tracklist ---
                self.start_playback(self.getFocusId(), self.cache[self.id])
            elif self.getFocusId() == 23:			# --- ADD TO QUEUE ---
                pass
            elif self.getFocusId() == 24:			# --- ADD TO PLAYLIST ---
                pass
            elif self.getFocusId() == 25:			# --- ADD TO LIBRARY ---
                r = self.api.add_album_to_library(self.id)
                if r:
                    xbmc.executebuiltin("XBMC.Notification(Rhapsody, Added to Library..., 2000, %s)" %(self.app.__addon_icon__))
                    #self.app.lib_albums.fresh = False
                    self.app.reinit_lists()
                else:
                    xbmc.executebuiltin("XBMC.Notification(Rhapsody, Add to Library failed..., 2000, %s)" %(self.app.__addon_icon__))
            else: pass
        elif action.getId() == 10:
            self.list_instance.pos = self.pos        # --- Esc ---
            self.close()
        elif action.getId() == 92:                  # --- Back ---
            self.list_instance.pos = self.pos
            self.close()
        elif action.getId() == 18:                  # --- Tab ---
            self.list_instance.pos = self.pos
            self.close()
        else:
            pass


    def start_playback(self, id, artist):
        print "Album dialog: start playback"
        if not self.now_playing_matches_artist_dialog():
            self.app.player.now_playing = {'pos': 0, 'type':'artist', 'item':self.toptracks, 'id':artist['artist_id']}
            self.app.player.build()
        if self.app.player.now_playing['type'] != 'artist':
            self.app.player.now_playing = {'pos': 0, 'type':'artist', 'item':self.toptracks, 'id':artist['artist_id']}
            self.app.player.build()
        if id == self.listcontrol_id:
            self.app.player.now_playing['pos'] = self.clist.getSelectedPosition()
        #xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song..., 5000, %s)" %(self.app.__addon_icon__))
        #self.app.player.get_session()
        thread.start_new_thread(self.app.player.get_session, () )
        self.app.player.check_session = False
        if id == 21:
            print "id is 21, let's select the playing track and focus the tracklist"
            while not self.tracks_ready:
                if self.list_ready:
                    return
                xbmc.sleep(100)
                print str(self.list_ready)+": waiting for list"
            self.app.player.now_playing = {'pos': 0, 'type':'album', 'item':self.toptracks, 'id':artist['artist_id']}
            self.app.player.build()
            self.app.player.playselected(self.app.player.now_playing['pos'])
            #xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started, 2000, %s)" %(self.app.__addon_icon__))
            self.clist.selectItem(self.app.playlist.getposition())
            self.setFocusId(self.listcontrol_id)
        else:
            self.app.player.playselected(self.app.player.now_playing['pos'])
        #xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started, 2000, %s)" %(self.app.__addon_icon__))
        #thread.start_new_thread(self.app.player.session_test, () )
        #remove this when session handling is complete

    def now_playing_matches_artist_dialog(self):
        try:
            if self.app.player.now_playing['id'] == self.id:
                return True
            else:
                return False
        except:
            return True


    def reset_fields(self):
        self.getControl(6).setLabel("")
        self.getControl(7).setImage("")
        self.getControl(8).setLabel("")
        self.getControl(10).setLabel("")
        self.getControl(11).setText("")
        self.getControl(13).setLabel("")
        self.getControl(14).setText("")


    def manage_review(self, cache, artist):
        artist_id = artist["artist_id"]
        if artist["bio"] == "":
            #print "Getting review from Rhapsody"
            bio = self.api.get_bio(artist['artist_id'])
            if not bio:
                print "No biography available for this artist either. :-("
                artist["bio"] = ""
            else:
                artist["bio"]=bio

        else:
            #print "Already have the biography in memory for this artist"
            pass

    def manage_details(self, cache, artist):
        self.tracks_ready = False
        alb_id = artist["album_id"]
        if artist["tracks"] == "":
            # try to get info from cached album data
            if cache.has_key(alb_id) and (cache[alb_id]['tracks'] != ""):
                #print "Using genre, track, and label from cached album data"
                self.tracks_ready = True
            else:
                #print "Getting genre, tracks and label from Rhapsody"
                results = self.api.get_album_details(alb_id)
                if results:
                    #album["label"] = results["label"]
                    artist["label"] = "Unknown Label"
                    artist["tracks"] = results["tracks"]
                    artist["genre_id"] = results["tracks"][0]["genre"]["id"]
                    #album["style"] = results["primaryStyle"]
                    if not (artist["genre_id"] in self.app.cache.genre_dict__):
                        results = self.api.get_genre_detail(artist["genre_id"])
                        self.app.cache.genre_dict__[artist["genre_id"]] = results["name"]
                        self.app.cache.genre_modified = True
                        print "** Added missing genre "+artist["genre_id"]+" to genre cache ** "+results["name"]
                    artist["style"] = self.app.cache.genre['genredict'][artist['genre_id']]
                    self.tracks_ready = True
                else:
                    print "Album Detail api not returning response"
                    self.tracks_ready = True

        else:
            #print "Using genre, track, and label from cached album data"
            self.tracks_ready = True
            pass

    def manage_artwork(self, cache, artist):
        artist_id = artist["artist_id"]
        if os.path.isfile(cache[artist_id]['bigthumb']):
            return
        else:
            if not artist['thumb_url']:
                full_filename = self.img.handler(artist['thumb_url'], 'large', 'artist')
                print full_filename
            else:
                url = self.img.identify_largest_image(artist_id, "artist")
                bigthumb = self.img.handler(url, 'large', 'artist')
                full_filename = os.path.join(self.img.base_path, bigthumb)
            artist["bigthumb"] = full_filename



