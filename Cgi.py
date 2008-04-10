# evil presentations CGI interface
#
# Copyright (C) 2008 James Aylett

"""
evilpresentations' CGI driver.
"""

import Flickr, cgi, cgitb, os, time, urllib
from jinja import Template, Context, FileSystemLoader

class Driver:
    """evilpresentations' CGI driver; initialise with a Flickr object."""
    def __init__(self, flickr, install_dir):
        """Initialise driver."""
        self.flickr = flickr
        self.install_dir = install_dir

    def process_request(self):
        """Process an HTTP request."""
        cgitb.enable()
        method = os.environ.get('REQUEST_METHOD', 'GET')

        p = os.environ.get('PATH_INFO', '')

        p = p.split('/')
        p = map(lambda x: urllib.unquote_plus(x), p)

        if method=='GET':
            self.do_get(p)
        elif method=='POST':
            self.do_post(p)
        else:
            print "Status: 405 No, that ain't gonna work"
            # FIXME: should detect if POST is allowed...
            print "Allow: GET"
            print

    def do_post(self, p):
        """Process a POST request."""

        if p[1]=='presentation':
            self.make_presentation(p[2:])
        else:
            print "Status: 405 Never with POST, pretty boy"
            print "Allow: GET"
            print

    def do_get(self, p):
        """Process a GET request."""

        if p[1]=='presentation':
            self.do_presentation(p[2:])
        else:
            self.do_index()

    def do_index(self):
        tmpl = Template('index', FileSystemLoader(self.install_dir))
        c = Context()
        print "Content-Type: text/html; charset=utf-8"
        print
        print tmpl.render(c)

    def _get_photos(self, p):
        start = self.flickr.get_photos('start')
        middle = self.flickr.get_photos('middle', 8)
        end = self.flickr.get_photos('end')

        photos = []
        photos.extend(start)
        photos.extend(middle)
        photos.extend(end)

        return photos

    def _extract_metadata(self, p):
        affiliation = ''

        try:
            presenter = p[0]
            presenter = presenter.split(';')
            if len(presenter)>1:
                affiliation = presenter[1]
            presenter = presenter[0]
        except IndexError:
            presenter = ''
        dateline = time.strftime('%A %B %d, %Y')
        try:
            title = p[1]
        except IndexError:
            title = dateline
            dateline = ''

        return {'dateline': dateline, 'title': title, 'presenter': presenter, 'affiliation': affiliation}

    def make_presentation(self, p):
        photos = self._get_photos(p)
        metadata = self._extract_metadata(p)
        metadata['photos'] = photos

        print "Status: 201 Yeah, I've done it already"
        print "Location: " + self._make_uri(metadata)
        print

    def _make_uri(self, metadata):
        # FIXME
        return '/wibble'

    def do_presentation(self, p):
        # FIXME: cope with whatever _make_uri returns
        photos = self._get_photos(p)
        metadata = self._extract_metadata(p)
        metadata['photos'] = photos

        tmpl = Template('presentation', FileSystemLoader(self.install_dir))
        c = Context(metadata)
        print "Content-Type: text/html; charset=utf-8"
        print
        print tmpl.render(c)
