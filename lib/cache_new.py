import pickle
import time
import os
from rhapapi import Api

## sould be a wrapper for rhapapi

class newCache(object):
    def __init__(self):
        pass



    def get_album_review(self, album_id):
        print "Rhapapi: getting album review"
        url = "%salbums/%s/reviews?apikey=%s&catalog=%s" % (self.BASEURL, album_id, self.APIKEY, self.app.mem.catalog)
        req = self.__build_req(url)
        results = self.__get_data_from_rhapsody(req, 10)
        if results:
            return utils.remove_html_markup(results[0]["body"])
        else:
            return False
