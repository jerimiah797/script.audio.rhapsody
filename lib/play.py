import xbmc
import xbmcgui
import time



class Player(xbmc.Player):

	def __init__(self, **kwargs):
		self.app = kwargs.get('app')
		self.win = self.app.win
		self.cache = self.app.cache
		self.img = self.app.img
		self.api = self.app.api
		self.playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC) #player=self, app=self.app, api=self.api, img=self.img)
		self.now_playing = {'pos': 0, 'type': None, 'item':[], 'id': None}
		self.session = {'valid': None}#, 'id': None}
		self.notify = Notifier()
		#self.now_playing['item']['album_id'] = 'blank'
		self.onplay_lock = False

	def onPlayBackStarted(self):
		if not self.onplay_lock:
			self.onplay_lock = True
			self.validate_session(self.session)
			self.win.sync_playlist_pos()
			pos = self.playlist.getposition()
			self.now_playing['pos'] = pos
			print "Playing track "+str(pos+1)
			self.add_playable_track(1)
			self.add_playable_track(-1)
			self.win.sync_playlist_pos()
			pos2 = self.playlist.getposition()
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				self.now_playing['pos'] = pos2
				self.add_playable_track(1)
				self.add_playable_track(-1)
			self.notify.report_playback(self, self.api)
			xbmc.sleep(2)
			self.onplay_lock = False
		else:
			print "--------- blocked an extra play action from XBMC --------"


	def onPlayBackResumed(self):
		if not self.onplay_lock:
			self.onplay_lock = True
			self.validate_session(self.session)
			self.win.sync_playlist_pos()
			pos = self.playlist.getposition()
			self.now_playing['pos'] = pos
			print "Playing track "+str(pos+1)
			self.add_playable_track(1)
			self.add_playable_track(-1)
			self.win.sync_playlist_pos()
			pos2 = self.playlist.getposition()
			#print "pos: "+str(pos)+" pos2: "+str(pos2)
			if pos != pos2:
				print "Oh wait! We're not playing track "+str(pos+1)+"!"
				print "Playing track "+str(pos2+1)
				print "There, fixed it for ya. "
				self.now_playing['pos'] = pos2
				self.add_playable_track(1)
				self.add_playable_track(-1)
			self.notify.report_playback(self, self.api)
			xbmc.sleep(2)
			self.onplay_lock = False
		else:
			print "--------- blocked an extra play action from XBMC --------"

	def onPlayBackEnded(self):
		print "onPlaybackEnded was detected!"
		self.notify.report_playback(self, self.api)

	def onPlayBackStopped(self):
		print "onPlaybackStopped was detected!"
		self.notify.report_playback(self, self.api)

	def onQueueNextItem(self):
		print "onQueueNextItem was detected!"


	def build(self):
		print "Playlist: build dummy playlist"
		self.playlist.clear()
		#liz = None
		#if self.now_playing['type'] == "album":
		#	liz = self.now_playing['item']
		#elif self.now_playing['type'] == 'playlist':
		#	liz = self.now_playing['item']
		liz = self.now_playing['item']
		for i, track in enumerate(liz):
			self.playlist.add(track['previewURL'], listitem=xbmcgui.ListItem(''))
		xbmc.executebuiltin("XBMC.Notification(Rhapsody, Preparing to play..., 2000, %s)" %(self.app.__addon_icon__))


	def add_playable_track(self, offset):
		print "Playlist: add playable track"
		circ_pos = (self.now_playing['pos']+offset)%self.playlist.size()
		print "Fetching track "+str(circ_pos+1)
		item = self.now_playing['item'][circ_pos]
		alb_id = item['albumId']
		try:
			thumb = self.img.base_path+self.img.handler(self.cache.album[alb_id]['thumb_url'], 'small', 'album')
		except:
			thumb = "none.png"
		#thumb = "none.png"
		tid = item['trackId']
		tname = self.playlist.__getitem__(circ_pos).getfilename()
		playurl = self.api.get_playable_url(tid)
		if not playurl:
			return False
		self.playlist.remove(tname)
		li = xbmcgui.ListItem(
	            item["name"],
	            path=item["previewURL"],
	            iconImage=thumb,
	            thumbnailImage=thumb
				)
		info = {
	            "title": item["name"],
	            "album": item["displayAlbumName"],
	            "artist": item["displayArtistName"],
	            "duration": item["playbackSeconds"],
	            "tracknumber": int(item["trackIndex"]),
				}
		li.setInfo("music", info)
		self.playlist.add(playurl, listitem=li, index=circ_pos)
		return True


	def validate_session(self, session):
		print "player.validate_session"
		valid = self.api.validate_session(session)
		if valid:
			return True
		else:
			#self.get_session()
			#return True
			self.stop()


	def get_session(self):
		print "player.get_session:"
		self.session = self.api.get_session()
		#print "Session:"+str(self.session)


class Notifier():

	def __init__(self):
		self.current_track = None
		self.ztime = None
		self.duration = None
		self.time = None

	def report_playback(self, player, api):
		pos = player.playlist.getposition()
		#print player.now_playing['item'][pos]
		track_id = player.now_playing['item'][pos]['trackId']
		#print "report playback: "+track_id
		if self.current_track:
			print "reporting stop event for current track"
			now = time.time()
			self.duration = int(now - self.time)
			print "duration: "+str(self.duration)
			api.log_playstop(self.current_track, self.ztime, self.duration)
			print "clearing current track info"
			self.current_track = None
			self.duration = None
			self.ztime = None
			self.time = None
		if player.isPlaying():
			print "setting current track info and reporting play start event"
			self.current_track = track_id
			self.ztime = api.log_playstart(self.current_track)
			self.time = time.time()
