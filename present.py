#!/usr/bin/python
#
# evil presentations runner
#
# Copyright (C) 2008 James Aylett

import sys
sys.path.append('/home/james/projects/sja/evilpresentation')

import Flickr, Cgi

api_key = '724e7d87e4cda750215d7c9e192adee3'

f = Flickr.Flickr(api_key)
c = Cgi.Driver(f)
c.do_get()
