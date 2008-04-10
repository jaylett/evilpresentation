#!/usr/bin/python
#
# evil presentations runner
#
# Copyright (C) 2008 James Aylett

install_dir = '/home/james/projects/sja/evilpresentation'

import sys
sys.path.append(install_dir)

import Flickr, Cgi

api_key = '724e7d87e4cda750215d7c9e192adee3'

f = Flickr.Flickr(api_key)
c = Cgi.Driver(f, install_dir)
c.do_get()
