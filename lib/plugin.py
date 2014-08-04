'''
    Rhaposdy XBMC Plugin
    Copyright (C) 2014 Jerimiah Ham

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


# call plugin like this: plugin://script.audio.rhapsody/?track=ABC&token=XYZ
        

import xbmc
import xbmcgui
import xbmcplugin
import cgi
import urllib
import urllib2
import json
import base64
import datetime
import time

def get_it(args):
  #BASEURL = "http://api.rhapsody.com/v1/"
  S_BASEURL = "https://api.rhapsody.com/v1/"
  #APIKEY = "22Q1bFiwGxYA2eaG4vVAGsJqi3SQWzmd"
  token = None

  #def parse_query(query, clean=True):
  def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    #if clean:
    #    q['mode'] = q.get('mode', 'main')
    #    q['play'] = q.get('play', '')
    return q

  plugin_url = args[0]
  plugin_handle = int(args[1])
  plugin_queries = parse_query(args[2][1:])

  #print('plugin url: ' + plugin_url)
  #print('plugin queries: ' + str(plugin_queries))
  #print('plugin handle: ' + str(plugin_handle))

  track = plugin_queries['track']
  token = plugin_queries['token']


  def __get_data_from_rhapsody(req, timeout):
    succeed = 0
    while succeed < 1:
      try:
        response = urllib2.urlopen(req, timeout=timeout)
        try:
          results = json.load(response)
          return results
        except:
          return True
      except urllib2.HTTPError, e:
        print "------------------  Bad server response ----------------"
        print e.headers
        print e
        succeed += 1
      except urllib2.URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        succeed += 1
    return False

  def __build_member_req(url):
    #print "access token: "+self.token
    header = b'Bearer ' + token
    req = urllib2.Request(url)
    req.add_header('Authorization', header)
    return req

  def get_playable_url(track_id):
    print "Rhapsody Plugin: getting playable url"
    url = "%splay/%s" %(S_BASEURL, track_id)
    req = __build_member_req(url)
    results = __get_data_from_rhapsody(req, 5)
    if not results:
      return False
    if results['url'][:5] == u'undef':
      return False
    else:
      return results['url']


  try:
    url = get_playable_url(track)
    #print url
    item = xbmcgui.ListItem(path=url)
    item.setProperty('mimetype','audio/mp4')
    xbmcplugin.setResolvedUrl(int(args[1]), True, item)
    #xbmcplugin.endOfDirectory(plugin_handle)
  except:
    #xbmcplugin.endOfDirectory(plugin_handle)
    pass

