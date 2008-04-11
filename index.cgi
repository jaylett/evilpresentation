#!/usr/bin/python
#
# evil presentations runner
#
# Copyright (C) 2008 James Aylett

install_dir = '/home/james/projects/sja/evilpresentation'

import sys
sys.path.append(install_dir)

import Flickr, Cgi, Config

api_key = Config.api_key

f = Flickr.Flickr(api_key)
c = Cgi.Driver(f, install_dir)
c.process_request()
