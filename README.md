rhapsody-xbmc
=============

XMBC addon for the Rhapsody music service. Uses the new public developer API (aka Motorhead API).


Installation:

1) Install XBMC 12 or 13 

2) clone the repo to your local user XBMC addons folder.
    Windows: c:\Users\<username>\AppData\Roaming\XBMC\addons

2a) rename the folder from rhapsody-xbmc to script.audio.rhapsody

INSTRUCTIONS FOR CONFLUENCE ONLY: (See below for all other skins)
    
3) Copy the default skin folder (skin.confluence) from the main program directory to the user addons folder so you can modify it safely.
    Windows: C:\Program Files (x86)\XBMC\addons
    
4) Copy the 3 fonts in script.audio.rhapsody to the fonts folder inside \addons\skin.confluence\

5) Replace the Font.xml file in the skin.confluence folder with the one in script.audio.rhapsody\resources\

Skip to step 6

**************** FOR ALL OTHER SKINS:
    
3) Copy the 3 fonts in script.audio.rhapsody to the fonts folder inside \addons\skin.the_name_of_the_skin\

4) Open the Font.xml file in script.audio.rhapsody\resources\ in a text editor. Copy to the clipboard the xml starting with the "Normal Fonts (rhapsody)" starting at line 4, down including the closing font tag around line 115, right before there's a comment "Normal Fonts" .  

5) Open the Fonts.xml file in the skin folder you are installing Rhapsody in (\addons\skin.the_name_of_the_skin\720p\font.xml). Paste the xml from the previous step into the file, right below the first <fontset> tag near the top of the file. Save the file. 

***************************



6) Launch XBMC and then launch the plugin  (Select Music, then Addons, then Rhapsody). 

7) Sign in, then use the arrow keys, enter key, and delete key for navigation, select, and back. Tab toggles the visualizer. 

Working: Popular albums, New Releases, Popular Tracks, Library Albums, Listening History

Still to do: Playlists, Search, Queue, Radio, Artist Pages for Browse and Library, automatic font installation for any skin

Special features: Quick browse all albums in a category while in the album detail view. Press 'down' to enable quicknav, then left / right for previous/next album in current list. 
