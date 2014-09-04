import xbmc
import xbmcgui
import time
import thread
import os
from lib import view
from lib import utils

class Player(xbmc.Player):

	def __init__(self, *args, **kwargs):
		xbmc.Player.__init__( self )
		self.app = kwargs.get('app')
		self.win = self.app.win
		self.cache = self.app.cache
		self.img = self.app.img
		self.api = self.app.api
		self.playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC) #player=self, app=self.app, api=self.api, img=self.img)
		self.now_playing = {'pos': 0, 'type': None, 'item':[], 'id': None}
		self.session = []
		self.session_lock = False
		self.check_session = True
		self.notify = Notifier()
		#self.now_playing['item']['album_id'] = 'blank'
		self.onplay_lock = False

	def onPlayBackStarted(self):
		if not self.onplay_lock:
			self.onplay_lock = True
			#print "Locking playback routine to block multiple calls +++++++++++++++++++"
			self.win.sync_playlist_pos()
			pos = self.playlist.getposition()
			self.now_playing['pos'] = pos
			print "OnPlaybackStarted: Playing track "+str(pos+1)
			self.win.sync_playlist_pos()
			pos2 = self.playlist.getposition()
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				self.now_playing['pos'] = pos2
			thread.start_new_thread(self.notify.report_playback, (self, self.api))
			# update listening history if current view
			if self.win.getProperty('browseview') == "history_tracks":
				self.app.hist_tracks.build()
				print "OnPlaybackStarted: rebuilt history tracklist"
				view.draw_mainwin(self.win, self.app)
			xbmc.sleep(20)
			if self.check_session == True:
				thread.start_new_thread(self.validate_session, (self, self.session) )
			self.check_session = True
			self.onplay_lock = False
		else:
			#print "--------- blocked an extra play action from XBMC --------"
			pass


	def onPlayBackResumed(self):
		if not self.onplay_lock:
			self.onplay_lock = True
			self.win.sync_playlist_pos()
			pos = self.playlist.getposition()
			self.now_playing['pos'] = pos
			print "OnPlaybackResumed: Playing track "+str(pos+1)
			self.win.sync_playlist_pos()
			pos2 = self.playlist.getposition()
			#print "pos: "+str(pos)+" pos2: "+str(pos2)
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				self.now_playing['pos'] = pos2
				#self.add_playable_track(1)
				#self.add_playable_track(-1)
			thread.start_new_thread(self.notify.report_playback, (self, self.api))
			xbmc.sleep(20)
			if self.check_session == True:
				thread.start_new_thread(self.validate_session, (self, self.session) )
			self.check_session = True
			self.onplay_lock = False
		else:
			#print "--------- blocked an extra play action from XBMC --------"
			pass

	def onPlayBackEnded(self):
		print "onPlaybackEnded was detected!"
		thread.start_new_thread(self.notify.report_playback, (self, self.api))
		# update listening history if current view
		if self.win.getProperty('browseview') == "history_tracks":
			self.app.hist_tracks.build()
			print "OnPlaybackEnded: rebuilt history tracklist"
			view.draw_mainwin(self.win, self.app)

	def onPlayBackStopped(self):
		print "onPlaybackStopped was detected!"
		thread.start_new_thread(self.notify.report_playback, (self, self.api))
		#update listening history if current view
		if self.win.getProperty('browseview') == "history_tracks":
			self.app.hist_tracks.build()
			print "OnPlaybackStopped: rebuilt history tracklist"
			view.draw_mainwin(self.win, self.app)

	def onQueueNextItem(self):
		print "onQueueNextItem was detected!"


	def build(self):
		#print "Playlist: build playlist"
		self.playlist.clear()
		liz = self.now_playing['item']
		for i, track in enumerate(liz):
			#utils.prettyprint(track)
			#print "track "+str(i+1)+": "+track['name']
			#alb_id = track['albumId']
			alb_id = track['album']['id']
			try:
				thumb = os.path.join(self.img.base_path, self.img.handler(self.cache.album[alb_id]['thumb_url'], 'small', 'album'))
			except:
				thumb = "none.png"
			tid = track['id']
			#tid = i+1
			#print tid
			#print self.app.mem.access_token
			playurl = "plugin://script.audio.rhapsody/?track=%s&token=%s" % (tid, self.app.mem.access_token)
			#print playurl

			li = xbmcgui.ListItem(
	            track["name"],
	            path=playurl,
	            iconImage=thumb,
	            thumbnailImage=thumb
				)
			info = {
	            "title": track["name"],
	            "album": track["album"]["name"],
	            "artist": track["artist"]["name"],
	            "duration": track["duration"],
	            "tracknumber": i+1,
				}
			li.setInfo("music", info)
			li.setProperty('mimetype','audio/mp4')
			self.playlist.add(playurl, listitem=li)
		#xbmc.executebuiltin("XBMC.Notification(Rhapsody, Preparing to play..., 2000, %s)" %(self.app.__addon_icon__))


	def validate_session(self, s, session):
		valid = self.api.validate_session(session)
		if valid == None:
			#pop the "Are you still listening?" Yes/No dialog
			print "Session timed out. Are you still listening?"
			xbmc.sleep(5000)  #wait a few seconds so we don't stomp on playstop notification values
			self.stop()
		elif valid:
			#print "Playback session validated."
			pass
		elif not valid:
			#pop "Playback stopped because you're streaming from somewhere else"
			print "Playback stopped because you're streaming from somewhere else"
			xbmc.sleep(5000) #wait a few seconds so we don't stomp on playstop notification values
			self.stop()
		else:
			print "Unexpected result validating session. Stopping playback"
			xbmc.sleep(5000) #wait a few seconds so we don't stomp on playstop notification values
			self.stop()
		return


	def get_session(self):
		#self.session_lock = True
		#time.sleep(5)
		print "Creating playback session."
		self.session = self.api.get_session()
		#time.sleep(2)
		#self.session_lock = False
		print "Created playback session."

	def session_test(self):
		count = 1
		while count <20:
			xbmc.sleep(5000)
			self.api.validate_session(self.session)
			count += 1
			



class Notifier():

	def __init__(self):
		self.current_track = None
		self.ztime = None
		self.duration = None
		self.time = None

	def report_playback(self, player, api):
		pos = player.playlist.getposition()
		#print player.now_playing['item'][pos]
		track_id = player.now_playing['item'][pos]['id']
		#print "report playback: "+track_id
		if self.current_track:
			#print "reporting stop event for current track"
			now = time.time()
			self.duration = int(now - self.time)
			#print "duration: "+str(self.duration)
			api.log_playstop(self.current_track, self.ztime, self.duration)
			#print "clearing current track info"
			self.current_track = None
			self.duration = None
			self.ztime = None
			self.time = None
		if player.isPlaying():
			#print "setting current track info and reporting play start event"
			self.current_track = track_id
			self.ztime = api.log_playstart(self.current_track)
			self.time = time.time()
