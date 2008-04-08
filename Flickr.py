# Simple interface to the bits of Flickr we need.
#
# Copyright (C) 2008 James Aylett

"""Talk to Flickr. Make it less painful than it really is."""

import urllib, urllib2, os, os.path, sys, json, random
import datetime, time, smtplib, textwrap, pwd, getopt

try:
    from xml.etree.ElementTree import fromstring as etree_fromstring # python 2.5
except:
    from elementtree.ElementTree import fromstring as etree_fromstring # python 2.4

class FlickrError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Flickr:
    def __init__(self, key):
        self.key = key

    def get_photos(self, photo_type, number=1):
        fetch = 500 # number*2
        photos = self.find_photos_by_machine_tag('evil:purpose=%s' % photo_type, fetch)
        if len(photos) < number:
            number = len(photos)
        return random.sample(photos, number)

    def find_photos_by_machine_tag(self, mtag, number):
        # FIXME: shouldn't *really* hard-code the license ids
        data = self.call_api('flickr.photos.search', { 'sort': 'random', 'machine_tags': mtag, 'per_page': number }) # commercial use only
        #data = self.call_api('flickr.photos.search', { 'sort': 'random', 'machine_tags': mtag, 'license': '4,5,6', 'per_page': number }) # commercial use only
        photos = etree_fromstring(data)
        if photos.tag!='rsp':
            raise FlickrError('XML looks all funny (rsp missing)!')
        if photos.get('stat')!='ok':
            raise FlickrError('XML looks all funny (stat=%s)!' % photos.get('stat'))
        photos = photos[0]
        if photos.tag!='photos':
            raise FlickrError('XML looks all funny (photos missing)!')
        res = []
        for photo in photos:
            if photo.tag!='photo':
                next
            photo_uri = 'http://farm%s.static.flickr.com/%s/%s_%s.jpg' % (photo.get('farm'), photo.get('server'), photo.get('id'), photo.get('secret'))
            user_uri = 'http://flickr.com/people/%s/' % photo.get('owner')
            res.append([photo_uri, photo.get('title'), user_uri])
        return res

    def call_api(self, call, args):
        uri = 'http://api.flickr.com/services/rest/?api_key=%s&method=%s' % (urllib.quote_plus(self.key), urllib.quote_plus(call))

        uri += '&' + reduce(lambda x,y: x + '&' + y, map(lambda x: urllib.quote_plus(str(x)) + '=' + urllib.quote_plus(str(args[x])), args.keys()))
        f = urllib2.urlopen(uri)
        d = f.read()
        f.close()
        return d
