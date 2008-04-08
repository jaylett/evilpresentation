# evil presentations CGI interface
#
# Copyright (C) 2008 James Aylett

"""
evilpresentations' CGI driver.
"""

import Flickr, cgi, cgitb
from jinja import Template, Context, FileSystemLoader

class Driver:
    """evilpresentations' CGI driver; initialise with a Flickr object."""
    def __init__(self, flickr):
        """Initialise driver."""
        self.flickr = flickr

    def do_get(self):
        """Process a GET request."""
        cgitb.enable()

        start = self.flickr.get_photos('start')
        middle = self.flickr.get_photos('middle', 8)
        end = self.flickr.get_photos('end')

        photos = []
        photos.extend(start)
        photos.extend(middle)
        photos.extend(end)

        tmpl = Template('presentation', FileSystemLoader('.'))
        c = Context({'photos':photos})
        print tmpl.render(c)
