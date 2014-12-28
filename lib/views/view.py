import xbmcgui
import xbmc
import xbmcvfs

import os
import subprocess
import thread
import threading
from threading import Thread
from lib import utils
from base import DialogBase, WinBase
from loginWin import LoginWin

from artistDialog import ArtistDialog
from albumDialog import AlbumDialog

def draw_mainwin(win, app, results=None):
    frame = win.handle.getProperty('frame')
    if frame == "Settings":
        #print "Drawmain: No lists to draw on settings Page"
        win.handle.setFocusId(1001)
    elif (frame == "Search") and (win.search_ever_used == False):
        print "drawmainwin - skipping all that and focusing 402"
        win.handle.setFocusId(402)
    else:
        print "Performing draw_mainwin"
        print "Search submitted: "+str(win.search_submitted)
        view = win.handle.getProperty('browseview')
        list_instance = app.get_var('view_matrix')[view]
        if win.search_submitted == True:
            list_instance.fresh = False
        win.list_id = app.get_var('list_matrix')[win.getProperty('browseview')]
        win.clist = win.getControl(win.list_id)
        print "Drawmainwin: view: %s list instance: %s list id: %s" % (view, list_instance.name, str(win.list_id))
        win.make_visible(300, win.list_id)
        list_instance.make_active(results=results)
        if (win.search_submitted == False) and (frame == "Search"):
            win.handle.setFocusId(402)
            print "skipped setting focus on content list"
        else:
            win.setFocusId(win.list_id)
        if list_instance.pos:
            print "List position: "+str(list_instance.pos)
            win.clist.selectItem(list_instance.pos)
        win.search_submitted = False
        for index in range(win.clist.size()):
            li = win.clist.getListItem(index)
            if list_instance.type == "album":
                url = li.getProperty('thumb_url')
                thread.start_new_thread(load_album_thumb, (li, app, url))
            elif list_instance.type == "artist":
                artist_id = li.getProperty('artist_id')
                if not artist_id in app.cache.artist:
                    if artist_id == 'Art.0':
                        #print "detected artist 0 case!"
                        url = app.img.default_artist_img
                        genre = ""
                    else:
                        thread.start_new_thread(load_artist_thumb, (li, artist_id, app))
                        thread.start_new_thread(load_artist_genre, (li, artist_id, app))
                else:
                    if artist_id == 'Art.0':
                        #print "detected artist 0 case!"
                        url = app.img.default_artist_img
                        genre = ""
                    else:
                        thread.start_new_thread(get_artist_image_from_cache, (li, artist_id, app))
                        thread.start_new_thread(get_artist_genre_from_cache, (li, artist_id, app))
                    #elif frame == "Search":
                    #	print "drawmainwin - skipping all that and focusing 201"
                    #	win.handle.setFocusId(201)

#threadsafe wrapper for fetching and loading album thumbs
def load_album_thumb(li, app, url):
    li.setThumbnailImage(os.path.join(app.__addon_data__, app.img.handler(url, 'small', 'album')))

#threadsafe wrapper for image loading
def get_artist_image_from_cache(li, artist_id, app):
    if len(app.cache.artist[artist_id]['thumb_url']) > 5:
        url = app.cache.artist[artist_id]['thumb_url']
        li.setThumbnailImage(os.path.join(app.__addon_data__, app.img.handler(url, 'small', 'artist')))
    else:
        url = app.img.identify_artist_thumb(artist_id)
        if url:
            app.cache.artist[artist_id]['thumb_url'] = url
            li.setThumbnailImage(os.path.join(app.__addon_data__, app.img.handler(url, 'small', 'artist')))

def get_artist_genre_from_cache(li, artist_id, app):
    if app.cache.artist[artist_id]['style']:
        li.setLabel2(app.cache.artist[artist_id]['style'])
    else:
        g_id = app.api.get_artist_genre(artist_id)
        if g_id:
            if not (g_id in app.cache.genre_dict__):
                results = app.api.get_genre_detail(g_id)
                app.cache.genre_dict__[g_id] = results["name"]
                app.cache.genre_modified = True
                print "** Added missing genre "+g_id+" to genre cache ** "+results["name"]
            li.setLabel2(app.cache.genre_dict__[g_id])
            app.cache.artist[artist_id]['style'] = app.cache.genre_dict__[g_id]


def load_artist_thumb(li, artist_id, app):
    url = app.img.identify_artist_thumb(artist_id)
    if url:
        app.cache.artist[artist_id]['thumb_url'] = url
        li.setThumbnailImage(os.path.join(app.__addon_data__, app.img.handler(url, 'small', 'artist')))

def load_artist_genre(li, artist_id, app):
    g_id = app.api.get_artist_genre(artist_id)
    if g_id:
        li.setLabel2(app.cache.genre_dict__[g_id])
        app.cache.artist[artist_id]['style'] = app.cache.genre_dict__[g_id]


def draw_playlist_sublist(win, app, thing):
    #print "Draw playlist_sublist"

    cache = app.cache.playlist
    win.dlist = win.getControl(3651)
    win.dlist.reset()
    if win.manage_playlist_detail(app.cache.playlist, thing, thing['playlist_id']):
        #win.dlist = win.getControl(3651)
        #win.dlist.reset()
        liz = app.windowtracklist.get_playlist_litems(cache, thing['playlist_id'])
        for item in liz:
            win.dlist.addItem(item)
        ###win.sync_playlist_pos()
        #win.make_visible(3651)
    else:
        #print "resetting list"
        win.dlist.reset()
    win.make_visible(3651)

    def onAction(self, action):
        #print str(action.getId())
        #print type(action)
        if action.getId() == 7:
            if self.getFocus() == self.name:
                self.setFocus(self.pswd)
            elif self.getFocus() == self.pswd:
                self.setFocus(self.butn)
            elif self.getFocusId() == 22:
                self.app.set_var('exiting', False)
                self.close()
                self.name_txt = self.name.getText()
                self.pswd_txt = self.pswd.getText()
            else: pass
        elif action.getId() == 18:
            if self.getFocus() == self.name:
                self.setFocus(self.pswd)
            elif self.getFocus() == self.pswd:
                self.setFocus(self.butn)
            elif self.getFocus() == self.butn:
                self.setFocus(self.name)
            else: pass
        elif action.getId() == 10:
            print "ID 10 key - ESC"
            self.app.set_var('exiting', True)
            self.close()
            utils.goodbye_while_logged_out(self.app)
        #elif action.getId() == 92:
        #	self.app.set_var('exiting', True)
        #	self.close()
        #	utils.goodbye_while_logged_out(self.app)
        else:
            pass

    def onFocus(self, control):
        if control == 3001:
            self.name_select.setVisible(True)
            self.pswd_select.setVisible(False)
        elif control == 3002:
            self.name_select.setVisible(False)
            self.pswd_select.setVisible(True)
        elif control == 22:
            self.name_select.setVisible(False)
            self.pswd_select.setVisible(False)
        else: pass


class MainWin(WinBase):

    def __init__(self, *args, **kwargs):
        WinBase.__init__(self, *args)
        #print "running _init_ for mainwin"
        self.app = kwargs.get('app')
        self.mem = self.app.mem
        self.cache = self.app.cache
        self.img = self.app.img
        self.api = self.app.api
        self.player = self.app.player
        self.playlist = self.app.playlist
        self.setup = False
        self.list_id = None #main list xml id
        self.playlist_list_id = None #playlist tracks xml id
        self.handle = None
        self.frame_label = None
        self.clist = None #main list for active view
        self.dlist = None #list for playlist tracks view
        self.mem_playlist_selection = None
        self.search_strings = ["Artists", "Albums", "Tracks", "Broadcast Radio"]
        self.search_types = ["artist", "album", "track", "radio"]
        self.search_views = ["search_artists", "search_albums", "search_tracks", "search_broadcast"]
        self.search_types_index = 1
        self.selected_search_type = self.search_types[self.search_types_index]
        self.search_submitted = False
        self.search_ever_used = False
        print "Default search type: "+self.selected_search_type


    def onInit(self):
        #print "running onInit for mainwin"
        self.handle = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        self.handle.setProperty("browseview", self.app.view_keeper['browseview'])
        self.handle.setProperty("frame", self.app.view_keeper['frame'])
        self.main()

    def main(self):

        self.handle.setProperty("full_name", self.mem.first_name+" "+self.mem.last_name)
        self.handle.setProperty("country", self.mem.catalog)
        self.handle.setProperty("logged_in", "true")
        self.handle.setProperty("username", self.mem.username)
        self.handle.setProperty("date_created", self.mem.date_created)
        self.handle.setProperty("account_type", self.mem.account_type)
        self.handle.setProperty("search_string", self.search_strings[self.search_types_index])
        self.frame_label = self.getControl(121)
        draw_mainwin(self, self.app)


    def onAction(self, action):

        if action.getId() == 7:		#enter/select
            self.manage_action(7)
        elif action.getId() == 3:    #up
            self.manage_action(3)
        elif action.getId() == 4:    #down
            self.manage_action(4)
        if action.getId() == 10:
            choice = True
            utils.goodbye(self.app, choice)
        elif action.getId() == 92:
            choice = True
            utils.goodbye(self.app, choice)
        else:
            pass


    def manage_action(self, id):

        if id == 3 or id == 4:

            if self.getFocusId() == 3650:
                #print "doing stuff since playlist list is focused"
                pos = self.clist.getSelectedPosition()
                if pos != self.mem_playlist_selection:
                    self.mem_playlist_selection = self.clist.getSelectedPosition()
                    thing = self.app.get_var('list')[self.mem_playlist_selection]
                    draw_playlist_sublist(self, self.app, thing)
            else:
                pass

        if id == 7:

            if self.getFocusId() == 301 or self.getFocusId() == 501: # sliding panel on browse and library
                draw_mainwin(self, self.app)
                self.app.view_keeper = {'browseview': self.getProperty('browseview'), 'frame': self.getProperty('frame')}

            elif self.getFocusId() == 101: # left nav panel
                draw_mainwin(self, self.app)
                self.app.view_keeper = {'browseview': self.getProperty('browseview'), 'frame': self.getProperty('frame')}

            elif self.getFocusId() == 1001: # sign in with different account on settings page
                # Logout happens here
                self.app.set_var('logged_in', False)
                try:
                    os.remove(self.mem.filename)
                except OSError, e:  ## if failed, report it back to the user ##
                    print ("Error: %s - %s." % (e.filename,e.strerror))
                self.player.stop()
                self.playlist.clear()
                self.close()

            elif self.getFocusId() == 1002: # clear app data button on settings page
                path = "special://home/userdata/addon_data/script.audio.rhapsody/.clean_me"
                f = xbmcvfs.File(path, 'w')
                f.close()
                if xbmcvfs.exists("special://home/userdata/addon_data/script.audio.rhapsody/.clean_me"):
                    w = xbmcgui.Dialog().ok("Success!!", "Rhapsody must restart now to finish deleting cache files")
                    choice = False
                    utils.goodbye(self.app, choice)

                    # should pop a yes no dialog that deletes then quits instead of a notice
                    print "Housekeeping trigger file created"
                else:
                    print "Something went wrong creating housekeeping trigger file"

            elif self.getFocusId() == 401:  # new search button - opens keyboard dialog for text entry
                #self.app.mem.access_token = "sdlkfjlskdjf"
                #print "corrupted the access token for testing"
                kb = xbmc.Keyboard()
                kb.setHeading('Enter Artist, Album, Track, or Station')
                kb.doModal()
                if (kb.isConfirmed()):
                    text = kb.getText()
                    print text
                    results = self.app.api.get_search_results(text, self.selected_search_type)
                    if results:
                        #utils.prettyprint(results)
                        print "got search results!"
                        self.search_submitted = True
                        self.search_ever_used = True
                        print "set search_submitted to true"
                        draw_mainwin(self, self.app, results=results)
                        print "called draw_mainwin"

            elif self.getFocusId() == 402:
                print "OnAction happening for control 402"
                self.search_types_index = (self.search_types_index + 1) % 4
                self.selected_search_type = self.search_types[self.search_types_index]
                print "Search type changed to "+self.selected_search_type
                self.handle.setProperty("search_string", self.search_strings[self.search_types_index])
                self.handle.setProperty("browseview", self.search_views[self.search_types_index])
                draw_mainwin(self, self.app, results=None)

            #elif self.getFocusId() == 3651:
            #	print "OnAction: Lets play this playlist"







    def onClick(self, control):
        print "onClick detected! Control is "+str(control)
        try:
            pos = self.clist.getSelectedPosition()
            thing = self.app.get_var('list')[pos]
            print thing
        except:
            print "onclick shouldn't be processed for empty lists"
            return
        #print "mainwin onClick: id: "+str(id)
        if (control == 3350) or (control == 3351) or (control == 3550) or (control == 3451):
            self.alb_dialog = AlbumDialog("album.xml", self.app.__addon_path__, 'Default', '720p', current_list=self.app.get_var('list'),
                                          pos=pos, cache=self.cache.album, alb_id=thing, app=self.app)
            self.alb_dialog.setProperty("review", "has_review")
            self.alb_dialog.doModal()
            self.alb_dialog.id = None
            if self.empty_list():
                draw_mainwin(self, self.app)
            self.clist.selectItem(self.alb_dialog.pos)
        if (control == 3352) or (control == 3452) or (control == 3551):
            self.artist_dialog = ArtistDialog("artist.xml", self.app.__addon_path__, 'Default', '720p', current_list=self.app.get_var('list'),
                                          pos=pos, cache=self.cache.artist, artist_id=thing, app=self.app)
            self.artist_dialog.setProperty("review", "has_review")
            self.artist_dialog.doModal()
            self.artist_dialog.id = None
            if self.empty_list():
                draw_mainwin(self, self.app)
            self.clist.selectItem(self.artist_dialog.pos)

        #self.cache.save_album_data()

        elif control == 3353 or control == 3453 or control == 3950:
            self.start_playback(control)

        elif control == 3650:
            #self.manage_playlist_detail(thing['playlist_id'])
            pass

        elif control == 3651:
            print "Tring to play playlist"
            #thing = self.app.get_var('list')[pos]
            self.start_playback(control)


    def start_playback(self, id):

        view = self.handle.getProperty('browseview')
        list_instance = self.app.get_var('view_matrix')[view]
        print list_instance.name
        #utils.prettyprint(list_instance.data[self.mem_playlist_selection])
        if id == 3651:  #attempting to play member playlist
            self.player.now_playing = {'pos': 0, 'type':'playlist', 'item':list_instance.data[self.mem_playlist_selection]['tracks'], 'id':list_instance.name}
        else:
            self.player.now_playing = {'pos': 0, 'type':'playlist', 'item':list_instance.data, 'id':list_instance.name}  #['data']}
        self.player.build()
        if id == 3353 or id == 3453 or id == 3950:
            self.player.now_playing['pos'] = self.clist.getSelectedPosition()
        elif id == 3651:
            self.player.now_playing['pos'] = self.dlist.getSelectedPosition()
        #xbmc.executebuiltin("XBMC.Notification(Rhapsody, Fetching song..., 5000, %s)" %(self.app.__addon_icon__))
        #track = self.player.add_playable_track(0)
        #if not track:
        #	xbmc.executebuiltin("XBMC.Notification(Rhapsody, Problem with this song. Aborting..., 2000, %s)" %(self.app.__addon_icon__))
        #	print "Unplayable track. Can't play this track"
        #	#player.stop()
        #	return False
        #self.player.get_session()
        thread.start_new_thread(self.app.player.get_session, () )
        self.player.playselected(self.player.now_playing['pos'])
        #xbmc.executebuiltin("XBMC.Notification(Rhapsody, Playback started, 2000, %s)" %(self.app.__addon_icon__))
        if id == 21:
            self.clist.selectItem(self.playlist.getposition())
            self.setFocusId(3353)


    def onFocus(self, control):
        #print("onfocus(): control %i" % control)
        if self.getFocusId() == 3650:
            #print "doing stuff since playlist list is focused"
            pos = self.clist.getSelectedPosition()
            if pos != self.mem_playlist_selection:
                self.mem_playlist_selection = self.clist.getSelectedPosition()
                thing = self.app.get_var('list')[self.mem_playlist_selection]
                draw_playlist_sublist(self, self.app, thing)


    def make_visible(self, *args):
        for item in args:
            self.getControl(item).setVisible(True)


    def empty_list(self):
        if self.clist.size() < 2:
            #print "window list is empty.. redrawing"
            return True


    def sync_playlist_pos(self):
        try:
            if self.player.now_playing['id'] == 'toptracks':
                print "syncing playlist pos because player.now_playing id is 'toptracks'"
                self.clist.selectItem(self.playlist.getposition())
                self.toptracks.pos = self.playlist.getposition()
            elif self.player.now_playing['id'] == self.alb_dialog.id:
                print "syncing playlist pos because player.now_player id is current album id"
                self.alb_dialog.clist.selectItem(self.playlist.getposition())
            elif self.player.now_playing['id'] == 'playlist':
                print "syncing playlist pos because player.now_playing id is 'playlist'"
                self.dlist.selectItem(self.playlist.getposition())
                self.toptracks.pos = self.playlist.getposition()
        except:
            print "Didn't need to sync playlist position"
            pass



    def manage_playlist_detail(self, cache, playlist, pl_id):
        #alb_id = playlist["album_id"]
        if playlist["tracks"] == {}:
            # try to get info from cached album data
            if cache.has_key(pl_id) and (cache[pl_id]['tracks'] != {}):
                print "Using tracklist from cached album data"
                return True
            else:
                print "Getting playlist tracklist from Rhapsody"
                results = self.api.get_playlist_details(pl_id)
                if results:
                    #playlist["label"] = results["label"]
                    playlist["tracks"] = results
                    #playlist["style"] = results["primaryStyle"]
                    return True
                else:
                    print "Playlist contains no tracks!"
                    return False
        else:
            print "Using playlist tracks from data in memory"
            return True