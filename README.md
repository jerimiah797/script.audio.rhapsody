rhapsody-xbmc
=============

XMBC addon for the Rhapsody music service. Uses the new public developer API (aka Motorhead API). Only supports accounts with on-demand stream rights (no radio+ or unradio)


Installation:

1) Install XBMC 12 or 13 

2) clone the repo to your local user XBMC addons folder.

    Windows: 	C:\Users\<username>\AppData\Roaming\XBMC\addons
    Mac: 		/Users/<username>/Library/Application Support/XBMC/addons/
    Ubuntu:		/home/<username>/.xbmc/addons

3) Rename the folder from rhapsody-xbmc to script.audio.rhapsody

4) Launch XBMC and then launch the plugin  (Select Music, then Addons, then Rhapsody). 

5) Sign in, then use the arrow keys, enter key, and delete key for navigation, select, and back. Tab toggles the visualizer. 

Working: 

- Playback for Popular albums, New Releases, Popular Tracks, Library Albums, Listening History
- Sign in / out (restart rhapsody to update library, though)
- auto-update with git-pull at every quit
- Automatically install fonts
- Invoke visualizer manually
- Can browse playlists but can't play them yet
- Listening history page updates in real time during playback

Still to do: Playlists, Search, Queue, Radio, Artist Pages for Browse and Library, Genre browsing and filtering, library/playlist/queue management, 1080i skin support

Special features: Quick browse all albums in a category while in the album detail view. Press 'down' to enable quicknav, then left / right for previous/next album in current list. 
